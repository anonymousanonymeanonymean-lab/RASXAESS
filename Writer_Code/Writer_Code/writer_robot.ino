/*
 * WRITER ROBOT — Boustrophedon ("snake") exploration
 * ----------------------------------------------------------------
 * Target: ESP32 (plain DevKit, e.g. WROOM-32) + Arduino framework.
 *
 * ESP32 specifics baked into the pin map and thresholds below:
 *  - GPIO21/GPIO22 are reserved for I2C (Wire.begin default SDA/SCL) since
 *    the MPU6050 sits on that bus — nothing else uses those two pins.
 *  - GPIO34/35/36 are ADC1, input-only, used only for analogRead (gas +
 *    2 mics). They can't be outputs, which is fine since they never are.
 *  - Boot "strapping" pins (0, 2, 5, 12, 15) are avoided entirely for the
 *    ultrasonic/motor lines, since those can misbehave if pulled a
 *    certain way at power-on.
 *  - analogRead() on the ESP32 is 12-bit (0-4095) by default, not the
 *    10-bit (0-1023) you'd get on an Uno — GAS_ALERT_DELTA below is scaled
 *    for that, but still needs recalibrating against your actual sensor.
 *  - If you're using an ESP32-CAM board instead of a plain DevKit, note
 *    that its camera interface already claims most GPIOs, leaving too few
 *    free for this many sensors + motors. The usual fix is two boards: an
 *    ESP32-CAM dedicated to video, and a second plain ESP32 (this sketch)
 *    driving navigation/sensors/motors, talking to each other over
 *    UART/I2C/ESP-NOW if they need to share anything.
 * Sensors on THIS board: 3x HC-SR04 ultrasonic (front/left/right), MPU6050
 * gyroscope, analog gas sensor (MQ-x), 4 drive motors.
 *
 * The camera and the 2 microphones live on a separate Raspberry Pi, which
 * has the compute budget for real keyword spotting ("help"/"au secours")
 * and left/right mic-amplitude comparison — this board just executes what
 * the Pi asks for. The two boards talk over Serial2 (UART), see the
 * PI LINK section below for the wire protocol.
 *
 * Division of responsibility: the Pi decides WHERE the sound is (it owns
 * the mics) and tells this board to steer left/right/forward; this board
 * still enforces its own front-ultrasonic safety stop regardless of what
 * the Pi asks for, and times out to a full stop if the Pi link goes
 * quiet — a bad or lost link should never make the robot run blind.
 *
 * Coordinate frame: the entry door is the local origin (0,0). Position is
 * estimated purely by dead-reckoning (gyro heading + time*speed for
 * distance) — there is no GPS indoors. This drifts the longer the robot
 * travels without a correction, which is exactly why, on the command-post
 * side, a position is only trusted as "confirmed" once a beacon has
 * relayed it back through the mesh — everything beyond that is shown as
 * a growing uncertainty zone, not a precise dot.
 *
 * Navigation pattern: forward until the front sensor reports a wall, then
 * a double turn (turn -> short sidestep -> same-direction turn again) to
 * step into the next row, reversing travel direction. The turn direction
 * of this pair ALTERNATES at every row end (right-right, then left-left,
 * then right-right, ...). This is the part that's easy to get backwards:
 * a FIXED turn direction makes the sidestep flip north/south/north/south
 * every row, so the robot just oscillates over the same two strips and
 * never covers the rest of the room. Alternating keeps the sidestep going
 * the same way every time, so each row is a genuinely new strip — the
 * same reason a real lawnmower turns opposite ways at opposite ends.
 *
 * Interrupts to the pattern:
 *   - A loud/"help"-like sound pauses coverage, the robot turns toward the
 *     loudest direction, approaches, logs the position, then returns to
 *     the exact pose where it paused and resumes coverage from there.
 *   - A gas reading is tracked passively and continuously; no detour is
 *     needed, we just remember where the strongest reading was recorded.
 * ----------------------------------------------------------------
 */

#include <Wire.h>
#include <MPU6050.h>

// =================================================================
// PIN CONFIG — adjust to your wiring
// =================================================================
// GPIO21 (SDA) and GPIO22 (SCL) are intentionally NOT used below — they're
// reserved for the MPU6050's I2C bus (see Wire.begin(21, 22) in setup()).
#define US_FRONT_TRIG 13
#define US_FRONT_ECHO 14
#define US_LEFT_TRIG  27
#define US_LEFT_ECHO  26
#define US_RIGHT_TRIG 25
#define US_RIGHT_ECHO 33

#define GAS_SENSOR_PIN 34   // analog (ADC1, input-only)

#define PI_LINK_RX 16  // ESP32 Serial2 RX  <- Pi TX
#define PI_LINK_TX 17  // ESP32 Serial2 TX  -> Pi RX
#define PI_LINK_BAUD 115200

#define MOTOR_LEFT_FWD  32
#define MOTOR_LEFT_BWD  4
#define MOTOR_RIGHT_FWD 18
#define MOTOR_RIGHT_BWD 19

// =================================================================
// TUNABLE PARAMETERS — calibrate on your actual robot
// =================================================================
const float WALL_STOP_CM      = 15.0;  // front distance considered "blocked"
const float SIDE_CLEAR_CM     = 12.0;  // min clearance needed during a sidestep
const float ROW_STEP_CM       = 25.0;  // lateral spacing between coverage rows
const float FORWARD_SPEED_CMS = 12.0;  // cm/s at your drive PWM — measure this
const int   GAS_ALERT_DELTA   = 160;   // rise above baseline considered "near source" (0-4095 scale)
// GAS_ALERT_DELTA is a rough starting point — print raw analogRead() values
// over Serial with your actual gas sensor module and recalibrate before
// relying on it. SOUND_THRESHOLD / mic deadband now live on the Pi.
const float ARRIVED_TOL_CM    = 8.0;   // tolerance when returning to a saved pose
const unsigned long STEER_TIMEOUT_MS   = 800;  // stop if no STEER msg from Pi in this long
const unsigned long TELEMETRY_PERIOD_MS = 200; // how often to send POSE to the Pi

enum TurnDir { DIR_LEFT = -1, DIR_RIGHT = 1 };

// =================================================================
// TYPES
// =================================================================
struct Pose { float x; float y; float heading; }; // heading in degrees

enum RobotState {
  SNAKE_FORWARD,
  SNAKE_TURN_1,
  SNAKE_SIDESTEP,
  SNAKE_TURN_2,
  APPROACH_SOUND,
  RETURN_TO_PAUSE,
  MISSION_DONE
};

enum ReturnSubState { RTURN_AIM, RTURN_DRIVE };
enum BeaconType { BEACON_HAZARD, BEACON_VICTIM, BEACON_STRUCTURAL };

// =================================================================
// GLOBAL STATE
// =================================================================
RobotState state = SNAKE_FORWARD;
RobotState stateBeforeInterrupt = SNAKE_FORWARD; // resume snake exactly where it paused

Pose pose = {0, 0, 0};     // entry door = local origin (0,0)
Pose pausedPose;           // saved pose when a sound interrupt fires
Pose sidestepStartPose;    // marks the start of the current sidestep, to measure ROW_STEP_CM

// Alternates after every completed row-end turn pair (right-right, then
// left-left, then right-right, ...) so the sidestep always progresses the
// same physical direction across the room instead of flipping back and forth.
TurnDir rowTurnDir = DIR_LEFT;

unsigned long lastPoseUpdate = 0;
float turnTargetHeading = 0;

// Tracks what the LAST motor command actually was, so updatePose() only
// accumulates forward distance on ticks where the robot really moved
// forward — important now that sound-approach mixes turn-nudge and
// forward ticks within the same state.
bool lastActionWasForward = false;

// return-to-pause sub-state
ReturnSubState returnSub = RTURN_AIM;

// ---- link to the Raspberry Pi (sound localization + keyword spotting) ----
HardwareSerial PiLink(2); // ESP32 UART2
enum SteerCmd { STEER_NONE, STEER_FWD, STEER_LEFT, STEER_RIGHT, STEER_ARRIVED };
SteerCmd lastSteerCmd = STEER_NONE;
unsigned long lastSteerMsgTime = 0;
unsigned long lastTelemetryTime = 0;
String piRxBuffer = "";
bool helpEventPending = false;

// gas tracking
int gasBaseline = 0;
int gasMaxReading = 0;
Pose gasSourcePose;
bool gasSourceLogged = false;

// victim tracking
Pose lastVictimPose;
int victimCount = 0;

MPU6050 mpu;

// =================================================================
// SETUP / LOOP
// =================================================================
void setup() {
  Serial.begin(115200);
  PiLink.begin(PI_LINK_BAUD, SERIAL_8N1, PI_LINK_RX, PI_LINK_TX);
  Wire.begin(21, 22); // SDA, SCL — reserved for the MPU6050, see pin map above
  mpu.initialize();

  pinMode(US_FRONT_TRIG, OUTPUT); pinMode(US_FRONT_ECHO, INPUT);
  pinMode(US_LEFT_TRIG, OUTPUT);  pinMode(US_LEFT_ECHO, INPUT);
  pinMode(US_RIGHT_TRIG, OUTPUT); pinMode(US_RIGHT_ECHO, INPUT);
  pinMode(MOTOR_LEFT_FWD, OUTPUT);  pinMode(MOTOR_LEFT_BWD, OUTPUT);
  pinMode(MOTOR_RIGHT_FWD, OUTPUT); pinMode(MOTOR_RIGHT_BWD, OUTPUT);

  calibrateGas();
  lastPoseUpdate = millis();
  Serial.println("Writer robot ready. Entry door = (0,0). Starting coverage.");
}

void loop() {
  updatePose();          // dead-reckoning runs every cycle, in every state
  trackGasLeak();        // passive — just watches for the strongest reading so far
  pollPiLink();           // read any pending messages from the Pi
  sendTelemetryIfDue();   // keep the Pi updated on pose/gas/front distance

  // The Pi confirmed a "help" keyword — pollPiLink() sets helpEventPending.
  // This interrupts the snake pattern from any state except while we're
  // already responding to one.
  if (state != APPROACH_SOUND && state != RETURN_TO_PAUSE && helpEventPending) {
    helpEventPending = false;
    Serial.println("Pi confirmed a call for help — pausing coverage pattern.");
    pausedPose = pose;
    stateBeforeInterrupt = state;
    stopMotors();
    lastSteerCmd = STEER_NONE;
    lastSteerMsgTime = millis();
    state = APPROACH_SOUND;
  }

  switch (state) {
    case SNAKE_FORWARD:   runSnakeForward();                       break;
    case SNAKE_TURN_1:    runTurn(SNAKE_SIDESTEP, true);           break;
    case SNAKE_SIDESTEP:  runSidestep();                           break;
    case SNAKE_TURN_2:    runTurn(SNAKE_FORWARD, false);           break;
    case APPROACH_SOUND:  runApproachSound();                      break;
    case RETURN_TO_PAUSE: runReturnToPause();                      break;
    case MISSION_DONE:    stopMotors();                            break;
  }
}

// =================================================================
// POSE ESTIMATION (gyro heading + time-based distance)
// =================================================================
void updatePose() {
  unsigned long now = millis();
  float dt = (now - lastPoseUpdate) / 1000.0;
  lastPoseUpdate = now;

  int16_t gx, gy, gz;
  mpu.getRotation(&gx, &gy, &gz);
  float gyroZ_dps = gz / 131.0; // MPU6050 default sensitivity @ +/-250 deg/s
  pose.heading = normalizeAngle(pose.heading + gyroZ_dps * dt);

  if (lastActionWasForward) {
    float dist = FORWARD_SPEED_CMS * dt;
    pose.x += dist * cos(radians(pose.heading));
    pose.y += dist * sin(radians(pose.heading));
  }
}

// =================================================================
// SNAKE / BOUSTROPHEDON NAVIGATION
// =================================================================
void runSnakeForward() {
  if (readUltrasonicCM(US_FRONT_TRIG, US_FRONT_ECHO) < WALL_STOP_CM) {
    stopMotors();
    turnTargetHeading = normalizeAngle(pose.heading + 90 * rowTurnDir);
    state = SNAKE_TURN_1;
  } else {
    moveForward();
  }
}

// isFirstTurn marks the sidestep origin once the first of the two turns completes.
// When the SECOND turn of the pair completes (isFirstTurn == false), flip
// rowTurnDir so the NEXT row-end turns the opposite way.
void runTurn(RobotState nextState, bool isFirstTurn) {
  if (angleReached(pose.heading, turnTargetHeading)) {
    stopMotors();
    if (isFirstTurn) {
      sidestepStartPose = pose;
    } else {
      rowTurnDir = (rowTurnDir == DIR_LEFT) ? DIR_RIGHT : DIR_LEFT;
    }
    state = nextState;
  } else {
    turnInPlace(rowTurnDir);
  }
}

void runSidestep() {
  float traveled = distanceBetween(pose, sidestepStartPose);
  float sideReading = readUltrasonicCM(US_FRONT_TRIG, US_FRONT_ECHO); // now facing sideways

  if (sideReading < SIDE_CLEAR_CM) {
    // Hit the room's boundary while trying to step into the next row —
    // there is no further row to cover.
    stopMotors();
    state = MISSION_DONE;
    Serial.println("Side boundary reached during step-over — area fully covered.");
    return;
  }

  if (traveled >= ROW_STEP_CM) {
    stopMotors();
    turnTargetHeading = normalizeAngle(pose.heading + 90 * rowTurnDir);
    state = SNAKE_TURN_2;
  } else {
    moveForward();
  }
}

// =================================================================
// SOUND SOURCE APPROACH — driven by the Pi over the serial link
// The Pi owns the mics and sends a fresh STEER command whenever its L/R
// comparison updates (see pollPiLink()). This board just executes the
// latest command, but two local safeguards always win: the front
// ultrasonic (never drive into a wall just because the Pi said forward),
// and a timeout (if the Pi goes quiet, stop rather than keep coasting on
// a stale command).
// =================================================================
void runApproachSound() {
  float frontDist = readUltrasonicCM(US_FRONT_TRIG, US_FRONT_ECHO);
  bool linkStale = (millis() - lastSteerMsgTime) > STEER_TIMEOUT_MS;

  if (frontDist < WALL_STOP_CM || lastSteerCmd == STEER_ARRIVED) {
    // Close to an obstacle, or the Pi told us we've arrived.
    stopMotors();
    lastVictimPose = pose;
    victimCount++;
    Serial.print("Victim position logged: (");
    Serial.print(pose.x); Serial.print(", "); Serial.print(pose.y); Serial.println(")");
    dropBeacon(BEACON_VICTIM, pose.x, pose.y);
    state = RETURN_TO_PAUSE;
    returnSub = RTURN_AIM;
    return;
  }

  if (linkStale) {
    stopMotors(); // Pi link went quiet — don't keep acting on a stale command
    return;
  }

  switch (lastSteerCmd) {
    case STEER_LEFT:  turnInPlace(DIR_LEFT);  break;
    case STEER_RIGHT: turnInPlace(DIR_RIGHT); break;
    case STEER_FWD:   moveForward();          break;
    default:          stopMotors();           break; // no command yet
  }
}

// =================================================================
// RETURN TO THE POINT WHERE THE SNAKE PATTERN WAS INTERRUPTED
// =================================================================
void runReturnToPause() {
  float dx = pausedPose.x - pose.x;
  float dy = pausedPose.y - pose.y;
  float dist = sqrt(dx * dx + dy * dy);

  if (dist < ARRIVED_TOL_CM) {
    stopMotors();
    pose.heading = pausedPose.heading; // snap back to the heading the snake pattern expects
    state = stateBeforeInterrupt;      // resume coverage exactly where it paused
    Serial.println("Back at pause point — resuming coverage pattern.");
    return;
  }

  float targetHeading = degrees(atan2(dy, dx));
  float diff = angularDiff(pose.heading, targetHeading);

  if (returnSub == RTURN_AIM) {
    if (fabs(diff) < 3.0) {
      returnSub = RTURN_DRIVE;
    } else {
      turnInPlace(diff > 0 ? DIR_RIGHT : DIR_LEFT);
    }
  } else {
    // Minimal obstacle handling on the way back — re-aim if something blocks the path.
    // TODO: replace with real local avoidance/replanning for a cluttered interior.
    if (readUltrasonicCM(US_FRONT_TRIG, US_FRONT_ECHO) < WALL_STOP_CM) {
      returnSub = RTURN_AIM;
    } else {
      moveForward();
    }
  }
}

// =================================================================
// GAS LEAK TRACKING (passive — runs continuously while exploring)
// =================================================================
void calibrateGas() {
  long sum = 0;
  const int N = 50;
  for (int i = 0; i < N; i++) { sum += analogRead(GAS_SENSOR_PIN); delay(20); }
  gasBaseline = sum / N;
  gasMaxReading = gasBaseline;
}

void trackGasLeak() {
  int reading = analogRead(GAS_SENSOR_PIN);
  if (reading > gasMaxReading) {
    gasMaxReading = reading;
    gasSourcePose = pose;
    gasSourceLogged = false;
  }
  if (!gasSourceLogged && (gasMaxReading - gasBaseline) > GAS_ALERT_DELTA) {
    gasSourceLogged = true;
    Serial.print("Gas source candidate at (");
    Serial.print(gasSourcePose.x); Serial.print(", "); Serial.print(gasSourcePose.y);
    Serial.println(") -- strongest reading so far.");
    dropBeacon(BEACON_HAZARD, gasSourcePose.x, gasSourcePose.y);
  }
}

// =================================================================
// RASPBERRY PI LINK — simple text protocol over Serial2, one message
// per line, comma-separated, newline-terminated. Kept as plain text
// (not binary) so it's easy to read on a logic analyzer / serial monitor
// while debugging the wiring.
//
// Pi -> ESP32:
//   HELP                      keyword "help" confirmed, start approach
//   STEER,LEFT|RIGHT|FWD      steering update while approaching
//   ARRIVED                   Pi is confident we've reached the source
//
// ESP32 -> Pi (see sendTelemetryIfDue):
//   POSE,x,y,heading,state,front_cm,gas_reading
//   BEACON,type,x,y           whenever dropBeacon() fires, for Pi-side logging
// =================================================================
void pollPiLink() {
  while (PiLink.available()) {
    char c = PiLink.read();
    if (c == '\n') {
      handlePiMessage(piRxBuffer);
      piRxBuffer = "";
    } else if (c != '\r') {
      piRxBuffer += c;
      if (piRxBuffer.length() > 64) piRxBuffer = ""; // guard against a corrupt/unterminated line
    }
  }
}

void handlePiMessage(const String &line) {
  if (line == "HELP") {
    helpEventPending = true;
  } else if (line.startsWith("STEER,")) {
    String dir = line.substring(6);
    lastSteerMsgTime = millis();
    if (dir == "LEFT")       lastSteerCmd = STEER_LEFT;
    else if (dir == "RIGHT") lastSteerCmd = STEER_RIGHT;
    else if (dir == "FWD")   lastSteerCmd = STEER_FWD;
  } else if (line == "ARRIVED") {
    lastSteerCmd = STEER_ARRIVED;
    lastSteerMsgTime = millis();
  }
}

void sendTelemetryIfDue() {
  unsigned long now = millis();
  if (now - lastTelemetryTime < TELEMETRY_PERIOD_MS) return;
  lastTelemetryTime = now;

  float frontDist = readUltrasonicCM(US_FRONT_TRIG, US_FRONT_ECHO);
  PiLink.print("POSE,");
  PiLink.print(pose.x);   PiLink.print(",");
  PiLink.print(pose.y);   PiLink.print(",");
  PiLink.print(pose.heading); PiLink.print(",");
  PiLink.print((int)state);   PiLink.print(",");
  PiLink.print(frontDist);    PiLink.print(",");
  PiLink.println(gasMaxReading);
}

// =================================================================
// BEACON HANDOFF — bridges into your beacon/RF module
// =================================================================
void dropBeacon(BeaconType type, float x, float y) {
  // TODO: build the full beacon frame (type, x, y, timestamp, message) and
  // hand it to your RF module (e.g. LoRa) to actually deposit/broadcast it.
  Serial.print("[BEACON] type="); Serial.print(type);
  Serial.print(" pos=("); Serial.print(x); Serial.print(","); Serial.print(y);
  Serial.println(")");

  PiLink.print("BEACON,"); PiLink.print(type); PiLink.print(",");
  PiLink.print(x); PiLink.print(","); PiLink.println(y);
}

// =================================================================
// LOW-LEVEL HARDWARE HELPERS
// =================================================================
void moveForward() {
  lastActionWasForward = true;
  digitalWrite(MOTOR_LEFT_FWD, HIGH);  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, HIGH); digitalWrite(MOTOR_RIGHT_BWD, LOW);
}

void turnInPlace(TurnDir dir) {
  lastActionWasForward = false;
  if (dir == DIR_LEFT) {
    digitalWrite(MOTOR_LEFT_FWD, LOW);   digitalWrite(MOTOR_LEFT_BWD, HIGH);
    digitalWrite(MOTOR_RIGHT_FWD, HIGH); digitalWrite(MOTOR_RIGHT_BWD, LOW);
  } else {
    digitalWrite(MOTOR_LEFT_FWD, HIGH);  digitalWrite(MOTOR_LEFT_BWD, LOW);
    digitalWrite(MOTOR_RIGHT_FWD, LOW);  digitalWrite(MOTOR_RIGHT_BWD, HIGH);
  }
}

void stopMotors() {
  lastActionWasForward = false;
  digitalWrite(MOTOR_LEFT_FWD, LOW);  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, LOW); digitalWrite(MOTOR_RIGHT_BWD, LOW);
}

float readUltrasonicCM(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 30000); // 30ms timeout (~5m range)
  if (duration == 0) return 999.0; // no echo = treat as clear
  return duration * 0.0343f / 2.0f;
}

float normalizeAngle(float a) {
  return fmod(fmod(a, 360.0) + 360.0, 360.0);
}

float angularDiff(float from, float to) {
  return fmod((to - from) + 540.0, 360.0) - 180.0;
}

bool angleReached(float current, float target) {
  return fabs(angularDiff(current, target)) < 3.0;
}

float distanceBetween(Pose a, Pose b) {
  float dx = a.x - b.x, dy = a.y - b.y;
  return sqrt(dx * dx + dy * dy);
}

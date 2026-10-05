# TECHNICAL SOLUTION AND ARCHITECTURE

## 1. Proposed Solution

We keep the knowledge in the environment instead of in the robot. The Writer explores without GPS and stores each detected event in a beacon it drops; the beacons relay the event over LoRa to the ONA, which validates it, translates its position and forwards it to the Command Post. The Command Post creates a mission that returns through the ONA to the Executor, which follows the beacons and intervenes. If the network fails, the beacons still hold the data, so the mission can continue.

## 2. Architecture

### 2.1 System Architecture and Data Flow

The system has five subsystems and one rule: there is no direct link between Writer and Executor, Writer and Command Post, or Executor and Command Post. All information goes through the beacons or the ONA. Each subsystem exposes a clear interface (`Robot State` $\rightarrow$ `Event` $\rightarrow$ `Beacon Packet` $\rightarrow$ `Translated Data` $\rightarrow$ `Mission`), so that modules can be developed and tested separately.

* **Uplink data flow:** Detection (Writer) $\rightarrow$ event message $\rightarrow$ beacon storage $\rightarrow$ LoRa transmission (direct or multi-hop relay, with ACK and retry) $\rightarrow$ ONA reception $\rightarrow$ validation (CRC, source, sequence, timestamp) $\rightarrow$ deduplication $\rightarrow$ local storage $\rightarrow$ coordinate and event processing $\rightarrow$ outbox queue (PENDING) $\rightarrow$ MQTT/TLS transmission $\rightarrow$ (marked SENT after acknowledgement) $\rightarrow$ Command Post ingestion $\rightarrow$ live map update.

* **Mission flow:** The Command Post creates a mission and sends it to the ONA, which delivers it to the Executor over LoRa; the Executor enters the zone, reads the beacons along its route and reports completion. If the uplink fails, the beacons keep the data and the Executor recovers it by reading them locally.

### 2.2 Writer Robot Autonomy

The Writer is built around two boards linked by a serial connection (UART or USB).

* **ESP32 (WROOM):** Reads three ultrasonic sensors, a gyroscope and a gas sensor and drives four motors; it keeps the Writer's local frame (X, Y), whose origin is the deployment point, and avoids obstacles and debris.

* **Raspberry Pi:** Handles perception with a camera and two microphones, and an NLP analysis listens for the word "aide" (help).

* **State Machine:** `EXPLORE` $\rightarrow$ `DETECT` $\rightarrow$ `CLASSIFY` $\rightarrow$ `DROP BEACON` $\rightarrow$ `EXPLORE`, with a `RETURN` state when the battery or the beacon stock is low.

The two boards exchange short messages. The ESP32 sends its pose, gas reading and obstacle distance, so that the Pi can attach a local position to any detection; the Pi sends back a help event with a direction, which the ESP32 uses to move toward the voice.

### 2.3 Event Detection and Beacon Deposition

* **Trapped worker:** Detected by the Pi when the word "aide" is heard; the direction estimated from the two microphones is sent to the ESP32, and the robot moves toward the voice while avoiding obstacles.

* **Gas leak:** Detected from the gas concentration, with the source located by following its gradient.

Each detection gets a confidence score and a severity (LOW, MEDIUM or HIGH) and is stamped with the current pose.

**Deposition rule:** The Writer drops a beacon:

1. Every 10 m of travel since the last beacon (value to be set from the measured LoRa range).

2. At junctions and sharp turns.

3. When an event is confirmed.
   The event message is written into that beacon, so that the event is anchored to a physical node whose position is recorded.

### 2.4 Beacon Message and Signal Design

Each beacon is both a memory node and a relay node. In Phase 1 the event message is JSON, which is easy to debug. For transmission, the message is carried by a compact binary frame of 29 bytes, under the 32-byte target.

* **Compact beacon frame (total 29 bytes):**

  * **Header (16 bytes):** protocol version (1), message type (1: EVENT, HEARTBEAT, ACK), mission ID (2), source ID (2), boot ID (2), sequence number (2), timestamp (4), hop count (1), TTL (1).

  * **Payload (11 bytes):** event ID (2), event type (1: 1=GAS_LEAK, 2=TRAPPED_WORKER), severity (1: 0-2), x and y in decimetres in the local ENU frame (2+2), gas ppm (2, 0 for a worker), validity (1).

  * **Check (2 bytes):** CRC-16.

* **Radio and protocol:** An ESP32 with an SX1262 LoRa radio. The lightweight binary protocol provides CRC-16 for integrity, sequence number and boot ID for loss detection, ACK and retry for reliability, deduplication on source ID, boot ID and sequence, and TTL with hop count against loops.

* **Routing:** Beacons support a direct mode (beacon to ONA) and a multi-hop mode with parent-based (gradient) routing.

* **Memory and aging:** Each beacon keeps its events in non-volatile memory. Records are marked stale once their validity has expired.

* **Firmware states:** `BOOT` $\rightarrow$ `RADIO_INIT` $\rightarrow$ `DISCOVERY` $\rightarrow$ `RUNNING` $\leftrightarrow$ `DEGRADED`.

### 2.5 Frame Translation

Beacons store positions in the Writer's local ENU (East, North, Up) frame and never invent GPS coordinates. The ONA converts them with a static anchor: the entrance O has a known GPS position $(\varphi_0, \lambda_0)$ and the heading of the local z-axis (clockwise from North) is calibrated once, denoted as $\psi$.

A local position $(x, y)$ gives:

$$
E = x \sin \psi - y \cos \psi
$$

$$
N = x \cos \psi + y \sin \psi
$$

$$
\varphi = \varphi_0 + \frac{N}{R} \cdot \frac{180}{\pi}
$$

$$
\lambda = \lambda_0 + \frac{E}{R \cos \varphi_0} \cdot \frac{180}{\pi}
$$

Where $R = 6371000 \text{ m}$. If the local frame is already aligned with East and North, $\psi = 0$ and only the second equations apply.

### 2.6 Outside Network Architecture (ONA)

The ONA is the only gateway between the disconnected zone and the Command Post, and it keeps the local radio network isolated from the external network. The ONA validates each frame (CRC, format, source, sequence, timestamp), deduplicates it, stores it in SQLite, processes it (normalisation and coordinate conversion), queues it as PENDING and publishes it through MQTT/TLS, marking it SENT after confirmation. If the WAN is down, the data stay PENDING and are sent automatically on reconnection (store-and-forward).

### 2.7 Command Post

The Command Post is the remote supervision and mission-management layer. It receives the validated, translated events from the ONA over MQTT with TLS and passes them to a Python/FastAPI backend that stores them in a spatial database (SQLite for the prototype, PostgreSQL/PostGIS later). The operator sees them on the Living Map, a web dashboard with layers for robots, beacons, events, communication links and missions, updated in real time. A message-aging mechanism (`NEW` $\rightarrow$ `ACTIVE` $\rightarrow$ `STALE` $\rightarrow$ `EXPIRED/RESOLVED`) separates recent information from outdated memory.

### 2.8 Executor Robot

The Executor receives the mission (target position, type, priority, hazard) through the ONA before entering the zone, with primitives such as `GO_TO`, `AVOID_ZONE`, `STOP` and `RETURN`. It follows the beacon signals to the target, which avoids re-exploring the area, and reads the stored event data locally.

* For a trapped worker: it assesses the scene, removes light debris within a force limit to avoid further collapse, and delivers an oxygen mask and a medical kit.

* For a gas leak: it avoids the gas area given in the mission and activates the filtering or extraction unit.
  If the mission link fails, it can still read beacons on site and use the position given in the mission.

## 3. Technologies Used

| Subsystem | Technologies | 
| ----- | ----- | 
| **Writer robot** | ESP32 (WROOM), 3 ultrasonic sensors, gyroscope, gas sensor, 4 motors; Raspberry Pi, camera, 2 microphones, NLP; UART/USB serial link; LoRa interface | 
| **Beacons** | ESP32 + SX1262 LoRa (prototype), ESP32-S3 on custom PCB (final); binary protocol with CRC-16, ACK/retry, TTL and hop count; parent-based routing; non-volatile memory | 
| **ONA** | PC (prototype) with ESP32 + LoRa on USB/UART, Python (ROS 2 for modular integration), SQLite, MQTT over TLS, Internet (Wi-Fi/4G) | 
| **Command Post** | Python/FastAPI, MQTT over TLS, WebSocket, React, Leaflet or MapLibre, SQLite then PostgreSQL/PostGIS | 
| **Executor robot** | Beacon-guided navigation, debris removal, oxygen mask and medical kit, gas filtering unit | 
| **Development** | Simulation (virtual robots, simulated radio), hardware-in-the-loop tests, GitHub | 

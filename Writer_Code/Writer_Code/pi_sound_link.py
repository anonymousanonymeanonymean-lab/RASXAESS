#!/usr/bin/env python3
"""
Raspberry Pi side: two-mic sound localization + offline keyword spotting,
PLUS camera-based visual survivor detection, linked to the ESP32 (Writer
robot) over a serial cable. Whichever modality currently has the person —
camera or mics — drives the steering; the camera wins when a person is
actually in frame, since a bounding-box offset is a much more precise
direction cue than a left/right amplitude comparison.

Audio hardware assumption: a 2-channel (stereo) input where the LEFT mic
feeds the left channel and the RIGHT mic feeds the right channel. Swap
MIC_LEFT_CH / MIC_RIGHT_CH below if your wiring ends up mirrored.

Keyword spotting uses Vosk (https://alphacephei.com/vosk) for fully
OFFLINE speech recognition — important since the robot has no network
connectivity while exploring.

Visual detection uses OpenCV's DNN module with the MobileNet-SSD Caffe
model (a 20-class detector that includes "person") via the official Pi
Camera Module through picamera2. On a Pi 4 this runs at a few FPS on
small (300x300) frames — plenty for a slow-moving exploration robot.

Setup:
  1. pip install sounddevice numpy vosk pyserial opencv-python picamera2
  2. Download a small Vosk model (e.g. vosk-model-small-fr-0.22 or
     vosk-model-small-en-us-0.15) from https://alphacephei.com/vosk/models,
     unzip it next to this script, point VOSK_MODEL_PATH at the folder.
  3. Get MobileNetSSD_deploy.prototxt + MobileNetSSD_deploy.caffemodel —
     easiest is `git clone https://github.com/djmv/MobilNet_SSD_opencv`,
     which bundles both files directly (original model from
     https://github.com/chuanqi305/MobileNet-SSD). Point MOBILENET_PROTOTXT
     / MOBILENET_MODEL at the two files.
  4. Enable the camera: `sudo raspi-config` -> Interface Options -> Camera
     (or on recent Pi OS it's enabled by default with picamera2).

Protocol with the ESP32 (see writer_robot_navigation.ino, "RASPBERRY PI
LINK" section) — one line per message, comma-separated:
  Pi  -> ESP32 : HELP
                 STEER,LEFT|RIGHT|FWD
                 ARRIVED
  ESP32 -> Pi  : POSE,x,y,heading,state,front_cm,gas_reading
                 BEACON,type,x,y
"""

import sys
import json
import queue
import threading
import time

import numpy as np
import sounddevice as sd
import serial
import cv2
from picamera2 import Picamera2
from vosk import Model, KaldiRecognizer

# =================================================================
# CONFIG — adjust to your hardware
# =================================================================
SERIAL_PORT = "/dev/ttyUSB0"   # ESP32 plugged in via USB; use /dev/serial0 for a GPIO UART wire
SERIAL_BAUD = 115200

SAMPLE_RATE = 16000             # Vosk models expect 16 kHz mono
BLOCK_MS = 100                  # audio callback block size
MIC_LEFT_CH = 0                 # input channel index for the left mic
MIC_RIGHT_CH = 1                # input channel index for the right mic

AMP_DIFF_DEADBAND = 300         # |left-right| RMS below this = "roughly ahead", just advance
ARRIVED_AMP_THRESHOLD = 6000    # RMS level considered "very close to the source"
STEER_SEND_PERIOD_S = 0.2       # how often to send a fresh STEER command while approaching

VOSK_MODEL_PATH = "model"       # path to the unzipped Vosk model folder
HELP_KEYWORDS = ["aide", "secours", "au secours", "help"]
HELP_COOLDOWN_S = 15            # don't re-trigger HELP more than once per this window

# ---- camera / visual person detection ----
MOBILENET_PROTOTXT = "MobileNetSSD_deploy.prototxt"
MOBILENET_MODEL = "MobileNetSSD_deploy.caffemodel"
MOBILENET_CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                      "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                      "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                      "sofa", "train", "tvmonitor"]
PERSON_CLASS_ID = MOBILENET_CLASSES.index("person")

CAMERA_FRAME_SIZE = (320, 240)   # capture resolution — small and fast
DETECT_INPUT_SIZE = (300, 300)   # MobileNet-SSD's expected input size
PERSON_CONFIDENCE = 0.5          # minimum detection confidence to trust
PERSON_CONFIRM_FRAMES = 4        # consecutive confident frames before triggering (debounce)
PERSON_LOST_TIMEOUT_S = 0.6      # if not seen for this long, fall back to audio steering
PERSON_NEAR_HEIGHT_RATIO = 0.75  # bbox height / frame height above this = "close, arrived"
VISUAL_DX_DEADBAND = 0.12        # |dx| below this (as a fraction of half-width) = "roughly centered"

# All numeric thresholds above are rough starting points — print the raw
# values with your actual sensors in your actual room and recalibrate
# before trusting them.

APPROACH_SOUND_STATE = 4        # must match RobotState's enum order in the .ino

# =================================================================
# SHARED STATE
# =================================================================
state_lock = threading.Lock()
latest_amp_left = 0.0
latest_amp_right = 0.0
esp32_state = None              # last RobotState int reported by the ESP32
esp32_pose = (0.0, 0.0, 0.0)
last_help_sent = 0.0            # shared cooldown — either modality can trigger HELP

# Visual detection state. dx is the detected person's horizontal offset
# from frame center, normalized to roughly [-1, 1] (negative = left of
# center). None means no person is currently in frame.
latest_visual_dx = None
latest_visual_near = False
latest_visual_seen_at = 0.0
visual_confirm_streak = 0

ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.05)
audio_queue = queue.Queue()


# =================================================================
# SERIAL LINK TO THE ESP32
# =================================================================
def send_line(line: str):
    ser.write((line + "\n").encode())


def serial_reader_loop():
    """Continuously parse POSE / BEACON lines coming from the ESP32."""
    global esp32_state, esp32_pose
    buf = ""
    while True:
        chunk = ser.read(256).decode(errors="ignore")
        if not chunk:
            continue
        buf += chunk
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if parts[0] == "POSE" and len(parts) >= 7:
                x, y, heading, st, front_cm, gas = parts[1:7]
                with state_lock:
                    esp32_state = int(st)
                    esp32_pose = (float(x), float(y), float(heading))
            elif parts[0] == "BEACON" and len(parts) >= 4:
                btype, bx, by = parts[1], parts[2], parts[3]
                print(f"[beacon] type={btype} pos=({bx},{by})")
                # TODO: forward this to your mission log / Outside Network relay


# =================================================================
# AUDIO — amplitude tracking (for steering) + feeding the recognizer
# =================================================================
def audio_callback(indata, frames, time_info, status):
    global latest_amp_left, latest_amp_right
    if status:
        print(status, file=sys.stderr)

    left = indata[:, MIC_LEFT_CH]
    right = indata[:, MIC_RIGHT_CH]
    with state_lock:
        latest_amp_left = float(np.sqrt(np.mean(left.astype(np.float32) ** 2)))
        latest_amp_right = float(np.sqrt(np.mean(right.astype(np.float32) ** 2)))

    # Feed a mono mix of both mics to the speech recognizer thread.
    mono = ((left.astype(np.int32) + right.astype(np.int32)) // 2).astype(np.int16)
    audio_queue.put(bytes(mono))


def steering_loop():
    """While the ESP32 reports it's in APPROACH_SOUND, keep sending a STEER
    command. If a person is currently visible in the camera, that bounding
    box offset drives the direction — it's a much more precise cue than
    the mic comparison. If no one is in frame right now (occluded by
    debris, around a corner, etc.), fall back to the audio left/right
    comparison. Outside APPROACH_SOUND this just idles."""
    last_sent = 0.0
    while True:
        time.sleep(0.02)
        with state_lock:
            in_approach = (esp32_state == APPROACH_SOUND_STATE)
            left, right = latest_amp_left, latest_amp_right
            vis_dx = latest_visual_dx
            vis_near = latest_visual_near
            vis_fresh = (time.time() - latest_visual_seen_at) < PERSON_LOST_TIMEOUT_S

        if not in_approach:
            continue
        if time.time() - last_sent < STEER_SEND_PERIOD_S:
            continue
        last_sent = time.time()

        if vis_dx is not None and vis_fresh:
            # Camera has the person right now — trust it over the mics.
            if vis_near:
                send_line("ARRIVED")
            elif abs(vis_dx) > VISUAL_DX_DEADBAND:
                send_line("STEER,LEFT" if vis_dx < 0 else "STEER,RIGHT")
            else:
                send_line("STEER,FWD")
            continue

        # No one in frame right now — fall back to audio phonotaxis.
        diff = left - right
        max_amp = max(left, right)
        if max_amp > ARRIVED_AMP_THRESHOLD:
            send_line("ARRIVED")
        elif abs(diff) > AMP_DIFF_DEADBAND:
            send_line("STEER,LEFT" if diff > 0 else "STEER,RIGHT")
        else:
            send_line("STEER,FWD")


# =================================================================
# VISUAL SURVIVOR DETECTION (Pi Camera Module + MobileNet-SSD)
# =================================================================
def vision_loop():
    global latest_visual_dx, latest_visual_near, latest_visual_seen_at, visual_confirm_streak, last_help_sent

    net = cv2.dnn.readNetFromCaffe(MOBILENET_PROTOTXT, MOBILENET_MODEL)

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": CAMERA_FRAME_SIZE, "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()

    frame_w, frame_h = CAMERA_FRAME_SIZE

    while True:
        frame = picam2.capture_array()  # RGB888, shape (h, w, 3)

        blob = cv2.dnn.blobFromImage(frame, 0.007843, DETECT_INPUT_SIZE, 127.5)
        net.setInput(blob)
        detections = net.forward()

        best_conf = 0.0
        best_box = None
        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            class_id = int(detections[0, 0, i, 1])
            if class_id != PERSON_CLASS_ID or confidence < PERSON_CONFIDENCE:
                continue
            if confidence > best_conf:
                best_conf = confidence
                box = detections[0, 0, i, 3:7] * np.array([frame_w, frame_h, frame_w, frame_h])
                best_box = box.astype(int)

        if best_box is not None:
            start_x, start_y, end_x, end_y = best_box
            box_cx = (start_x + end_x) / 2.0
            box_h = end_y - start_y

            dx = (box_cx - frame_w / 2.0) / (frame_w / 2.0)  # normalized [-1, 1]
            near = (box_h / frame_h) > PERSON_NEAR_HEIGHT_RATIO

            with state_lock:
                latest_visual_dx = dx
                latest_visual_near = near
                latest_visual_seen_at = time.time()
                visual_confirm_streak += 1
                streak = visual_confirm_streak
                currently_approaching = (esp32_state == APPROACH_SOUND_STATE)

            if streak >= PERSON_CONFIRM_FRAMES and not currently_approaching:
                now = time.time()
                with state_lock:
                    cooldown_ok = (now - last_help_sent) > HELP_COOLDOWN_S
                if cooldown_ok:
                    with state_lock:
                        last_help_sent = now
                    print(f"[visual] person confirmed (conf={best_conf:.2f}) — triggering approach")
                    send_line("HELP")
        else:
            with state_lock:
                visual_confirm_streak = 0
                # Don't clear latest_visual_dx immediately — PERSON_LOST_TIMEOUT_S
                # in steering_loop handles the "no longer fresh" fallback instead,
                # so a single missed frame doesn't abruptly drop back to audio.


# =================================================================
# KEYWORD SPOTTING (offline, via Vosk)
# =================================================================
def keyword_loop():
    global last_help_sent
    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    while True:
        data = audio_queue.get()
        if rec.AcceptWaveform(data):
            text = json.loads(rec.Result()).get("text", "")
        else:
            text = json.loads(rec.PartialResult()).get("partial", "")

        if not text:
            continue

        if any(kw in text for kw in HELP_KEYWORDS):
            now = time.time()
            if now - last_help_sent > HELP_COOLDOWN_S:
                last_help_sent = now
                print(f'[help] keyword matched in: "{text}"')
                send_line("HELP")


# =================================================================
# MAIN
# =================================================================
def main():
    threading.Thread(target=serial_reader_loop, daemon=True).start()
    threading.Thread(target=steering_loop, daemon=True).start()
    threading.Thread(target=keyword_loop, daemon=True).start()
    threading.Thread(target=vision_loop, daemon=True).start()

    block_size = int(SAMPLE_RATE * BLOCK_MS / 1000)
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=2, dtype="int16",
                         blocksize=block_size, callback=audio_callback):
        print("Listening... (Ctrl+C to stop)")
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()

"""MQTT Command Post simulator.

Publishes a realistic mission scenario to the same topics the ONA uses.
Run:  python mqtt_simulator.py
"""
from __future__ import annotations

import json
import random
import ssl
import time
import uuid
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

import sim_config as cfg


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mk_client() -> mqtt.Client:
    try:
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                        client_id=f"cp-sim-{uuid.uuid4().hex[:6]}",
                        protocol=mqtt.MQTTv5)
    except Exception:
        c = mqtt.Client(client_id=f"cp-sim-{uuid.uuid4().hex[:6]}")
    if cfg.MQTT_USERNAME:
        c.username_pw_set(cfg.MQTT_USERNAME, cfg.MQTT_PASSWORD)
    if cfg.MQTT_TLS:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        c.tls_set_context(ctx)
    return c


def publish(client: mqtt.Client, suffix: str, payload: dict) -> None:
    topic = f"{cfg.TOPIC_BASE}/{suffix}"
    client.publish(topic, json.dumps(payload), qos=1)
    print(f"[SIM] {topic}: {payload.get('event_type', payload.get('source_id',''))}")


def main() -> None:
    print(f"[SIM] Connecting to {cfg.MQTT_BROKER}:{cfg.MQTT_PORT} (TLS={cfg.MQTT_TLS})")
    client = _mk_client()
    client.connect(cfg.MQTT_BROKER, cfg.MQTT_PORT, 60)
    client.loop_start()
    time.sleep(1.0)

    # --- Mission status ---
    publish(client, "status", {
        "mission_id": cfg.MISSION_ID,
        "status": "active",
        "ts": _now(),
    })

    # --- Writer enters, deploys beacons ---
    writer_x = 0.0
    writer_y = 0.0
    for i in range(3):
        writer_x += 5.0
        writer_y += 3.0
        publish(client, "positions", {
            "source_id": "WRITER_01",
            "robot_type": "WRITER",
            "status": "MOVING",
            "frame_id": "FRAME_LOCAL_01",
            "local_x": writer_x,
            "local_y": writer_y,
            "local_z": 0.0,
            "battery": 90 - i * 2,
        })
        time.sleep(1.0)

        bid = f"BEACON_{i+1:02d}"
        publish(client, "status", {
            "beacon_id": bid,
            "mission_id": cfg.MISSION_ID,
            "status": "ONLINE",
            "frame_id": "FRAME_LOCAL_01",
            "local_x": writer_x,
            "local_y": writer_y,
            "battery": 100,
            "hop_count": i,
            "parent_id": "ONA" if i == 0 else f"BEACON_{i:02d}",
            "rssi": -55.0 - i * 3,
            "snr": 9.0 - i * 0.5,
        })
        if i > 0:
            publish(client, "devices", {
                "mission_id": cfg.MISSION_ID,
                "source_id": f"BEACON_{i:02d}",
                "target_id": f"BEACON_{i+1:02d}",
                "rssi": -60.0 - i * 2,
                "snr": 8.5,
                "status": "UP",
            })
        time.sleep(1.0)

    # --- Events ---
    events = [
        ("GAS",      "HIGH",     0.94),
        ("FIRE",     "CRITICAL", 0.96),
        ("VICTIM",   "HIGH",     0.88),
        ("OBSTACLE", "LOW",      0.72),
    ]
    for i, (etype, sev, conf) in enumerate(events):
        payload = {
            "message_id": str(uuid.uuid4()),
            "mission_id": cfg.MISSION_ID,
            "source_id": f"BEACON_{i+1:02d}",
            "source_type": "BEACON",
            "message_type": "EVENT",
            "boot_id": "a3f9",
            "sequence_number": 100 + i,
            "event_timestamp": _now(),
            "frame_id": "FRAME_LOCAL_01",
            "coordinate_reference": "ENU",
            "local_x": writer_x + random.uniform(-3, 3),
            "local_y": writer_y + random.uniform(-3, 3),
            "local_z": 0.0,
            "event_type": etype,
            "severity": sev,
            "confidence": conf,
            "priority": "CRITICAL" if sev == "CRITICAL" else "HIGH",
            "payload": {"note": f"simulated {etype}"},
        }
        publish(client, "events", payload)
        time.sleep(2.0)

    # --- Executor standby ---
    publish(client, "positions", {
        "source_id": "EXECUTOR_01",
        "robot_type": "EXECUTOR",
        "status": "STANDBY",
        "frame_id": "FRAME_LOCAL_01",
        "local_x": 0.0,
        "local_y": 0.0,
        "local_z": 0.0,
        "battery": 100,
    })

    print("[SIM] Scenario done. Sleeping (Ctrl+C to exit).")
    try:
        while True:
            time.sleep(5)
            # keep alive with heartbeats
            publish(client, "positions", {
                "source_id": "WRITER_01",
                "robot_type": "WRITER",
                "status": "IDLE",
                "frame_id": "FRAME_LOCAL_01",
                "local_x": writer_x,
                "local_y": writer_y,
                "local_z": 0.0,
                "battery": 80,
            })
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
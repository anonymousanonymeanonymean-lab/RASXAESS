# ONA — Outside Network Area

**The Living Map: Spatial Memory for Emergency Robots** — TSYP 14 Technical Challenge  
IEEE RAS × IEEE AESS — Tunisia Section

The ONA is the mandatory gateway between a disconnected intervention zone
(Beacons + Writer Robot) and the remote Command Post.

```
BEACON  ──LoRa/Beacon v1.0──▶  ONA  ──MQTT/TLS──▶  COMMAND POST
WRITER  ──LoRa/MAVLink 2  ──▶  ONA  ──MQTT/TLS──▶  COMMAND POST
```

The ONA performs:
`Receive → Decode → Validate → Normalize → Process → Coordinate → Store → Queue → Sync → Transmit`.

---

## Requirements

- Python 3.11+
- Linux / macOS / Windows
- (Optional) Mosquitto broker for MQTT testing

---

## Installation

```bash
git clone <repo-url> ona
cd ona

python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
cp config/config.example.yaml config/config.yaml
```

Edit `.env` and `config/config.yaml` as needed.

---

## Running the ONA

```bash
python -m app.main
```

REST API available at `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

Health check:
```bash
curl http://127.0.0.1:8000/health
```

---

## Running the Simulators

In separate terminals:

```bash
python -m simulator.beacon_simulator
python -m simulator.writer_simulator
python -m simulator.command_post_simulator
```

Phase B: these are stubs. They will emit real frames in later phases.

---

## Tests

```bash
pytest
```

---

## Project Layout

```
app/            Core application code
  communication/  Radio abstraction, protocol handlers, MQTT
  processing/     Validation, normalization, deduplication, coordinates
  database/       SQLite + repositories
  services/       Ingestion, outbox, devices, health
  api/            FastAPI routes & schemas
  config/         Settings + logging
  utils/          IDs, time, checksums
simulator/      Beacon / Writer / Command Post simulators
tests/          Unit / integration / protocol / system tests
config/         Functional YAML configuration
```

---

## Architecture Principles

- **Hardware independence**: `RadioInterface` with `SerialLoRaRadio` and `SimulatedRadio`.
- **Protocol independence**: internal `MissionMessage` model.
- **Store-and-forward**: SQLite + persistent Outbox (Phase G).
- **No silent failures**: every validation step yields an explicit status.
- **No invented GPS**: coordinates stay local unless a frame transformation is validated.

---

## Development Order

Phase A — Architecture ✅  
Phase B — Skeleton ✅ (this)  
Phase C — Data model + SQLite schema  
Phase D — Beacon Protocol v1.0  
Phase E — MAVLink 2  
Phase F — Validation pipeline + CoordinateManager  
Phase G — Store-and-forward / Outbox  
Phase H — MQTT/TLS  
Phase I — REST API complete  
Phase J — Simulators complete  
Phase K — Failure injection  
Phase L — Integration tests

---

## License

Prototype for TSYP 14 — The Living Map.
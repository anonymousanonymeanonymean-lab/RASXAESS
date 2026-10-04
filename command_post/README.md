# COMMAND POST — TSYP 14 "The Living Map"

Real-time operational picture + spatial memory visualization for emergency robotics.

```
BEACON / WRITER → ONA → MQTT/TLS → COMMAND POST → OPERATOR
```

## Components
- **backend** — FastAPI, SQLite, MQTT ingestion, REST, WebSocket
- **simulator** — MQTT publisher (testable without ONA)
- **frontend** — React + TypeScript + Vite + Leaflet (Living Map)

## Quick start
```bash
cp .env.example .env             # configure
cd simulator && pip install -r requirements.txt
python mqtt_simulator.py         # in one terminal
cd ../backend && pip install -r requirements.txt
uvicorn app.main:app --reload    # in another
cd ../frontend && npm install && npm run dev
```

Open http://localhost:5173
"""Configuration system. Secrets via .env only."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env", override=False)


class Settings(BaseModel):
    mission_id: str = "mission_default"
    mission_name: str = "Command Post Mission"
    environment: str = "urban_sar"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    db_path: str = "./data/command_post.db"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]

    mqtt_enabled: bool = True
    mqtt_broker: str = ""
    mqtt_port: int = 8883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_ca_cert: str = ""
    mqtt_client_id: str = "command-post-01"
    mqtt_qos: int = 1
    mqtt_tls: bool = True

    aging_new_seconds: int = 10
    aging_active_seconds: int = 60
    aging_recent_seconds: int = 300
    aging_stale_seconds: int = 900


def _bool(v: str | None, default: bool = False) -> bool:
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def load_settings() -> Settings:
    origins = os.getenv("CP_CORS_ORIGINS", "http://localhost:5173")
    s = Settings(
        mission_id=os.getenv("CP_MISSION_ID", "mission_default"),
        mission_name=os.getenv("CP_MISSION_NAME", "Command Post Mission"),
        environment=os.getenv("CP_ENVIRONMENT", "urban_sar"),
        api_host=os.getenv("CP_API_HOST", "0.0.0.0"),
        api_port=int(os.getenv("CP_API_PORT", "8000")),
        db_path=os.getenv("CP_DB_PATH", "./data/command_post.db"),
        log_level=os.getenv("CP_LOG_LEVEL", "INFO"),
        cors_origins=[o.strip() for o in origins.split(",") if o.strip()],
        mqtt_enabled=_bool(os.getenv("CP_MQTT_ENABLED"), True),
        mqtt_broker=os.getenv("MQTT_BROKER", ""),
        mqtt_port=int(os.getenv("MQTT_PORT", "8883")),
        mqtt_username=os.getenv("MQTT_USERNAME", ""),
        mqtt_password=os.getenv("MQTT_PASSWORD", ""),
        mqtt_ca_cert=os.getenv("MQTT_CA_CERT", ""),
        mqtt_client_id=os.getenv("MQTT_CLIENT_ID", "command-post-01"),
        mqtt_qos=int(os.getenv("MQTT_QOS", "1")),
        mqtt_tls=_bool(os.getenv("MQTT_TLS"), True),
        aging_new_seconds=int(os.getenv("CP_AGING_NEW_SECONDS", "10")),
        aging_active_seconds=int(os.getenv("CP_AGING_ACTIVE_SECONDS", "60")),
        aging_recent_seconds=int(os.getenv("CP_AGING_RECENT_SECONDS", "300")),
        aging_stale_seconds=int(os.getenv("CP_AGING_STALE_SECONDS", "900")),
    )
    Path(s.db_path).parent.mkdir(parents=True, exist_ok=True)
    return s
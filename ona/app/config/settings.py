"""ONA configuration system.

Loads secrets from .env and functional config from config/config.yaml.
Environment variables override YAML values for deployment flexibility.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"
EXAMPLE_CONFIG_PATH = CONFIG_DIR / "config.example.yaml"


class RadioConfig(BaseModel):
    backend: str = "simulated"
    port: Optional[str] = None
    baudrate: int = 115200
    frequency_hz: int = 868_000_000
    bandwidth_hz: int = 125_000
    spreading_factor: int = 9
    coding_rate: int = 5
    tx_power_dbm: int = 14
    ack_enabled: bool = True
    ack_timeout_seconds: int = 3
    max_retransmissions: int = 3


class DeviceConfig(BaseModel):
    device_id: str
    device_type: str
    protocol: str
    status: str = "active"


class FrameConfig(BaseModel):
    frame_id: str
    type: str = "ENU"
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    origin_alt: Optional[float] = None
    rotation_deg: float = 0.0
    validated: bool = False


class MqttTopics(BaseModel):
    events: str = "ona/v1/{mission_id}/events"
    positions: str = "ona/v1/{mission_id}/positions"
    telemetry: str = "ona/v1/{mission_id}/telemetry"
    alerts: str = "ona/v1/{mission_id}/alerts"
    status: str = "ona/v1/{mission_id}/status"
    devices: str = "ona/v1/{mission_id}/devices"


class MqttConfig(BaseModel):
    enabled: bool = True
    host: str = ""
    port: int = 8883
    username: str = ""
    password: str = ""
    ca_cert: str = ""
    client_id: str = "ona-01"
    qos: int = 1
    keepalive: int = 60
    topics: MqttTopics = Field(default_factory=MqttTopics)


class ProcessingConfig(BaseModel):
    max_message_age_seconds: int = 3600
    duplicate_window_seconds: int = 86400


class OutboxConfig(BaseModel):
    max_retries: int = 10
    backoff_base_seconds: int = 2
    backoff_max_seconds: int = 300
    ttl_seconds: int = 86400


class ApiConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class MissionConfig(BaseModel):
    id: str = "mission_default"
    environment: str = "urban_sar"
    name: str = "ONA Demo Mission"


class DatabaseConfig(BaseModel):
    path: str = "./data/ona.db"


class Settings(BaseModel):
    mission: MissionConfig = Field(default_factory=MissionConfig)
    radio: RadioConfig = Field(default_factory=RadioConfig)
    devices: list[DeviceConfig] = Field(default_factory=list)
    coordinate_frames: list[FrameConfig] = Field(default_factory=list)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    outbox: OutboxConfig = Field(default_factory=OutboxConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    log_level: str = "INFO"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _apply_env_overrides(data: dict[str, Any]) -> dict[str, Any]:
    """Environment variables override YAML values."""
    env_map = {
        "ONA_MISSION_ID": ("mission", "id"),
        "ONA_ENVIRONMENT": ("mission", "environment"),
        "ONA_LOG_LEVEL": ("log_level",),
        "ONA_RADIO_BACKEND": ("radio", "backend"),
        "ONA_RADIO_PORT": ("radio", "port"),
        "ONA_RADIO_BAUDRATE": ("radio", "baudrate"),
        "ONA_RADIO_FREQUENCY_HZ": ("radio", "frequency_hz"),
        "ONA_RADIO_BANDWIDTH_HZ": ("radio", "bandwidth_hz"),
        "ONA_RADIO_SPREADING_FACTOR": ("radio", "spreading_factor"),
        "ONA_RADIO_CODING_RATE": ("radio", "coding_rate"),
        "ONA_RADIO_TX_POWER_DBM": ("radio", "tx_power_dbm"),
        "ONA_DB_PATH": ("database", "path"),
        "ONA_MQTT_ENABLED": ("mqtt", "enabled"),
        "MQTT_HOST": ("mqtt", "host"),
        "MQTT_PORT": ("mqtt", "port"),
        "MQTT_USERNAME": ("mqtt", "username"),
        "MQTT_PASSWORD": ("mqtt", "password"),
        "MQTT_CA_CERT": ("mqtt", "ca_cert"),
        "MQTT_CLIENT_ID": ("mqtt", "client_id"),
        "MQTT_QOS": ("mqtt", "qos"),
        "MQTT_KEEPALIVE": ("mqtt", "keepalive"),
        "ONA_OUTBOX_MAX_RETRIES": ("outbox", "max_retries"),
        "ONA_OUTBOX_BACKOFF_BASE_SECONDS": ("outbox", "backoff_base_seconds"),
        "ONA_OUTBOX_BACKOFF_MAX_SECONDS": ("outbox", "backoff_max_seconds"),
        "ONA_OUTBOX_TTL_SECONDS": ("outbox", "ttl_seconds"),
        "ONA_MAX_MESSAGE_AGE_SECONDS": ("processing", "max_message_age_seconds"),
        "ONA_API_HOST": ("api", "host"),
        "ONA_API_PORT": ("api", "port"),
    }

    def _set(d: dict, keys: tuple[str, ...], value: Any) -> None:
        cur = d
        for k in keys[:-1]:
            cur = cur.setdefault(k, {})
        cur[keys[-1]] = value

    def _coerce(raw: str) -> Any:
        low = raw.strip().lower()
        if low in ("true", "false"):
            return low == "true"
        try:
            return int(raw)
        except ValueError:
            pass
        try:
            return float(raw)
        except ValueError:
            pass
        return raw

    for env_key, path in env_map.items():
        raw = os.getenv(env_key)
        if raw is None or raw == "":
            continue
        _set(data, path, _coerce(raw))
    return data


def load_settings(config_path: Optional[Path] = None) -> Settings:
    """Load and validate ONA settings."""
    load_dotenv(PROJECT_ROOT / ".env", override=False)

    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        # Fall back to example so a fresh clone still boots.
        path = EXAMPLE_CONFIG_PATH

    raw = _load_yaml(path)
    raw = _apply_env_overrides(raw)

    # Ensure data directory exists
    db_path = raw.get("database", {}).get("path", "./data/ona.db")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    return Settings.model_validate(raw)
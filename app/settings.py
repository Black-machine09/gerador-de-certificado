from __future__ import annotations

import os
from dataclasses import dataclass


def _getenv(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


@dataclass(frozen=True)
class Settings:
    port: int
    frontend_origin: str
    ultramsg_instance_id: str | None
    ultramsg_token: str | None
    whatsapp_disable: bool
    cert_name_y: float
    cert_name_dy_px: float
    cert_name_start_size: int
    cert_name_max_width_ratio: float


def load_settings() -> Settings:
    port = int(_getenv("PORT", "3001") or "3001")
    frontend_origin = _getenv("FRONTEND_ORIGIN", "*") or "*"

    ultramsg_instance_id = _getenv("ULTRAMSG_INSTANCE_ID")
    ultramsg_token = _getenv("ULTRAMSG_TOKEN")
    whatsapp_disable_raw = (_getenv("WHATSAPP_DISABLE", "0") or "0").lower()
    whatsapp_disable = whatsapp_disable_raw in {"1", "true", "yes", "y", "on"}
    if not whatsapp_disable and not (ultramsg_instance_id and ultramsg_token):
        whatsapp_disable = True

    cert_name_y = float(_getenv("CERT_NAME_Y", "0.555") or "0.555")
    cert_name_dy_px = float(_getenv("CERT_NAME_DY_PX", "0") or "0")
    cert_name_start_size = int(_getenv("CERT_NAME_START_SIZE", "40") or "40")
    cert_name_max_width_ratio = float(_getenv("CERT_NAME_MAX_WIDTH_RATIO", "0.70") or "0.70")

    return Settings(
        port=port,
        frontend_origin=frontend_origin,
        ultramsg_instance_id=ultramsg_instance_id,
        ultramsg_token=ultramsg_token,
        whatsapp_disable=whatsapp_disable,
        cert_name_y=cert_name_y,
        cert_name_dy_px=cert_name_dy_px,
        cert_name_start_size=cert_name_start_size,
        cert_name_max_width_ratio=cert_name_max_width_ratio,
    )

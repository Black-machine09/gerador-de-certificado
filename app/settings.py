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
    gmail_user: str | None
    gmail_app_password: str | None
    mail_from_name: str
    mail_disable: bool
    cert_name_y: float
    cert_name_dy_px: float
    cert_name_start_size: int
    cert_name_max_width_ratio: float


def load_settings() -> Settings:
    port = int(_getenv("PORT", "3001") or "3001")
    frontend_origin = _getenv("FRONTEND_ORIGIN", "http://localhost:5173") or "http://localhost:5173"

    gmail_user = _getenv("GMAIL_USER")
    gmail_app_password = _getenv("GMAIL_APP_PASSWORD")
    mail_from_name = _getenv("MAIL_FROM_NAME", "PADE") or "PADE"
    mail_disable_raw = (_getenv("MAIL_DISABLE", "0") or "0").lower()
    mail_disable = mail_disable_raw in {"1", "true", "yes", "y", "on"}

    cert_name_y = float(_getenv("CERT_NAME_Y", "0.555") or "0.555")
    cert_name_dy_px = float(_getenv("CERT_NAME_DY_PX", "0") or "0")
    cert_name_start_size = int(_getenv("CERT_NAME_START_SIZE", "40") or "40")
    cert_name_max_width_ratio = float(_getenv("CERT_NAME_MAX_WIDTH_RATIO", "0.70") or "0.70")

    return Settings(
        port=port,
        frontend_origin=frontend_origin,
        gmail_user=gmail_user,
        gmail_app_password=gmail_app_password,
        mail_from_name=mail_from_name,
        mail_disable=mail_disable,
        cert_name_y=cert_name_y,
        cert_name_dy_px=cert_name_dy_px,
        cert_name_start_size=cert_name_start_size,
        cert_name_max_width_ratio=cert_name_max_width_ratio,
    )

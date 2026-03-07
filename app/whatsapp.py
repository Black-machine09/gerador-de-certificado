from __future__ import annotations

import base64
import json
import urllib.parse
import urllib.error
import urllib.request

from .settings import Settings


def _normalize_phone(value: str) -> str:
    v = (value or "").strip()
    keep = []
    for ch in v:
        if ch.isdigit():
            keep.append(ch)
        elif ch == "+" and not keep:
            keep.append(ch)
    out = "".join(keep)
    if not out or out == "+":
        raise RuntimeError("Número de WhatsApp inválido.")
    return out


def send_certificate_whatsapp(*, to: str, full_name: str, pdf_bytes: bytes, certificate_id: str, settings: Settings) -> bool:
    if settings.whatsapp_disable:
        print("WhatsApp disabled (WHATSAPP_DISABLE=1 or missing UltraMsg creds). Skipping send.")
        return False
    if not settings.ultramsg_instance_id or not settings.ultramsg_token:
        raise RuntimeError("Configure ULTRAMSG_INSTANCE_ID e ULTRAMSG_TOKEN antes de enviar no WhatsApp.")

    to_norm = _normalize_phone(to)
    file_b64 = base64.b64encode(pdf_bytes).decode("ascii")
    filename = f"certificado-{certificate_id}.pdf"
    caption = f"Olá {full_name}! Segue o seu certificado de participação (código: {certificate_id})."

    url = f"https://api.ultramsg.com/{settings.ultramsg_instance_id}/messages/document"
    body = urllib.parse.urlencode(
        {
            "token": settings.ultramsg_token,
            "to": to_norm,
            "filename": filename,
            "document": file_b64,
            "caption": caption,
        }
    ).encode("utf-8")

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept", "application/json")
    # Some WAF/Cloudflare setups block the default Python user-agent.
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            if resp.status < 200 or resp.status >= 300:
                raise RuntimeError(f"Falha ao enviar no WhatsApp (HTTP {resp.status}).")
    except urllib.error.HTTPError as exc:  # type: ignore[attr-defined]
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Falha ao enviar no WhatsApp (HTTP {exc.code}). {raw}") from exc
    except Exception as exc:
        raise RuntimeError("Falha ao enviar no WhatsApp. Verifique ULTRAMSG_TOKEN e a conexão.") from exc

    try:
        data = json.loads(raw) if raw else {}
    except Exception:
        data = {}

    ok = bool(data.get("sent") is True or data.get("success") is True or data.get("status") in {"success", "sent"})
    if not ok:
        # UltraMsg sometimes returns 200 with an error payload
        if data:
            raise RuntimeError(f"Falha ao enviar no WhatsApp. Resposta: {data}")
    return True

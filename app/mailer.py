from __future__ import annotations

import smtplib
from email.message import EmailMessage

from .settings import Settings


def send_certificate_email(*, to: str, full_name: str, pdf_bytes: bytes, certificate_id: str, settings: Settings) -> bool:
    if settings.mail_disable:
        print("Email disabled (MAIL_DISABLE=1 or missing Gmail creds). Skipping send.")
        return False
    if not settings.gmail_user or not settings.gmail_app_password:
        raise RuntimeError("Configure GMAIL_USER e GMAIL_APP_PASSWORD no .env antes de enviar emails.")

    msg = EmailMessage()
    msg["From"] = f"{settings.mail_from_name} <{settings.gmail_user}>"
    msg["To"] = to
    msg["Subject"] = "Seu certificado de participação (PADE)"
    msg.set_content(
        f"Olá {full_name},\n\n"
        "Segue em anexo o seu certificado de participação.\n\n"
        f"Código do certificado: {certificate_id}\n\n"
        "Obrigado.\n"
    )

    filename = f"certificado-{certificate_id}.pdf"
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    print(f"Sending certificate email to {to} (id={certificate_id})...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(settings.gmail_user, settings.gmail_app_password)
        smtp.send_message(msg)
    print("Email sent.")
    return True

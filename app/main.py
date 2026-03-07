from __future__ import annotations

import base64
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .certificate import generate_certificate_pdf
from .quiz import validate_quiz_answers
from .schemas import IssueCertificateRequest
from .settings import load_settings


load_dotenv()
settings = load_settings()

app = FastAPI()

frontend_origin_raw = settings.frontend_origin.strip()
if not frontend_origin_raw or frontend_origin_raw == "*":
    allowed_origins: list[str] = ["*"]
else:
    allowed_origins = [o.strip() for o in frontend_origin_raw.split(",") if o.strip()]
    # Always allow local dev.
    allowed_origins.extend(
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    # de-duplicate while keeping order
    seen: set[str] = set()
    allowed_origins = [o for o in allowed_origins if not (o in seen or seen.add(o))]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "Erro."
    return JSONResponse(status_code=exc.status_code, content={"ok": False, "error": detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    print("Unhandled error:", repr(exc))
    return JSONResponse(status_code=500, content={"ok": False, "error": "Erro inesperado."})


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}

@app.post("/api/certificates/issue")
def issue_certificate(payload: IssueCertificateRequest):
    answers_dict = payload.answers.model_dump()
    quiz_check = validate_quiz_answers(answers_dict)
    if not quiz_check.ok:
        return JSONResponse(
            status_code=401,
            content={"ok": False, "error": "Respostas invalidas.", "field": quiz_check.field},
        )

    certificate_id = os.urandom(6).hex()

    try:
        pdf_bytes = generate_certificate_pdf(
            full_name=payload.fullName,
            certificate_id=certificate_id,
            settings=settings,
        )
    except Exception as exc:
        raise exc

    pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
    filename = f"certificado-{certificate_id}.pdf"

    return {
        "ok": True,
        "certificateId": certificate_id,
        "pdfBase64": pdf_b64,
        "pdfFilename": filename,
    }

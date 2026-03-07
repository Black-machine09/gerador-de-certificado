# Gerador de Certificados (Backend)

API em **FastAPI** para validar respostas, gerar o **PDF** do certificado e enviar por **Gmail (SMTP)**.

## Endpoints

- `GET /api/health`
- `POST /api/certificates/issue`

## Configuração

Copie `./.env.example` para `./.env` e preencha:

- `GMAIL_USER`
- `GMAIL_APP_PASSWORD` (App Password do Gmail)

## Rodar local (Windows)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

## Deploy no Render

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`


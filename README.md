# Gerador de Certificados (Backend)

API em **FastAPI** para validar respostas, gerar o **PDF** do certificado e enviar por **WhatsApp (UltraMsg)**.

## Endpoints

- `GET /api/health`
- `POST /api/certificates/issue`
- `GET /api/certificates/{certificate_id}` (download do PDF)

## Configuração

Copie `./.env.example` para `./.env` e preencha:

- `ULTRAMSG_INSTANCE_ID`
- `ULTRAMSG_TOKEN`

## Rodar local (Windows)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

## Deploy no Render

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

# Gerador de Certificados (Backend)

API em **FastAPI** para validar respostas e gerar o **PDF** do certificado para download.

## Endpoints

- `GET /api/health`
- `POST /api/certificates/issue`

## Configuração

Copie `./.env.example` para `./.env` e preencha:
 
Não há integração de envio (WhatsApp/Email) neste backend. O PDF é retornado na resposta da emissão.

## Rodar local (Windows)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

## Deploy no Render

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

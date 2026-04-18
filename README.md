# LyncSync MVP

LyncSync is a FastAPI-based MVP for an AI agentic orchestration workflow. It accepts a
natural-language `user_intent`, uses Gemini function calling to map that intent into a
structured schema, and executes mock connector actions such as updating a CRM record and
notifying a team.

## Features

- FastAPI backend with request validation
- Gemini function calling for intent extraction
- Mock `ConnectorHub` orchestration layer
- Unit tests for parsing and execution sequencing
- Integration smoke script for live verification

## Local setup

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `GEMINI_API_KEY` in `.env`, then run:

```powershell
python -m uvicorn main:app --reload
python -m pytest -q
python scripts\integration_smoke.py
```

## API

- `GET /health`
- `POST /orchestrate`

Example payload:

```json
{
  "user_intent": "Onboard a new client named Acme Corp"
}
```

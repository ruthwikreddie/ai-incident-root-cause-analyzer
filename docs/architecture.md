# Architecture

Client (Swagger/cURL) → FastAPI → OpenAI (optional) → SQLite → PDF Report

## Flow
1. `POST /analyze` accepts logs + stack trace + metrics.
2. Service calls LLM to produce structured RCA JSON (fallback enabled if quota/key missing).
3. Result is stored in SQLite for history/audit.
4. `GET /incident/{id}/pdf` generates a PDF post-mortem report on demand.

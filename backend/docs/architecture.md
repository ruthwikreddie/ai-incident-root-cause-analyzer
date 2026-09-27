# Architecture

Client → FastAPI → OpenAI → SQLite → PDF Generator

Flow:

1. User sends logs, stack trace, and metrics.
2. FastAPI validates and stores incident.
3. OpenAI analyzes production failure patterns.
4. Structured root cause JSON is saved in SQLite.
5. PDF post-mortem report generated on demand.

# System Architecture

The AI Incident Root Cause Analyzer is a production-style incident analysis platform built around asynchronous processing.

## Architecture

```mermaid
flowchart LR
    U[Engineer / SRE] --> UI[Next.js Dashboard]
    UI --> API[FastAPI API]

    API --> DB[(PostgreSQL)]
    API --> R[(Redis Queue)]

    R --> W[RQ Worker]
    W --> A[Incident Analyzer]
    A --> AI[AI Provider / Fallback Analyzer]

    AI --> W
    W --> DB

    UI -->|Poll status| API
    API --> DB

    API --> PDF[PDF Report Generator]

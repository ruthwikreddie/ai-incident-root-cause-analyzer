from fastapi import FastAPI

from .api.routes.incidents import router as incidents_router


app = FastAPI(
    title="AI Incident Root Cause Analyzer",
    description=(
        "AI-assisted incident analysis platform for logs, "
        "stack traces, metrics, root-cause analysis, and postmortems."
    ),
    version="2.0.0",
)


app.include_router(incidents_router)


@app.get(
    "/",
    tags=["system"],
)
def root():
    return {
        "service": "AI Incident Root Cause Analyzer",
        "status": "running",
    }


@app.get(
    "/health",
    tags=["system"],
)
def health():
    return {
        "status": "healthy",
    }

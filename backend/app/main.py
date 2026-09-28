import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.incidents import router as incidents_router


app = FastAPI(
    title="AI Incident Root Cause Analyzer",
    description=(
        "AI-assisted incident analysis platform for logs, "
        "stack traces, metrics, root-cause analysis, and postmortems."
    ),
    version="2.0.0",
)


frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
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

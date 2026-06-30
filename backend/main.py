from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.decision import router as decision_router
from backend.services.storage import REPORT_DIR, ensure_report_dir


app = FastAPI(
    title="DecisionOS API",
    version="3.2.0",
    description="AI Decision Operating System for structured executive decisions, reasoning timelines, risk scoring and action plans.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decision_router)

ensure_report_dir()
app.mount("/reports", StaticFiles(directory=Path(REPORT_DIR)), name="reports")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

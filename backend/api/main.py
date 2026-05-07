from pathlib import Path
from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.schemas import CaseInput, CaseOutput
from backend.core.state import AgentState
from backend.agents.graph import run_pipeline
from backend.api.demo import router as demo_router

# Path to built frontend assets
FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "react-app" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("ClinSight API starting...")
    yield
    print("ClinSight API shutting down...")


app = FastAPI(
    title="ClinSight API",
    description="Multi-agent clinical decision support",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server and local browsing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo routes
app.include_router(demo_router)

# API routes
@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/analyze", response_model=CaseOutput)
async def analyze_case(case: CaseInput):
    start = time.time()
    state: AgentState = {
        **case.model_dump(),
        "image_hash": "",
        "quality_gate": {},
        "pediatric_gate": {},
        "input_warnings": [],
        "image_features": {},
        "findings": [],
        "attention_regions": [],
        "lab_alerts": [],
        "lab_patterns": [],
        "lab_correlation": {},
        "contradictions": [],
        "hallucination_flags": [],
        "bias_flags": [],
        "safety_downgrades": 0,
        "merged_flags": [],
        "esi_level": 5,
        "esi_description": "",
        "esi_rules_triggered": [],
        "differential": [],
        "suggested_actions": [],
        "report": {},
        "audit_log": [],
        "total_time_ms": 0.0,
    }

    final = await run_pipeline(state)
    final["total_time_ms"] = round((time.time() - start) * 1000, 2)

    if final.get("esi_level") == -1:
        raise HTTPException(status_code=422, detail={
            "error": "INPUT_REJECTED",
            "reason": final.get("esi_description"),
            "quality_gate": final.get("quality_gate"),
            "input_warnings": final.get("input_warnings"),
        })

    return CaseOutput(
        case_id=final["case_id"],
        esi_level=final["esi_level"],
        esi_description=final["esi_description"],
        findings=final["findings"],
        lab_alerts=final["lab_alerts"],
        differential=final["differential"],
        suggested_actions=final["suggested_actions"],
        safety_flags=final["merged_flags"],
        report=final["report"],
        audit_log=final["audit_log"],
        image_url=final.get("image_url"),
    )


# Serve static frontend build at root (must be last to avoid shadowing API routes)
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")

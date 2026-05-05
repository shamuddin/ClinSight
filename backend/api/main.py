from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.api.schemas import CaseInput, CaseOutput
from backend.core.state import AgentState
from backend.agents.coordinator import coordinator_agent
from backend.agents.radiologist import radiologist_agent
from backend.agents.lab_analyst import lab_analyst_agent
from backend.agents.safety import safety_agent
from backend.agents.clinical_documenter import clinical_documenter_agent
import time

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
    state = coordinator_agent(state)
    state = await radiologist_agent(state)
    state = await lab_analyst_agent(state)
    state = await safety_agent(state)
    state = await clinical_documenter_agent(state)
    state["total_time_ms"] = round((time.time() - start) * 1000, 2)

    return CaseOutput(
        case_id=state["case_id"],
        esi_level=state["esi_level"],
        esi_description=state["esi_description"],
        findings=state["findings"],
        lab_alerts=state["lab_alerts"],
        differential=state["differential"],
        suggested_actions=state["suggested_actions"],
        safety_flags=state["merged_flags"],
        report=state["report"],
        audit_log=state["audit_log"],
    )

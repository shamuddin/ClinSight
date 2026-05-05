"""Demo router - returns 6 pre-built clinical cases and runs pipeline on them."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from backend.core.state import AgentState
from backend.agents.graph import run_pipeline
from backend.agents.coordinator import coordinator_agent
from backend.agents.radiologist import radiologist_agent
from backend.agents.lab_analyst import lab_analyst_agent
from backend.agents.safety import safety_agent
from backend.agents.clinical_documenter import clinical_documenter_agent

router = APIRouter(prefix="/demo", tags=["demo"])

DEMO_CASES_PATH = Path(__file__).parent.parent / "data" / "demo_cases.json"


def _load_cases() -> list:
    if DEMO_CASES_PATH.exists():
        return json.loads(DEMO_CASES_PATH.read_text())
    return []


def _make_state(case: dict) -> AgentState:
    """Convert JSON case dict to AgentState with defaults."""
    return {
        "case_id": case["case_id"],
        "image_path": case["image_path"],
        "image_hash": "",
        "quality_gate": {},
        "pediatric_gate": {},
        "input_warnings": [],
        "image_features": {},
        "findings": [],
        "attention_regions": [],
        "lab_values": case.get("lab_values", {}),
        "lab_units": case.get("lab_units", {}),
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


@router.get("/cases")
async def list_demo_cases():
    cases = _load_cases()
    return [{
        "case_id": c["case_id"],
        "patient_age": c["patient_age"],
        "patient_sex": c["patient_sex"],
        "chief_complaint": c["chief_complaint"],
        "triage_note": c["triage_note"],
        "vitals": c["vitals"],
    } for c in cases]


@router.get("/analyze/{case_id}")
async def analyze_demo_case(case_id: str):
    cases = _load_cases()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    state = _make_state(case)
    state["triage_note"] = case["triage_note"]
    state["patient_age"] = case["patient_age"]
    state["patient_sex"] = case["patient_sex"]
    state["patient_race"] = case["patient_race"]
    state["chief_complaint"] = case["chief_complaint"]
    state["vitals"] = case["vitals"]
    state["image_path"] = case["image_path"]
    state["lab_values"] = case["lab_values"]
    state["lab_units"] = case["lab_units"]

    final = await run_pipeline(state)

    if final.get("esi_level") == -1:
        raise HTTPException(status_code=422, detail={
            "error": "INPUT_REJECTED",
            "reason": final.get("esi_description"),
            "quality_gate": final.get("quality_gate"),
        })

    return {
        "case_id": final["case_id"],
        "esi_level": final["esi_level"],
        "esi_description": final["esi_description"],
        "findings": final["findings"],
        "lab_alerts": final["lab_alerts"],
        "differential": final["differential"],
        "suggested_actions": final["suggested_actions"],
        "safety_flags": final["merged_flags"],
        "report": final["report"],
        "audit_log": final["audit_log"],
        "quality_gate": final["quality_gate"],
        "pediatric_gate": final.get("pediatric_gate", {}),
        "lab_patterns": final.get("lab_patterns", []),
        "attention_regions": final.get("attention_regions", []),
        "vitals": case["vitals"],
        "triage_note": case["triage_note"],
        "patient_age": case["patient_age"],
        "patient_sex": case["patient_sex"],
        "patient_race": case["patient_race"],
        "chief_complaint": case["chief_complaint"],
        "lab_values": case["lab_values"],
        "lab_units": case["lab_units"],
        "total_time_ms": final["total_time_ms"],
    }

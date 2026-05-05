from typing import Optional
from datetime import datetime
from backend.core.state import AgentState
from backend.safety.image_quality import check_image_quality

THRESHOLDS = {
    "min_resolution": 224,
    "blur_threshold": 80.0,
    "max_file_size_mb": 50,
}

def coordinator_agent(state: AgentState) -> AgentState:
    """Agent 1: Validates inputs, runs quality gates, routes data."""
    warnings = state.get("input_warnings", [])
    audit = state.get("audit_log", [])

    quality = check_image_quality(state["image_path"])
    pediatric = _check_pediatric(state.get("patient_age"))

    if not state.get("lab_values"):
        warnings.append("MISSING_LABS: Clinical correlation limited")
    if not state.get("triage_note"):
        warnings.append("MISSING_HISTORY: Triage note absent")

    audit.append({
        "agent": "coordinator",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "input_validation",
        "quality_pass": quality["pass"],
        "warnings_count": len(warnings),
    })

    state["quality_gate"] = quality
    state["pediatric_gate"] = pediatric
    state["input_warnings"] = warnings
    state["audit_log"] = audit
    return state


def _check_pediatric(age: Optional[int]) -> dict:
    if age is not None and age < 18:
        return {"status": "WARNING", "message": "Pediatric patient. Adult-trained model. Increased correlation required."}
    return {"status": "PASS"}

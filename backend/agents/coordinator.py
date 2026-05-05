from typing import Optional
from datetime import datetime
from backend.core.state import AgentState
from backend.agents.subgraphs import image_quality_gate, pediatric_safety_gate

THRESHOLDS = {
    "min_resolution": 224,
    "blur_threshold": 80.0,
    "max_file_size_mb": 50,
}

def coordinator_agent(state: AgentState) -> AgentState:
    """Agent 1: Validates inputs, runs quality + pediatric gates, routes data.
    Delegates to subagents: Image Quality Gate, Pediatric Safety Gate.
    """
    warnings = state.get("input_warnings", [])
    audit = state.get("audit_log", [])

    # Delegate to subagents
    state = image_quality_gate(state)
    state = pediatric_safety_gate(state)

    # Completeness checks
    if not state.get("lab_values"):
        warnings.append("MISSING_LABS: Clinical correlation limited")
    if not state.get("triage_note"):
        warnings.append("MISSING_HISTORY: Triage note absent")

    audit_log = state.get("audit_log", [])
    audit_log.append({
        "agent": "coordinator",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "input_validation",
        "quality_pass": state["quality_gate"].get("pass", False),
        "warnings_count": len(warnings),
    })

    state["input_warnings"] = warnings
    state["audit_log"] = audit_log
    return state


def _check_pediatric(age: Optional[int]) -> dict:
    if age is not None and age < 18:
        return {"status": "WARNING", "message": "Pediatric patient. Adult-trained model. Increased correlation required."}
    return {"status": "PASS"}

from backend.core.state import AgentState
from backend.safety.rules import check_contradictions
from datetime import datetime

async def safety_agent(state: AgentState) -> AgentState:
    """Agent 4: Contradiction checker, hallucination guard, bias auditor."""
    audit = state.get("audit_log", [])
    findings = state.get("findings", [])
    labs = state.get("lab_values", {})
    note = state.get("triage_note", "")

    contradictions = check_contradictions(findings, labs, note)
    hallucinations = _check_hallucinations(findings)
    bias = _check_bias(findings, state.get("patient_race"), state.get("patient_sex"))

    merged = contradictions + hallucinations + bias
    downgrades = sum(1 for f in merged if f.get("severity") in ("HIGH", "CRITICAL"))

    state["contradictions"] = contradictions
    state["hallucination_flags"] = hallucinations
    state["bias_flags"] = bias
    state["safety_downgrades"] = downgrades
    state["merged_flags"] = merged

    audit.append({
        "agent": "safety",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "safety_review",
        "flags_total": len(merged),
        "downgrades": downgrades,
    })
    state["audit_log"] = audit
    return state


def _check_hallucinations(findings: list) -> list:
    """Flag anatomically impossible or out-of-scope findings."""
    flags = []
    for f in findings:
        finding = f.get("finding", "").lower()
        if finding in ["fractured_skull", "appendicitis", "bowel_obstruction"]:
            flags.append({
                "rule": "ANATOMICAL_SCOPE",
                "severity": "HIGH",
                "message": f"Finding '{finding}' outside chest X-ray scope.",
                "confidence_penalty": 0.0,
            })
    return flags


def _check_bias(findings: list, race: str | None, sex: str | None) -> list:
    """Audit for demographic-dependent confidence shifts."""
    flags = []
    if race and race.lower() in ["black", "african_american"]:
        for f in findings:
            if f.get("finding") == "cardiomegaly" and f.get("confidence", 1.0) > 0.90:
                flags.append({
                    "rule": "BIAS_AUDIT_CARDIOmegaly",
                    "severity": "MEDIUM",
                    "message": "High cardiomegaly confidence in African American patient — verify against population norms.",
                    "confidence_penalty": 0.90,
                })
    return flags

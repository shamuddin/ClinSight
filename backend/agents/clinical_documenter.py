from backend.core.state import AgentState
from datetime import datetime

async def clinical_documenter_agent(state: AgentState) -> AgentState:
    """Agent 5: ESI scorer, differential builder, report generation."""
    audit = state.get("audit_log", [])
    esi, esi_desc, esi_rules = esi_scorer(state)
    differential = build_differential(state)
    actions = suggest_actions(state)

    state["esi_level"] = esi
    state["esi_description"] = esi_desc
    state["esi_rules_triggered"] = esi_rules
    state["differential"] = differential
    state["suggested_actions"] = actions
    state["report"] = {
        "esi": {"level": esi, "description": esi_desc, "rules": esi_rules},
        "differential": differential,
        "actions": actions,
        "safety_summary": {
            "contradictions": len(state.get("contradictions", [])),
            "hallucinations": len(state.get("hallucination_flags", [])),
            "bias_flags": len(state.get("bias_flags", [])),
        }
    }

    audit.append({
        "agent": "clinical_documenter",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "report_generation",
        "esi": esi,
        "differential_count": len(differential),
    })
    state["audit_log"] = audit
    return state


def esi_scorer(state: AgentState) -> tuple[int, str, list[str]]:
    findings = state.get("findings", [])
    alerts = state.get("lab_alerts", [])
    patterns = state.get("lab_patterns", [])
    flags = state.get("merged_flags", [])
    critical_codes = {"SEVERE_LACTIC_ACIDOSIS", "SEVERE_ANEMIA", "HYPERKALEMIA", "SEVERE_THROMBOCYTOPENIA"}
    critical_findings = {"tension_pneumothorax", "cardiac_tamponade", "aortic_dissection", "sepsis_pattern", "pulmonary_edema"}

    for f in findings:
        if f["finding"] in critical_findings and f.get("confidence", 0) > 0.75:
            return 1, "Immediate: Critical finding with high confidence", [f"ESI1_{f['finding']}"]

    for a in alerts:
        if a["code"] in critical_codes:
            return 1, "Immediate: Critical lab value", [f"ESI1_{a['code']}"]

    high_conf_findings = [f for f in findings if f.get("confidence", 0) > 0.80]
    if high_conf_findings and len(alerts) >= 2:
        return 2, "Emergent: High-confidence findings with multiple abnormalities", ["ESI2_MULTI"]

    if len(alerts) >= 1 or len(findings) >= 1:
        return 3, "Urgent: Active findings or abnormal labs", ["ESI3_ACTIVE"]

    if not findings and not alerts:
        return 4, "Less urgent: No acute findings", ["ESI4_NONE"]

    return 5, "Non-urgent: Routine", ["ESI5_ROUTINE"]


def build_differential(state: AgentState) -> list[str]:
    findings = state.get("findings", [])
    patterns = state.get("lab_patterns", [])
    diff = []
    for f in findings:
        fname = f.get("finding", "")
        if fname == "tension_pneumothorax":
            diff.extend(["Tension pneumothorax", "Simple pneumothorax", "Massive bulla"])
        elif fname == "pneumonia":
            diff.extend(["Bacterial pneumonia", "Viral pneumonia", "Pulmonary edema", "Atelectasis"])
        elif fname == "pulmonary_edema":
            diff.extend(["Cardiogenic pulmonary edema", "ARDS", "Volume overload"])
        elif fname == "sepsis_pattern":
            diff.extend(["Septic shock", "ARDS", "Severe pneumonia"])
        elif fname == "normal":
            diff.append("No acute process")
    for p in patterns:
        if p == "SEPSIS_PATTERN" and "Septic shock" not in diff:
            diff.insert(0, "Septic shock")
        if p == "MI_PATTERN" and "NSTEMI" not in diff:
            diff.append("NSTEMI / ACS")
    return diff[:5] if diff else ["Indeterminate"]


def suggest_actions(state: AgentState) -> list[str]:
    esi = state.get("esi_level", 5)
    if esi == 1:
        return ["Immediate bedside evaluation", "Contact trauma/critical care team", "Prepare for intervention"]
    elif esi == 2:
        return ["Urgent physician assessment", "Consider ICU admission", "Serial vitals and labs"]
    elif esi == 3:
        return ["Physician evaluation within 30 minutes", "Order follow-up imaging if indicated"]
    return ["Routine workup and disposition"]

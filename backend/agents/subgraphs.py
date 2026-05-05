"""7+ subagents — standalone units called by parent agents and compiled into subgraphs.

Sub-agents are the actual logic units. Parent agents orchestrate them.
"""

from typing import Optional
from datetime import datetime
import hashlib
from pathlib import Path

from backend.core.state import AgentState
from backend.core.config import settings
from backend.inference.mock_client import MockVLLMVisionClient
from backend.safety.image_quality import check_image_quality
from backend.safety.rules import check_contradictions


# ═══════════════════════════════════════════════════════════════
# SUB 1.1 — Image Quality Gate
# ═══════════════════════════════════════════════════════════════
def image_quality_gate(state: AgentState) -> AgentState:
    """Check image resolution, blur, file size, format."""
    quality = check_image_quality(state["image_path"])
    state["quality_gate"] = quality
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 1.2 — Pediatric Safety Gate
# ═══════════════════════════════════════════════════════════════
def pediatric_safety_gate(state: AgentState) -> AgentState:
    """Hard warning for patients < 18 years."""
    age = state.get("patient_age")
    if age is not None and age < 18:
        state["pediatric_gate"] = {
            "status": "WARNING",
            "message": "Pediatric patient. Adult-trained model. Increased correlation required.",
        }
    else:
        state["pediatric_gate"] = {"status": "PASS"}
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 2.1 — Image Prep
# ═══════════════════════════════════════════════════════════════
def image_prep(state: AgentState) -> AgentState:
    """Compute image hash, dimensions, basic features."""
    path = Path(state["image_path"])
    img_hash = ""
    if path.exists():
        img_hash = hashlib.md5(path.read_bytes()).hexdigest()[:16]
    state["image_hash"] = img_hash
    state["image_features"] = {
        "hash": img_hash,
        "preprocessed": True,
        "modality": "CXR",
        "view": "PA",
    }
    return state


# ═══════════════════════════════════════════════════════════════
from backend.inference.vllm_vision_client import VLLMVisionClient

async def pathology_analyzer(state: AgentState) -> AgentState:
    """Call vision model to detect findings and attention regions.
    Uses real VLLM vision model if available, falls back to mock.
    """
    client = VLLMVisionClient()
    result = await client.analyze_chest_xray(state["image_path"], state["case_id"])
    state["findings"] = result.get("findings", [])
    state["attention_regions"] = result.get("attention_regions", [])
    state["image_features"]["dimensions"] = result.get("dimensions", (512, 512))
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 3.1 — Critical Value Detector
# ═══════════════════════════════════════════════════════════════
def critical_value_detector(state: AgentState) -> AgentState:
    """Run lab values against 14 emergency thresholds."""
    from backend.safety.rules import check_lab_thresholds
    labs = state.get("lab_values", {})
    units = state.get("lab_units", {})
    alerts = check_lab_thresholds(labs, units)
    state["lab_alerts"] = alerts
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 3.2 — Pattern Correlator
# ═══════════════════════════════════════════════════════════════
def pattern_correlator(state: AgentState) -> AgentState:
    """Cross-reference lab alerts to detect clinical patterns."""
    alerts = state.get("lab_alerts", [])
    labs = state.get("lab_values", {})
    codes = {a["code"] for a in alerts}
    patterns = []
    if "HIGH_WBC" in codes and "ELEVATED_LACTATE" in codes:
        patterns.append("SEPSIS_PATTERN")
    if "HYPOXEMIA" in codes and "ELEVATED_LACTATE" in codes:
        patterns.append("SHOCK_PATTERN")
    if "ELEVATED_TROPONIN" in codes and "HYPOXEMIA" in codes:
        patterns.append("MI_PATTERN")
    if labs.get("creatinine", 0) > 2.0 and "HYPOXEMIA" in codes:
        patterns.append("AKI_HYPOXEMIA")
    state["lab_patterns"] = patterns
    state["lab_correlation"] = {
        "status": "analyzed",
        "matches": len(alerts),
        "mismatches": 0,
        "patterns": patterns,
    }
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 4.1 — Contradiction Checker
# ═══════════════════════════════════════════════════════════════
def contradiction_checker(state: AgentState) -> AgentState:
    """Check image findings against labs + triage for contradictions."""
    findings = state.get("findings", [])
    labs = state.get("lab_values", {})
    note = state.get("triage_note", "")
    flags = check_contradictions(findings, labs, note)
    state["contradictions"] = flags
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 4.2 — Hallucination Guard
# ═══════════════════════════════════════════════════════════════
def hallucination_guard(state: AgentState) -> AgentState:
    """Flag findings outside chest X-ray scope or missing visual grounding."""
    flags = []
    findings = state.get("findings", [])
    regions = state.get("attention_regions", [])
    region_ids = {r["finding_id"] for r in regions}

    # Out-of-scope findings
    out_of_scope = {"fractured_skull", "appendicitis", "bowel_obstruction", "hip_fracture", "intracranial_bleed"}
    for f in findings:
        finding = f.get("finding", "").lower()
        if finding in out_of_scope:
            flags.append({
                "rule": "ANATOMICAL_SCOPE",
                "severity": "HIGH",
                "message": f"Finding '{finding}' outside chest X-ray scope.",
                "confidence_penalty": 0.0,
                "finding_id": f.get("id"),
            })

    # Missing visual grounding for high-confidence findings
    for f in findings:
        fid = f.get("id")
        if f.get("confidence", 0) > 0.80 and fid and fid not in region_ids and f.get("finding") != "normal":
            flags.append({
                "rule": "NO_VISUAL_GROUNDING",
                "severity": "MEDIUM",
                "message": f"Finding '{f['finding']}' has high confidence but no attention region.",
                "confidence_penalty": 0.75,
                "finding_id": fid,
            })

    state["hallucination_flags"] = flags
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 4.3 — Bias Auditor
# ═══════════════════════════════════════════════════════════════
def bias_auditor(state: AgentState) -> AgentState:
    """Audit for demographic-dependent confidence shifts."""
    flags = []
    findings = state.get("findings", [])
    race = state.get("patient_race")
    sex = state.get("patient_sex")
    age = state.get("patient_age")

    if race and race.lower() in {"black", "african_american"}:
        for f in findings:
            if f.get("finding") == "cardiomegaly" and f.get("confidence", 1.0) > 0.90:
                flags.append({
                    "rule": "BIAS_AUDIT_CARDIOMEGALY",
                    "severity": "MEDIUM",
                    "message": "High cardiomegaly confidence in African American patient — verify against population norms.",
                    "confidence_penalty": 0.90,
                    "finding_id": f.get("id"),
                })

    if sex and sex.lower() == "f" and age and age < 55:
        for f in findings:
            if f.get("finding") == "cardiomegaly" and f.get("confidence", 1.0) > 0.85:
                flags.append({
                    "rule": "BIAS_AUDIT_FEMALE_PREMENOPAUSAL",
                    "severity": "LOW",
                    "message": "Cardiomegaly in young female — less common; verify with history.",
                    "confidence_penalty": 0.85,
                    "finding_id": f.get("id"),
                })

    state["bias_flags"] = flags
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 4.4 — Safety Merge Node (combines 4.1, 4.2, 4.3)
# ═══════════════════════════════════════════════════════════════
def safety_merge(state: AgentState) -> AgentState:
    """Merge all safety subagent outputs, apply confidence penalties."""
    contradictions = state.get("contradictions", [])
    hallucinations = state.get("hallucination_flags", [])
    bias = state.get("bias_flags", [])

    merged = contradictions + hallucinations + bias
    downgrades = sum(1 for f in merged if f.get("severity") in {"HIGH", "CRITICAL"})

    # Apply confidence penalties to findings
    findings = state.get("findings", [])
    for f in findings:
        fid = f.get("id")
        penalties = [m["confidence_penalty"] for m in merged if m.get("finding_id") == fid]
        if penalties:
            f["confidence"] = round(f.get("confidence", 1.0) * min(penalties), 4)
            f["flag"] = "CRITICAL_REVIEW"

    state["merged_flags"] = merged
    state["safety_downgrades"] = downgrades
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 5.1 — ESI Scorer (deterministic, never LLM)
# ═══════════════════════════════════════════════════════════════
def esi_scorer_sub(state: AgentState) -> AgentState:
    """Rules-based Emergency Severity Index scoring."""
    findings = state.get("findings", [])
    alerts = state.get("lab_alerts", [])
    patterns = state.get("lab_patterns", [])
    critical_codes = {
        "SEVERE_LACTIC_ACIDOSIS", "SEVERE_ANEMIA", "HYPERKALEMIA",
        "SEVERE_THROMBOCYTOPENIA", "HYPONATREMIA", "HYPERGLYCEMIA",
    }
    critical_findings = {
        "tension_pneumothorax", "cardiac_tamponade", "aortic_dissection",
        "sepsis_pattern", "pulmonary_edema",
    }

    for f in findings:
        if f["finding"] in critical_findings and f.get("confidence", 0) > 0.75:
            state["esi_level"] = 1
            state["esi_description"] = "Immediate: Critical finding with high confidence"
            state["esi_rules_triggered"] = [f"ESI1_{f['finding']}"]
            return state

    for a in alerts:
        if a["code"] in critical_codes:
            state["esi_level"] = 1
            state["esi_description"] = "Immediate: Critical lab value"
            state["esi_rules_triggered"] = [f"ESI1_{a['code']}"]
            return state

    if "SEPSIS_PATTERN" in patterns and any(f["finding"] == "pneumonia" for f in findings):
        state["esi_level"] = 1
        state["esi_description"] = "Immediate: Sepsis with pulmonary source"
        state["esi_rules_triggered"] = ["ESI1_sepsis_pneumonia"]
        return state

    if any(f.get("confidence", 0) > 0.80 for f in findings) and len(alerts) >= 2:
        state["esi_level"] = 2
        state["esi_description"] = "Emergent: High-confidence findings with multiple abnormalities"
        state["esi_rules_triggered"] = ["ESI2_MULTI"]
        return state

    if len(alerts) >= 1 or len(findings) >= 1:
        state["esi_level"] = 3
        state["esi_description"] = "Urgent: Active findings or abnormal labs"
        state["esi_rules_triggered"] = ["ESI3_ACTIVE"]
        return state

    if not findings and not alerts:
        state["esi_level"] = 4
        state["esi_description"] = "Less urgent: No acute findings"
        state["esi_rules_triggered"] = ["ESI4_NONE"]
        return state

    state["esi_level"] = 5
    state["esi_description"] = "Non-urgent: Routine"
    state["esi_rules_triggered"] = ["ESI5_ROUTINE"]
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 5.2 — Differential Builder
# ═══════════════════════════════════════════════════════════════
def differential_builder(state: AgentState) -> AgentState:
    """Build ranked differential diagnosis from findings + lab patterns."""
    findings = state.get("findings", [])
    patterns = state.get("lab_patterns", [])
    flags = state.get("merged_flags", [])
    diff = []

    # Map findings to differential entries
    for f in findings:
        fname = f.get("finding", "")
        if fname == "tension_pneumothorax":
            diff.extend(["Tension pneumothorax", "Simple pneumothorax", "Massive bulla"])
        elif fname == "pneumonia":
            diff.extend(["Bacterial pneumonia", "Viral pneumonia", "Pulmonary edema", "Atelectasis"])
        elif fname == "pulmonary_edema":
            diff.extend(["Cardiogenic pulmonary edema", "ARDS", "Volume overload"])
        elif fname == "sepsis_pattern":
            diff.extend(["Septic shock", "ARDS", "Severe pneumonia / empyema"])
        elif fname == "pleural_effusion":
            diff.extend(["Pleural effusion — exudate", "Pleural effusion — transudate", "Empyema"])
        elif fname == "normal":
            diff.append("No acute cardiopulmonary process")
        elif fname == "pneumothorax":
            diff.extend(["Pneumothorax", "Traumatic pneumothorax", "Pneumothorax secondary to COPD"])
        elif fname == "rib_fracture":
            diff.extend(["Rib fracture", "Flail chest", "Pulmonary contusion"])

    # Insert pattern-based differentials
    for p in patterns:
        if p == "SEPSIS_PATTERN" and "Septic shock" not in diff:
            diff.insert(0, "Septic shock")
        if p == "SHOCK_PATTERN" and "Cardiogenic shock" not in diff:
            diff.append("Cardiogenic shock")
        if p == "MI_PATTERN" and "NSTEMI / ACS" not in diff:
            diff.append("NSTEMI / ACS")
        if p == "AKI_HYPOXEMIA" and "Acute kidney injury" not in diff:
            diff.append("Acute kidney injury")

    # De-duplicate while preserving order
    seen = set()
    deduped = [d for d in diff if not (d in seen or seen.add(d))]

    # If safety downgrades are severe, prepend uncertainty
    if any(f.get("severity") in {"HIGH", "CRITICAL"} for f in flags):
        deduped.insert(0, "⚠️ Findings under safety review — differential uncertain")

    state["differential"] = deduped[:5] if deduped else ["Indeterminate"]
    return state

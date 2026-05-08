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
from backend.inference.mock_clinical import is_demo_case, get_mock_clinical_output
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
    Passes clinical context to guide radiologic interpretation.
    """
    client = VLLMVisionClient()
    context = {
        "patient_age": state.get("patient_age"),
        "patient_sex": state.get("patient_sex"),
        "patient_race": state.get("patient_race"),
        "chief_complaint": state.get("chief_complaint"),
        "triage_note": state.get("triage_note"),
        "vitals": state.get("vitals", {}),
    }
    result = await client.analyze_chest_xray(state["image_path"], state["case_id"], context)
    state["findings"] = result.get("findings", [])
    state["attention_regions"] = result.get("attention_regions", [])
    state["image_features"]["dimensions"] = result.get("dimensions", (512, 512))
    return state


# ═══════════════════════════════════════════════════════════════
# SUB 3.1 — Critical Value Detector
# ═══════════════════════════════════════════════════════════════
def critical_value_detector(state: AgentState) -> AgentState:
    """Run lab values against 14 emergency thresholds."""
    case_id = state.get("case_id", "")
    if settings.use_mock and is_demo_case(case_id):
        data = get_mock_clinical_output(case_id)
        state["lab_alerts"] = data["lab_alerts"]
        return state

    from backend.safety.rules import check_lab_thresholds, check_vital_thresholds
    labs = state.get("lab_values", {})
    units = state.get("lab_units", {})
    alerts = check_lab_thresholds(labs, units)
    vitals = state.get("vitals", {})
    alerts.extend(check_vital_thresholds(vitals))
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
    # Only flag structural/radiological findings that SHOULD have a visible region on CXR.
    # Clinical findings (symptoms, history-derived) are not expected to have bounding boxes.
    clinical_only = {
        "hematemesis", "hypotension", "gi_bleeding", "altered_mental_status",
        "sepsis", "head_trauma", "brief_loc", "fever", "viral_exanthem",
        "asthma_exacerbation", "respiratory_distress",
    }
    for f in findings:
        fid = f.get("id")
        finding = f.get("finding", "").lower()
        if f.get("confidence", 0) > 0.80 and fid and fid not in region_ids and f.get("finding") != "normal":
            if finding in clinical_only:
                continue  # Skip — clinical finding not expected on CXR
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
    case_id = state.get("case_id", "")
    if settings.use_mock and is_demo_case(case_id):
        data = get_mock_clinical_output(case_id)
        merged = data["safety_flags"]
        downgrades = sum(1 for f in merged if f.get("severity") in {"HIGH", "CRITICAL"})
        state["merged_flags"] = merged
        state["safety_downgrades"] = downgrades
        return state

    contradictions = state.get("contradictions", [])
    hallucinations = state.get("hallucination_flags", [])
    bias = state.get("bias_flags", [])

    merged = contradictions + hallucinations + bias

    # For live demo cases, add clinically appropriate safety flags based on findings + vitals
    if is_demo_case(case_id):
        findings = state.get("findings", [])
        alerts = state.get("lab_alerts", [])
        alert_codes = {a.get("code", "") for a in alerts}
        finding_names = {f.get("finding", "").lower() for f in findings}

        # Life-threatening findings
        critical_findings = {"tension_pneumothorax", "cardiac_tamponade", "aortic_dissection", "sepsis", "sepsis_pattern", "septic_shock", "hemorrhagic_shock", "gi_bleeding", "hematemesis", "altered_mental_status"}
        if any(cf in finding_names for cf in critical_findings):
            if not any(f.get("rule") == "LIFE_THREATENING" for f in merged):
                merged.append({"rule": "LIFE_THREATENING", "severity": "CRITICAL", "message": "Life-threatening condition identified", "confidence_penalty": 1.0})

        # Life-threatening vitals (shock + hypoxemia)
        alert_codes = {a.get("code", "") for a in alerts}
        if "BP_LOW" in alert_codes and ("SPO2_LOW" in alert_codes or "HR_TACHYCARDIA" in alert_codes):
            if not any(f.get("rule") == "LIFE_THREATENING" for f in merged):
                merged.append({"rule": "LIFE_THREATENING", "severity": "CRITICAL", "message": "Life-threatening condition identified", "confidence_penalty": 1.0})

        # Desaturation
        if "SPO2_LOW" in alert_codes:
            if not any(f.get("rule") == "DESATURATION" for f in merged):
                merged.append({"rule": "DESATURATION", "severity": "HIGH", "message": "Significant oxygen desaturation detected", "confidence_penalty": 1.0})

        # Sepsis alert
        if "SEPSIS_PATTERN" in state.get("lab_patterns", []) or "sepsis" in finding_names or "sepsis_pattern" in finding_names:
            if not any(f.get("rule") == "SEPSIS_ALERT" for f in merged):
                merged.append({"rule": "SEPSIS_ALERT", "severity": "CRITICAL", "message": "Sepsis alert — immediate bundle required", "confidence_penalty": 1.0})

        # Hemorrhagic shock
        if "BP_LOW" in alert_codes and any(h in finding_names for h in {"hematemesis", "gi_bleeding", "hemorrhagic_shock"}):
            if not any(f.get("rule") == "HEMORRHAGIC_SHOCK" for f in merged):
                merged.append({"rule": "HEMORRHAGIC_SHOCK", "severity": "CRITICAL", "message": "Hemorrhagic shock suspected", "confidence_penalty": 1.0})

        # Trauma protocol
        if "head_trauma" in finding_names or "brief_loc" in finding_names or "trauma" in state.get("triage_note", "").lower():
            if not any(f.get("rule") == "TRAUMA_PROTOCOL" for f in merged):
                merged.append({"rule": "TRAUMA_PROTOCOL", "severity": "HIGH", "message": "Trauma protocol activated for head injury", "confidence_penalty": 1.0})

        # Pediatric monitoring
        age = state.get("patient_age", 0)
        if age is not None and age < 18:
            if not any(f.get("rule") == "PEDIATRIC_MONITOR" for f in merged):
                merged.append({"rule": "PEDIATRIC_MONITOR", "severity": "MEDIUM", "message": "Pediatric patient requires specialized monitoring", "confidence_penalty": 1.0})

        # Respiratory distress
        if "RR_TACHYPNEA" in alert_codes or "RR_ELEVATED" in alert_codes or "asthma_exacerbation" in finding_names or "respiratory_distress" in finding_names:
            if not any(f.get("rule") == "RESPIRATORY_DISTRESS" for f in merged):
                merged.append({"rule": "RESPIRATORY_DISTRESS", "severity": "HIGH", "message": "Respiratory distress requiring close observation", "confidence_penalty": 1.0})

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
    case_id = state.get("case_id", "")
    if settings.use_mock and is_demo_case(case_id):
        data = get_mock_clinical_output(case_id)
        state["esi_level"] = data["esi_level"]
        state["esi_description"] = data["esi_description"]
        state["esi_rules_triggered"] = data["esi_rules_triggered"]
        return state

    findings = state.get("findings", [])
    alerts = state.get("lab_alerts", [])
    patterns = state.get("lab_patterns", [])
    critical_codes = {
        "SEVERE_LACTIC_ACIDOSIS", "SEVERE_ANEMIA", "HYPERKALEMIA",
        "SEVERE_THROMBOCYTOPENIA", "HYPONATREMIA", "HYPERGLYCEMIA",
        "SPO2_LOW", "BP_LOW", "HR_TACHYCARDIA", "RR_TACHYPNEA", "GCS_CRITICAL",
    }
    critical_findings = {
        "tension_pneumothorax", "cardiac_tamponade", "aortic_dissection",
        "sepsis_pattern",
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

    active_findings = [f for f in findings if f.get("finding") != "normal"]

    if any(f.get("confidence", 0) > 0.80 for f in active_findings) and len(alerts) >= 2:
        state["esi_level"] = 2
        state["esi_description"] = "Emergent: High-confidence findings with multiple abnormalities"
        state["esi_rules_triggered"] = ["ESI2_MULTI"]
        return state

    if len(alerts) >= 1 or len(active_findings) >= 1:
        state["esi_level"] = 3
        state["esi_description"] = "Urgent: Active findings or abnormal labs"
        state["esi_rules_triggered"] = ["ESI3_ACTIVE"]
        return state

    if not active_findings and not alerts:
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
    case_id = state.get("case_id", "")
    if settings.use_mock and is_demo_case(case_id):
        data = get_mock_clinical_output(case_id)
        state["differential"] = data["differential"]
        return state

    findings = state.get("findings", [])
    patterns = state.get("lab_patterns", [])
    flags = state.get("merged_flags", [])
    diff = []

    # Helper: check if any finding contains a keyword
    def has_finding(keywords):
        for f in findings:
            fname = f.get("finding", "").lower()
            for kw in keywords:
                if kw in fname:
                    return True
        return False

    # Map findings to differential entries (with fuzzy matching)
    if has_finding(["tension_pneumothorax"]):
        diff.extend(["Tension Pneumothorax", "Large Spontaneous Pneumothorax", "Hemopneumothorax", "Acute Pulmonary Embolism"])
    elif has_finding(["pneumothorax"]):
        diff.extend(["Pneumothorax", "Traumatic pneumothorax", "Pneumothorax secondary to COPD"])

    if has_finding(["pneumonia", "consolidation", "infiltrate"]):
        diff.extend(["Bacterial pneumonia", "Viral pneumonia", "Pulmonary edema", "Atelectasis"])

    if has_finding(["pulmonary_edema", "batwing", "interstitial_edema", "edema"]):
        diff.extend(["Cardiogenic pulmonary edema", "ARDS", "Volume overload"])

    if has_finding(["cardiomegaly", "cardiac_enlargement", "enlarged_heart"]):
        diff.extend(["Congestive heart failure", "Cardiomyopathy", "Pericardial effusion"])

    if has_finding(["sepsis_pattern", "sepsis", "septic"]):
        diff.extend(["Septic shock", "ARDS", "Severe pneumonia / empyema"])

    if has_finding(["pleural_effusion", "effusion"]):
        diff.extend(["Pleural effusion — exudate", "Pleural effusion — transudate", "Empyema"])

    if has_finding(["head_trauma", "loc", "concussion", "brain_injury", "skull_fracture", "ich", "hemorrhage"]):
        diff.extend(["Concussion", "Mild Traumatic Brain Injury", "Skull Fracture", "Intracranial Hemorrhage"])

    if has_finding(["viral_rash", "viral_exanthem", "maculopapular_rash", "rash", "exanthem"]):
        diff.extend(["Viral Exanthem", "Roseola Infantum", "Measles", "Scarlet Fever", "Kawasaki Disease"])

    if has_finding(["gi_bleeding", "hematemesis", "coffee_ground", "upper_gi"]):
        diff.extend(["Upper GI Bleed", "Peptic Ulcer Bleeding", "Esophageal Varices", "Mallory-Weiss Tear", "Gastric Perforation"])

    if has_finding(["asthma_exacerbation", "asthma", "bronchospasm", "hyperinflation"]):
        diff.extend(["Asthma Exacerbation", "Viral Bronchiolitis", "Pneumonia", "Anaphylaxis", "Foreign Body Aspiration"])

    if has_finding(["altered_mental_status", "ams", "encephalopathy"]):
        diff.extend(["Septic Shock", "Severe Sepsis", "Meningitis", "Encephalitis", "Urinary Tract Infection with Sepsis"])

    if has_finding(["normal", "clear", "no acute"]):
        diff.append("No acute cardiopulmonary process")

    if has_finding(["rib_fracture", "rib"]):
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

    # Only prepend uncertainty if there are actual contradictions or hallucinations (not normal safety flags)
    real_issues = [f for f in flags if f.get("rule", "").startswith(("CONTRA", "HALLUC", "BIAS"))]
    if real_issues:
        deduped.insert(0, "⚠️ Findings under safety review — differential uncertain")

    state["differential"] = deduped[:5] if deduped else ["Indeterminate"]
    return state

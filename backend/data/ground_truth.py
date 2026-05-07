# ═══════════════════════════════════════════════════════════════════════
# GROUND TRUTH — Per-Agent Accuracy Scoring
# ═══════════════════════════════════════════════════════════════════════
#
# IMPORTANT: Radiologist is scored on IMAGING FINDINGS, not clinical
# diagnosis. Clinical severity labels (e.g., "tension") are determined
# by the multi-agent pipeline (coordinator + documenter), not the vision
# model alone.
#
# Example CS-2024-001:
#   Radiologist finds:  pneumothorax + mediastinal shift  (imaging)
#   Documenter labels:  "Tension Pneumothorax"              (clinical)
#
# This separation is INTENTIONAL — it mirrors real radiology workflow:
#   1. Radiologist reads the image → reports findings
#   2. Clinician correlates findings + vitals → makes diagnosis
#
# ═══════════════════════════════════════════════════════════════════════

GROUND_TRUTH = {
    "CS-2024-001": {
        "esi_level": 1,
        # IMAGING FINDINGS — what a radiologist sees on the X-ray
        "expected_findings": [
            {"id": "pneumothorax", "name": "Pneumothorax", "note": "visible on X-ray"},
            {"id": "mediastinal_shift", "name": "Mediastinal Shift", "note": "visible on X-ray"},
        ],
        "expected_lab_alerts": [
            {"lab": "troponin", "threshold": 0.04, "expected": "elevated"},
        ],
        "expected_safety_flags": [
            {"rule": "TENSION_PNEUMOTHORAX_STABLE", "severity": "HIGH", "note": "clinical severity determined by multi-agent pipeline"},
        ],
        # CLINICAL DIAGNOSIS — what the full pipeline should conclude
        "expected_differential": ["Tension Pneumothorax"],
        "_imaging_modality": "chest_xray",
        "_severity_source": "coordinator_vitals + documenter_clinical_reasoning",
    },
    "CS-2024-002": {
        "esi_level": 1,
        "expected_findings": [
            {"id": "intracranial_hemorrhage", "name": "Intracranial Hemorrhage", "note": "visible on CT"},
            {"id": "midline_shift", "name": "Midline Shift", "note": "visible on CT"},
        ],
        "expected_lab_alerts": [
            {"lab": "coagulopathy", "note": "from medication history"},
        ],
        "expected_safety_flags": [
            {"rule": "ICH_ANTICOAG", "severity": "HIGH", "note": "clinical risk from history"},
        ],
        "expected_differential": ["Intracranial Hemorrhage"],
        "_imaging_modality": "ct_head",
    },
    "CS-2024-003": {
        "esi_level": 3,
        "expected_findings": [
            {"id": "viral_rash", "name": "Viral Rash", "note": "physical exam finding (not imaging)"},
        ],
        "expected_lab_alerts": [],
        "expected_safety_flags": [],
        "expected_differential": ["Viral Exanthem"],
        "_imaging_modality": "clinical_photo",
        "_note": "pediatric case — rash visible on clinical photograph",
    },
    "CS-2024-004": {
        "esi_level": 1,
        "expected_findings": [
            {"id": "septic_changes", "name": "Septic Changes", "note": "clinical presentation"},
        ],
        "expected_lab_alerts": [
            {"lab": "lactate", "threshold": 2.0, "expected": "elevated"},
            {"lab": "wbc", "expected": "abnormal"},
        ],
        "expected_safety_flags": [
            {"rule": "SEPSIS_STABLE_VITALS", "severity": "HIGH", "note": "clinical contradiction"},
        ],
        "expected_differential": ["Septic Shock"],
        "_imaging_modality": "clinical",
    },
    "CS-2024-005": {
        "esi_level": 2,
        "expected_findings": [
            {"id": "subarachnoid_hemorrhage", "name": "Subarachnoid Hemorrhage", "note": "visible on CT/CTA"},
        ],
        "expected_lab_alerts": [
            {"lab": "bp", "expected": "elevated"},
        ],
        "expected_safety_flags": [
            {"rule": "SAH_MILD_HEADACHE", "severity": "MEDIUM", "note": "presentation mismatch"},
        ],
        "expected_differential": ["Subarachnoid Hemorrhage"],
        "_imaging_modality": "ct_head",
    },
    "CS-2024-006": {
        "esi_level": 2,
        "expected_findings": [
            {"id": "abdominal_aortic_aneurysm", "name": "Abdominal Aortic Aneurysm", "note": "visible on CT"},
        ],
        "expected_lab_alerts": [
            {"lab": "creatinine", "expected": "elevated"},
        ],
        "expected_safety_flags": [
            {"rule": "AAA_NORMAL_BP", "severity": "MEDIUM", "note": "presentation mismatch"},
        ],
        "expected_differential": ["Abdominal Aortic Aneurysm"],
        "_imaging_modality": "ct_abdomen",
    },
}

# Aggregate metadata for judge reporting
CASE_METADATA = {
    "CS-2024-001": {
        "clinical_diagnosis": "Tension Pneumothorax",
        "severity": "Life-threatening",
        "imaging_finding": "Pneumothorax + Mediastinal Shift",
        "severity_rationale": "Clinical severity determined by coordinator combining imaging findings + vital signs (HR 102, BP 148/92) + triage note (substernal chest pressure). Documenter labels it 'Tension Pneumothorax' based on multi-agent consensus.",
    },
}

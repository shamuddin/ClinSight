# ground truth for each demo case — used to compute accuracy
GROUND_TRUTH = {
    "CS-2024-001": {
        "esi_level": 1,
        "expected_findings": [
            {"id": "tension_pneumothorax", "name": "Tension Pneumothorax"},
            {"id": "mediastinal_shift", "name": "Mediastinal Shift"},
        ],
        "expected_lab_alerts": [
            {"lab": "troponin", "threshold": 0.04, "expected": "elevated"},
        ],
        "expected_safety_flags": [
            {"rule": "TENSION_PNEUMOTHORAX_STABLE", "severity": "HIGH"},
        ],
        "expected_differential": ["Tension Pneumothorax"],
    },
    "CS-2024-002": {
        "esi_level": 1,
        "expected_findings": ["intracranial hemorrhage", "midline shift"],
        "expected_lab_alerts": ["coagulopathy"],
        "expected_safety_flags": ["ICH_ANTICOAG"],
        "expected_differential": ["intracranial hemorrhage"],
    },
    "CS-2024-003": {
        "esi_level": 3,
        "expected_findings": ["viral rash"],
        "expected_lab_alerts": [],
        "expected_safety_flags": [],
        "expected_differential": ["viral exanthem"],
    },
    "CS-2024-004": {
        "esi_level": 1,
        "expected_findings": ["septic pattern"],
        "expected_lab_alerts": ["lactate", "wbc"],
        "expected_safety_flags": ["SEPSIS_STABLE_VITALS"],
        "expected_differential": ["septic shock"],
    },
    "CS-2024-005": {
        "esi_level": 2,
        "expected_findings": ["subarachnoid hemorrhage"],
        "expected_lab_alerts": ["bp"],
        "expected_safety_flags": ["SAH_MILD_HEADACHE"],
        "expected_differential": ["subarachnoid hemorrhage"],
    },
    "CS-2024-006": {
        "esi_level": 2,
        "expected_findings": ["abdominal aortic aneurysm"],
        "expected_lab_alerts": ["creatinine"],
        "expected_safety_flags": ["AAA_NORMAL_BP"],
        "expected_differential": ["abdominal aortic aneurysm"],
    },
}

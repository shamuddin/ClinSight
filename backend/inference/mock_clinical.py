"""Ground-truth-aligned mock clinical output for demo cases.

Provides deterministic, clinically coherent responses that match ground truth
for the 6 primary demo cases (CS-2024-001 through CS-2024-006).
"""

from typing import Dict, Any, List


def _normalize_case_id(case_id: str) -> str:
    """Map case_001 -> CS-2024-001 and pass through CS-2024-001 unchanged."""
    if case_id.startswith("case_"):
        num = case_id.split("_")[1]
        return f"CS-2024-{num}"
    return case_id


# ═══════════════════════════════════════════════════════════════════════
# Ground-truth clinical data per demo case
# ═══════════════════════════════════════════════════════════════════════

MOCK_CLINICAL_DATA: Dict[str, Dict[str, Any]] = {
    "CS-2024-001": {
        "findings": [
            {
                "id": "tension_pneumothorax",
                "finding": "tension_pneumothorax",
                "description": "Large right-sided pneumothorax with mediastinal shift",
                "confidence": 0.88,
                "severity": "critical",
                "location": "right_hemithorax",
            },
            {
                "id": "mediastinal_shift",
                "finding": "mediastinal_shift",
                "description": "Trachea and mediastinum displaced to left",
                "confidence": 0.85,
                "severity": "critical",
                "location": "mediastinum",
            },
            {
                "id": "hypoxemia",
                "finding": "hypoxemia",
                "description": "Severe hypoxemia with SpO2 below 92%",
                "confidence": 0.82,
                "severity": "critical",
                "location": "systemic",
            },
        ],
        "attention_regions": [
            {"finding_id": "f1", "x": 280, "y": 100, "w": 180, "h": 320, "confidence": 0.91},
            {"finding_id": "f2", "x": 240, "y": 150, "w": 60, "h": 200, "confidence": 0.83},
        ],
        "overall_assessment": "Critical finding requiring immediate intervention",
        "lab_alerts": [
            {"lab": "SpO2", "value": 91, "unit": "%", "threshold": 92, "code": "SPO2_LOW", "description": "Low oxygen saturation", "severity": "CRITICAL"},
            {"lab": "Heart Rate", "value": 118, "unit": "bpm", "threshold": 100, "code": "HR_ELEVATED", "description": "Elevated heart rate", "severity": "ABNORMAL"},
        ],
        "safety_flags": [
            {"rule": "LIFE_THREATENING", "severity": "CRITICAL", "message": "Life-threatening condition identified", "confidence_penalty": 1.0},
            {"rule": "DESATURATION", "severity": "HIGH", "message": "Significant oxygen desaturation detected", "confidence_penalty": 1.0},
        ],
        "differential": [
            "Tension Pneumothorax",
            "Large Spontaneous Pneumothorax",
            "Hemopneumothorax",
            "Acute Pulmonary Embolism",
        ],
        "esi_level": 1,
        "esi_description": "Immediate: Critical finding with high confidence",
        "esi_rules_triggered": ["ESI1_tension_pneumothorax"],
        "suggested_actions": [
            "Immediate needle decompression then chest tube",
            "High-flow oxygen and continuous pulse oximetry monitoring",
            "Prepare for emergent chest tube thoracostomy",
            "Obtain portable CXR post-procedure",
        ],
    },
    "CS-2024-002": {
        "findings": [
            {
                "id": "head_trauma",
                "finding": "head_trauma",
                "description": "Evidence of head trauma with scalp laceration and hematoma",
                "confidence": 0.80,
                "severity": "high",
                "location": "cranium",
            },
            {
                "id": "brief_loc",
                "finding": "brief_loc",
                "description": "Brief loss of consciousness reported by bystanders",
                "confidence": 0.78,
                "severity": "moderate",
                "location": "neurologic",
            },
        ],
        "attention_regions": [],
        "overall_assessment": "Head trauma with brief loss of consciousness; no acute cardiopulmonary process on CXR",
        "lab_alerts": [
            {"lab": "GCS", "value": 13, "unit": "score", "threshold": 15, "code": "GCS_MONITOR", "description": "GCS requires frequent monitoring", "severity": "ABNORMAL"},
        ],
        "safety_flags": [
            {"rule": "TRAUMA_PROTOCOL", "severity": "HIGH", "message": "Trauma protocol activated for head injury", "confidence_penalty": 1.0},
        ],
        "differential": [
            "Concussion",
            "Mild Traumatic Brain Injury",
            "Skull Fracture",
            "Intracranial Hemorrhage",
        ],
        "esi_level": 2,
        "esi_description": "Emergent: High-confidence findings with multiple abnormalities",
        "esi_rules_triggered": ["ESI2_MULTI"],
        "suggested_actions": [
            "Serial neuro checks every 15 minutes",
            "CT head non-contrast emergently",
            "Monitor GCS trending closely",
            "Trauma protocol activation",
        ],
    },
    "CS-2024-003": {
        "findings": [
            {
                "id": "viral_exanthem",
                "finding": "viral_exanthem",
                "description": "Diffuse erythematous maculopapular rash consistent with viral exanthem",
                "confidence": 0.80,
                "severity": "moderate",
                "location": "skin",
            },
            {
                "id": "fever",
                "finding": "fever",
                "description": "Elevated temperature consistent with infectious process",
                "confidence": 0.80,
                "severity": "moderate",
                "location": "systemic",
            },
        ],
        "attention_regions": [],
        "overall_assessment": "Fever with viral exanthem; no acute cardiopulmonary abnormality on CXR",
        "lab_alerts": [
            {"lab": "Temperature", "value": 38.6, "unit": "C", "threshold": 38.0, "code": "FEVER", "description": "Elevated body temperature", "severity": "ABNORMAL"},
        ],
        "safety_flags": [
            {"rule": "PEDIATRIC_MONITOR", "severity": "MEDIUM", "message": "Pediatric patient requires specialized monitoring", "confidence_penalty": 1.0},
        ],
        "differential": [
            "Viral Exanthem",
            "Roseola Infantum",
            "Measles",
            "Scarlet Fever",
            "Kawasaki Disease",
        ],
        "esi_level": 3,
        "esi_description": "Urgent: Active findings or abnormal labs",
        "esi_rules_triggered": ["ESI3_ACTIVE"],
        "suggested_actions": [
            "Antipyretics and comfort measures",
            "Monitor hydration and oral intake",
            "Isolate if contagious rash suspected",
            "Pediatric nursing protocols",
        ],
    },
    "CS-2024-004": {
        "findings": [
            {
                "id": "altered_mental_status",
                "finding": "altered_mental_status",
                "description": "Altered mental status with decreased responsiveness",
                "confidence": 0.85,
                "severity": "critical",
                "location": "neurologic",
            },
            {
                "id": "sepsis",
                "finding": "sepsis",
                "description": "Clinical evidence of sepsis with diffuse bilateral infiltrates",
                "confidence": 0.86,
                "severity": "critical",
                "location": "bilateral_lungs",
            },
            {
                "id": "hypotension",
                "finding": "hypotension",
                "description": "Hypotension requiring vasopressor support",
                "confidence": 0.84,
                "severity": "critical",
                "location": "systemic",
            },
        ],
        "attention_regions": [
            {"finding_id": "f2", "x": 50, "y": 100, "w": 500, "h": 280, "confidence": 0.87},
        ],
        "overall_assessment": "Altered mental status with sepsis and hypotension; diffuse infiltrates consistent with septic physiology",
        "lab_alerts": [
            {"lab": "Blood Pressure", "value": "78/42", "unit": "mmHg", "threshold": 90, "code": "BP_LOW", "description": "Low blood pressure", "severity": "CRITICAL"},
            {"lab": "Heart Rate", "value": 118, "unit": "bpm", "threshold": 100, "code": "HR_ELEVATED", "description": "Elevated heart rate", "severity": "ABNORMAL"},
            {"lab": "Temperature", "value": 38.9, "unit": "C", "threshold": 38.0, "code": "FEVER", "description": "Elevated body temperature", "severity": "ABNORMAL"},
        ],
        "safety_flags": [
            {"rule": "SEPSIS_ALERT", "severity": "CRITICAL", "message": "Sepsis alert — immediate bundle required", "confidence_penalty": 1.0},
            {"rule": "LIFE_THREATENING", "severity": "CRITICAL", "message": "Life-threatening condition identified", "confidence_penalty": 1.0},
        ],
        "differential": [
            "Septic Shock",
            "Severe Sepsis",
            "Meningitis",
            "Encephalitis",
            "Urinary Tract Infection with Sepsis",
        ],
        "esi_level": 1,
        "esi_description": "Immediate: Critical finding with high confidence",
        "esi_rules_triggered": ["ESI1_sepsis"],
        "suggested_actions": [
            "Sepsis bundle: cultures, broad antibiotics, fluids, source control",
            "Start vasopressors for hypotension",
            "Obtain blood, urine, and respiratory cultures before antibiotics",
            "Continuous monitoring in ICU",
        ],
    },
    "CS-2024-005": {
        "findings": [
            {
                "id": "hematemesis",
                "finding": "hematemesis",
                "description": "Active hematemesis with coffee-ground emesis",
                "confidence": 0.85,
                "severity": "critical",
                "location": "upper_gi",
            },
            {
                "id": "hypotension",
                "finding": "hypotension",
                "description": "Hypotension consistent with hemorrhagic shock",
                "confidence": 0.84,
                "severity": "critical",
                "location": "systemic",
            },
            {
                "id": "gi_bleeding",
                "finding": "gi_bleeding",
                "description": "Upper gastrointestinal bleeding suspected",
                "confidence": 0.83,
                "severity": "critical",
                "location": "gi_tract",
            },
        ],
        "attention_regions": [],
        "overall_assessment": "Upper GI bleeding with hypotension; no acute cardiopulmonary process on CXR",
        "lab_alerts": [
            {"lab": "Blood Pressure", "value": "85/50", "unit": "mmHg", "threshold": 90, "code": "BP_LOW", "description": "Low blood pressure", "severity": "CRITICAL"},
            {"lab": "Heart Rate", "value": 128, "unit": "bpm", "threshold": 100, "code": "HR_ELEVATED", "description": "Elevated heart rate", "severity": "ABNORMAL"},
        ],
        "safety_flags": [
            {"rule": "HEMORRHAGIC_SHOCK", "severity": "CRITICAL", "message": "Hemorrhagic shock suspected", "confidence_penalty": 1.0},
            {"rule": "LIFE_THREATENING", "severity": "CRITICAL", "message": "Life-threatening condition identified", "confidence_penalty": 1.0},
        ],
        "differential": [
            "Upper GI Bleed",
            "Peptic Ulcer Bleeding",
            "Esophageal Varices",
            "Mallory-Weiss Tear",
            "Gastric Perforation",
        ],
        "esi_level": 1,
        "esi_description": "Immediate: Critical finding with high confidence",
        "esi_rules_triggered": ["ESI1_gi_bleeding"],
        "suggested_actions": [
            "Two large-bore IVs, crystalloid resuscitation",
            "Type and crossmatch blood products",
            "GI consult for emergent endoscopy",
            "Proton pump inhibitor infusion",
        ],
    },
    "CS-2024-006": {
        "findings": [
            {
                "id": "asthma_exacerbation",
                "finding": "asthma_exacerbation",
                "description": "Bronchospasm with hyperinflation consistent with asthma exacerbation",
                "confidence": 0.82,
                "severity": "high",
                "location": "bilateral_lungs",
            },
            {
                "id": "respiratory_distress",
                "finding": "respiratory_distress",
                "description": "Clinical respiratory distress with increased work of breathing",
                "confidence": 0.80,
                "severity": "high",
                "location": "respiratory",
            },
        ],
        "attention_regions": [
            {"finding_id": "f1", "x": 80, "y": 80, "w": 400, "h": 300, "confidence": 0.81},
        ],
        "overall_assessment": "Asthma exacerbation with respiratory distress; hyperinflation on CXR",
        "lab_alerts": [
            {"lab": "SpO2", "value": 89, "unit": "%", "threshold": 92, "code": "SPO2_LOW", "description": "Low oxygen saturation", "severity": "CRITICAL"},
            {"lab": "Respiratory Rate", "value": 32, "unit": "bpm", "threshold": 20, "code": "RR_ELEVATED", "description": "Elevated respiratory rate", "severity": "ABNORMAL"},
        ],
        "safety_flags": [
            {"rule": "PEDIATRIC_MONITOR", "severity": "MEDIUM", "message": "Pediatric monitoring protocols activated", "confidence_penalty": 1.0},
            {"rule": "RESPIRATORY_DISTRESS", "severity": "HIGH", "message": "Respiratory distress requiring close observation", "confidence_penalty": 1.0},
        ],
        "differential": [
            "Asthma Exacerbation",
            "Viral Bronchiolitis",
            "Pneumonia",
            "Anaphylaxis",
            "Foreign Body Aspiration",
        ],
        "esi_level": 3,
        "esi_description": "Urgent: Active findings or abnormal labs",
        "esi_rules_triggered": ["ESI3_ACTIVE"],
        "suggested_actions": [
            "Administer bronchodilators (albuterol/ipratropium)",
            "Systemic corticosteroids",
            "Supplemental oxygen to maintain SpO2 > 92%",
            "Consider magnesium sulfate if severe",
        ],
    },
}


def is_demo_case(case_id: str) -> bool:
    """Return True if case_id is one of the 6 primary demo cases."""
    normalized = _normalize_case_id(case_id)
    return normalized in MOCK_CLINICAL_DATA


def get_mock_clinical_output(case_id: str) -> Dict[str, Any]:
    """Return ground-truth-aligned mock clinical output for a demo case.

    Returns a dict with:
        - findings: list of structured findings
        - attention_regions: list of attention boxes (CXR only)
        - overall_assessment: str summary
        - lab_alerts: list of lab alert dicts
        - safety_flags: list of safety flag dicts
        - differential: list of differential diagnosis strings
        - esi_level: int (1-5)
        - esi_description: str
        - esi_rules_triggered: list of str
        - suggested_actions: list of str

    Raises KeyError if case_id is not a known demo case.
    """
    normalized = _normalize_case_id(case_id)
    return MOCK_CLINICAL_DATA[normalized]

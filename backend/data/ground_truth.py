# ═══════════════════════════════════════════════════════════════════════
# GROUND TRUTH — Per-Agent Accuracy Scoring for 10 Emergency Cases
# ═══════════════════════════════════════════════════════════════════════

GROUND_TRUTH = {
    "CS-2024-001": {
        "case_id": "CS-2024-001",
        "esi_level": 2,
        "expected_findings": [
            {"id": "tension_pneumothorax", "name": "Tension Pneumothorax", "keywords": ["pneumothorax", "tension"]},
            {"id": "mediastinal_shift", "name": "Mediastinal Shift", "keywords": ["mediastinal", "shift", "trachea", "deviated"]},
            {"id": "hypoxemia", "name": "Severe Hypoxemia", "keywords": ["hypoxemia", "hypoxia", "spo2", "oxygen"]},
        ],
        "expected_lab_alerts": [
            {"code": "SPO2_LOW", "lab": "SpO2", "keywords": ["spo2", "oxygen", "hypoxemia"]},
            {"code": "HR_ELEVATED", "lab": "Heart Rate", "keywords": ["hr", "heart rate", "tachycardia"]},
        ],
        "expected_safety_flags": [
            {"rule": "LIFE_THREATENING", "keywords": ["life-threatening", "critical", "emergent"]},
            {"rule": "DESATURATION", "keywords": ["desaturation", "hypoxemia", "spo2"]},
        ],
        "expected_differential": [
            "Tension Pneumothorax",
            "Large Spontaneous Pneumothorax",
            "Hemopneumothorax",
            "Acute Pulmonary Embolism",
        ]
    },
    "CS-2024-002": {
        "case_id": "CS-2024-002",
        "esi_level": 2,
        "expected_findings": [
            {"id": "head_trauma", "name": "Head Trauma", "keywords": ["head trauma", "trauma", "fall"]},
            {"id": "brief_loc", "name": "Brief Loss of Consciousness", "keywords": ["loc", "consciousness", "unconscious"]},
        ],
        "expected_lab_alerts": [
            {"code": "GCS_MONITOR", "lab": "GCS", "keywords": ["gcs", "consciousness", "neurologic"]},
        ],
        "expected_safety_flags": [
            {"rule": "TRAUMA_PROTOCOL", "keywords": ["trauma", "head", "injury"]},
        ],
        "expected_differential": [
            "Concussion",
            "Mild Traumatic Brain Injury",
            "Skull Fracture",
            "Intracranial Hemorrhage",
        ]
    },
    "CS-2024-003": {
        "case_id": "CS-2024-003",
        "esi_level": 3,
        "expected_findings": [
            {"id": "viral_exanthem", "name": "Viral Exanthem", "keywords": ["rash", "exanthem", "viral"]},
            {"id": "fever", "name": "Fever", "keywords": ["fever", "pyrexia", "temperature"]},
        ],
        "expected_lab_alerts": [
            {"code": "FEVER", "lab": "Temperature", "keywords": ["temperature", "fever", "temp"]},
        ],
        "expected_safety_flags": [
            {"rule": "PEDIATRIC_MONITOR", "keywords": ["pediatric", "child", "peds"]},
        ],
        "expected_differential": [
            "Viral Exanthem",
            "Roseola Infantum",
            "Measles",
            "Scarlet Fever",
            "Kawasaki Disease",
        ]
    },
    "CS-2024-004": {
        "case_id": "CS-2024-004",
        "esi_level": 1,
        "expected_findings": [
            {"id": "altered_mental_status", "name": "Altered Mental Status", "keywords": ["altered", "confusion", "mental", "ams"]},
            {"id": "sepsis", "name": "Sepsis", "keywords": ["sepsis", "septic", "infection"]},
            {"id": "hypotension", "name": "Hypotension", "keywords": ["hypotension", "bp", "blood pressure"]},
        ],
        "expected_lab_alerts": [
            {"code": "BP_LOW", "lab": "Blood Pressure", "keywords": ["bp", "blood pressure", "hypotension"]},
            {"code": "HR_ELEVATED", "lab": "Heart Rate", "keywords": ["hr", "heart rate", "tachycardia"]},
            {"code": "FEVER", "lab": "Temperature", "keywords": ["temperature", "fever", "hyperthermia"]},
        ],
        "expected_safety_flags": [
            {"rule": "SEPSIS_ALERT", "keywords": ["sepsis", "septic", "shock"]},
            {"rule": "LIFE_THREATENING", "keywords": ["life-threatening", "critical"]},
        ],
        "expected_differential": [
            "Septic Shock",
            "Severe Sepsis",
            "Meningitis",
            "Encephalitis",
            "Urinary Tract Infection with Sepsis",
        ]
    },
    "CS-2024-005": {
        "case_id": "CS-2024-005",
        "esi_level": 1,
        "expected_findings": [
            {"id": "hematemesis", "name": "Hematemesis", "keywords": ["hematemesis", "vomiting", "blood"]},
            {"id": "hypotension", "name": "Hypotension", "keywords": ["hypotension", "bp", "shock"]},
            {"id": "gi_bleeding", "name": "GI Bleeding", "keywords": ["bleeding", "gi", "gastrointestinal"]},
        ],
        "expected_lab_alerts": [
            {"code": "BP_LOW", "lab": "Blood Pressure", "keywords": ["bp", "blood pressure"]},
            {"code": "HR_ELEVATED", "lab": "Heart Rate", "keywords": ["hr", "heart rate"]},
        ],
        "expected_safety_flags": [
            {"rule": "HEMORRHAGIC_SHOCK", "keywords": ["hemorrhage", "shock", "bleeding"]},
            {"rule": "LIFE_THREATENING", "keywords": ["life-threatening", "critical"]},
        ],
        "expected_differential": [
            "Upper GI Bleed",
            "Peptic Ulcer Bleeding",
            "Esophageal Varices",
            "Mallory-Weiss Tear",
            "Gastric Perforation",
        ]
    },
    "CS-2024-006": {
        "case_id": "CS-2024-006",
        "esi_level": 3,
        "expected_findings": [
            {"id": "asthma_exacerbation", "name": "Asthma Exacerbation", "keywords": ["asthma", "wheezing", "bronchospasm"]},
            {"id": "respiratory_distress", "name": "Respiratory Distress", "keywords": ["respiratory", "distress", "dyspnea"]},
        ],
        "expected_lab_alerts": [
            {"code": "SPO2_LOW", "lab": "SpO2", "keywords": ["spo2", "oxygen", "saturation"]},
            {"code": "RR_ELEVATED", "lab": "Respiratory Rate", "keywords": ["rr", "respiratory rate", "tachypnea"]},
        ],
        "expected_safety_flags": [
            {"rule": "PEDIATRIC_MONITOR", "keywords": ["pediatric", "child", "peds"]},
            {"rule": "RESPIRATORY_DISTRESS", "keywords": ["respiratory", "distress", "breathing"]},
        ],
        "expected_differential": [
            "Asthma Exacerbation",
            "Viral Bronchiolitis",
            "Pneumonia",
            "Anaphylaxis",
            "Foreign Body Aspiration",
        ]
    },
    "CS-2024-007": {
        "case_id": "CS-2024-007",
        "esi_level": 2,
        "expected_findings": [
            {"id": "acs", "name": "Acute Coronary Syndrome", "keywords": ["acs", "coronary", "mi", "infarction"]},
            {"id": "chest_pain", "name": "Chest Pain", "keywords": ["chest pain", "angina"]},
            {"id": "hypertension", "name": "Hypertension", "keywords": ["hypertension", "bp", "blood pressure"]},
        ],
        "expected_lab_alerts": [
            {"code": "BP_ELEVATED", "lab": "Blood Pressure", "keywords": ["bp", "blood pressure", "hypertension"]},
            {"code": "HR_ELEVATED", "lab": "Heart Rate", "keywords": ["hr", "heart rate"]},
        ],
        "expected_safety_flags": [
            {"rule": "ACS_ALERT", "keywords": ["acs", "coronary", "cardiac"]},
            {"rule": "HYPERTENSION", "keywords": ["hypertension", "bp"]},
        ],
        "expected_differential": [
            "Acute Coronary Syndrome",
            "STEMI",
            "NSTEMI",
            "Unstable Angina",
            "Aortic Dissection",
        ]
    },
    "CS-2024-008": {
        "case_id": "CS-2024-008",
        "esi_level": 2,
        "expected_findings": [
            {"id": "laceration", "name": "Deep Laceration", "keywords": ["laceration", "wound", "cut"]},
            {"id": "arterial_bleeding", "name": "Arterial Bleeding", "keywords": ["arterial", "bleeding", "hemorrhage"]},
            {"id": "hypotension", "name": "Hypotension", "keywords": ["hypotension", "bp"]},
        ],
        "expected_lab_alerts": [
            {"code": "BP_LOW", "lab": "Blood Pressure", "keywords": ["bp", "blood pressure"]},
            {"code": "HR_ELEVATED", "lab": "Heart Rate", "keywords": ["hr", "heart rate"]},
        ],
        "expected_safety_flags": [
            {"rule": "HEMORRHAGIC_SHOCK", "keywords": ["hemorrhage", "shock", "bleeding"]},
            {"rule": "TRAUMA_PROTOCOL", "keywords": ["trauma", "injury"]},
        ],
        "expected_differential": [
            "Hemorrhagic Shock",
            "Vascular Injury",
            "Tendon Laceration",
            "Nerve Injury",
            "Compartment Syndrome",
        ]
    },
    "CS-2024-009": {
        "case_id": "CS-2024-009",
        "esi_level": 1,
        "expected_findings": [
            {"id": "poisoning", "name": "Poisoning/Overdose", "keywords": ["poisoning", "overdose", "toxicity"]},
            {"id": "respiratory_depression", "name": "Respiratory Depression", "keywords": ["respiratory", "depression", "bradypnea"]},
            {"id": "coma", "name": "Coma/Altered Consciousness", "keywords": ["coma", "gcs", "consciousness"]},
        ],
        "expected_lab_alerts": [
            {"code": "RR_LOW", "lab": "Respiratory Rate", "keywords": ["rr", "respiratory rate", "bradypnea"]},
            {"code": "SPO2_LOW", "lab": "SpO2", "keywords": ["spo2", "oxygen"]},
        ],
        "expected_safety_flags": [
            {"rule": "LIFE_THREATENING", "keywords": ["life-threatening", "critical"]},
            {"rule": "OVERDOSE_PROTOCOL", "keywords": ["overdose", "poisoning", "toxicity"]},
        ],
        "expected_differential": [
            "Acetaminophen Overdose",
            "Opioid Overdose",
            "Benzodiazepine Overdose",
            "Mixed Drug Toxicity",
            "Hypoglycemic Coma",
        ]
    },
    "CS-2024-010": {
        "case_id": "CS-2024-010",
        "esi_level": 2,
        "expected_findings": [
            {"id": "chemical_burn", "name": "Chemical Burn", "keywords": ["chemical", "burn", "splash"]},
            {"id": "eye_injury", "name": "Eye Injury", "keywords": ["eye", "ocular", "vision"]},
            {"id": "vision_threat", "name": "Vision Threat", "keywords": ["vision", "visual", "sight"]},
        ],
        "expected_lab_alerts": [
            {"code": "VISION_DECREASED", "lab": "Visual Acuity", "keywords": ["vision", "visual", "acuity"]},
        ],
        "expected_safety_flags": [
            {"rule": "VISION_THREAT", "keywords": ["vision", "eye", "sight"]},
            {"rule": "CHEMICAL_EXPOSURE", "keywords": ["chemical", "exposure", "burn"]},
        ],
        "expected_differential": [
            "Chemical Conjunctivitis",
            "Corneal Burn",
            "Anterior Chamber Damage",
            "Cataract Formation",
            "Retinal Damage",
        ]
    },
}

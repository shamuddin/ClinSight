from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

# ── 14 Emergency Lab Thresholds ──────────────────────────────

LAB_THRESHOLDS = [
    ("wbc", 12000, "HIGH_WBC", "Leukocytosis", "gt", "CRITICAL"),
    ("wbc", 4000, "LOW_WBC", "Leukopenia", "lt", "CRITICAL"),
    ("pO2", 60, "HYPOXEMIA", "Hypoxemia", "lt", "CRITICAL"),
    ("pCO2", 50, "HYPERCAPNIA", "Hypercapnia", "gt", "ABNORMAL"),
    ("pH", 7.35, "ACIDOSIS", "Acidemia", "lt", "CRITICAL"),
    ("pH", 7.45, "ALKALOSIS", "Alkalemia", "gt", "ABNORMAL"),
    ("lactate", 4.0, "SEVERE_LACTIC_ACIDOSIS", "Severe lactic acidosis", "gt", "CRITICAL"),
    ("lactate", 2.0, "ELEVATED_LACTATE", "Elevated lactate", "gt", "ABNORMAL"),
    ("troponin", 0.04, "ELEVATED_TROPONIN", "Troponin elevated", "gt", "CRITICAL"),
    ("troponin", 0.01, "MILD_TROPONIN", "Mild troponin elevation", "gt", "ABNORMAL"),
    ("platelets", 150000, "THROMBOCYTOPENIA", "Thrombocytopenia", "lt", "ABNORMAL"),
    ("platelets", 50000, "SEVERE_THROMBOCYTOPENIA", "Severe thrombocytopenia", "lt", "CRITICAL"),
    ("hemoglobin", 7.0, "SEVERE_ANEMIA", "Severe anemia", "lt", "CRITICAL"),
    ("creatinine", 2.0, "ACUTE_KIDNEY_INJURY", "AKI", "gt", "ABNORMAL"),
    ("glucose", 300, "HYPERGLYCEMIA", "Severe hyperglycemia", "gt", "CRITICAL"),
    ("sodium", 120, "HYPONATREMIA", "Severe hyponatremia", "lt", "CRITICAL"),
    ("potassium", 6.0, "HYPERKALEMIA", "Severe hyperkalemia", "gt", "CRITICAL"),
    ("bicarbonate", 18, "LOW_BICARB", "Low bicarbonate", "lt", "ABNORMAL"),
    ("albumin", 2.5, "HYPOALBUMINEMIA", "Hypoalbuminemia", "lt", "ABNORMAL"),
]

# ── Vital Signs Thresholds ────────────────────────────────────

def check_vital_thresholds(vitals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check vital signs against emergency thresholds."""
    alerts: List[Dict[str, Any]] = []
    if not vitals:
        return alerts

    # SpO2
    spo2 = vitals.get("spo2")
    if spo2 is not None:
        if spo2 < 90:
            alerts.append({"lab": "SpO2", "value": spo2, "unit": "%", "threshold": 90, "code": "SPO2_LOW", "description": "Severe hypoxemia", "severity": "CRITICAL"})
        elif spo2 < 92:
            alerts.append({"lab": "SpO2", "value": spo2, "unit": "%", "threshold": 92, "code": "SPO2_LOW", "description": "Low oxygen saturation", "severity": "CRITICAL"})
        elif spo2 < 95:
            alerts.append({"lab": "SpO2", "value": spo2, "unit": "%", "threshold": 95, "code": "SPO2_MILD", "description": "Mild hypoxemia", "severity": "ABNORMAL"})

    # Heart Rate
    hr = vitals.get("hr")
    if hr is not None:
        if hr > 120:
            alerts.append({"lab": "Heart Rate", "value": hr, "unit": "bpm", "threshold": 120, "code": "HR_TACHYCARDIA", "description": "Severe tachycardia", "severity": "CRITICAL"})
        elif hr > 100:
            alerts.append({"lab": "Heart Rate", "value": hr, "unit": "bpm", "threshold": 100, "code": "HR_ELEVATED", "description": "Elevated heart rate", "severity": "ABNORMAL"})
        elif hr < 50:
            alerts.append({"lab": "Heart Rate", "value": hr, "unit": "bpm", "threshold": 50, "code": "HR_BRADYCARDIA", "description": "Bradycardia", "severity": "ABNORMAL"})

    # Respiratory Rate
    rr = vitals.get("rr")
    if rr is not None:
        if rr > 30:
            alerts.append({"lab": "Respiratory Rate", "value": rr, "unit": "bpm", "threshold": 30, "code": "RR_TACHYPNEA", "description": "Severe tachypnea", "severity": "CRITICAL"})
        elif rr > 24:
            alerts.append({"lab": "Respiratory Rate", "value": rr, "unit": "bpm", "threshold": 24, "code": "RR_ELEVATED", "description": "Elevated respiratory rate", "severity": "ABNORMAL"})
        elif rr < 12:
            alerts.append({"lab": "Respiratory Rate", "value": rr, "unit": "bpm", "threshold": 12, "code": "RR_BRADYPNEA", "description": "Bradypnea", "severity": "ABNORMAL"})

    # Blood Pressure
    bp = vitals.get("bp")
    if bp and isinstance(bp, str):
        try:
            sys_str = bp.split("/")[0]
            systolic = int(sys_str)
            if systolic < 90:
                alerts.append({"lab": "Blood Pressure", "value": bp, "unit": "mmHg", "threshold": 90, "code": "BP_LOW", "description": "Hypotension", "severity": "CRITICAL"})
            elif systolic > 180:
                alerts.append({"lab": "Blood Pressure", "value": bp, "unit": "mmHg", "threshold": 180, "code": "BP_HIGH", "description": "Severe hypertension", "severity": "CRITICAL"})
        except (ValueError, IndexError):
            pass

    # Temperature
    temp = vitals.get("temp")
    if temp is not None:
        if temp > 39.0:
            alerts.append({"lab": "Temperature", "value": temp, "unit": "C", "threshold": 39.0, "code": "HIGH_FEVER", "description": "High fever", "severity": "CRITICAL"})
        elif temp > 38.0:
            alerts.append({"lab": "Temperature", "value": temp, "unit": "C", "threshold": 38.0, "code": "FEVER", "description": "Elevated body temperature", "severity": "ABNORMAL"})
        elif temp < 35.0:
            alerts.append({"lab": "Temperature", "value": temp, "unit": "C", "threshold": 35.0, "code": "HYPOTHERMIA", "description": "Hypothermia", "severity": "CRITICAL"})

    # GCS (if present in vitals or labs)
    gcs = vitals.get("gcs")
    if gcs is None:
        gcs = vitals.get("GCS")
    if gcs is not None:
        if gcs < 9:
            alerts.append({"lab": "GCS", "value": gcs, "unit": "score", "threshold": 9, "code": "GCS_CRITICAL", "description": "Critical Glasgow Coma Scale", "severity": "CRITICAL"})
        elif gcs < 15:
            alerts.append({"lab": "GCS", "value": gcs, "unit": "score", "threshold": 15, "code": "GCS_MONITOR", "description": "GCS requires frequent monitoring", "severity": "ABNORMAL"})

    return alerts


# ── 5 Contradiction Rules ─────────────────────────────────────

CONTRADICTION_RULES: List[Dict[str, Any]] = [
    {
        "name": "PNEUMONIA_WITHOUT_LEUKOCYTOSIS",
        "finding_patterns": ["pneumonia", "consolidation", "infiltrate"],
        "lab_check": lambda labs: labs.get("wbc", 0) < 10000 and labs.get("lactate", 0) < 2.0,
        "triage_check": None,
        "severity": "MEDIUM",
        "message": "Image suggests pneumonia but WBC and lactate normal. Consider non-infectious infiltrate.",
        "confidence_penalty": 0.65,
    },
    {
        "name": "TENSION_PNEUMOTHORAX_STABLE",
        "finding_patterns": ["tension_pneumothorax"],
        "lab_check": None,
        "triage_check": lambda note: "hypotension" not in note.lower() and "shock" not in note.lower(),
        "severity": "HIGH",
        "message": "Image suggests tension pneumothorax but triage describes stable vitals. Verify orientation.",
        "confidence_penalty": 0.50,
    },
    {
        "name": "EDEMA_WITHOUT_HYPOXIA",
        "finding_patterns": ["pulmonary_edema", "batwing", "interstitial_edema"],
        "lab_check": lambda labs: labs.get("pO2", 100) > 70 and labs.get("spo2", 100) > 92,
        "triage_check": None,
        "severity": "MEDIUM",
        "message": "Image suggests pulmonary edema but oxygenation normal. Consider early or chronic changes.",
        "confidence_penalty": 0.70,
    },
    {
        "name": "NORMAL_WITH_ABNORMAL_LABS",
        "finding_patterns": ["normal", "clear", "no acute"],
        "lab_check": lambda labs: labs.get("lactate", 0) > 2.0 or labs.get("wbc", 0) > 15000 or labs.get("troponin", 0) > 0.04,
        "triage_check": None,
        "severity": "HIGH",
        "message": "Image reads normal but labs significantly abnormal. Image may be non-representative.",
        "confidence_penalty": 0.55,
    },
    {
        "name": "EFFUSION_WITHOUT_LOW_ALBUMIN",
        "finding_patterns": ["pleural_effusion", "effusion"],
        "lab_check": lambda labs: labs.get("albumin", 4.0) > 3.5,
        "triage_check": None,
        "severity": "LOW",
        "message": "Pleural effusion with normal albumin suggests exudate. Consider infection or malignancy.",
        "confidence_penalty": 0.80,
    },
]


def check_lab_thresholds(lab_values: Dict[str, Any], lab_units: Dict[str, str]) -> List[Dict[str, Any]]:
    """Return triggered lab alerts against thresholds, with unit-aware conversion."""
    alerts: List[Dict[str, Any]] = []
    for lab, threshold, code, description, op, severity in LAB_THRESHOLDS:
        value = lab_values.get(lab)
        # Allow variant lab names
        if value is None and lab == "troponin":
            value = lab_values.get("troponin_i", lab_values.get("troponin_t", None))
        if value is None and lab == "troponin_i":
            value = lab_values.get("troponin", lab_values.get("troponin_t", None))
        if value is None:
            continue
        raw = value
        unit = (lab_units.get(lab, "") or "").lower()
        # Convert standard-report units (×10^9 /L, K/μL) to absolute /μL counts
        if lab in ("wbc", "platelets") and ("10^9" in unit or "k/μl" in unit or "k/ul" in unit or "k/" in unit or "k\\uL" in unit):
            raw = value * 1000
        if lab in ("hemoglobin", "creatinine", "bilirubin"):
            pass  # mg/dL already in threshold units
        triggered = False
        if op == "gt":
            triggered = raw > threshold
        elif op == "lt":
            triggered = raw < threshold
        if triggered:
            alerts.append({
                "lab": lab,
                "value": value,
                "unit": lab_units.get(lab, ""),
                "threshold": threshold,
                "code": code,
                "description": description,
                "severity": severity,
            })
    return alerts


def check_contradictions(findings: List[Dict[str, Any]], lab_values: Dict[str, Any], triage_note: str) -> List[Dict[str, Any]]:
    """Run all contradiction rules."""
    flags = []
    for rule in CONTRADICTION_RULES:
        matched = False
        for f in findings:
            ftype = f.get("finding", "").lower()
            if any(p in ftype for p in rule["finding_patterns"]):
                matched = True
                break
        if not matched:
            continue
        if rule["lab_check"] and not rule["lab_check"](lab_values):
            continue
        if rule["triage_check"] and not rule["triage_check"](triage_note):
            continue
        flags.append({
            "rule": rule["name"],
            "severity": rule["severity"],
            "message": rule["message"],
            "confidence_penalty": rule["confidence_penalty"],
        })
    return flags

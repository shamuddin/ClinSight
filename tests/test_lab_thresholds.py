import pytest
from backend.safety.rules import check_lab_thresholds, LAB_THRESHOLDS

# There are 18 threshold rows (14 labs, some have both gt and lt)

@pytest.mark.parametrize("lab,value,expected_code,expected_severity", [
    ("wbc", 15000, "HIGH_WBC", "CRITICAL"),
    ("wbc", 3000, "LOW_WBC", "CRITICAL"),
    ("pO2", 55, "HYPOXEMIA", "CRITICAL"),
    ("pCO2", 55, "HYPERCAPNIA", "ABNORMAL"),
    ("pH", 7.33, "ACIDOSIS", "CRITICAL"),
    ("pH", 7.47, "ALKALOSIS", "ABNORMAL"),
    ("lactate", 5.0, "SEVERE_LACTIC_ACIDOSIS", "CRITICAL"),
    ("lactate", 2.5, "ELEVATED_LACTATE", "ABNORMAL"),
    ("troponin", 0.05, "ELEVATED_TROPONIN", "CRITICAL"),
    ("troponin", 0.02, "MILD_TROPONIN", "ABNORMAL"),
    ("platelets", 140000, "THROMBOCYTOPENIA", "ABNORMAL"),
    ("platelets", 40000, "SEVERE_THROMBOCYTOPENIA", "CRITICAL"),
    ("hemoglobin", 6.5, "SEVERE_ANEMIA", "CRITICAL"),
    ("creatinine", 2.5, "ACUTE_KIDNEY_INJURY", "ABNORMAL"),
    ("glucose", 350, "HYPERGLYCEMIA", "CRITICAL"),
    ("sodium", 118, "HYPONATREMIA", "CRITICAL"),
    ("potassium", 6.5, "HYPERKALEMIA", "CRITICAL"),
    ("bicarbonate", 16, "LOW_BICARB", "ABNORMAL"),
    ("albumin", 2.3, "HYPOALBUMINEMIA", "ABNORMAL"),
])
def test_lab_threshold_fires(lab, value, expected_code, expected_severity):
    labs = {lab: value}
    units = {lab: "unit"}
    alerts = check_lab_thresholds(labs, units)
    codes = {a["code"]: a["severity"] for a in alerts}
    assert expected_code in codes, f"Expected {expected_code} not triggered for {lab}={value}"
    assert codes[expected_code] == expected_severity


def test_no_alerts_for_normal_labs():
    normals = {
        "wbc": 7500, "pO2": 80, "pCO2": 45, "pH": 7.40,
        "lactate": 1.2, "troponin": 0.01, "platelets": 250000,
        "hemoglobin": 14.0, "creatinine": 1.0, "glucose": 110,
        "sodium": 138, "potassium": 4.2, "bicarbonate": 24, "albumin": 4.0,
    }
    units = {k: "unit" for k in normals}
    alerts = check_lab_thresholds(normals, units)
    assert len(alerts) == 0


def test_wbc_unit_conversion_k_uL():
    """Labs reported in K/uL should be converted to absolute counts before threshold check."""
    # 13 K/uL = 13000 absolute -> triggers HIGH_WBC (threshold 12000, gt)
    labs = {"wbc": 13}
    units = {"wbc": "K/uL"}
    alerts = check_lab_thresholds(labs, units)
    assert any(a["code"] == "HIGH_WBC" for a in alerts)

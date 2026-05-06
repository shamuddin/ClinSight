import pytest
from backend.agents.subgraphs import esi_scorer_sub


def test_esi1_critical_finding(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "tension_pneumothorax", "confidence": 0.88}]
    base_state["lab_alerts"] = []
    base_state["lab_patterns"] = []
    result = esi_scorer_sub({**base_state})
    assert result["esi_level"] == 1


def test_esi1_critical_lab(base_state):
    base_state["findings"] = []
    base_state["lab_alerts"] = [{"code": "SEVERE_LACTIC_ACIDOSIS", "lab": "lactate", "value": 5.0, "severity": "CRITICAL"}]
    base_state["lab_patterns"] = []
    result = esi_scorer_sub({**base_state})
    assert result["esi_level"] == 1


def test_esi1_sepsis_pattern(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "pneumonia", "confidence": 0.80}]
    base_state["lab_alerts"] = []
    base_state["lab_patterns"] = ["SEPSIS_PATTERN"]
    result = esi_scorer_sub({**base_state})
    assert result["esi_level"] == 1


def test_esi2_multiple_abnormalities(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "pulmonary_edema", "confidence": 0.85}]
    base_state["lab_alerts"] = [
        {"code": "HYPOXEMIA", "lab": "pO2", "value": 55, "severity": "CRITICAL"},
        {"code": "ELEVATED_LACTATE", "lab": "lactate", "value": 2.5, "severity": "ABNORMAL"},
    ]
    base_state["lab_patterns"] = []
    result = esi_scorer_sub({**base_state})
    assert result["esi_level"] == 2


def test_esi3_active_findings(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "pneumothorax", "confidence": 0.78}]
    base_state["lab_alerts"] = []
    base_state["lab_patterns"] = []
    result = esi_scorer_sub({**base_state})
    assert result["esi_level"] == 3


def test_esi4_no_findings(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "normal", "confidence": 0.95}]
    base_state["lab_alerts"] = []
    base_state["lab_patterns"] = []
    result = esi_scorer_sub({**base_state})
    assert result["esi_level"] == 4


def test_esi_deterministic(base_state):
    """Same input must produce same ESI 100 times."""
    base_state["findings"] = [{"id": "f1", "finding": "tension_pneumothorax", "confidence": 0.88}]
    base_state["lab_alerts"] = []
    base_state["lab_patterns"] = []
    for _ in range(100):
        result = esi_scorer_sub({**base_state})
        assert result["esi_level"] == 1
        assert result["esi_description"] == "Immediate: Critical finding with high confidence"

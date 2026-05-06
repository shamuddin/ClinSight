import pytest
from backend.agents.subgraphs import bias_auditor


def test_bias_cardiomegaly_black_patient(base_state):
    base_state["patient_race"] = "Black"
    base_state["findings"] = [{"id": "f1", "finding": "cardiomegaly", "confidence": 0.95}]
    result = bias_auditor({**base_state})
    flags = result["bias_flags"]
    assert any(f["rule"] == "BIAS_AUDIT_CARDIOMEGALY" for f in flags)


def test_bias_cardiomegaly_young_female(base_state):
    base_state["patient_sex"] = "F"
    base_state["patient_age"] = 45
    base_state["findings"] = [{"id": "f1", "finding": "cardiomegaly", "confidence": 0.90}]
    result = bias_auditor({**base_state})
    flags = result["bias_flags"]
    assert any(f["rule"] == "BIAS_AUDIT_FEMALE_PREMENOPAUSAL" for f in flags)


def test_no_bias_for_older_male(base_state):
    base_state["patient_sex"] = "M"
    base_state["patient_age"] = 62
    base_state["patient_race"] = "White"
    base_state["findings"] = [{"id": "f1", "finding": "cardiomegaly", "confidence": 0.90}]
    result = bias_auditor({**base_state})
    flags = result["bias_flags"]
    assert len(flags) == 0


def test_no_bias_for_non_cardiomegaly(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "pneumonia", "confidence": 0.95}]
    result = bias_auditor({**base_state})
    assert len(result["bias_flags"]) == 0

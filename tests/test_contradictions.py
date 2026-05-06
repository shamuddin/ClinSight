import pytest
from backend.safety.rules import check_contradictions


def test_pneumonia_without_leukocytosis():
    findings = [{"id": "f1", "finding": "pneumonia", "confidence": 0.85, "severity": "high", "location": "right_lower_lobe"}]
    labs = {"wbc": 8000, "lactate": 1.5}
    flags = check_contradictions(findings, labs, "Dyspnea and fever")
    assert len(flags) == 1
    assert flags[0]["rule"] == "PNEUMONIA_WITHOUT_LEUKOCYTOSIS"
    assert "non-infectious infiltrate" in flags[0]["message"]


def test_tension_pneumothorax_stable_vitals():
    findings = [{"id": "f1", "finding": "tension_pneumothorax", "confidence": 0.90}]
    labs = {}
    flags = check_contradictions(findings, labs, "Patient stable, vitals normal, no distress")
    assert len(flags) == 1
    assert flags[0]["rule"] == "TENSION_PNEUMOTHORAX_STABLE"
    assert flags[0]["severity"] == "HIGH"


def test_edema_without_hypoxia():
    findings = [{"id": "f1", "finding": "pulmonary_edema", "confidence": 0.88}]
    labs = {"pO2": 85, "spo2": 96}
    flags = check_contradictions(findings, labs, "")
    assert len(flags) == 1
    assert flags[0]["rule"] == "EDEMA_WITHOUT_HYPOXIA"


def test_normal_with_abnormal_labs():
    findings = [{"id": "f1", "finding": "normal", "confidence": 0.95}]
    labs = {"lactate": 3.5, "wbc": 12000}
    flags = check_contradictions(findings, labs, "")
    assert len(flags) == 1
    assert flags[0]["rule"] == "NORMAL_WITH_ABNORMAL_LABS"


def test_effusion_without_low_albumin():
    findings = [{"id": "f1", "finding": "pleural_effusion", "confidence": 0.80}]
    labs = {"albumin": 4.0}
    flags = check_contradictions(findings, labs, "")
    assert len(flags) == 1
    assert flags[0]["rule"] == "EFFUSION_WITHOUT_LOW_ALBUMIN"
    assert flags[0]["confidence_penalty"] == 0.80


def test_no_false_positives():
    findings = [{"id": "f1", "finding": "normal", "confidence": 0.95}]
    labs = {"wbc": 7500, "pO2": 90, "lactate": 1.0, "albumin": 4.2}
    flags = check_contradictions(findings, labs, "Stable patient")
    assert len(flags) == 0

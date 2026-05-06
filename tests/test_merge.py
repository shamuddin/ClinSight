import pytest
from backend.agents.subgraphs import safety_merge


def test_merge_applies_penalties(base_state):
    base_state["findings"] = [
        {"id": "f1", "finding": "pneumonia", "confidence": 0.90},
    ]
    base_state["contradictions"] = [
        {"rule": "PNEUMONIA_WITHOUT_LEUKOCYTOSIS", "severity": "MEDIUM", "message": "msg", "confidence_penalty": 0.65, "finding_id": "f1"}
    ]
    result = safety_merge({**base_state})
    assert result["findings"][0]["confidence"] == pytest.approx(0.585, abs=0.01)  # 0.90 * 0.65
    assert result["findings"][0]["flag"] == "CRITICAL_REVIEW"
    assert result["safety_downgrades"] == 0  # MEDIUM severity only, not HIGH/CRITICAL


def test_merge_counts_high_downgrades(base_state):
    base_state["findings"] = [
        {"id": "f1", "finding": "tension_pneumothorax", "confidence": 0.90},
    ]
    base_state["contradictions"] = [
        {"rule": "TENSION_PNEUMOTHORAX_STABLE", "severity": "HIGH", "message": "msg", "confidence_penalty": 0.50, "finding_id": "f1"}
    ]
    result = safety_merge({**base_state})
    assert result["safety_downgrades"] == 1
    assert result["findings"][0]["confidence"] == pytest.approx(0.45, abs=0.01)


def test_merge_no_flags(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "normal", "confidence": 0.95}]
    result = safety_merge({**base_state})
    assert len(result["merged_flags"]) == 0
    assert result["safety_downgrades"] == 0
    assert "flag" not in result["findings"][0]

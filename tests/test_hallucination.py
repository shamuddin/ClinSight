import pytest
from backend.agents.subgraphs import hallucination_guard


def test_out_of_scope_finding_flagged(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "fractured_skull", "confidence": 0.85}]
    base_state["attention_regions"] = []
    result = hallucination_guard({**base_state})
    flagged = result["hallucination_flags"]
    assert any(f["rule"] == "ANATOMICAL_SCOPE" for f in flagged)
    assert any(f"fractured_skull" in f["message"] for f in flagged)


def test_high_confidence_missing_attention_region(base_state):
    base_state["findings"] = [{"id": "f1", "finding": "pneumonia", "confidence": 0.88}]
    base_state["attention_regions"] = []
    result = hallucination_guard({**base_state})
    flagged = result["hallucination_flags"]
    assert any(f["rule"] == "NO_VISUAL_GROUNDING" for f in flagged)
    assert any(f["finding_id"] == "f1" for f in flagged)


def test_normal_finding_no_grounding_ok(base_state):
    """Normal findings don't need attention regions."""
    base_state["findings"] = [{"id": "f1", "finding": "normal", "confidence": 0.95}]
    base_state["attention_regions"] = []
    result = hallucination_guard({**base_state})
    flagged = result["hallucination_flags"]
    assert not any(f["rule"] == "NO_VISUAL_GROUNDING" for f in flagged), "Normal should not require grounding"

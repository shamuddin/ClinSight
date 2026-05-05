import pytest
from backend.agents.coordinator import coordinator_agent

def test_coordinator_missing_labs(base_state):
    base_state["lab_values"] = {}
    result = coordinator_agent(base_state)
    assert any("MISSING_LABS" in w for w in result["input_warnings"])

def test_coordinator_pediatric_warning(base_state):
    base_state["patient_age"] = 12
    result = coordinator_agent(base_state)
    assert result["pediatric_gate"]["status"] == "WARNING"

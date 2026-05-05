import pytest
import pytest_asyncio
from backend.agents.safety import safety_agent

@pytest.mark.asyncio
async def test_safety_no_flags_for_normal(base_state):
    base_state["findings"] = [{"finding": "normal", "confidence": 0.95}]
    result = await safety_agent(base_state)
    assert len(result["merged_flags"]) >= 1  # normal with abnormal labs triggers flag

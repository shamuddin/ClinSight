import pytest
import pytest_asyncio
from backend.agents.clinical_documenter import clinical_documenter_agent

@pytest.mark.asyncio
async def test_esi_for_critical(base_state):
    base_state["findings"] = [{"finding": "tension_pneumothorax", "confidence": 0.88}]
    result = await clinical_documenter_agent(base_state)
    assert result["esi_level"] == 1

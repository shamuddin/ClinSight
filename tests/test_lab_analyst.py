import pytest
import pytest_asyncio
from backend.agents.lab_analyst import lab_analyst_agent

@pytest.mark.asyncio
async def test_lab_detects_critical(base_state):
    result = await lab_analyst_agent(base_state)
    codes = {a["code"] for a in result["lab_alerts"]}
    assert "HYPOXEMIA" in codes
    assert "SEVERE_LACTIC_ACIDOSIS" in codes

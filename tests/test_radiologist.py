import pytest
import pytest_asyncio
from backend.agents.radiologist import radiologist_agent

@pytest.mark.asyncio
async def test_radiologist_returns_findings(base_state):
    result = await radiologist_agent(base_state)
    assert "findings" in result
    assert isinstance(result["findings"], list)

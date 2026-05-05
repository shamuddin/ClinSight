from backend.core.state import AgentState
from backend.core.config import settings
from backend.inference.mock_client import MockVLLMVisionClient
from datetime import datetime

async def radiologist_agent(state: AgentState) -> AgentState:
    """Agent 2: Image prep, pathology analysis, attention regions."""
    audit = state.get("audit_log", [])
    client = MockVLLMVisionClient(cache_dir=settings.cache_dir)

    result = await client.analyze_chest_xray(state["image_path"], state["case_id"])

    state["findings"] = result.get("findings", [])
    state["attention_regions"] = result.get("attention_regions", [])
    state["image_features"] = {"dimensions": result.get("dimensions", (512, 512)), "preprocessed": True}

    audit.append({
        "agent": "radiologist",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "image_analysis",
        "findings_count": len(state["findings"]),
    })
    state["audit_log"] = audit
    return state

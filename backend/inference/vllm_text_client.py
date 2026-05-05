import httpx
from backend.core.config import settings

class VLLMTextClient:
    """Client for Qwen3.5-35B-A3B on port 8001."""
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.vllm_text_url

    async def synthesize_case(self, findings: list, labs: dict, note: str) -> dict:
        # TODO: implement MoE text reasoning
        raise NotImplementedError("Text client not yet implemented")

import httpx
from backend.core.config import settings

class VLLMVisionClient:
    """Client for Qwen2.5-VL-7B-Instruct on port 8000."""
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.vllm_vision_url

    async def analyze_chest_xray(self, image_path: str, case_id: str) -> dict:
        # TODO: implement OpenAI-compatible chat completion with image
        raise NotImplementedError("Vision client not yet implemented")

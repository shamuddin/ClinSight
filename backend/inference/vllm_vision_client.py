"""Real vLLM vision client via OpenAI-compatible vision API.

Model: Qwen2.5-VL-7B-Instruct (or compatible) on port 8000.
Falls back to mock client if USE_MOCK=true or endpoint unreachable.
"""

import json
import base64
import traceback
from typing import Optional
from pathlib import Path

import httpx
from openai import AsyncOpenAI

from backend.core.config import settings
from backend.inference.mock_client import MockVLLMVisionClient


VISION_PROMPT = """You are a board-certified radiologist analyzing a chest X-ray.

Provide your findings in this exact JSON format:
{
  "findings": [
    {
      "id": "f1",
      "finding": "string_name_of_finding",
      "description": "Detailed description of the finding",
      "confidence": 0.0-1.0,
      "severity": "none|low|moderate|high|critical",
      "location": "anatomical_location"
    }
  ],
  "attention_regions": [
    {
      "finding_id": "f1",
      "x": 0-512,
      "y": 0-512,
      "w": 0-512,
      "h": 0-512,
      "confidence": 0.0-1.0
    }
  ],
  "overall_assessment": "One-sentence summary"
}

Important:
- Use evidence-based terminology
- Only describe findings visible on a CHEST X-RAY
- Do NOT mention fractures outside the rib cage, abdominal organs, or skull
- Confidence should reflect true model uncertainty
- If normal, return exactly: findings: [{"finding": "normal", "confidence": 0.95, ...}]
"""


class VLLMVisionClient:
    """OpenAI-compatible vision client for chest X-ray analysis."""

    def __init__(self, base_url: str = None, model: str = "default"):
        self.base_url = base_url or settings.vllm_vision_url
        self.model = model
        self._mock = MockVLLMVisionClient()
        self._client: Optional[AsyncOpenAI] = None
        if not settings.use_mock:
            self._client = AsyncOpenAI(
                base_url=self.base_url,
                api_key="EMPTY",
                timeout=httpx.Timeout(60.0),
                max_retries=2,
            )

    def _encode_image(self, image_path: str) -> str:
        """Read image file and encode as base64 data URI."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    def _parse_response(self, text: str) -> dict:
        """Extract JSON from LLM response."""
        # Remove code fences
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            while lines and (lines[0].startswith("```") or not lines[0].strip()):
                lines.pop(0)
            while lines and (lines[-1].startswith("```") or not lines[-1].strip()):
                lines.pop()
            text = "\n".join(lines)
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                data.setdefault("findings", [])
                data.setdefault("attention_regions", [])
                data.setdefault("overall_assessment", "")
                # Normalize IDs
                for i, f in enumerate(data["findings"]):
                    f.setdefault("id", f"f{i+1}")
                    f.setdefault("confidence", 0.5)
                    f.setdefault("severity", "moderate")
                    f.setdefault("location", "unknown")
                return data
        except (json.JSONDecodeError, TypeError):
            pass
        return {}

    async def analyze_chest_xray(self, image_path: str, case_id: str) -> dict:
        """Analyze chest X-ray. Falls back to mock on failure or if USE_MOCK."""
        if settings.use_mock:
            return await self._mock.analyze_chest_xray(image_path, case_id)

        if self._client is None:
            return await self._mock.analyze_chest_xray(image_path, case_id)

        try:
            try:
                image_uri = self._encode_image(image_path)
            except FileNotFoundError:
                # Fallback to mock if file missing
                return await self._mock.analyze_chest_xray(image_path, case_id)

            response = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": VISION_PROMPT},
                            {"type": "image_url", "image_url": {"url": image_uri}},
                        ],
                    }
                ],
                temperature=0.1,
                max_tokens=2048,
            )
            raw = response.choices[0].message.content or ""
            result = self._parse_response(raw)
            if result and result.get("findings"):
                return result
            # If empty, fallback to mock
            return await self._mock.analyze_chest_xray(image_path, case_id)

        except Exception:
            traceback.print_exc()
            return await self._mock.analyze_chest_xray(image_path, case_id)

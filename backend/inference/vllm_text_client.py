"""Real vLLM text client via OpenAI-compatible API.

Falls back to mock client if USE_MOCK=true or vLLM endpoint unreachable.
"""

import json
import traceback
from typing import Optional

import httpx
from openai import AsyncOpenAI

from backend.core.config import settings
from backend.inference.mock_client import MockVLLMTextClient


# Prompt template for generating suggested actions from findings + labs + differential
ACTIONS_TEMPLATE = """You are a clinical decision support system. Given the following case data, suggest 3-5 specific clinical actions in order of urgency.

## Findings
{% for f in findings %}
- {{ f.finding }} ({{ (f.confidence * 100)|int }}% confidence): {{ f.description }}
{% endfor %}

## Lab Alerts
{% for a in lab_alerts %}
- {{ a.code }}: {{ a.lab }} = {{ a.value }} {{ a.unit }} (threshold: {{ a.threshold }})
{% endfor %}

## Differential Diagnosis
{% for d in differential %}
{{ loop.index }}. {{ d }}
{% endfor %}

## Patient
- Age: {{ age }}, Sex: {{ sex }}, Race: {{ race }}
- Chief complaint: {{ chief_complaint }}
- Vitals: BP {{ vitals.bp }}, HR {{ vitals.hr }}, SpO2 {{ vitals.spo2 }}%, Temp {{ vitals.temp }}

Return ONLY a JSON array of strings. Example:
["Immediate decompression for tension pneumothorax", "Start broad-spectrum antibiotics", "Continuous cardiac monitoring"]
"""


# Fallback simple template when jinja is not available
ACTIONS_SIMPLE = """Given these findings {findings_summary}, lab alerts {lab_summary}, and differential {differential}, list 3-5 clinical actions in order of urgency.
Return ONLY a JSON array of strings.
"""


class VLLMTextClient:
    """OpenAI-compatible text client for Qwen3.5-35B-A3B on port 8001."""

    def __init__(self, base_url: str = None, model: str = "qwen3.5-35b-a3b"):
        self.base_url = base_url or settings.vllm_text_url
        self.model = model
        self._mock = MockVLLMTextClient()
        self._client: Optional[AsyncOpenAI] = None
        if not settings.use_mock:
            self._client = AsyncOpenAI(
                base_url=self.base_url,
                api_key="EMPTY",
                timeout=httpx.Timeout(60.0),
                max_retries=2,
            )

    def _build_actions_prompt(self, state: dict) -> str:
        """Build plain-text prompt from state."""
        findings = state.get("findings", [])
        alerts = state.get("lab_alerts", [])
        diff = state.get("differential", [])
        vitals = state.get("vitals", {})

        f_str = "; ".join(
            f"{f.get('finding')} ({int(f.get('confidence',0)*100)}%)" for f in findings
        ) or "none"
        l_str = "; ".join(
            f"{a.get('code')} ({a.get('lab')}={a.get('value')})" for a in alerts
        ) or "none"
        d_str = "; ".join(diff) or "undetermined"

        return (
            f"You are a clinical decision support system.\n"
            f"Findings: {f_str}\n"
            f"Lab alerts: {l_str}\n"
            f"Differential: {d_str}\n"
            f"Patient: {state.get('patient_age','?')}yo {state.get('patient_sex','?')}, "
            f"chief complaint: {state.get('chief_complaint','?')}\n"
            f"Vitals: BP {vitals.get('bp','?')}, HR {vitals.get('hr','?')}, "
            f"SpO2 {vitals.get('spo2','?')}%, Temp {vitals.get('temp','?')}\n\n"
            f"Suggest 3-5 specific clinical actions in order of urgency. "
            f"Return ONLY a JSON array of strings."
        )

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM and return raw text."""
        if self._client is None:
            raise RuntimeError("Real client not initialized (USE_MOCK=true)")

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinical decision support assistant. Respond with valid JSON only when requested."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=512,
        )
        return response.choices[0].message.content or ""

    def _parse_json_array(self, text: str) -> list:
        """Extract JSON array from LLM response."""
        text = text.strip()
        # Remove markdown fences
        if text.startswith("```"):
            lines = text.splitlines()
            while lines and (lines[0].startswith("```") or not lines[0].strip()):
                lines.pop(0)
            while lines and (lines[-1].startswith("```") or not lines[-1].strip()):
                lines.pop()
            text = "\n".join(lines)
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [str(item) for item in data]
        except json.JSONDecodeError:
            pass
        # Fallback: parse bullet points / numbered lines
        actions = []
        for line in text.splitlines():
            line = line.strip().lstrip("-*0123456789. ").strip()
            if line:
                actions.append(line)
        return actions[:5]

    async def generate_actions(self, state: dict) -> list:
        """Generate suggested clinical actions from case state."""
        if settings.use_mock:
            return await self._mock.generate_actions(state)

        prompt = self._build_actions_prompt(state)
        try:
            raw = await self._call_llm(prompt)
            return self._parse_json_array(raw)
        except Exception:
            traceback.print_exc()
            return await self._mock.generate_actions(state)

    async def generate_report(self, state: dict) -> dict:
        """Generate structured clinical report. Falls back to deterministic generation."""
        if settings.use_mock:
            return await self._mock.generate_report(state)

        # Very simple prompt — deterministic formatting is sufficient for report
        prompt = (
            f"Summarize this clinical case in one paragraph.\n"
            f"ESI Level: {state.get('esi_level','?')} — {state.get('esi_description','?')}\n"
            f"Findings: {'; '.join(f.get('finding','') for f in state.get('findings',[]))}\n"
            f"Differential: {'; '.join(state.get('differential',[]))}\n"
            f"Actions: {'; '.join(state.get('suggested_actions',[]))}\n"
            f"Return a short paragraph."
        )
        try:
            raw = await self._call_llm(prompt)
            return {
                "summary": raw.strip(),
                "esi": {
                    "level": state.get("esi_level"),
                    "description": state.get("esi_description"),
                    "rules": state.get("esi_rules_triggered", []),
                },
                "differential": state.get("differential", []),
                "actions": state.get("suggested_actions", []),
                "safety_summary": {
                    "flags": len(state.get("merged_flags", [])),
                    "downgrades": state.get("safety_downgrades", 0),
                },
            }
        except Exception:
            traceback.print_exc()
            return await self._mock.generate_report(state)

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
            f"Orders for {state.get('patient_age','?')}yo {state.get('patient_sex','?')} with {state.get('chief_complaint','?')}. "
            f"Vitals: BP {vitals.get('bp','?')}, HR {vitals.get('hr','?')}, RR {vitals.get('rr','?')}, SpO2 {vitals.get('spo2','?')}%. "
            f"Imaging: {f_str}. Labs: {l_str}.\n\n"
            f'Respond with exactly one JSON array like this example and nothing else:\n'
            f'["Needle decompression", "High-flow O2", "IV access", "Type and cross", "Chest tube"]'
        )

    async def _call_llm(self, prompt: str, guided_json: dict = None) -> str:
        """Call the LLM and return raw text."""
        if self._client is None:
            raise RuntimeError("Real client not initialized (USE_MOCK=true)")

        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 256,
        }
        if guided_json:
            kwargs["extra_body"] = {"guided_json": guided_json}
        response = await self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    def _strip_thinking(self, text: str) -> str:
        """Strip Qwen3.5 thinking process markers."""
        # Remove everything before the first actual answer marker
        markers = [
            "Final Answer:", "Answer:", "Output:", "Actions:",
            "Clinical Actions:", "Suggested Actions:", "Recommendations:",
        ]
        lower = text.lower()
        best_idx = len(text)
        for m in markers:
            idx = lower.find(m.lower())
            if idx != -1:
                best_idx = min(best_idx, idx + len(m))
        if best_idx < len(text):
            text = text[best_idx:]
        # Also strip common thinking headers
        for header in ["Thinking Process:", "Analyze the Request:", "Role:", "Input:", "Task:", "Output Format:", "Constraints:"]:
            text = text.replace(header, "")
        return text.strip()

    def _parse_json_array(self, text: str) -> list:
        """Extract JSON array from LLM response, handling Qwen3.5 thinking output."""
        text = self._strip_thinking(text)
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
        # Fallback: parse bullet points / numbered lines, skip thinking artifacts
        skip_prefixes = {
            "thinking", "process", "analyze", "request", "role", "input", "task",
            "output", "format", "constraints", "note", "important", "write", "list",
            "example", "respond", "orders for", "patient:", "vitals:", "imaging:",
            "labs:", "json array", "you are", "emergency medicine", "concise clinical",
            "never explain", "never repeat", "always respond", "only and nothing",
        }
        skip_phrases = {
            "json array", "nothing else", "example output", "respond with exactly",
            "emergency medicine", "clinical orders only", "never explain",
            "never repeat", "always respond",
        }
        actions = []
        for line in text.splitlines():
            line = line.strip().lstrip("-*0123456789. \"[]'").strip()
            if not line:
                continue
            lower = line.lower()
            if any(lower.startswith(p) for p in skip_prefixes):
                continue
            if any(p in lower for p in skip_phrases):
                continue
            if lower in {"json array of strings", "only", "return only"}:
                continue
            actions.append(line)
        return actions[:5]

    async def generate_actions(self, state: dict) -> list:
        """Generate suggested clinical actions from case state."""
        if settings.use_mock:
            return await self._mock.generate_actions(state)

        prompt = self._build_actions_prompt(state)
        # vLLM guided_json schema to force array-of-strings output
        guided_schema = {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 6,
        }
        try:
            raw = await self._call_llm(prompt, guided_json=guided_schema)
            data = json.loads(raw.strip())
            if isinstance(data, list):
                return [str(item) for item in data[:5]]
        except Exception:
            traceback.print_exc()
        return await self._mock.generate_actions(state)

    async def generate_report(self, state: dict) -> dict:
        """Generate structured clinical report. Deterministic — no LLM call needed."""
        if settings.use_mock:
            return await self._mock.generate_report(state)

        findings = state.get("findings", [])
        diff = state.get("differential", [])
        actions = state.get("suggested_actions", [])
        esi_level = state.get("esi_level", "?")
        esi_desc = state.get("esi_description", "")

        finding_str = "; ".join(f.get("finding", "") for f in findings) or "none"
        diff_str = "; ".join(diff) or "undetermined"
        action_str = "; ".join(actions) or "none"

        summary = (
            f"ESI {esi_level} — {esi_desc}. "
            f"Findings: {finding_str}. "
            f"Differential: {diff_str}. "
            f"Actions: {action_str}."
        )

        return {
            "summary": summary,
            "esi": {
                "level": esi_level,
                "description": esi_desc,
                "rules": state.get("esi_rules_triggered", []),
            },
            "differential": diff,
            "actions": actions,
            "safety_summary": {
                "flags": len(state.get("merged_flags", [])),
                "downgrades": state.get("safety_downgrades", 0),
            },
        }

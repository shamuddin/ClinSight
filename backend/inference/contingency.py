import json
from pathlib import Path
from typing import Dict, Any, Optional
from backend.core.config import settings

class ContingencyFallback:
    """
    Returns pre-cached model outputs when vLLM is unavailable.
    Enables demo survival if GPU crashes.
    Falls back further to deterministic safe output if cache is missing.
    """
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or settings.cache_dir
        self._cache: Dict[str, dict] = {}
        self._load_all()

    def _load_all(self):
        if not self.cache_dir.exists():
            return
        for p in self.cache_dir.glob("*_merged.json"):
            try:
                self._cache[p.stem] = json.loads(p.read_text())
            except (json.JSONDecodeError, OSError):
                continue

    def load_case(self, case_id: str) -> dict:
        """Return cached output for a case."""
        key = f"{case_id}_merged"
        if key in self._cache:
            return self._cache[key]
        # Ultimate fallback: deterministic safe output
        return self._emergency_fallback(case_id)

    def _emergency_fallback(self, case_id: str) -> dict:
        """Even if cache is missing, return safe output."""
        return {
            "esi_level": 3,
            "esi_description": "URGENT: System operating in fallback mode. Manual review required.",
            "findings": [],
            "differential": ["Unable to assess — system in contingency mode"],
            "suggested_actions": ["Immediate manual assessment required"],
            "flag": "CONTINGENCY_MODE_ACTIVE"
        }

    def warm(self, case_id: str, data: dict) -> None:
        """Pre-cache output for a case (called during benchmark/generate)."""
        self._cache[f"{case_id}_merged"] = data
        if self.cache_dir.exists():
            try:
                (self.cache_dir / f"{case_id}_merged.json").write_text(json.dumps(data, indent=2))
            except OSError:
                pass

    def is_available(self, case_id: str) -> bool:
        """Check if we have a contingency entry for this case."""
        return f"{case_id}_merged" in self._cache

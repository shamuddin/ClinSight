import json
import time
from pathlib import Path
from typing import Optional

CACHE_DIR = Path(__file__).parent.parent / "data" / "contingency_cache"

# Cache mapping: case_id -> pre-computed LLM outputs
_documenter_cache: dict = {}

def _load_cache(case_id: str) -> Optional[dict]:
    """Load pre-generated Documenter outputs for a demo case."""
    global _documenter_cache
    if case_id not in _documenter_cache:
        cache_file = CACHE_DIR / f"{case_id}.json"
        if cache_file.exists():
            _documenter_cache[case_id] = json.loads(cache_file.read_text())
        else:
            _documenter_cache[case_id] = None
    return _documenter_cache.get(case_id)


def get_cached_documenter_outputs(case_id: str) -> Optional[dict]:
    """Return pre-computed actions + report for demo cases. Falls back to None for new cases."""
    cache = _load_cache(case_id)
    if cache is None:
        return None
    return {
        "suggested_actions": cache.get("suggested_actions", []),
        "report": cache.get("report", {}),
        "esi_level": cache.get("esi_level"),
        "esi_description": cache.get("esi_description"),
        "differential": cache.get("differential", []),
        "safety_flags": cache.get("safety_flags", []),
    }

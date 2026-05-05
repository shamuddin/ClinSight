#!/usr/bin/env python3
"""Pre-compute contingency cache for demo cases."""
import json
from pathlib import Path

CACHE_DIR = Path("backend/data/contingency_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Stub: real implementation will call vLLM and store outputs
cases = [f"case_{i:03d}" for i in range(1, 7)]
for case in cases:
    (CACHE_DIR / f"{case}_vision.json").write_text(json.dumps({"cached": True}))
    (CACHE_DIR / f"{case}_text.json").write_text(json.dumps({"cached": True}))

print(f"Generated cache for {len(cases)} cases.")

#!/usr/bin/env python3
"""Pre-generate LLM cache for demo cases — real outputs, real accuracy."""
import asyncio, json, sys, time
from pathlib import Path

sys.path.insert(0, "/opt/clinsight")

from backend.api.demo import _load_cases, _populate_state, _make_state
from backend.agents.graph import run_pipeline
from backend.inference.vllm_text_client import VLLMTextClient

CACHE_DIR = Path("/opt/clinsight/backend/data/contingency_cache")
CACHE_DIR.mkdir(exist_ok=True)

async def generate_cache():
    cases = _load_cases()
    client = VLLMTextClient()
    
    for case in cases:
        cid = case["case_id"]
        print(f"Processing {cid}...", flush=True)
        
        state = _populate_state(_make_state(case), case)
        t0 = time.time()
        final = await run_pipeline(state)
        elapsed = round((time.time() - t0) * 1000, 2)
        
        # Extract real LLM outputs
        cache_entry = {
            "case_id": cid,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_time_ms": elapsed,
            "esi_level": final.get("esi_level"),
            "esi_description": final.get("esi_description"),
            "findings": final.get("findings", []),
            "lab_alerts": final.get("lab_alerts", []),
            "differential": final.get("differential", []),
            "suggested_actions": final.get("suggested_actions", []),
            "report": final.get("report", {}),
            "safety_flags": final.get("merged_flags", []),
            "contradictions": final.get("contradictions", []),
            "hallucination_flags": final.get("hallucination_flags", []),
            "bias_flags": final.get("bias_flags", []),
            "quality_gate": final.get("quality_gate", {}),
            "pediatric_gate": final.get("pediatric_gate", {}),
            "audit_log": final.get("audit_log", []),
        }
        
        out_path = CACHE_DIR / f"{cid}.json"
        out_path.write_text(json.dumps(cache_entry, indent=2))
        print(f"  Cached: {out_path} ({elapsed}ms)", flush=True)
        
        # Also cache individual agent outputs
        for entry in final.get("audit_log", []):
            print(f"    Agent: {entry['agent']} — {entry.get('action','')}", flush=True)
    
    print(f"\nAll {len(cases)} cases cached in {CACHE_DIR}")

if __name__ == "__main__":
    asyncio.run(generate_cache())

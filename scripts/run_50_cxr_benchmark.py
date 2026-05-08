#!/usr/bin/env python3
"""Run 50-case live benchmark on AMD MI300X for ClinSight CXR cases."""
import json, urllib.request, time, os, sys
from datetime import datetime
from pathlib import Path

# Load all 50 case IDs from demo_cases.json
DEMO_CASES_PATH = "/opt/clinsight/backend/data/demo_cases.json"
RESULTS_DIR = "/opt/clinsight/benchmarks/gpu_results/batch_50_cxr_live"

with open(DEMO_CASES_PATH) as f:
    cases_data = json.load(f)
CASES = [c["case_id"] for c in cases_data]

RESULTS = []

# Detect if running inside docker container
if os.path.exists("/.dockerenv"):
    BASE_URL = "http://172.17.0.1:3000"
else:
    BASE_URL = "http://localhost:3000"

os.makedirs(RESULTS_DIR, exist_ok=True)

print("=== CLINSIGHT 50-CXR LIVE BENCHMARK ===")
print("Start:", datetime.now().isoformat())
print("Cases:", len(CASES))
print("Base URL:", BASE_URL)
print()

for case_id in CASES:
    start = time.time()
    try:
        url = BASE_URL + "/demo/analyze/" + case_id
        resp = urllib.request.urlopen(url, timeout=300)
        data = json.load(resp)
        elapsed = time.time() - start
        
        result = {
            "case_id": case_id,
            "elapsed_sec": round(elapsed, 2),
            "total_time_ms": data.get("total_time_ms", 0),
            "esi_level": data.get("esi_level", -1),
            "findings_count": len(data.get("findings", [])),
            "safety_flags": len(data.get("safety_flags", [])),
            "cached": data.get("cached", True),
            "status": "success"
        }
        RESULTS.append(result)
        
        # Save individual result
        with open(f"{RESULTS_DIR}/{case_id}_result.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print("[%s] %.1fs | ESI=%d | findings=%d | flags=%d | cached=%s" % (
            case_id, elapsed, data.get("esi_level", -1), 
            len(data.get("findings", [])), len(data.get("safety_flags", [])),
            data.get("cached", True)
        ))
    except Exception as e:
        elapsed = time.time() - start
        RESULTS.append({
            "case_id": case_id,
            "elapsed_sec": round(elapsed, 2),
            "status": "error: " + str(e)[:100]
        })
        print("[%s] ERROR: %s" % (case_id, e))

print()
print("=== SUMMARY ===")
success_times = [r["elapsed_sec"] for r in RESULTS if r["status"] == "success"]
success_results = [r for r in RESULTS if r["status"] == "success"]
if success_times:
    print("Cases: %d/%d successful" % (len(success_times), len(CASES)))
    print("Mean latency: %.2fs" % (sum(success_times)/len(success_times)))
    print("Min: %.2fs | Max: %.2fs" % (min(success_times), max(success_times)))
    print("Total wall time: %.1fs" % sum(success_times))
else:
    print("No successful runs.")

# Save summary JSON
summary = {
    "timestamp": datetime.now().isoformat(),
    "mode": "Real AMD MI300X Inference",
    "gpu": "AMD Instinct MI300X",
    "vram": "192 GB HBM3",
    "rocm": "7.0",
    "vision_model": "Qwen2.5-VL-7B-Instruct",
    "text_model": "Qwen3.5-35B-A3B (MoE)",
    "framework": "LangGraph · vLLM · ROCm",
    "cases_tested": len(CASES),
    "successful": len(success_times),
    "mean_latency_sec": round(sum(success_times)/len(success_times), 2) if success_times else None,
    "min_latency_sec": round(min(success_times), 2) if success_times else None,
    "max_latency_sec": round(max(success_times), 2) if success_times else None,
    "results": success_results
}

with open(f"{RESULTS_DIR}/benchmark_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nSaved summary:", f"{RESULTS_DIR}/benchmark_summary.json")
print("Done:", datetime.now().isoformat())

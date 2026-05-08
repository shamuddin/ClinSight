#!/usr/bin/env python3
"""Real benchmark on AMD MI300X for ClinSight."""
import json, urllib.request, time, csv, statistics
from datetime import datetime

CASES = ["CS-2024-001", "CS-2024-002", "CS-2024-003", "CS-2024-004", "CS-2024-005", "CS-2024-006"]
RESULTS = []

print("=== CLINSIGHT REAL BENCHMARK ===")
print("Start:", datetime.now().isoformat())
print("Cases:", CASES)
print()

for case_id in CASES:
    start = time.time()
    try:
        # When running inside docker container, use host gateway IP
    import os
    if os.path.exists("/.dockerenv"):
        base_url = "http://172.17.0.1:3000"
    else:
        base_url = "http://localhost:3000"
    url = base_url + "/demo/analyze/" + case_id
        resp = urllib.request.urlopen(url, timeout=300)
        data = json.load(resp)
        elapsed = time.time() - start
        RESULTS.append({
            "case_id": case_id,
            "elapsed_sec": round(elapsed, 2),
            "total_time_ms": data.get("total_time_ms", 0),
            "esi_level": data.get("esi_level", -1),
            "findings_count": len(data.get("findings", [])),
            "safety_flags": len(data.get("safety_flags", [])),
            "cached": data.get("cached", True),
            "status": "success"
        })
        print("[%s] %.1fs | ESI=%d | findings=%d" % (case_id, elapsed, data.get("esi_level", -1), len(data.get("findings", []))))
    except Exception as e:
        elapsed = time.time() - start
        RESULTS.append({
            "case_id": case_id,
            "elapsed_sec": round(elapsed, 2),
            "status": "error: " + str(e)[:50]
        })
        print("[%s] ERROR: %s" % (case_id, e))

print()
print("=== SUMMARY ===")
success_times = [r["elapsed_sec"] for r in RESULTS if r["status"] == "success"]
if success_times:
    print("Cases: %d/%d successful" % (len(success_times), len(CASES)))
    print("Mean latency: %.1fs" % statistics.mean(success_times))
    print("Min: %.1fs | Max: %.1fs" % (min(success_times), max(success_times)))
    print("Total wall time: %.1fs" % sum(success_times))
else:
    print("No successful runs.")

# Save CSV
with open("/mnt/scratch/clinsight-clean/benchmarks/real_benchmark.csv", "w", newline="") as f:
    fieldnames = ["case_id", "elapsed_sec", "total_time_ms", "esi_level", "findings_count", "safety_flags", "cached", "status"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(RESULTS)

# Save JSON
summary = {
    "timestamp": datetime.now().isoformat(),
    "mode": "real_amd_mi300x",
    "gpu": "AMD Instinct MI300X",
    "rocm": "7.0",
    "vision_model": "Qwen2.5-VL-7B-Instruct",
    "text_model": "Qwen3.5-35B-A3B",
    "cases_tested": len(CASES),
    "successful": len(success_times),
    "mean_latency_sec": round(statistics.mean(success_times), 2) if success_times else None,
    "min_latency_sec": round(min(success_times), 2) if success_times else None,
    "max_latency_sec": round(max(success_times), 2) if success_times else None,
    "results": RESULTS
}
with open("/mnt/scratch/clinsight-clean/benchmarks/real_benchmark.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nSaved: real_benchmark.csv + real_benchmark.json")

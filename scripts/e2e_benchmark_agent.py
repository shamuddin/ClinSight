#!/usr/bin/env python3
"""ClinSight E2E Benchmark Agent
Runs all demo cases, captures latency + GPU util, generates judge-ready report.
Usage: python scripts/e2e_benchmark_agent.py [API_BASE]
"""
import requests, time, json, sys, os, subprocess
from statistics import mean, stdev
from pathlib import Path
from datetime import datetime

API_BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("API_URL", "http://129.212.176.125:3000")
BENCH_DIR = Path(__file__).resolve().parent.parent / "benchmarks"
CASES = [f"CS-2024-{i:03d}" for i in range(1, 11)]  # 001-010

def get_cases():
    try:
        r = requests.get(f"{API_BASE}/demo/cases", timeout=10)
        data = r.json()
        return [c["case_id"] for c in data]
    except:
        return []

def benchmark_case(case_id: str) -> dict:
    url = f"{API_BASE}/demo/analyze/{case_id}"
    start = time.time()
    try:
        r = requests.get(url, timeout=180)
        elapsed = time.time() - start
        data = r.json()
        return {
            "case_id": case_id,
            "latency_sec": round(elapsed, 2),
            "status_code": r.status_code,
            "esi_level": data.get("esi_level"),
            "findings_count": len(data.get("findings", [])),
            "cached": bool(data.get("cached")),
            "error": data.get("error"),
        }
    except Exception as e:
        return {"case_id": case_id, "latency_sec": -1, "error": str(e)}

def capture_rocm_smi():
    try:
        # If running locally with rocm-smi
        result = subprocess.run(["rocm-smi", "--showmeminfo", "VRAM", "--csv"],
                              capture_output=True, text=True, timeout=5)
        return result.stdout[:500]
    except:
        return ""

print("═" * 60)
print("E2E BENCHMARK AGENT")
print("═" * 60)
print(f"Target: {API_BASE}")
print(f"Cases:  {CASES}")
print(f"Time:   {datetime.utcnow().isoformat()}Z\n")

# Discover available cases
available = get_cases()
print(f"Available cases on server: {available}")
to_run = [c for c in CASES if c in available] or available

results = []
for cid in to_run:
    print(f"[Benchmarking {cid}]...", end=" ", flush=True)
    res = benchmark_case(cid)
    results.append(res)
    if res.get("error"):
        print(f"ERROR: {res['error'][:60]}")
    else:
        print(f"{res['latency_sec']:.1f}s | ESI {res.get('esi_level','?')} | {res['findings_count']} findings")
    time.sleep(1)

# Compute stats
latencies = [r["latency_sec"] for r in results if r["latency_sec"] > 0]
if latencies:
    stats = {
        "count": len(latencies),
        "mean_sec": round(mean(latencies), 2),
        "min_sec": round(min(latencies), 2),
        "max_sec": round(max(latencies), 2),
        "stdev_sec": round(stdev(latencies), 2) if len(latencies) > 1 else 0,
    }
    print("\n── STATISTICS ──")
    for k,v in stats.items(): print(f"  {k}: {v}")
else:
    stats = {"count": 0, "error": "No successful runs"}

# Save report
report = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "target": API_BASE,
    "stats": stats,
    "runs": results,
    "rocm_smi": capture_rocm_smi(),
}
report_path = BENCH_DIR / f"benchmark_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
report_path.write_text(json.dumps(report, indent=2))
print(f"\nReport saved: {report_path}")

# Also save CSV for histogram
if latencies:
    csv_path = BENCH_DIR / f"latency_real_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_path.write_text("case_id,latency_sec\n" + "\n".join(f"{r['case_id']},{r['latency_sec']}" for r in results if r["latency_sec"] > 0))
    print(f"CSV saved:   {csv_path}")

print("═" * 60)

#!/usr/bin/env python3
"""ClinSight Live Inference Guard
Ensures judge demo runs REAL LLM inference, never cached/mocked.
Usage: python scripts/live_inference_guard.py [API_BASE]
"""
import requests, sys, time, json, os
from statistics import mean

API_BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("API_URL", "http://129.212.176.125:3000")
CASE_ID = "CS-2024-001"
RUNS = 3
MIN_SECONDS = 10.0   # Real 35B inference should take >10s
MAX_SECONDS = 120.0  # But not forever

def analyze():
    url = f"{API_BASE}/demo/analyze/{CASE_ID}"
    print(f"  POST {url}")
    start = time.time()
    try:
        r = requests.get(url, timeout=180)
        elapsed = time.time() - start
        data = r.json()
        return elapsed, data
    except Exception as e:
        print(f"  ✗ Request failed: {e}")
        return None, None

print("═" * 60)
print("LIVE INFERENCE GUARD")
print("═" * 60)
print(f"Target: {API_BASE}")
print(f"Case:   {CASE_ID}")
print(f"Runs:   {RUNS}\n")

times = []
findings_hashes = []

for i in range(RUNS):
    print(f"[Run {i+1}/{RUNS}]")
    elapsed, data = analyze()
    if elapsed is None:
        print("  ✗ ABORT — backend unreachable")
        sys.exit(1)
    
    times.append(elapsed)
    findings = json.dumps(data.get("findings", []), sort_keys=True)
    findings_hashes.append(hash(findings))
    
    # Check timing
    if elapsed < MIN_SECONDS:
        print(f"  🔴 TOO FAST: {elapsed:.1f}s — likely CACHED or MOCK")
        print(f"     Expected: >{MIN_SECONDS}s for real 35B inference")
    elif elapsed > MAX_SECONDS:
        print(f"  🟡 SLOW: {elapsed:.1f}s — may be overloaded")
    else:
        print(f"  ✅ TIMING OK: {elapsed:.1f}s")
    
    # Check badge/label
    report = data.get("report", {})
    if "cache" in str(report).lower() or data.get("cached"):
        print(f"  🔴 CACHE FLAG DETECTED in response")
    
    # Check for real-looking content
    diff = data.get("differential", [])
    actions = data.get("suggested_actions", [])
    if len(diff) < 2 or len(actions) < 2:
        print(f"  🟡 Sparse output — possible fallback/mocked data")
    else:
        print(f"  ✅ Content: {len(diff)} differentials, {len(actions)} actions")
    
    time.sleep(2)

print("\n── SUMMARY ──")
avg_time = mean(times)
unique_hashes = len(set(findings_hashes))
print(f"Mean latency:   {avg_time:.1f}s")
print(f"Variation:      {unique_hashes} unique outputs out of {RUNS} runs")

verdict = "✅ LIVE INFERENCE CONFIRMED"
if avg_time < MIN_SECONDS:
    verdict = "🔴 CACHED/MOCK DETECTED"
elif unique_hashes == 1 and RUNS > 1:
    verdict = "🟡 DETERMINISTIC OUTPUT — possible cache or temperature=0"

print(f"VERDICT: {verdict}")
print("═" * 60)

if "🔴" in verdict:
    sys.exit(1)

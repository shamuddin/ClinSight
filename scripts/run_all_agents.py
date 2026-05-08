#!/usr/bin/env python3
"""ClinSight Master Agent Runner
Executes all 8 acceleration agents in priority order.
Usage: python scripts/run_all_agents.py [DROPLET_IP]
"""
import subprocess, sys, os
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
BASE = SCRIPTS.parent

AGENTS = [
    ("Judge Readiness Verify",   "judge_readiness_verify.py",  []),
    ("Clinical Advisory Gen",    "clinical_advisory_gen.py", []),
    ("Pitch Deck Assembler",     "pitch_deck_assembler.py",  []),
    ("Type Safety Bridge",       "type_safety_bridge.py",    []),
    ("Safety Parallelizer",      "safety_parallelizer.py",   []),
    ("Sync & Deploy",            "sync_deploy_agent.py",     sys.argv[1:] if len(sys.argv) > 1 else []),
    ("Live Inference Guard",     "live_inference_guard.py",  sys.argv[1:] if len(sys.argv) > 1 else []),
    ("E2E Benchmark",            "e2e_benchmark_agent.py",   sys.argv[1:] if len(sys.argv) > 1 else []),
]

print("=" * 70)
print("CLINSIGHT MASTER AGENT RUNNER")
print("=" * 70)

for name, script, args in AGENTS:
    path = SCRIPTS / script
    if not path.exists():
        print(f"\n[SKIP] {name}: {script} not found")
        continue
    print(f"\n{'─' * 70}")
    print(f"[RUN] {name}")
    print(f"{'─' * 70}")
    cmd = ["python3", str(path)] + args
    result = subprocess.run(cmd, cwd=str(BASE))
    if result.returncode != 0:
        print(f"  ⚠ {name} exited with code {result.returncode}")

print("\n" + "=" * 70)
print("ALL AGENTS COMPLETE")
print("=" * 70)

#!/usr/bin/env python3
"""
ClinSight Development Status Reporter
=====================================

One command to see current project state vs DEVELOPMENT_PLAN targets.

Usage:
    cd /mnt/k/Hackthon/ClinSight
    python3 scripts/check_status.py
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path("/mnt/k/Hackthon/ClinSight")


class C:
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    INFO = "\033[94m"
    END = "\033[0m"


def check_file_exists(path: str, min_bytes: int = 10) -> Tuple[bool, str]:
    """Check if a file exists and has content."""
    p = REPO_ROOT / path
    if not p.exists():
        return False, f"{path} missing"
    if p.stat().st_size < min_bytes:
        return False, f"{path} empty/too small ({p.stat().st_size}b)"
    return True, f"{path} OK ({p.stat().st_size}b)"


def check_dir_exists(path: str) -> Tuple[bool, str]:
    p = REPO_ROOT / path
    if not p.exists():
        return False, f"{path} missing"
    files = list(p.iterdir())
    return True, f"{path} exists ({len(files)} items)"


def run_pytest() -> Tuple[bool, str]:
    try:
        r = subprocess.run(
            ["python3", "-m", "pytest", "-q", "--tb=short"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode == 0:
            passed = r.stdout.count("passed")
            return True, f"{passed} tests passed"
        return False, f"pytest failed (exit {r.returncode})\n{r.stdout[-300:]}"
    except Exception as e:
        return False, f"pytest exception: {e}"


def check_git() -> Tuple[bool, str]:
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = r.stdout.strip().splitlines()
        return True, f"HEAD: {lines[0] if lines else 'unknown'}"
    except Exception as e:
        return False, f"git check failed: {e}"


def main():
    print(f"{C.INFO}╔══════════════════════════════════════════════════════════════╗{C.END}")
    print(f"{C.INFO}║         ClinSight Development Status Report                  ║{C.END}")
    print(f"{C.INFO}╚══════════════════════════════════════════════════════════════╝{C.END}")

    sections = []

    # ── Phase 0: Foundation ──
    print(f"\n{C.INFO}Phase 0: Foundation & Tooling{C.END}")
    p0 = [
        check_file_exists("requirements.txt"),
        check_file_exists("requirements-dev.txt"),
        check_file_exists(".pre-commit-config.yaml"),
        check_file_exists("pytest.ini"),
        check_file_exists("backend/core/state.py"),
        check_file_exists("backend/api/main.py"),
    ]
    for ok, msg in p0:
        color = C.OK if ok else C.FAIL
        print(f"  {color}[{'PASS' if ok else 'FAIL'}]{C.END} {msg}")
    p0_ok = sum(1 for ok, _ in p0 if ok)
    print(f"  {C.INFO}Phase 0 Score: {p0_ok}/{len(p0)}{C.END}")
    sections.append(("Phase 0", p0_ok, len(p0)))

    # ── Phase 1: Core Agents ──
    print(f"\n{C.INFO}Phase 1: Core Agents & State{C.END}")
    p1 = [
        check_file_exists("backend/agents/coordinator.py", min_bytes=100),
        check_file_exists("backend/agents/radiologist.py", min_bytes=100),
        check_file_exists("backend/agents/lab_analyst.py", min_bytes=100),
        check_file_exists("backend/agents/safety.py", min_bytes=100),
        check_file_exists("backend/agents/clinical_documenter.py", min_bytes=100),
        check_file_exists("backend/agents/graph.py", min_bytes=100),
        check_file_exists("backend/agents/subgraphs.py", min_bytes=100),
        check_file_exists("backend/safety/rules.py", min_bytes=500),
        check_file_exists("backend/safety/image_quality.py", min_bytes=500),
        check_file_exists("backend/inference/mock_client.py", min_bytes=500),
        check_file_exists("backend/inference/vllm_vision_client.py", min_bytes=500),
        check_file_exists("backend/inference/vllm_text_client.py", min_bytes=500),
    ]
    for ok, msg in p1:
        color = C.OK if ok else C.FAIL
        print(f"  {color}[{'PASS' if ok else 'FAIL'}]{C.END} {msg}")
    p1_ok = sum(1 for ok, _ in p1 if ok)
    print(f"  {C.INFO}Phase 1 Score: {p1_ok}/{len(p1)}{C.END}")
    sections.append(("Phase 1", p1_ok, len(p1)))

    # ── Phase 2: Frontend ──
    print(f"\n{C.INFO}Phase 2: Frontend Shell{C.END}")
    p2 = [
        check_file_exists("frontend/react-app/src/App.tsx"),
        check_file_exists("frontend/react-app/src/components/Dashboard.tsx"),
        check_file_exists("frontend/react-app/src/components/ImageViewer.tsx"),
        check_file_exists("frontend/react-app/src/components/AgentActivity.tsx"),
        check_file_exists("frontend/react-app/src/components/SafetyPanel.tsx"),
        check_file_exists("frontend/react-app/src/components/PhysicianVeto.tsx"),
        check_file_exists("frontend/react-app/src/components/WhatIfComparison.tsx"),
    ]
    for ok, msg in p2:
        color = C.OK if ok else C.FAIL
        print(f"  {color}[{'PASS' if ok else 'FAIL'}]{C.END} {msg}")
    p2_ok = sum(1 for ok, _ in p2 if ok)
    print(f"  {C.INFO}Phase 2 Score: {p2_ok}/{len(p2)}{C.END}")
    sections.append(("Phase 2", p2_ok, len(p2)))

    # ── Phase 3: GPU / Models ──
    print(f"\n{C.INFO}Phase 3: GPU Droplet & Real Inference{C.END}")
    p3_checks = [
        check_file_exists("scripts/setup_amd_gpu.sh"),
        check_file_exists("scripts/start_vllm_vision.sh"),
        check_file_exists("scripts/start_vllm_text.sh"),
        check_file_exists("scripts/master_recovery.py", min_bytes=1000),
        check_file_exists("scripts/droplet_recovery.sh", min_bytes=1000),
        check_dir_exists("backend/data/contingency_cache"),
        check_file_exists("backend/data/demo_cases.json"),
    ]
    for ok, msg in p3_checks:
        color = C.OK if ok else C.FAIL
        print(f"  {color}[{'PASS' if ok else 'FAIL'}]{C.END} {msg}")
    p3_ok = sum(1 for ok, _ in p3_checks if ok)
    print(f"  {C.INFO}Phase 3 Score: {p3_ok}/{len(p3_checks)}{C.END}")
    sections.append(("Phase 3", p3_ok, len(p3_checks)))

    # ── Tests ──
    print(f"\n{C.INFO}Tests{C.END}")
    t_ok, t_msg = run_pytest()
    color = C.OK if t_ok else C.WARN
    print(f"  {color}[{'PASS' if t_ok else 'WARN'}]{C.END} {t_msg}")

    # ── Git ──
    print(f"\n{C.INFO}Git{C.END}")
    g_ok, g_msg = check_git()
    color = C.OK if g_ok else C.WARN
    print(f"  {color}[{'OK' if g_ok else 'WARN'}]{C.END} {g_msg}")

    # ── Summary ──
    total_done = sum(d for _, d, _ in sections)
    total_all = sum(t for _, _, t in sections)
    pct = (total_done / total_all * 100) if total_all > 0 else 0

    print(f"\n{'='*60}")
    print(f"  OVERALL: {total_done}/{total_all} checks passing ({pct:.0f}%)")
    for name, done, total in sections:
        bar = "█" * int(20 * done / total)
        print(f"  {name:12} |{bar:<20}| {done}/{total}")
    print(f"{'='*60}")

    # Phase mapping from DEVELOPMENT_PLAN
    print(f"\n{C.INFO}DEVELOPMENT_PLAN Phase Mapping:{C.END}")
    print("  Phase 0 (Foundation)      → scaffolding, deps, tooling")
    print("  Phase 1 (Core Agents)     → 5 parent + 7 subagents, state schema")
    print("  Phase 2 (Data/Frontend)   → 6 cases, mock cache, React shell")
    print("  Phase 3 (GPU/Models)      → MI300X droplet, vLLM, real inference")
    print("  Phase 4 (Safety Stress)   → contradiction, hallucination, bias tests")
    print("  Phase 5 (Benchmarks)      → latency, throughput, GPU evidence")
    print("  Phase 6 (E2E Integration) → kill switch, contingency fallback")
    print("  Phase 7 (Frontend Polish) → styling, animations, demo video")
    print("  Phase 8 (HF Space/Pitch)  → Space app, pitch deck, slides")


if __name__ == "__main__":
    main()

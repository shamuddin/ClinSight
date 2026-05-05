#!/usr/bin/env python3
"""Benchmark runner for ClinSight inference performance.

Measures end-to-end latency, per-agent timing, throughput, and token rates
for both mock and real vLLM backends.

Usage:
    # Mock mode (default — no GPU needed)
    python scripts/run_benchmark.py --mode mock --cases 6 --iterations 10

    # Real vLLM mode (requires servers running on GPU droplet)
    python scripts/run_benchmark.py --mode real \
        --vision-url http://gpu-host:8000/v1 \
        --text-url http://gpu-host:8001/v1 \
        --cases 6 --iterations 5

Output:
    benchmarks/benchmark_report_YYYYMMDD_HHMMSS.json
"""

import argparse
import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Any

# Ensure repo root in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.agents.graph import run_pipeline
from backend.core.state import AgentState
from backend.inference.vllm_vision_client import VLLMVisionClient
from backend.inference.vllm_text_client import VLLMTextClient
from backend.core.config import settings


# ── Ground-truth expectations for 6 demo cases ──
# Used for accuracy scoring when running in real mode.
GROUND_TRUTH: dict[str, dict[str, Any]] = {
    "CS-2024-001": {
        "esi": 1,
        "expected_findings": {"tension_pneumothorax", "mediastinal_shift"},
        "expected_actions": {"needle decompression", "chest tube"},
    },
    "CS-2024-002": {
        "esi": 2,
        "expected_findings": {"pneumonia", "pleural_effusion"},
        "expected_actions": {"antibiotics"},
    },
    "CS-2024-003": {
        "esi": 1,
        "expected_findings": {"pulmonary_edema", "cardiomegaly"},
        "expected_actions": {"diuretic", "vasodilator"},
    },
    "CS-2024-004": {
        "esi": 3,
        "expected_findings": {"pneumothorax", "rib_fracture"},
        "expected_actions": {"chest tube"},
    },
    "CS-2024-005": {
        "esi": 5,
        "expected_findings": {"normal"},
        "expected_actions": set(),
    },
    "CS-2024-006": {
        "esi": 1,
        "expected_findings": {"sepsis_pattern", "pleural_effusion"},
        "expected_actions": {"sepsis bundle", "cultures", "antibiotics"},
    },
}


# ── Case loader ──
def load_demo_cases() -> list[AgentState]:
    case_file = Path("backend/data/demo_cases.json")
    raw = json.loads(case_file.read_text())
    cases = []
    for item in raw:
        state: AgentState = {
            "case_id": item["case_id"],
            "image_path": str(Path("backend") / item["image_path"]),
            "image_hash": "",
            "lab_values": item.get("lab_values", {}),
            "lab_units": item.get("lab_units", {}),
            "triage_note": item.get("triage_note", ""),
            "patient_age": item.get("patient_age"),
            "patient_sex": item.get("patient_sex"),
            "patient_race": item.get("patient_race"),
            "chief_complaint": item.get("chief_complaint", ""),
            "vitals": item.get("vitals", {}),
            "quality_gate": {},
            "pediatric_gate": {},
            "input_warnings": [],
            "image_features": {},
            "findings": [],
            "attention_regions": [],
            "lab_alerts": [],
            "lab_patterns": [],
            "lab_correlation": {},
            "contradictions": [],
            "hallucination_flags": [],
            "bias_flags": [],
            "safety_downgrades": 0,
            "merged_flags": [],
            "esi_level": 5,
            "esi_description": "",
            "esi_rules_triggered": [],
            "differential": [],
            "suggested_actions": [],
            "report": {},
            "audit_log": [],
            "total_time_ms": 0.0,
        }
        cases.append(state)
    return cases


# ── Accuracy metrics ──
def score_accuracy(case_id: str, result: AgentState) -> dict[str, float]:
    gt = GROUND_TRUTH.get(case_id, {})
    if not gt:
        return {"esi_accuracy": 0.0, "finding_recall": 0.0, "action_recall": 0.0}

    # ESI accuracy
    esi_acc = 1.0 if result.get("esi_level") == gt["esi"] else 0.0

    # Finding recall
    found = {f.get("finding", "").lower() for f in result.get("findings", [])}
    expected = {e.lower() for e in gt.get("expected_findings", set())}
    if expected:
        finding_rec = len(found & expected) / len(expected)
    else:
        finding_rec = 1.0 if not found else 0.0

    # Action recall (substring match)
    actions = " ".join(result.get("suggested_actions", [])).lower()
    expected_act = gt.get("expected_actions", set())
    if expected_act:
        act_rec = sum(1 for a in expected_act if a.lower() in actions) / len(expected_act)
    else:
        act_rec = 1.0

    return {
        "esi_accuracy": esi_acc,
        "finding_recall": finding_rec,
        "action_recall": act_rec,
    }


# ── Single run ──
async def run_single(state: AgentState, mode: str) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        result = await run_pipeline(state)
    except Exception as exc:
        return {
            "case_id": state["case_id"],
            "status": "error",
            "error": str(exc),
            "latency_sec": round(time.perf_counter() - t0, 3),
        }
    latency = time.perf_counter() - t0

    entry = {
        "case_id": state["case_id"],
        "status": "success",
        "latency_sec": round(latency, 3),
        "esi_level": result.get("esi_level"),
        "findings_count": len(result.get("findings", [])),
        "alerts_count": len(result.get("lab_alerts", [])),
        "actions_count": len(result.get("suggested_actions", [])),
        "safety_flags": len(result.get("merged_flags", [])),
        "accuracy": score_accuracy(state["case_id"], result),
    }
    return entry


# ── Benchmark orchestrator ──
async def benchmark(mode: str, cases: int, iterations: int) -> dict[str, Any]:
    all_cases = load_demo_cases()
    selected = all_cases[:cases]

    results: list[dict] = []
    for i in range(iterations):
        print(f"\n=== Iteration {i+1}/{iterations} ===")
        for state in selected:
            entry = await run_single(state, mode)
            results.append(entry)
            tag = "✓" if entry["status"] == "success" else "✗"
            print(
                f"  {tag} {entry['case_id']:12} "
                f"{entry['latency_sec']:6.2f}s  "
                f"ESI:{entry.get('esi_level','?')}  "
                f"Findings:{entry['findings_count']}  "
                f"Actions:{entry['actions_count']}"
            )
            if mode == "real" and entry.get("accuracy"):
                acc = entry["accuracy"]
                print(
                    f"       Acc → ESI:{acc['esi_accuracy']:.0f}  "
                    f"Find:{acc['finding_recall']:.2f}  "
                    f"Act:{acc['action_recall']:.2f}"
                )

    # Aggregates
    latencies = [r["latency_sec"] for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] == "error"]
    summary = {
        "mode": mode,
        "total_cases": len(results),
        "success_rate": round(len(latencies) / len(results), 3) if results else 0,
        "mean_latency_sec": round(sum(latencies) / len(latencies), 3) if latencies else None,
        "min_latency_sec": round(min(latencies), 3) if latencies else None,
        "max_latency_sec": round(max(latencies), 3) if latencies else None,
        "errors": len(errors),
        "error_details": [{"case_id": e["case_id"], "error": e["error"]} for e in errors],
    }

    if mode == "real":
        accs = [r["accuracy"] for r in results if "accuracy" in r]
        if accs:
            summary["mean_esi_accuracy"] = round(sum(a["esi_accuracy"] for a in accs) / len(accs), 3)
            summary["mean_finding_recall"] = round(sum(a["finding_recall"] for a in accs) / len(accs), 3)
            summary["mean_action_recall"] = round(sum(a["action_recall"] for a in accs) / len(accs), 3)

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": summary,
        "results": results,
    }
    return report


# ── CLI ──
def main() -> int:
    parser = argparse.ArgumentParser(description="ClinSight Benchmark Runner")
    parser.add_argument("--mode", choices=["mock", "real"], default="mock", help="Backend mode")
    parser.add_argument("--cases", type=int, default=6, help="Number of demo cases to run")
    parser.add_argument("--iterations", type=int, default=10, help="Iterations per case")
    parser.add_argument("--vision-url", default="http://localhost:8000/v1", help="vLLM vision endpoint")
    parser.add_argument("--text-url", default="http://localhost:8001/v1", help="vLLM text endpoint")
    parser.add_argument("--output-dir", default="benchmarks", help="Where to write report")
    args = parser.parse_args()

    if args.mode == "real":
        settings.use_mock = False
        settings.vllm_vision_url = args.vision_url
        settings.vllm_text_url = args.text_url
        print(f"Real mode: vision={args.vision_url}  text={args.text_url}")
    else:
        print("Mock mode (no GPU required)")

    report = asyncio.run(benchmark(args.mode, args.cases, args.iterations))

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"benchmark_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved: {out_file}")

    # Print summary table
    s = report["summary"]
    print("\n=== Summary ===")
    print(f"  Mode:            {s['mode']}")
    print(f"  Cases:           {s['total_cases']}")
    print(f"  Success rate:    {s['success_rate']:.1%}")
    if s['mean_latency_sec'] is not None:
        print(f"  Mean latency:    {s['mean_latency_sec']}s")
        print(f"  Min / Max:       {s['min_latency_sec']}s / {s['max_latency_sec']}s")
    if "mean_esi_accuracy" in s:
        print(f"  ESI accuracy:    {s['mean_esi_accuracy']:.1%}")
        print(f"  Finding recall:  {s['mean_finding_recall']:.2f}")
        print(f"  Action recall:   {s['mean_action_recall']:.2f}")
    if s['errors']:
        print(f"  Errors:          {s['errors']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""GPU health check and warm-up utility for AMD ROCm + vLLM.

Usage:
    python scripts/gpu_health_check.py [http://localhost:8000/v1]

Checks:
    1. ROCm GPU visibility (torch.cuda / rocm)
    2. vLLM server health (GET /health)
    3. Simple warm-up inference call
    4. Memory utilization
"""

import sys
import time
import json
import subprocess
from pathlib import Path

import httpx


def check_rocm_gpu() -> dict:
    """Check AMD GPU via torch."""
    try:
        import torch
        if not torch.cuda.is_available():
            return {"ok": False, "error": "torch.cuda not available", "devices": 0}
        count = torch.cuda.device_count()
        props = []
        for i in range(count):
            name = torch.cuda.get_device_name(i)
            mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            props.append({"id": i, "name": name, "total_memory_gb": round(mem, 1)})
        return {"ok": True, "devices": count, "details": props}
    except ImportError:
        return {"ok": False, "error": "torch not installed", "devices": 0}


def check_vllm_health(url: str) -> dict:
    """Ping vLLM /health endpoint."""
    try:
        r = httpx.get(f"{url}/health", timeout=10.0)
        return {"ok": r.status_code == 200, "status_code": r.status_code}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def warmup_call(url: str, model: str = "default") -> dict:
    """Send a tiny completion to warm up KV cache."""
    try:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Say 'warmup OK'"}],
            "max_tokens": 10,
            "temperature": 0,
        }
        t0 = time.time()
        r = httpx.post(f"{url}/chat/completions", json=payload, timeout=30.0)
        latency = round(time.time() - t0, 2)
        return {
            "ok": r.status_code == 200,
            "status_code": r.status_code,
            "latency_sec": latency,
            "response": r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else None,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def memory_snapshot() -> dict:
    """Get per-GPU memory usage."""
    try:
        import torch
        snaps = []
        for i in range(torch.cuda.device_count()):
            alloc = torch.cuda.memory_allocated(i) / (1024**3)
            reserved = torch.cuda.memory_reserved(i) / (1024**3)
            snaps.append({"id": i, "allocated_gb": round(alloc, 2), "reserved_gb": round(reserved, 2)})
        return {"ok": True, "gpus": snaps}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    vision_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/v1"
    text_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8001/v1"

    results = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "checks": {}}

    # 1. GPU
    print("[1/5] ROCm GPU check...")
    gpu = check_rocm_gpu()
    results["checks"]["gpu"] = gpu
    if gpu["ok"]:
        print(f"  ✓ {gpu['devices']} GPU(s) detected")
        for d in gpu["details"]:
            print(f"    GPU {d['id']}: {d['name']} ({d['total_memory_gb']} GB)")
    else:
        print(f"  ✗ {gpu.get('error')}")

    # 2. Vision server
    print(f"[2/5] Vision server ({vision_url})...")
    v_health = check_vllm_health(vision_url)
    results["checks"]["vision_health"] = v_health
    print(f"  {'✓' if v_health['ok'] else '✗'} /health → {v_health.get('status_code', 'ERR')}")

    # 3. Text server
    print(f"[3/5] Text server ({text_url})...")
    t_health = check_vllm_health(text_url)
    results["checks"]["text_health"] = t_health
    print(f"  {'✓' if t_health['ok'] else '✗'} /health → {t_health.get('status_code', 'ERR')}")

    # 4. Warm-ups
    if v_health["ok"]:
        print("[4/5] Warm-up vision model...")
        v_warm = warmup_call(vision_url)
        results["checks"]["vision_warmup"] = v_warm
        print(f"  {'✓' if v_warm['ok'] else '✗'} {v_warm.get('latency_sec', '-')}s")
    else:
        print("[4/5] Skipping vision warm-up (server down)")
        results["checks"]["vision_warmup"] = {"ok": False, "skipped": True}

    if t_health["ok"]:
        print("[5/5] Warm-up text model...")
        t_warm = warmup_call(text_url)
        results["checks"]["text_warmup"] = t_warm
        print(f"  {'✓' if t_warm['ok'] else '✗'} {t_warm.get('latency_sec', '-')}s")
    else:
        print("[5/5] Skipping text warm-up (server down)")
        results["checks"]["text_warmup"] = {"ok": False, "skipped": True}

    # 6. Memory
    print("\n--- GPU Memory ---")
    mem = memory_snapshot()
    results["checks"]["memory"] = mem
    if mem["ok"]:
        for g in mem["gpus"]:
            print(f"  GPU {g['id']}: alloc {g['allocated_gb']} GB / reserved {g['reserved_gb']} GB")
    else:
        print(f"  {mem.get('error')}")

    # Save
    out = Path("backend/data/gpu_health.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nReport saved: {out}")

    all_ok = gpu["ok"] and v_health["ok"] and t_health["ok"]
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

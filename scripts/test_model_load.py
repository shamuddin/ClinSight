#!/usr/bin/env python3
"""
GPU Model Validation Script

Connects to the GPU droplet's vLLM endpoints, verifies both vision and text
models respond, measures load time, and reports GPU memory usage via rocm-smi.
"""

import json
import subprocess
import sys
import time
from typing import Any

import requests

# Endpoints
VISION_URL = "http://134.199.202.5:8000/v1"
TEXT_URL = "http://134.199.202.5:8001/v1"
TIMEOUT_SECONDS = 120


def run_rocm_smi() -> dict[str, Any]:
    """Execute rocm-smi and parse JSON output."""
    try:
        result = subprocess.run(
            ["rocm-smi", "--showmeminfo", "vram", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except FileNotFoundError:
        print("ERROR: rocm-smi not found. Ensure ROCm is installed and in PATH.")
        return {}
    except subprocess.CalledProcessError as e:
        print(f"ERROR: rocm-smi failed: {e.stderr}")
        return {}
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse rocm-smi JSON: {e}")
        return {}


def format_gpu_memory(data: dict[str, Any]) -> str:
    """Pretty-print GPU memory info from rocm-smi JSON."""
    if not data:
        return "No GPU memory data available."
    lines = ["GPU Memory Usage (rocm-smi):"]
    for gpu_id, metrics in data.items():
        vram = metrics.get("VRAM", {})
        used = vram.get("used", "N/A")
        total = vram.get("total", "N/A")
        lines.append(f"  GPU {gpu_id}: {used} / {total}")
    return "\n".join(lines)


def check_model(endpoint_url: str, model_name: str, is_vision: bool = False) -> bool:
    """Check if a vLLM model endpoint is healthy and responds to a test request."""
    print(f"\nChecking {model_name} at {endpoint_url} ...")

    # 1. Verify the model list endpoint
    models_url = f"{endpoint_url}/models"
    try:
        start = time.perf_counter()
        resp = requests.get(models_url, timeout=TIMEOUT_SECONDS)
        latency = time.perf_counter() - start
        resp.raise_for_status()
        models = resp.json().get("data", [])
        model_ids = [m.get("id", "unknown") for m in models]
        print(f"  Models available: {model_ids} (list latency: {latency:.3f}s)")
    except requests.exceptions.RequestException as e:
        print(f"  FAILED to list models: {e}")
        return False

    # 2. Send a minimal completion/chat request to verify inference works
    chat_url = f"{endpoint_url}/chat/completions"
    payload: dict[str, Any] = {
        "model": model_ids[0] if model_ids else "default",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 5,
        "temperature": 0.0,
    }
    if is_vision:
        # For vision models, send a simple text-only message to keep the test lightweight
        payload["messages"] = [
            {"role": "user", "content": "Describe a circle in one word."}
        ]

    try:
        start = time.perf_counter()
        resp = requests.post(chat_url, json=payload, timeout=TIMEOUT_SECONDS)
        latency = time.perf_counter() - start
        resp.raise_for_status()
        body = resp.json()
        choices = body.get("choices", [])
        content = choices[0].get("message", {}).get("content", "") if choices else ""
        print(f"  Inference OK (latency: {latency:.3f}s) — response: {content!r}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  FAILED inference request: {e}")
        return False
    except (KeyError, IndexError) as e:
        print(f"  FAILED to parse response: {e}")
        return False


def main() -> int:
    print("=" * 60)
    print("GPU Model Load Validation")
    print("=" * 60)

    # GPU memory baseline
    print("\n--- GPU Memory (before) ---")
    mem_before = run_rocm_smi()
    print(format_gpu_memory(mem_before))

    overall_start = time.perf_counter()
    results: dict[str, bool] = {}

    # Test vision endpoint
    results["vision"] = check_model(VISION_URL, "Vision Model", is_vision=True)

    # Test text endpoint
    results["text"] = check_model(TEXT_URL, "Text Model", is_vision=False)

    overall_latency = time.perf_counter() - overall_start

    # GPU memory after
    print("\n--- GPU Memory (after) ---")
    mem_after = run_rocm_smi()
    print(format_gpu_memory(mem_after))

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    all_ok = all(results.values())
    for name, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  {name}: {status}")
    print(f"  Overall latency: {overall_latency:.3f}s")
    print(f"  Overall result: {'PASS' if all_ok else 'FAIL'}")
    print("=" * 60)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

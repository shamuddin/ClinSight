#!/bin/bash
set -e

echo "=== Installing vLLM ==="
pip install vllm --extra-index-url https://download.pytorch.org/whl/rocm7.0 2>&1 | tail -5

echo "=== Installing ClinSight deps ==="
cd /shared-docker
pip install -r requirements.txt 2>&1 | tail -5

echo "=== Done ==="

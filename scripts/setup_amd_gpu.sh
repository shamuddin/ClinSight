#!/usr/bin/env bash
# =============================================================================
# AMD ROCm + vLLM One-Click Setup for GPU Droplet
# =============================================================================
# Run this once on a fresh AMD GPU instance (Ubuntu 22.04/24.04).
# Requires: AMD GPU with ROCm support (MI100+, MI200+, W6800, RX 7900 XTX, etc.)
# =============================================================================
set -euo pipefail

echo "=== AMD GPU Setup ==="
echo "Target: ROCm 6.x + PyTorch + vLLM (ROCm)"

# ── Configurable env ──
export ROCM_VERSION="${ROCM_VERSION:-6.1}"
export PYTHON_VERSION="${PYTHON_VERSION:-3.11}"

# ── System deps ──
echo "[1/6] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev \
    build-essential cmake git wget curl vim \
    libopencv-dev libjpeg-dev libpng-dev libtiff-dev \
    rocm-opencl-runtime rocminfo rocprofiler-dev

# ── ROCm check ──
echo "[2/6] Verifying ROCm / GPU..."
if ! command -v rocminfo &>/dev/null; then
    echo "ERROR: rocminfo not found. Install ROCm first:"
    echo "  https://rocm.docs.amd.com/projects/install-on-linux/en/latest/"
    exit 1
fi
rocminfo | grep -E "Name:|Marketing name" || true

# ── Python venv ──
echo "[3/6] Creating Python virtual environment..."
python${PYTHON_VERSION} -m venv ~/clinsight-venv
source ~/clinsight-venv/bin/activate
pip install --upgrade pip wheel setuptools

# ── PyTorch (ROCm) ──
echo "[4/6] Installing PyTorch for ROCm..."
pip install torch==2.4.0+rocm${ROCM_VERSION} torchvision \
    --index-url "https://download.pytorch.org/whl/rocm${ROCM_VERSION}"

# ── vLLM (ROCm) ──
echo "[5/6] Building vLLM with ROCm support (this takes ~15-30 min)..."
# Use env var to skip CUDA-only compilation
export VLLM_INSTALL_PYNCCL="0"
export VLLM_TARGET_DEVICE="cuda"   # ROCm uses CUDA target in vLLM build system
pip install vllm==0.6.3 \
    --extra-index-url "https://download.pytorch.org/whl/rocm${ROCM_VERSION}" \
    --no-build-isolation

# ── ClinSight deps ──
echo "[6/6] Installing ClinSight Python dependencies..."
cd "$(dirname "$0")/.."  # repo root
pip install -r requirements.txt

echo ""
echo "=== Setup Complete ==="
echo "Activate: source ~/clinsight-venv/bin/activate"
echo "Next:    ./scripts/start_vllm_vision.sh &"
echo "         ./scripts/start_vllm_text.sh &"
echo "         python ./scripts/gpu_health_check.py"

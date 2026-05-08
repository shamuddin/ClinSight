#!/bin/bash
# ClinSight AMD Evidence Capture Script
# Run this INSIDE the rocm container (or on host if code is on host)
# Usage: bash capture_amd_evidence.sh

set -e

EVIDENCE_DIR="/mnt/scratch/results/evidence_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$EVIDENCE_DIR"

echo "=========================================="
echo "  ClinSight AMD Evidence Capture"
echo "  $(date)"
echo "=========================================="

# ── 1. System Info ──
echo "[1/8] Collecting system info..."
{
    echo "HOSTNAME: $(hostname)"
    echo "DATE: $(date -Iseconds)"
    echo "UPTIME: $(uptime)"
    uname -a
} > "$EVIDENCE_DIR/system_info.txt"

# ── 2. rocm-smi Baseline ──
echo "[2/8] Capturing rocm-smi baseline..."
rocm-smi --showmeminfo --showpower --showclkfrq --json > "$EVIDENCE_DIR/rocm-smi-baseline.json" 2>/dev/null || rocm-smi > "$EVIDENCE_DIR/rocm-smi-baseline.txt"

# ── 3. GPU Health JSON (detailed) ──
echo "[3/8] Capturing detailed GPU health..."
rocm-smi --showmeminfo vram --showpower --showclkfrq --showtemp --json > "$EVIDENCE_DIR/rocm-smi-detailed.json" 2>/dev/null || true

# ── 4. Verify vLLM Endpoints ──
echo "[4/8] Verifying vLLM endpoints..."
{
    echo "=== Vision Model (port 8000) ==="
    curl -s --max-time 10 http://localhost:8000/v1/models || echo "VISION_ENDPOINT_FAILED"
    echo ""
    echo "=== Text Model (port 8001) ==="
    curl -s --max-time 10 http://localhost:8001/v1/models || echo "TEXT_ENDPOINT_FAILED"
    echo ""
    echo "=== Backend Health (port 3000) ==="
    curl -s --max-time 10 http://localhost:3000/health || echo "BACKEND_ENDPOINT_FAILED"
} > "$EVIDENCE_DIR/endpoint_checks.txt"

# ── 5. Check Docker Processes ──
echo "[5/8] Checking container processes..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" > "$EVIDENCE_DIR/docker_ps.txt" 2>/dev/null || echo "docker ps failed" > "$EVIDENCE_DIR/docker_ps.txt"

# ── 6. Run Real Benchmark (if script exists) ──
echo "[6/8] Running real benchmark..."
if [ -f "/opt/clinsight/scripts/run_benchmark.py" ]; then
    cd /opt/clinsight
    python scripts/run_benchmark.py --mode real --cases 6 --iterations 3 --output "$EVIDENCE_DIR/benchmark_report_real.json" 2>&1 | tee "$EVIDENCE_DIR/benchmark_log.txt" || echo "BENCHMARK_FAILED" >> "$EVIDENCE_DIR/benchmark_log.txt"
else
    echo "Benchmark script not found at /opt/clinsight/scripts/run_benchmark.py" > "$EVIDENCE_DIR/benchmark_log.txt"
fi

# ── 7. rocm-smi Under Load (after benchmark) ──
echo "[7/8] Capturing rocm-smi post-benchmark..."
rocm-smi --showmeminfo --showpower --showclkfrq --json > "$EVIDENCE_DIR/rocm-smi-post-benchmark.json" 2>/dev/null || rocm-smi > "$EVIDENCE_DIR/rocm-smi-post-benchmark.txt"

# ── 8. Package Summary ──
echo "[8/8] Generating summary..."
{
    echo "Evidence captured at: $(date -Iseconds)"
    echo "Location: $EVIDENCE_DIR"
    echo ""
    echo "Files captured:"
    ls -lh "$EVIDENCE_DIR/"
    echo ""
    echo "Total size:"
    du -sh "$EVIDENCE_DIR/"
} > "$EVIDENCE_DIR/SUMMARY.txt"

echo ""
echo "=========================================="
echo "  DONE! Evidence captured at:"
echo "  $EVIDENCE_DIR"
echo "=========================================="
echo ""
echo "To copy to local machine, run:"
echo "  scp -r root@129.212.176.125:$EVIDENCE_DIR ./"

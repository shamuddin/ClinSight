#!/bin/bash
# ClinSight — Live rocm-smi Capture During Inference
# Run this on the server during a case analysis to get judge-ready GPU evidence
#
# Usage:
#   bash /opt/clinsight/scripts/capture_rocm_smi_live.sh
#
# What it does:
#   1. Starts rocm-smi monitoring in background (saves every 2 seconds)
#   2. Triggers Case 001 analysis via curl
#   3. Stops monitoring when analysis completes
#   4. Saves everything to /opt/clinsight/benchmarks/gpu_results/

set -e

API_BASE="http://localhost:3000"
CASE_ID="CS-2024-001"
OUTPUT_DIR="/opt/clinsight/benchmarks/gpu_results/rocm_smi_live_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "  ClinSight Live GPU Evidence Capture"
echo "  Target: $CASE_ID"
echo "  Output: $OUTPUT_DIR"
echo "=========================================="
echo ""

# --- Step 1: Capture baseline rocm-smi ---
echo "[1/5] Capturing baseline rocm-smi..."
rocm-smi > "$OUTPUT_DIR/rocm_smi_baseline.txt" 2>&1
cat "$OUTPUT_DIR/rocm_smi_baseline.txt"
echo ""

# --- Step 2: Start background rocm-smi monitoring ---
echo "[2/5] Starting background rocm-smi monitoring (every 2s)..."
ROCM_LOG="$OUTPUT_DIR/rocm_smi_stream.txt"
echo "=== rocm-smi live stream ===" > "$ROCM_LOG"

# Background process: append rocm-smi every 2 seconds
(
  while true; do
    echo "--- $(date '+%H:%M:%S') ---" >> "$ROCM_LOG"
    rocm-smi --showuse --showpower --showtemp --showvoltage --showclocks >> "$ROCM_LOG" 2>&1
    echo "" >> "$ROCM_LOG"
    sleep 2
  done
) &
ROCM_PID=$!

echo "    Background PID: $ROCM_PID"
echo ""

# --- Step 3: Trigger case analysis ---
echo "[3/5] Triggering $CASE_ID analysis..."
START_TIME=$(date +%s)
curl -s "$API_BASE/demo/analyze/$CASE_ID" > "$OUTPUT_DIR/case_result.json" 2>&1 &
CURL_PID=$!

echo "    curl PID: $CURL_PID"
echo "    Inference running... (~23 seconds)"
echo ""

# --- Step 4: Show live status while waiting ---
echo "[4/5] Live status (Ctrl+C to cancel):"
while kill -0 $CURL_PID 2>/dev/null; do
  echo -n "."
  sleep 1
done
echo ""

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo "    Analysis complete in ${ELAPSED}s"
echo ""

# --- Step 5: Stop monitoring and capture final state ---
echo "[5/5] Stopping monitor and capturing final rocm-smi..."
kill $ROCM_PID 2>/dev/null || true
wait $ROCM_PID 2>/dev/null || true

rocm-smi > "$OUTPUT_DIR/rocm_smi_final.txt" 2>&1

echo ""
echo "=========================================="
echo "  CAPTURE COMPLETE"
echo "=========================================="
echo ""
echo "Files saved to: $OUTPUT_DIR"
echo ""
echo "Contents:"
ls -lh "$OUTPUT_DIR"
echo ""
echo "--- Final rocm-smi snapshot ---"
cat "$OUTPUT_DIR/rocm_smi_final.txt"
echo ""
echo "--- Case result (first 5 lines) ---"
head -5 "$OUTPUT_DIR/case_result.json"
echo ""
echo "=========================================="
echo "INSTRUCTIONS FOR SCREENSHOT:"
echo "=========================================="
echo "1. Open a terminal"
echo "2. Run:  watch -n 1 rocm-smi"
echo "3. In another terminal, run:  bash /opt/clinsight/scripts/capture_rocm_smi_live.sh"
echo "4. Take a screenshot of the watch terminal when GPU% spikes"
echo "5. The screenshot should show: GPU name, Temp, Power, VRAM%, GPU%, Clocks"
echo ""

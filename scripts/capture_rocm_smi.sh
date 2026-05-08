#!/bin/bash
# Capture rocm-smi output during live inference on AMD MI300X
set -e

OUTDIR="/mnt/scratch/clinsight-clean/benchmarks/gpu_results"
mkdir -p "$OUTDIR"

echo "=== Starting rocm-smi capture during inference ==="
echo "Output dir: $OUTDIR"

# Clear previous capture
> "$OUTDIR/rocm_smi_during.txt"

# Start rocm-smi capture loop in background
(
  for i in $(seq 1 60); do
    echo "=== snapshot $i ===" >> "$OUTDIR/rocm_smi_during.txt"
    rocm-smi >> "$OUTDIR/rocm_smi_during.txt" 2>&1
    echo "" >> "$OUTDIR/rocm_smi_during.txt"
    sleep 2
  done
) &
ROCM_PID=$!

echo "rocm-smi capture PID: $ROCM_PID"

# Run one inference case
echo "Starting inference..."
python3 -c "
import urllib.request, json
try:
    resp = urllib.request.urlopen('http://172.17.0.1:3000/demo/analyze/CS-2024-001', timeout=300)
    data = json.load(resp)
    print('Inference complete:', data.get('case_id'), 'ESI=', data.get('esi_level'), 'time=', data.get('total_time_ms'))
except Exception as e:
    print('Inference error:', e)
"

# Wait for a few more seconds after inference completes
echo "Inference done. Capturing cooldown..."
sleep 10

# Stop rocm-smi capture
kill $ROCM_PID 2>/dev/null || true
wait $ROCM_PID 2>/dev/null || true

echo "=== Capture complete ==="
echo "File: $OUTDIR/rocm_smi_during.txt"
wc -l "$OUTDIR/rocm_smi_during.txt"

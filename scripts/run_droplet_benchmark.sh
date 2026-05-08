#!/bin/bash
# Run real benchmark on droplet
set -e
cd /mnt/scratch/clinsight-clean

echo "=== ROCm SMI Capture ==="
mkdir -p benchmarks/gpu_results
docker exec rocm rocm-smi > benchmarks/gpu_results/rocm_smi_idle.txt 2>&1
docker exec rocm rocm-smi --showproductname >> benchmarks/gpu_results/rocm_smi_idle.txt 2>&1
docker exec rocm rocm-smi -a > benchmarks/gpu_results/rocm_smi_detail.txt 2>&1
date >> benchmarks/gpu_results/rocm_smi_idle.txt

echo "=== Starting Benchmark ==="
python3 benchmarks/run_real_benchmark.py 2>&1 | tee /tmp/bench.log

echo "=== ROCm SMI After ==="
docker exec rocm rocm-smi > benchmarks/gpu_results/rocm_smi_after.txt 2>&1

echo "=== Done ==="
cat /tmp/bench.log | tail -20

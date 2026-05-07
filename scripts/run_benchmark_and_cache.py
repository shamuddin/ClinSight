#!/usr/bin/env python3
"""Run benchmark + generate cache on the GPU droplet."""
import subprocess, time, json, os, sys

os.environ["USE_MOCK"] = "false"

# 1. Check servers
for port, name in [(8000,"vision"),(8001,"text")]:
    r = subprocess.run(f"curl -s http://127.0.0.1:{port}/v1/models", shell=True, capture_output=True, text=True)
    if r.returncode == 0:
        try:
            d = json.loads(r.stdout)
            print(f"  {name} ({port}): {d['data'][0]['id']}")
        except:
            print(f"  {name} ({port}): ERROR")
    else:
        print(f"  {name} ({port}): DOWN")
        sys.exit(1)

# 2. GPU baseline
print("\n=== ROCm Baseline ===")
subprocess.run("rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -8", shell=True)

# 3. Run benchmark with correct URLs
print("\n=== Running Benchmark (3 cases, 1 iteration) ===")
env = os.environ.copy()
env["USE_MOCK"] = "false"
r = subprocess.run(
    ["python3", "-c",
     "import sys; sys.path.insert(0, '/opt/clinsight'); "
     "from backend.core.config import settings; "
     "settings.use_mock=False; "
     "settings.vllm_vision_url='http://localhost:8000/v1'; "
     "settings.vllm_text_url='http://localhost:8001/v1'; "
     "print('config_ok')"],
    capture_output=True, text=True)
print(r.stdout.strip())

# Now run benchmark script
r = subprocess.run(
    ["python3", "scripts/run_benchmark.py", "--mode", "real", "--cases", "3", "--iterations", "1",
     "--vision-url", "http://127.0.0.1:8000/v1", "--text-url", "http://127.0.0.1:8001/v1"],
    capture_output=True, text=True, cwd="/opt/clinsight", env=env, timeout=600)
print(r.stdout[-3000:] if len(r.stdout) > 3000 else r.stdout)
print(r.stderr[-1000:] if len(r.stderr) > 1000 else r.stderr)

# 4. GPU state
print("\n=== ROCm After Benchmark ===")
subprocess.run("rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -8", shell=True)

# 5. Find and copy benchmark report
reports = subprocess.run("ls -t /opt/clinsight/benchmarks/benchmark_report_*.json 2>/dev/null | head -1",
                         shell=True, capture_output=True, text=True).stdout.strip()
if reports:
    subprocess.run(f"cp {reports} /mnt/scratch/results/benchmark_report_latest.json", shell=True)
    print(f"\nBenchmark report: {reports}")
else:
    print("\nNo benchmark report found")

# 6. Generate contingency cache
print("\n=== Generating Contingency Cache ===")
r = subprocess.run(["python3", "scripts/generate_contingency_cache.py"],
                   capture_output=True, text=True, cwd="/opt/clinsight", env=env, timeout=600)
print(r.stdout[-2000:] if len(r.stdout) > 2000 else r.stdout)
print(r.stderr[-500:] if len(r.stderr) > 500 else r.stderr)

# 7. Copy files to results
print("\n=== Copying results ===")
subprocess.run("cp /opt/clinsight/backend/data/contingency_cache/*.json /mnt/scratch/results/ 2>/dev/null || true", shell=True)
subprocess.run("cp /opt/clinsight/benchmarks/*.json /mnt/scratch/results/ 2>/dev/null || true", shell=True)
print("Done")

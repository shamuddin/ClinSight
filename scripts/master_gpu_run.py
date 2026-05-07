#!/usr/bin/env python3
"""Master GPU execution: E2E + benchmark + rocm-smi capture + cache generation."""
import subprocess, time, json, sys, os
from pathlib import Path

CONTAINER = "rocm"
REPO = "/opt/clinsight"
HF_CACHE = "/mnt/scratch/hf_cache"
RESULTS = "/mnt/scratch/results"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def run_in_container(cmd: str, timeout=600):
    r = subprocess.run(
        ["docker", "exec", CONTAINER, "bash", "-c", cmd],
        capture_output=True, text=True, timeout=timeout
    )
    return r.stdout, r.stderr, r.returncode

def run_host(cmd: str, timeout=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout, r.stderr, r.returncode

os.makedirs(RESULTS, exist_ok=True)

# 1. Validate server
log("=== 1. Server validation ===")
out, err, code = run_in_container(f"cd {REPO} && python3 scripts/test_model_load.py", timeout=120)
Path(f"{RESULTS}/test_model_load.log").write_text(f"STDOUT:\n{out}\n\nSTDERR:\n{err}\n\nCODE:{code}")
log(f"test_model_load.py exit={code}")

# 2. rocm-smi baseline
log("=== 2. rocm-smi baseline ===")
out, _, _ = run_host("rocm-smi --showmeminfo vram --showuse --showtemp --showpower 2>/dev/null")
Path(f"{RESULTS}/rocm_smi_baseline.txt").write_text(out)
log("rocm-smi captured")

# 3. Run benchmark (3 cases, 2 iterations to save time)
log("=== 3. Benchmark ===")
out, err, code = run_in_container(
    f"cd {REPO} && python3 scripts/run_benchmark.py --mode real --cases 3 --iterations 2 --vision-url http://127.0.0.1:8000/v1 --text-url http://127.0.0.1:8000/v1",
    timeout=600
)
Path(f"{RESULTS}/benchmark.log").write_text(f"STDOUT:\n{out}\n\nSTDERR:\n{err}\n\nCODE:{code}")
log(f"Benchmark exit={code}")

# Copy benchmark JSON
out, _, _ = run_in_container(f"ls {REPO}/benchmarks/benchmark_report_*.json 2>/dev/null | tail -1")
if out.strip():
    latest = out.strip()
    run_in_container(f"cp {latest} {RESULTS}/benchmark_report.json")
    log(f"Copied {latest}")

# 4. rocm-smi during load
log("=== 4. rocm-smi during inference ===")
out, _, _ = run_host("rocm-smi --showmeminfo vram --showuse --showtemp --showpower 2>/dev/null")
Path(f"{RESULTS}/rocm_smi_during.txt").write_text(out)

# 5. Generate contingency cache for 3 cases
log("=== 5. Generating contingency cache ===")
cache_cases = [
    ("CS-2024-001", "CS-2024-001.png", {'troponin_i':0.12,'bnp':180,'crp':12,'wbc':9.2,'hemoglobin':14.1,'platelets':245,'creatinine':0.9,'glucose':105}, "45yo male chest pain"),
    ("CS-2024-002", "CS-2024-002.png", {'troponin_i':0.45,'bnp':450,'crp':35,'wbc':15.3,'hemoglobin':11.2,'platelets':198,'creatinine':1.4,'glucose':142}, "68yo female pneumonia"),
    ("CS-2024-003", "CS-2024-003.png", {'troponin_i':0.08,'bnp':1200,'crp':8,'wbc':7.1,'hemoglobin':13.5,'platelets':210,'creatinine':1.1,'glucose':95}, "72yo male pulmonary edema"),
]

for case_id, img, labs, note in cache_cases:
    py = f"""
import sys, asyncio, json
sys.path.insert(0, '{REPO}')
from backend.agents.graph import run_pipeline
state = {{
    'case_id': '{case_id}',
    'image_path': 'frontend/react-app/public/demo-images/{img}',
    'lab_values': {json.dumps(labs)},
    'lab_units': {{'troponin_i':'ng/L','bnp':'pg/mL','crp':'mg/L','wbc':'K/uL','hemoglobin':'g/dL','platelets':'K/uL','creatinine':'mg/dL','glucose':'mg/dL'}},
    'triage_note': '{note}',
    'patient_age': 45, 'patient_sex': 'M', 'patient_race': 'White', 'chief_complaint': 'Chest pain',
    'vitals': {{'bp':'120/80','hr':72,'rr':16,'temp':37.0,'spo2':98}},
    'image_hash':'','quality_gate':{{}},'pediatric_gate':{{}},'input_warnings':[],
    'image_features':{{}},'findings':[],'attention_regions':[],'lab_alerts':[],'lab_patterns':[],
    'lab_correlation':{{}},'contradictions':[],'hallucination_flags':[],'bias_flags':[],
    'safety_downgrades':0,'merged_flags':[],'esi_level':5,'esi_description':'','esi_rules_triggered':[],
    'differential':[],'suggested_actions':[],'report':{{}},'audit_log':[],'total_time_ms':0.0,
}}
async def test():
    final = await run_pipeline(state)
    with open('/mnt/scratch/results/{case_id}_merged.json', 'w') as f:
        json.dump(final, f, indent=2)
    print(json.dumps({{'esi':final.get('esi_level'),'findings':len(final.get('findings',[]))}}))
asyncio.run(test())
"""
    out, err, code = run_in_container(f"python3 -c \"{py}\"", timeout=300)
    Path(f"{RESULTS}/{case_id}_log.txt").write_text(f"STDOUT:\n{out}\nSTDERR:\n{err}\nCODE:{code}")
    log(f"Cache {case_id}: exit={code} output={out.strip()[:60]}")

log("=== ALL DONE ===")
out, _, _ = run_in_container(f"ls -la {RESULTS}/")
log(f"Results:\n{out}")

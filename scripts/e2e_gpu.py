#!/usr/bin/env python3
"""E2E test on the GPU droplet using BOTH vLLM servers."""
import asyncio, aiohttp, json, time, subprocess, sys

async def post_json(url, payload, timeout=300):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            return await resp.json()

async def main():
    BASE = "http://127.0.0.1:8002"
    
    state = {
        "case_id": "CS-2024-001",
        "image_path": "frontend/react-app/public/demo-images/CS-2024-001.png",
        "lab_values": {"troponin_i":0.12,"bnp":180,"crp":12,"wbc":9.2,"hemoglobin":14.1,"platelets":245,"creatinine":0.9,"glucose":105},
        "lab_units": {"troponin_i":"ng/L","bnp":"pg/mL","crp":"mg/L","wbc":"K/uL","hemoglobin":"g/dL","platelets":"K/uL","creatinine":"mg/dL","glucose":"mg/dL"},
        "triage_note": "52M chest pain 2hr substernal radiating L arm",
        "patient_age":52,"patient_sex":"Male","patient_race":"White","chief_complaint":"Chest pain",
        "vitals": {"bp":"148/92","hr":102,"rr":20,"spo2":97,"temp":37.1},
        "image_hash":"","quality_gate":{},"pediatric_gate":{},"input_warnings":[],
        "image_features":{},"findings":[],"attention_regions":[],"lab_alerts":[],"lab_patterns":[],
        "lab_correlation":{},"contradictions":[],"hallucination_flags":[],"bias_flags":[],
        "safety_downgrades":0,"merged_flags":[],"esi_level":5,"esi_description":"","esi_rules_triggered":[],
        "differential":[],"suggested_actions":[],"report":{},"audit_log":[],"total_time_ms":0.0
    }
    
    print("[E2E] Sending CS-2024-001...")
    t0 = time.time()
    result = await post_json(f"{BASE}/api/analyze", state)
    elapsed = time.time() - t0
    
    print(f"[E2E] TIME: {elapsed:.2f}s")
    esi = result.get("esi_level", "?")
    findings = len(result.get("findings", []))
    actions = len(result.get("suggested_actions", []))
    print(f"[E2E] ESI: {esi} | Findings: {findings} | Actions: {actions}")
    
    # Save result
    with open("/mnt/scratch/results/e2e_CS-2024-001.json", "w") as f:
        json.dump(result, f, indent=2)
    print("[E2E] Saved to /mnt/scratch/results/e2e_CS-2024-001.json")
    
    # GPU state
    gpu = subprocess.run(["rocm-smi", "--showmeminfo", "vram", "--showuse"], capture_output=True, text=True)
    with open("/mnt/scratch/results/e2e_rocm_smi.txt", "w") as f:
        f.write(f"After inference ({elapsed:.2f}s):\n")
        f.write(gpu.stdout)
    
    print("[E2E] GPU state captured")
    return {"elapsed": elapsed, "esi": esi, "findings": findings, "actions": actions}

if __name__ == "__main__":
    result = asyncio.run(main())
    print(json.dumps(result))

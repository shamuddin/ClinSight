import asyncio, sys, json, time, subprocess, os
from pathlib import Path

sys.path.insert(0, "/opt/clinsight")
from backend.agents.graph import run_pipeline

async def main():
    case_id = "CS-2024-001"
    state = {
        "case_id": case_id,
        "image_path": "frontend/react-app/public/demo-images/CS-2024-001.png",
        "lab_values": {"troponin_i":0.12,"bnp":180,"crp":12,"wbc":9.2,"hemoglobin":14.1,"platelets":245,"creatinine":0.9,"glucose":105},
        "lab_units": {"troponin_i":"ng/L","bnp":"pg/mL","crp":"mg/L","wbc":"K/uL","hemoglobin":"g/dL","platelets":"K/uL","creatinine":"mg/dL","glucose":"mg/dL"},
        "triage_note": "52M chest pain 2hr substernal radiating L arm",
        "patient_age":52, "patient_sex":"Male", "patient_race":"White", "chief_complaint":"Chest pain",
        "vitals": {"bp":"148/92","hr":102,"rr":20,"spo2":97,"temp":37.1},
        "image_hash":"", "quality_gate":{}, "pediatric_gate":{}, "input_warnings":[],
        "image_features":{}, "findings":[], "attention_regions":[], "lab_alerts":[], "lab_patterns":[],
        "lab_correlation":{}, "contradictions":[], "hallucination_flags":[], "bias_flags":[],
        "safety_downgrades":0, "merged_flags":[], "esi_level":5, "esi_description":"", "esi_rules_triggered":[],
        "differential":[], "suggested_actions":[], "report":{}, "audit_log":[], "total_time_ms":0.0
    }
    
    os.makedirs("/mnt/scratch/results", exist_ok=True)
    
    print(f"[E2E] Running pipeline case={case_id}...")
    t0 = time.time()
    final = await run_pipeline(state)
    elapsed = time.time() - t0
    
    esi = final.get("esi_level", "?")
    findings = len(final.get("findings", []))
    actions = len(final.get("suggested_actions", []))
    flags = len(final.get("merged_flags", []))
    
    print(f"[E2E] TIME: {elapsed:.2f}s")
    print(f"[E2E] ESI: {esi} | Findings: {findings} | Actions: {actions} | Flags: {flags}")
    
    # Save result
    out_path = f"/mnt/scratch/results/e2e_{case_id}.json"
    with open(out_path, "w") as f:
        json.dump(final, f, indent=2)
    print(f"[E2E] Saved to {out_path}")
    
    # GPU state
    try:
        gpu = subprocess.run(["rocm-smi", "--showmeminfo", "vram", "--showuse", "--showtemp", "--showpower"],
                            capture_output=True, text=True, timeout=10)
        gpu_path = f"/mnt/scratch/results/rocm_smi_post_e2e.txt"
        with open(gpu_path, "w") as f:
            f.write(f"After E2E inference (elapsed={elapsed:.2f}s):\n")
            f.write(gpu.stdout)
        print("[E2E] GPU state captured")
    except Exception as e:
        print(f"[E2E] GPU capture error: {e}")
    
    return {"elapsed": elapsed, "esi": esi, "findings": findings, "actions": actions, "flags": flags}

if __name__ == "__main__":
    result = asyncio.run(main())
    print(json.dumps(result))

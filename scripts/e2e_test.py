import asyncio, sys, os, time, json

sys.path.insert(0, "/opt/clinsight")

from backend.core.config import settings
settings.use_mock = False
settings.vllm_vision_url = "http://127.0.0.1:8000/v1"
settings.vllm_text_url = "http://127.0.0.1:8000/v1"

from backend.agents.graph import run_pipeline

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

async def main():
    t0 = time.time()
    final = await run_pipeline(state)
    elapsed = time.time() - t0
    print(f"PIPELINE_TIME: {elapsed:.2f}s")
    print(f"ESI: {final.get('esi_level')}")
    print(f"FINDINGS: {len(final.get('findings', []))}")
    print(f"ACTIONS: {len(final.get('suggested_actions', []))}")
    out_path = "/mnt/scratch/results/e2e_real.json"
    with open(out_path, "w") as f:
        json.dump(final, f, indent=2)
    print(f"SAVED {out_path}")

asyncio.run(main())

from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter(prefix="/judge", tags=["judge"])

CACHE_DIR = Path("/opt/clinsight/backend/data/contingency_cache")
CASES_PATH = Path(__file__).parent.parent / "data" / "demo_cases.json"

@router.get("/accuracy/{case_id}")
async def judge_accuracy(case_id: str):
    """Judge-facing endpoint: ground truth vs predicted, with full agent trace."""
    cache_file = CACHE_DIR / f"{case_id}.json"
    if not cache_file.exists():
        return {"error": "Run pipeline first to generate cache"}
    
    cache = json.loads(cache_file.read_text())
    cases = json.loads(CASES_PATH.read_text()) if CASES_PATH.exists() else []
    case = next((c for c in cases if c["case_id"] == case_id), {})
    
    # Ground truth mapping (from case definition)
    expected_esi = {
        "CS-2024-001": 1,  # Tension pneumothorax
        "CS-2024-002": 1,  # Head trauma with LOC
        "CS-2024-003": 3,  # Fever/rash (peds)
        "CS-2024-004": 1,  # Altered mental status (septic)
        "CS-2024-005": 2,  # Severe headache (SAH)
        "CS-2024-006": 2,  # Abdominal pain ( AAA )
    }.get(case_id, "unknown")
    
    predicted_esi = cache.get("esi_level")
    
    # Safety verification check
    safety_flags = cache.get("safety_flags", [])
    re_verification = {
        "flags_total": len(safety_flags),
        "high_severity_flags": sum(1 for f in safety_flags if isinstance(f, dict) and f.get("severity") == "HIGH"),
        "contradictions_caught": len(cache.get("contradictions", [])),
        "hallucinations_caught": len(cache.get("hallucination_flags", [])),
        "bias_flags": len(cache.get("bias_flags", [])),
        "safety_downgrades": cache.get("safety_downgrades", 0),
    }
    
    # Agent trace
    audit = cache.get("audit_log", [])
    agent_trace = []
    for entry in audit:
        agent_trace.append({
            "agent": entry.get("agent"),
            "action": entry.get("action"),
            "timestamp": entry.get("timestamp"),
            "details": {k:v for k,v in entry.items() if k not in ("agent","action","timestamp")}
        })
    
    return {
        "case_id": case_id,
        "ground_truth_esi": expected_esi,
        "predicted_esi": predicted_esi,
        "esi_correct": predicted_esi == expected_esi,
        
        "inputs": {
            "image": case.get("image_path"),
            "vitals": case.get("vitals"),
            "labs": case.get("lab_values"),
            "triage_note": case.get("triage_note"),
            "patient": {
                "age": case.get("patient_age"),
                "sex": case.get("patient_sex"),
                "race": case.get("patient_race"),
            }
        },
        
        "agent_outputs": {
            "coordinator": {
                "quality_pass": cache.get("quality_gate", {}).get("pass"),
                "pediatric_status": cache.get("pediatric_gate", {}).get("status"),
                "warnings": cache.get("input_warnings", []),
            },
            "radiologist": {
                "findings": cache.get("findings", []),
                "attention_regions": len(cache.get("attention_regions", [])),
            },
            "lab_analyst": {
                "alerts": cache.get("lab_alerts", []),
                "patterns": cache.get("lab_patterns", []),
            },
            "safety": re_verification,
            "documenter": {
                "differential": cache.get("differential", []),
                "actions": cache.get("suggested_actions", []),
                "report_summary": cache.get("report", {}).get("summary", "")[:200],
            }
        },
        
        "safety_verification": {
            "re_verification_active": re_verification["flags_total"] > 0,
            "contradiction_detection": re_verification["contradictions_caught"] > 0,
            "hallucination_check": re_verification["hallucinations_caught"] == 0,  # zero is good
            "bias_audit": re_verification["bias_flags"] == 0,
            "downgrades": re_verification["safety_downgrades"],
        },
        
        "agent_trace": agent_trace,
        "total_time_ms": cache.get("total_time_ms"),
        "generated_at": cache.get("generated_at"),
    }

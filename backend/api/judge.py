from fastapi import APIRouter
from pathlib import Path
import json
from typing import Dict, Any
from backend.core.accuracy import compute_accuracy, GROUND_TRUTH

router = APIRouter(prefix="/judge", tags=["judge"])

DEMO_CASES_PATH = Path(__file__).parent.parent / "data" / "demo_cases.json"

def _load_demo_cases():
    if DEMO_CASES_PATH.exists():
        return json.loads(DEMO_CASES_PATH.read_text())
    return []

@router.get("/accuracy/{case_id}")
async def judge_accuracy(case_id: str):
    """Judge-facing endpoint: ground truth metadata (run pipeline first)."""
    cases = _load_demo_cases()
    case = next((c for c in cases if c.get("case_id") == case_id), None)
    if not case:
        return {"error": f"Case {case_id} not found"}

    gt = GROUND_TRUTH.get(case_id, {})
    expected_esi = gt.get("esi_level")

    return {
        "case_id": case_id,
        "ground_truth_esi": expected_esi,
        "status": "ready_for_verification",
        "message": "Run the pipeline to see live accuracy scores",
        "expected_findings_count": len(gt.get("expected_findings", [])),
        "expected_alerts_count": len(gt.get("expected_lab_alerts", [])),
        "expected_flags_count": len(gt.get("expected_safety_flags", [])),
        "expected_differential_count": len(gt.get("expected_differential", [])),
    }


@router.post("/accuracy/compute")
async def judge_accuracy_compute(result: Dict[str, Any]):
    """Compute accuracy for a pipeline result object (called by frontend after run)."""
    try:
        return compute_accuracy(result)
    except Exception as e:
        return {"error": str(e)}


@router.get("/accuracy")
async def judge_aggregate():
    """Aggregate accuracy across all 6 demo cases (requires cache or pre-run)."""
    from pathlib import Path
    CACHE_DIR = Path("/opt/clinsight/backend/data/contingency_cache")
    results = []
    for f in CACHE_DIR.glob("*.json"):
        results.append(json.loads(f.read_text()))

    if not results:
        return {"error": "Run all demo cases first to compute aggregate accuracy"}

    from backend.core.accuracy import compute_aggregate_accuracy
    return compute_aggregate_accuracy(results)

"""Demo router - pre-built clinical cases + full pipeline + SSE streaming."""

import json
import time
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pathlib import Path
from pydantic import BaseModel, Field

from backend.core.state import AgentState
from backend.agents.graph import run_pipeline, app as pipeline_graph

router = APIRouter(prefix="/demo", tags=["demo"])

DEMO_CASES_PATH = Path(__file__).parent.parent / "data" / "demo_cases.json"


class DemoOverrideRequest(BaseModel):
    """Overrides for judge-facing what-if scenarios."""

    lab_overrides: dict[str, float] = Field(default_factory=dict)
    vitals_overrides: dict[str, float | str] = Field(default_factory=dict)
    scenario_name: str = "custom"


def _load_cases() -> list:
    if DEMO_CASES_PATH.exists():
        return json.loads(DEMO_CASES_PATH.read_text())
    return []


def _make_state(case: dict) -> AgentState:
    """Convert JSON case dict to AgentState with defaults."""
    return {
        "case_id":           case["case_id"],
        "image_path":        case["image_path"],
        "image_hash":        "",
        "quality_gate":      {},
        "pediatric_gate":    {},
        "input_warnings":    [],
        "image_features":    {},
        "findings":          [],
        "attention_regions": [],
        "lab_values":        case.get("lab_values", {}),
        "lab_units":         case.get("lab_units", {}),
        "lab_alerts":        [],
        "lab_patterns":      [],
        "lab_correlation":   {},
        "contradictions":    [],
        "hallucination_flags": [],
        "bias_flags":        [],
        "safety_downgrades": 0,
        "merged_flags":      [],
        "esi_level":         5,
        "esi_description":   "",
        "esi_rules_triggered": [],
        "differential":      [],
        "suggested_actions": [],
        "report":            {},
        "audit_log":         [],
        "total_time_ms":     0.0,
    }


def _populate_state(state: AgentState, case: dict) -> AgentState:
    """Fill case-specific fields into an AgentState."""
    state["triage_note"]      = case["triage_note"]
    state["patient_age"]      = case["patient_age"]
    state["patient_sex"]      = case["patient_sex"]
    state["patient_race"]     = case["patient_race"]
    state["chief_complaint"]  = case["chief_complaint"]
    state["vitals"]           = case["vitals"]
    state["image_path"]       = case["image_path"]
    state["lab_values"]       = case["lab_values"]
    state["lab_units"]        = case["lab_units"]
    return state


def _apply_overrides(case: dict, overrides: DemoOverrideRequest) -> dict:
    """Return a copy of a demo case with labs/vitals adjusted for what-if."""
    adjusted = json.loads(json.dumps(case))
    adjusted["lab_values"].update(overrides.lab_overrides)
    adjusted["vitals"].update(overrides.vitals_overrides)
    adjusted["case_id"] = f"{case['case_id']}::{overrides.scenario_name}"
    adjusted["triage_note"] = (
        f"{case['triage_note']} What-if scenario: {overrides.scenario_name}; "
        f"lab overrides={overrides.lab_overrides}; vitals overrides={overrides.vitals_overrides}."
    )
    return adjusted


def _build_response(final: dict, case: dict) -> dict:
    """Shared shape for both streaming and non-streaming endpoints."""
    return {
        "case_id":              final["case_id"],
        "esi_level":            final["esi_level"],
        "esi_description":      final["esi_description"],
        "findings":             final["findings"],
        "lab_alerts":           final["lab_alerts"],
        "differential":         final["differential"],
        "suggested_actions":    final["suggested_actions"],
        "safety_flags":         final["merged_flags"],
        "report":               final["report"],
        "audit_log":            final["audit_log"],
        "quality_gate":         final["quality_gate"],
        "pediatric_gate":       final.get("pediatric_gate", {}),
        "lab_patterns":         final.get("lab_patterns", []),
        "attention_regions":    final.get("attention_regions", []),
        # Safety sub-counts (for SafetyTheater component)
        "contradictions_count":  len(final.get("contradictions", [])),
        "hallucination_count":   len(final.get("hallucination_flags", [])),
        "bias_count":            len(final.get("bias_flags", [])),
        # Patient context
        "vitals":          case["vitals"],
        "triage_note":     case["triage_note"],
        "patient_age":     case["patient_age"],
        "patient_sex":     case["patient_sex"],
        "patient_race":    case["patient_race"],
        "chief_complaint": case["chief_complaint"],
        "lab_values":      case["lab_values"],
        "lab_units":       case["lab_units"],
        "total_time_ms":   final["total_time_ms"],
        # Image URL for frontend
        "image_url":       f"/demo/image/{final['case_id']}",
    }


# ─── GET /demo/cases ────────────────────────────────────────────────────────

@router.get("/cases")
async def list_demo_cases():
    cases = _load_cases()
    return [{
        "case_id":          c["case_id"],
        "patient_age":      c["patient_age"],
        "patient_sex":      c["patient_sex"],
        "chief_complaint":  c["chief_complaint"],
        "triage_note":      c["triage_note"],
        "vitals":           c["vitals"],
    } for c in cases]


# ─── GET /demo/image/{case_id} ──────────────────────────────────────────────

IMAGE_DIR = Path(__file__).parent.parent / "data" / "images"

@router.get("/image/{case_id}")
async def get_case_image(case_id: str):
    """Serve the actual chest X-ray PNG for a demo case."""
    # Strip what-if suffix
    base_id = case_id.split("::")[0]
    image_path = IMAGE_DIR / f"{base_id}.png"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(image_path), media_type="image/png")


# ─── GET /demo/analyze/{case_id} ─────────────────────────────────────────────

@router.get("/analyze/{case_id}")
async def analyze_demo_case(case_id: str):
    cases = _load_cases()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    state = _populate_state(_make_state(case), case)
    start = time.time()
    final = await run_pipeline(state)
    final["total_time_ms"] = round((time.time() - start) * 1000, 2)

    if final.get("esi_level") == -1:
        raise HTTPException(status_code=422, detail={
            "error":        "INPUT_REJECTED",
            "reason":       final.get("esi_description"),
            "quality_gate": final.get("quality_gate"),
        })

    return _build_response(final, case)


@router.post("/analyze/{case_id}/override")
async def analyze_demo_case_override(case_id: str, overrides: DemoOverrideRequest):
    cases = _load_cases()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    adjusted_case = _apply_overrides(case, overrides)
    state = _populate_state(_make_state(adjusted_case), adjusted_case)
    start = time.time()
    final = await run_pipeline(state)
    final["total_time_ms"] = round((time.time() - start) * 1000, 2)

    if final.get("esi_level") == -1:
        raise HTTPException(status_code=422, detail={
            "error":        "INPUT_REJECTED",
            "reason":       final.get("esi_description"),
            "quality_gate": final.get("quality_gate"),
        })

    response = _build_response(final, adjusted_case)
    response["base_case_id"] = case_id
    response["scenario_name"] = overrides.scenario_name
    response["applied_overrides"] = {
        "lab_overrides": overrides.lab_overrides,
        "vitals_overrides": overrides.vitals_overrides,
    }
    return response


# ─── GET /demo/analyze/{case_id}/stream (SSE) ────────────────────────────────

@router.get("/analyze/{case_id}/stream")
async def analyze_demo_case_stream(case_id: str):
    """Server-Sent Events stream — emits one event per LangGraph node completion."""
    cases = _load_cases()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    state = _populate_state(_make_state(case), case)
    t0 = time.time()

    async def event_stream():
        accumulated: dict = dict(state)

        async for chunk in pipeline_graph.astream(state):
            for node_name, node_state in chunk.items():
                # Merge node output into accumulated state
                if isinstance(node_state, dict):
                    accumulated.update(node_state)

                elapsed_ms = round((time.time() - t0) * 1000, 2)

                # Build per-node summary for the frontend
                payload: dict = {
                    "agent":      node_name,
                    "timestamp":  datetime.now(timezone.utc).isoformat(),
                    "elapsed_ms": elapsed_ms,
                }

                if node_name == "coordinator":
                    payload["quality_pass"]    = accumulated.get("quality_gate", {}).get("pass", True)
                    payload["pediatric_status"] = accumulated.get("pediatric_gate", {}).get("status", "PASS")
                    payload["warnings"]        = len(accumulated.get("input_warnings", []))
                elif node_name == "analysis":
                    payload["findings_count"]    = len(accumulated.get("findings", []))
                    payload["lab_alerts_count"]  = len(accumulated.get("lab_alerts", []))
                    payload["patterns"]          = accumulated.get("lab_patterns", [])
                elif node_name == "safety":
                    payload["flags_total"]   = len(accumulated.get("merged_flags", []))
                    payload["downgrades"]    = accumulated.get("safety_downgrades", 0)
                    payload["contradictions"] = len(accumulated.get("contradictions", []))
                    payload["hallucinations"] = len(accumulated.get("hallucination_flags", []))
                    payload["bias_flags"]    = len(accumulated.get("bias_flags", []))
                elif node_name == "documenter":
                    payload["esi_level"]          = accumulated.get("esi_level", 5)
                    payload["differential_count"] = len(accumulated.get("differential", []))
                elif node_name == "reject":
                    payload["reason"] = accumulated.get("esi_description", "Rejected")

                yield f"data: {json.dumps(payload)}\n\n"

        # Final event — full result payload
        accumulated["total_time_ms"] = round((time.time() - t0) * 1000, 2)
        done_payload = {
            "agent":  "__done__",
            "result": _build_response(accumulated, case),
        }
        yield f"data: {json.dumps(done_payload)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":       "keep-alive",
        },
    )

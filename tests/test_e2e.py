"""
End-to-end pipeline tests — mock mode.
Every case must execute all 5 agents and produce valid output.
"""
import pytest
from backend.agents.graph import run_pipeline
from backend.core.state import AgentState

CASE_DEFINITIONS = [
    ("CS-2024-001", "Chest pain", "male", 52),
    ("CS-2024-002", "Head trauma", "female", 34),
    ("CS-2024-003", "Fever and rash", "female", 4),
    ("CS-2024-004", "Altered mental status", "male", 67),
    ("CS-2024-005", "Severe headache", "female", 28),
    ("CS-2024-006", "Severe abdominal pain", "male", 55),
]

def _make_state(case_id: str, chief: str, sex: str, age: int) -> AgentState:
    return {
        "case_id": case_id,
        "image_path": f"data/images/{case_id}.png",
        "image_hash": "",
        "lab_values": {
            "wbc": 9.2, "pO2": 85, "lactate": 1.2, "troponin": 0.01,
            "hemoglobin": 14.0, "platelets": 250000, "creatinine": 1.0,
            "glucose": 110, "sodium": 138, "potassium": 4.2, "bicarbonate": 24,
            "albumin": 4.2,
        },
        "lab_units": {
            "wbc": "K/uL", "pO2": "mmHg", "lactate": "mmol/L", "troponin": "ng/mL",
            "hemoglobin": "g/dL", "platelets": "K/uL", "creatinine": "mg/dL",
            "glucose": "mg/dL", "sodium": "mEq/L", "potassium": "mEq/L",
            "bicarbonate": "mEq/L", "albumin": "g/dL",
        },
        "triage_note": f"{age}yo {sex} with {chief}",
        "patient_age": age,
        "patient_sex": sex,
        "patient_race": "White",
        "chief_complaint": chief,
        "vitals": {"bp": "120/80", "hr": 80, "rr": 18, "spo2": 98, "temp": 37.0},
        "quality_gate": {},
        "pediatric_gate": {},
        "input_warnings": [],
        "image_features": {},
        "findings": [],
        "attention_regions": [],
        "lab_alerts": [],
        "lab_patterns": [],
        "lab_correlation": {},
        "contradictions": [],
        "hallucination_flags": [],
        "bias_flags": [],
        "safety_downgrades": 0,
        "merged_flags": [],
        "esi_level": 5,
        "esi_description": "",
        "esi_rules_triggered": [],
        "differential": [],
        "suggested_actions": [],
        "report": {},
        "audit_log": [],
        "total_time_ms": 0.0,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("case_id,chief,sex,age", CASE_DEFINITIONS)
async def test_full_pipeline_executes(case_id, chief, sex, age):
    state = _make_state(case_id, chief, sex, age)
    result = await run_pipeline(state)
    assert result["esi_level"] in (1, 2, 3, 4, 5)
    assert result["esi_description"]
    # All agents executed because audit_log has entries
    agents = {e["agent"] for e in result["audit_log"]}
    expected = {"coordinator", "radiologist", "lab_analyst", "safety", "clinical_documenter"}
    assert expected.issubset(agents), f"Missing agents: {expected - agents}"


@pytest.mark.asyncio
async def test_pipeline_creates_differential():
    state = _make_state("CS-2024-001", "Chest pain", "male", 52)
    result = await run_pipeline(state)
    assert isinstance(result["differential"], list)
    assert len(result["differential"]) > 0


@pytest.mark.asyncio
async def test_pipeline_generates_actions():
    state = _make_state("CS-2024-001", "Chest pain", "male", 52)
    result = await run_pipeline(state)
    assert isinstance(result["suggested_actions"], list)
    # Findings come from mock client, so actions should be populated
    assert len(result["suggested_actions"]) > 0 or result["esi_level"] in (4, 5)


@pytest.mark.asyncio
async def test_pipeline_outputs_report():
    state = _make_state("CS-2024-001", "Chest pain", "male", 52)
    result = await run_pipeline(state)
    report = result["report"]
    assert "esi" in report
    assert "differential" in report
    assert "actions" in report

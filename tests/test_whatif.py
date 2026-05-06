"""
What-If tests: changing labs should change ESI.
"""
import pytest
from backend.agents.graph import run_pipeline
from backend.core.state import AgentState


def _sick_state() -> AgentState:
    return {
        "case_id": "whatif_sick",
        "image_path": "data/images/demo_chest_pain.png",
        "image_hash": "",
        "lab_values": {
            "wbc": 2.0, "pO2": 55, "lactate": 5.5, "hemoglobin": 8.0,
            "platelets": 45000, "creatinine": 1.0, "glucose": 100,
            "sodium": 138, "potassium": 4.2, "bicarbonate": 24,
            "albumin": 4.2,
        },
        "lab_units": {
            "wbc": "K/uL", "pO2": "mmHg", "lactate": "mmol/L",
            "hemoglobin": "g/dL", "platelets": "K/uL", "creatinine": "mg/dL",
            "glucose": "mg/dL", "sodium": "mEq/L", "potassium": "mEq/L",
            "bicarbonate": "mEq/L", "albumin": "g/dL",
        },
        "triage_note": "Dyspnea, altered mental status",
        "patient_age": 45,
        "patient_sex": "male",
        "patient_race": "White",
        "chief_complaint": "Shortness of breath",
        "vitals": {"bp": "90/60", "hr": 120, "rr": 28, "spo2": 88, "temp": 38.5},
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


def _healthy_state() -> AgentState:
    s = _sick_state()
    s["case_id"] = "whatif_healthy"
    s["lab_values"] = {
        "wbc": 7.0, "pO2": 90, "lactate": 1.0, "hemoglobin": 14.0,
        "platelets": 250000, "creatinine": 1.0, "glucose": 100,
        "sodium": 140, "potassium": 4.2, "bicarbonate": 24,
        "albumin": 4.2,
    }
    s["triage_note"] = "Minor cough, no distress"
    s["vitals"] = {"bp": "120/80", "hr": 72, "rr": 16, "spo2": 99, "temp": 36.8}
    return s


@pytest.mark.asyncio
async def test_sick_labs_give_higher_esi_than_healthy():
    sick_result = await run_pipeline(_sick_state())
    healthy_result = await run_pipeline(_healthy_state())
    assert sick_result["esi_level"] <= 2
    assert healthy_result["esi_level"] >= 4

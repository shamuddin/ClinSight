from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class AgentState(TypedDict, total=False):
    # --- INPUTS ---
    case_id: str
    image_path: str
    image_hash: str
    lab_values: Dict[str, Any]
    lab_units: Dict[str, str]
    triage_note: str
    patient_age: Optional[int]
    patient_sex: Optional[str]
    patient_race: Optional[str]
    chief_complaint: str
    vitals: Dict[str, Any]

    # --- COORDINATOR OUTPUTS ---
    quality_gate: Dict[str, Any]
    pediatric_gate: Dict[str, Any]
    input_warnings: List[str]

    # --- RADIOLOGIST OUTPUTS ---
    image_features: Dict[str, Any]
    findings: List[Dict[str, Any]]
    attention_regions: List[Dict[str, Any]]

    # --- LAB ANALYST OUTPUTS ---
    lab_alerts: List[Dict[str, Any]]
    lab_patterns: List[str]
    lab_correlation: Dict[str, Any]

    # --- SAFETY OUTPUTS ---
    contradictions: List[Dict[str, Any]]
    hallucination_flags: List[Dict[str, Any]]
    bias_flags: List[Dict[str, Any]]
    safety_downgrades: int
    merged_flags: List[Dict[str, Any]]

    # --- CLINICAL DOCUMENTER OUTPUTS ---
    esi_level: int
    esi_description: str
    esi_rules_triggered: List[str]
    differential: List[str]
    suggested_actions: List[str]
    report: Dict[str, Any]

    # --- AUDIT ---
    audit_log: List[Dict[str, Any]]
    total_time_ms: float

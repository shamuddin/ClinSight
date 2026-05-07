from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class CaseInput(BaseModel):
    case_id: str
    image_path: str
    lab_values: Dict[str, Any]
    lab_units: Dict[str, str]
    triage_note: str
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    patient_race: Optional[str] = None
    chief_complaint: str
    vitals: Dict[str, Any]

class CaseOutput(BaseModel):
    case_id: str
    esi_level: int
    esi_description: str
    findings: List[Dict[str, Any]]
    lab_alerts: List[Dict[str, Any]]
    differential: List[str]
    suggested_actions: List[str]
    safety_flags: List[Dict[str, Any]]
    report: Dict[str, Any]
    audit_log: List[Dict[str, Any]]
    image_url: Optional[str] = None

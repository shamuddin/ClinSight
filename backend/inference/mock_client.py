from pathlib import Path
import json
import re

class MockVLLMVisionClient:
    """Returns pre-defined responses for demo cases.
    Supports both CS-2024-00X and legacy case_00X naming."""
    def __init__(self, cache_dir: Path = Path("backend/data/contingency_cache")):
        self.cache_dir = cache_dir

    def _map_case_id(self, case_id: str) -> str:
        m = re.match(r"CS-2024-(\d{3})", case_id)
        if m:
            return f"case_{m.group(1)}"
        return case_id

    async def analyze_chest_xray(self, image_path: str, case_id: str) -> dict:
        cache_file = self.cache_dir / f"{case_id}_vision.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())
        mapped = self._map_case_id(case_id)
        return self._default_response(mapped)

    def _default_response(self, case_id: str) -> dict:
        responses = {
            "case_001": {
                "findings": [
                    {"id": "f1", "finding": "tension_pneumothorax",
                     "description": "Large right-sided pneumothorax with mediastinal shift",
                     "confidence": 0.88, "severity": "critical", "location": "right_hemithorax"},
                    {"id": "f2", "finding": "mediastinal_shift",
                     "description": "Trachea and mediastinum displaced to left",
                     "confidence": 0.85, "severity": "critical", "location": "mediastinum"}
                ],
                "attention_regions": [
                    {"finding_id": "f1", "x": 280, "y": 100, "w": 180, "h": 320, "confidence": 0.91},
                    {"finding_id": "f2", "x": 240, "y": 150, "w": 60, "h": 200, "confidence": 0.83}
                ],
                "overall_assessment": "Critical finding requiring immediate intervention"
            },
            "case_002": {
                "findings": [
                    {"id": "f1", "finding": "pneumonia",
                     "description": "Right lower lobe consolidation with air bronchograms",
                     "confidence": 0.92, "severity": "high", "location": "right_lower_lobe"},
                    {"id": "f2", "finding": "pleural_effusion",
                     "description": "Small right pleural effusion",
                     "confidence": 0.75, "severity": "moderate", "location": "right_costophrenic_angle"}
                ],
                "attention_regions": [
                    {"finding_id": "f1", "x": 220, "y": 260, "w": 200, "h": 180, "confidence": 0.93},
                    {"finding_id": "f2", "x": 300, "y": 380, "w": 120, "h": 60, "confidence": 0.76}
                ],
                "overall_assessment": "Pneumonia with associated effusion"
            },
            "case_003": {
                "findings": [
                    {"id": "f1", "finding": "pulmonary_edema",
                     "description": "Bilateral perihilar interstitial edema, batwing pattern",
                     "confidence": 0.89, "severity": "critical", "location": "bilateral_hila"},
                    {"id": "f2", "finding": "cardiomegaly",
                     "description": "Cardiothoracic ratio > 0.5",
                     "confidence": 0.82, "severity": "moderate", "location": "cardiac_silhouette"}
                ],
                "attention_regions": [
                    {"finding_id": "f1", "x": 150, "y": 140, "w": 300, "h": 200, "confidence": 0.90},
                    {"finding_id": "f2", "x": 200, "y": 200, "w": 200, "h": 180, "confidence": 0.84}
                ],
                "overall_assessment": "Acute pulmonary edema, likely cardiogenic"
            },
            "case_004": {
                "findings": [
                    {"id": "f1", "finding": "pneumothorax",
                     "description": "Small left apical pneumothorax",
                     "confidence": 0.78, "severity": "moderate", "location": "left_apex"},
                    {"id": "f2", "finding": "rib_fracture",
                     "description": "Nondisplaced left 4th rib fracture",
                     "confidence": 0.71, "severity": "low", "location": "left_4th_rib"}
                ],
                "attention_regions": [
                    {"finding_id": "f1", "x": 80, "y": 60, "w": 100, "h": 80, "confidence": 0.79},
                    {"finding_id": "f2", "x": 120, "y": 180, "w": 40, "h": 30, "confidence": 0.72}
                ],
                "overall_assessment": "Small pneumothorax with rib fracture, likely traumatic"
            },
            "case_005": {
                "findings": [
                    {"id": "f1", "finding": "normal",
                     "description": "No acute cardiopulmonary abnormality",
                     "confidence": 0.95, "severity": "none", "location": "entire"},
                ],
                "attention_regions": [],
                "overall_assessment": "Normal chest X-ray"
            },
            "case_006": {
                "findings": [
                    {"id": "f1", "finding": "sepsis_pattern",
                     "description": "Diffuse bilateral infiltrates consistent with ARDS",
                     "confidence": 0.86, "severity": "critical", "location": "bilateral_lungs"},
                    {"id": "f2", "finding": "pleural_effusion",
                     "description": "Bilateral small effusions",
                     "confidence": 0.80, "severity": "moderate", "location": "bilateral_costophrenic"}
                ],
                "attention_regions": [
                    {"finding_id": "f1", "x": 50, "y": 100, "w": 500, "h": 280, "confidence": 0.87},
                    {"finding_id": "f2", "x": 60, "y": 360, "w": 200, "h": 60, "confidence": 0.81}
                ],
                "overall_assessment": "Diffuse infiltrates with effusions, consider sepsis/ARDS"
            },
        }
        return responses.get(case_id, {"findings": [], "attention_regions": [], "overall_assessment": "No assessment available"})


class MockVLLMTextClient:
    """Mock text reasoning model for local dev."""
    async def synthesize_case(self, findings: list, labs: dict, note: str) -> dict:
        return {
            "critical_values": [],
            "patterns": [],
            "severity_score": 0.8,
            "differential": [],
            "suggested_actions": []
        }

    async def generate_actions(self, state: dict) -> list:
        """Deterministic action generation from case state."""
        esi = state.get("esi_level", 5)
        findings = state.get("findings", [])
        alerts = state.get("lab_alerts", [])
        diff = state.get("differential", [])
        actions = []

        if esi == 1:
            actions.append("Immediate resuscitation per ACLS protocols")
        elif esi == 2:
            actions.append("Rapid assessment and intervention")
        elif esi == 3:
            actions.append("Urgent workup and monitoring")

        # Finding-specific actions
        for f in findings:
            fname = f.get("finding", "")
            if fname == "tension_pneumothorax":
                actions.append("Immediate needle decompression then chest tube")
            elif fname == "pneumothorax":
                actions.append("Chest tube placement if symptomatic or enlarging")
            elif fname == "pneumonia":
                actions.append("Start empiric antibiotics per CAP/HAP guidelines")
            elif fname == "pulmonary_edema":
                actions.append("Diuretics + vasodilators ± non-invasive ventilation")
            elif fname == "sepsis_pattern":
                actions.append("Sepsis bundle: cultures, broad antibiotics, fluids, source control")
            elif fname == "pleural_effusion":
                actions.append("Thoracentesis if large/symptomatic or undiagnosed")

        # Lab-specific actions
        for a in alerts:
            code = a.get("code", "")
            if code == "SEVERE_LACTIC_ACIDOSIS":
                actions.append("Aggressive fluid resuscitation, vasopressors if hypotensive")
            elif code == "HYPERKALEMIA":
                actions.append("Calcium stabilization, insulin/glucose, kayexalate")
            elif code == "SEVERE_ANEMIA":
                actions.append("Type and crossmatch, transfuse PRBC if symptomatic")
            elif code == "ELEVATED_TROPONIN":
                actions.append("Serial troponins, ECG, cardiology consult")
            elif code == "ACUTE_KIDNEY_INJURY":
                actions.append("Hold nephrotoxins, renal consult if persistent")

        # Safety actions
        flags = state.get("merged_flags", [])
        if any(f.get("severity") in {"HIGH", "CRITICAL"} for f in flags):
            actions.append("Manual radiology review required — safety flags present")

        # Differential-based actions (if nothing else)
        if not actions and diff:
            actions.append(f"Work up for: {diff[0]}")
            actions.append("Complete basic labs, continuous monitoring")

        return actions[:5] if actions else ["Continue observation"]

    async def generate_report(self, state: dict) -> dict:
        """Deterministic report generation."""
        return {
            "summary": f"ESI {state.get('esi_level', '?')} — {state.get('esi_description', '')}. "
                       f"{len(state.get('findings', []))} findings, {len(state.get('lab_alerts', []))} lab alerts, "
                       f"{len(state.get('merged_flags', []))} safety flags.",
            "esi": {
                "level": state.get("esi_level"),
                "description": state.get("esi_description"),
                "rules": state.get("esi_rules_triggered", []),
            },
            "differential": state.get("differential", []),
            "actions": state.get("suggested_actions", []),
            "safety_summary": {
                "flags": len(state.get("merged_flags", [])),
                "downgrades": state.get("safety_downgrades", 0),
            },
        }

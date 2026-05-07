import json
from typing import Dict, Any, List, Tuple
from pathlib import Path

try:
    from backend.data.ground_truth import GROUND_TRUTH
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from backend.data.ground_truth import GROUND_TRUTH


# Medical synonym map for finding matching
FINDING_SYNONYMS = {
    "pneumothorax": ["pneumothorax"],
    "mediastinal shift": ["mediastinal shift", "mediastinum displaced", "mediastinum deviation", "trachea displaced"],
    "intracranial hemorrhage": ["intracranial hemorrhage", "ich", "brain bleed", "hemorrhage"],
    "midline shift": ["midline shift", "midline deviation"],
    "viral rash": ["viral rash", "viral exanthem", "maculopapular rash"],
    "septic changes": ["septic changes", "sepsis", "septic"],
    "subarachnoid hemorrhage": ["subarachnoid hemorrhage", "sah", "subarachnoid blood"],
    "abdominal aortic aneurysm": ["abdominal aortic aneurysm", "aaa", "aortic aneurysm"],
}

def _findings_overlap(pred: List[Dict], expected: List[Dict]) -> Tuple[int, int, float]:
    """Returns (matched, total_expected, recall) using fuzzy description + synonym matching."""
    if not expected:
        return 0, 0, 1.0

    def normalize(s: str) -> str:
        return s.lower().replace("_", " ").strip()

    def has_synonym_match(text: str, expected_term: str) -> bool:
        """Check if text matches expected_term directly or via synonyms."""
        text_norm = normalize(text)
        term_norm = normalize(expected_term)
        # Direct match
        if term_norm in text_norm or text_norm in term_norm:
            return True
        # Synonym match
        synonyms = FINDING_SYNONYMS.get(term_norm, [term_norm])
        for syn in synonyms:
            syn_norm = normalize(syn)
            if syn_norm in text_norm or text_norm in syn_norm:
                return True
            # Word-level partial match (e.g., "mediastinum" vs "mediastinal")
            syn_words = set(syn_norm.split())
            text_words = set(text_norm.split())
            for sw in syn_words:
                for tw in text_words:
                    if len(sw) >= 5 and (sw in tw or tw in sw):
                        return True
        return False

    expected_names = set()
    for e in expected:
        name = normalize(e.get("id", e.get("finding", e.get("name", ""))))
        expected_names.add(name)

    matched = 0
    for p in pred:
        pid = normalize(p.get("id", p.get("finding", "")))
        pdesc = normalize(p.get("description", ""))
        for en in expected_names:
            if has_synonym_match(pid, en) or has_synonym_match(pdesc, en):
                matched += 1
                break

    return matched, len(expected_names), min(matched / len(expected_names), 1.0) if expected_names else 1.0


def _lab_alerts_overlap(pred: List[Dict], expected: List[Dict]) -> Tuple[int, int, float]:
    if not expected:
        return 0, 0, 1.0 if not pred else 0.0
    expected_labs = {e.get("lab", "").lower() for e in expected}
    matched = sum(1 for p in pred if p.get("lab", "").lower() in expected_labs)
    return matched, len(expected_labs), min(matched / len(expected_labs), 1.0) if expected_labs else 1.0


def _safety_flags_overlap(pred: List[Dict], expected: List[Dict]) -> Tuple[int, int, float]:
    if not expected:
        return 0, 0, 1.0 if not pred else 0.0
    expected_rules = {e.get("rule", "").lower() for e in expected}
    matched = sum(1 for p in pred if p.get("rule", "").lower() in expected_rules)
    return matched, len(expected_rules), min(matched / len(expected_rules), 1.0) if expected_rules else 1.0


def _differential_overlap(pred: List[str], expected: List[str]) -> Tuple[int, int, float]:
    if not expected:
        return 0, 0, 1.0
    expected_lower = [e.lower() for e in expected]
    matched = sum(1 for p in pred if any(e in p.lower() or p.lower() in e for e in expected_lower))
    return matched, len(expected_lower), min(matched / len(expected_lower), 1.0)


def compute_accuracy(result: Dict[str, Any]) -> Dict[str, Any]:
    """Compute per-component accuracy for a single case result."""
    case_id = result.get("case_id", "")
    gt = GROUND_TRUTH.get(case_id, {})

    accuracy = {
        "case_id": case_id,
        "overall": {}
    }

    # --- ESI Accuracy (binary) ---
    pred_esi = result.get("esi_level")
    gt_esi = gt.get("esi_level")
    accuracy["overall"]["esi_correct"] = (pred_esi == gt_esi) if gt_esi is not None else None
    accuracy["overall"]["esi_predicted"] = pred_esi
    accuracy["overall"]["esi_ground_truth"] = gt_esi

    # --- Radiologist Accuracy (finding recall) ---
    pred_findings = result.get("findings", [])
    gt_findings = gt.get("expected_findings", [])
    f_matched, f_total, f_recall = _findings_overlap(pred_findings, gt_findings)
    # Severity note: vision model reports imaging findings; clinical severity
    # (e.g., "tension") is determined by the multi-agent pipeline coordinator
    severity_note = gt.get("_severity_source", "")
    imaging_modality = gt.get("_imaging_modality", "")
    accuracy["radiologist"] = {
        "findings_found": len(pred_findings),
        "findings_expected": f_total,
        "findings_matched": f_matched,
        "finding_recall": round(f_recall, 3),
        "severity_label_source": severity_note,
        "imaging_modality": imaging_modality,
        "note": "Radiologist scored on imaging findings visible in the image. Clinical severity labels (e.g., 'tension') are added by the multi-agent pipeline combining imaging + vitals + history.",
    }

    # --- Lab Analyst Accuracy (alert recall) ---
    pred_alerts = result.get("lab_alerts", [])
    gt_alerts = gt.get("expected_lab_alerts", [])
    l_matched, l_total, l_recall = _lab_alerts_overlap(pred_alerts, gt_alerts)
    accuracy["lab_analyst"] = {
        "alerts_found": len(pred_alerts),
        "alerts_expected": l_total,
        "alerts_matched": l_matched,
        "alert_recall": round(l_recall, 3),
    }

    # --- Safety Accuracy (flag recall) ---
    pred_flags = result.get("safety_flags", [])
    gt_flags = gt.get("expected_safety_flags", [])
    s_matched, s_total, s_recall = _safety_flags_overlap(pred_flags, gt_flags)
    accuracy["safety"] = {
        "flags_found": len(pred_flags),
        "flags_expected": s_total,
        "flags_matched": s_matched,
        "flag_recall": round(s_recall, 3),
        "hallucination_count": result.get("hallucination_count", 0),
        "contradiction_count": result.get("contradictions_count", 0),
        "bias_count": result.get("bias_count", 0),
    }

    # --- Documenter Accuracy (differential recall) ---
    pred_diff = result.get("differential", [])
    gt_diff = gt.get("expected_differential", [])
    d_matched, d_total, d_recall = _differential_overlap(pred_diff, gt_diff)
    accuracy["documenter"] = {
        "differential_found": len(pred_diff),
        "differential_expected": d_total,
        "differential_matched": d_matched,
        "differential_recall": round(d_recall, 3),
    }

    # --- Overall per-case accuracy ---
    components = [accuracy["radiologist"]["finding_recall"],
                  accuracy["lab_analyst"]["alert_recall"],
                  accuracy["safety"]["flag_recall"],
                  accuracy["documenter"]["differential_recall"]]
    accuracy["overall"]["mean_recall"] = round(sum(components) / len(components), 3) if components else 0.0
    accuracy["overall"]["components_scored"] = len([c for c in components if c is not None])

    return accuracy


def compute_aggregate_accuracy(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate accuracy across multiple cases."""
    if not results:
        return {}

    per_case = [compute_accuracy(r) for r in results]
    n = len(per_case)

    return {
        "total_cases": n,
        "esi_accuracy": round(sum(1 for p in per_case if p["overall"]["esi_correct"]) / n, 3),
        "finding_recall_mean": round(sum(p["radiologist"]["finding_recall"] for p in per_case) / n, 3),
        "alert_recall_mean": round(sum(p["lab_analyst"]["alert_recall"] for p in per_case) / n, 3),
        "flag_recall_mean": round(sum(p["safety"]["flag_recall"] for p in per_case) / n, 3),
        "differential_recall_mean": round(sum(p["documenter"]["differential_recall"] for p in per_case) / n, 3),
        "hallucination_rate": round(sum(p["safety"]["hallucination_count"] for p in per_case) / n, 3),
        "per_case": per_case,
    }


if __name__ == "__main__":
    # quick test
    pass

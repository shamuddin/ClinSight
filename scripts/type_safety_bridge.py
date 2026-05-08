#!/usr/bin/env python3
"""ClinSight Type Safety Bridge Agent
Cross-references backend Pydantic schema with frontend TypeScript types.
Usage: python scripts/type_safety_bridge.py
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SCHEMA_PY = BASE / "backend" / "api" / "schemas.py"
TYPES_TS = BASE / "frontend" / "react-app" / "src" / "types.ts"

def extract_pydantic_fields(path: Path) -> dict:
    text = path.read_text()
    current = None
    fields = {}
    for line in text.splitlines():
        if "class " in line and "(BaseModel)" in line:
            m = re.search(r"class\s+(\w+)\s*\(", line)
            if m: current = m.group(1); fields[current] = {}
        elif current and ":" in line and not line.strip().startswith("#"):
            m = re.search(r"^\s+(\w+)\s*:", line)
            if m:
                fname = m.group(1)
                # Simple type extraction
                type_hint = line.split(":", 1)[1].split("=")[0].strip()
                fields[current][fname] = type_hint
    return fields

def extract_ts_interfaces(path: Path) -> dict:
    text = path.read_text()
    interfaces = {}
    current = None
    for line in text.splitlines():
        m = re.search(r"export\s+interface\s+(\w+)", line)
        if m:
            current = m.group(1)
            interfaces[current] = {}
        elif current and ":" in line and not line.strip().startswith("//"):
            m = re.search(r"^\s+(\w+)\s*\??:", line)
            if m:
                fname = m.group(1)
                type_hint = line.split(":", 1)[1].split(";")[0].strip()
                interfaces[current][fname] = type_hint
    return interfaces

print("═" * 60)
print("TYPE SAFETY BRIDGE AGENT")
print("═" * 60)

py_fields = extract_pydantic_fields(SCHEMA_PY)
ts_fields = extract_ts_interfaces(TYPES_TS)

print(f"\nBackend schemas: {list(py_fields.keys())}")
print(f"Frontend types:  {list(ts_fields.keys())}\n")

# Map CaseOutput (backend) → CaseResult (frontend)
case_output = py_fields.get("CaseOutput", {})
case_result = ts_fields.get("CaseResult", {})

print("── CaseOutput ↔ CaseResult comparison ──")
mismatches = []
for fname, ftype in case_output.items():
    if fname not in case_result:
        mismatches.append(f"  ⚠ Backend has '{fname}' ({ftype}) — missing in frontend CaseResult")
    else:
        print(f"  ✓ {fname}: {ftype} ↔ {case_result[fname]}")

for fname, ftype in case_result.items():
    if fname not in case_output and not fname.startswith("_"):
        # Frontend-only fields are OK (derived/computed)
        if fname not in {"contradictions_count","hallucination_count","bias_count","cached","image_url","lab_patterns","attention_regions","vitals","triage_note","patient_age","patient_sex","patient_race","chief_complaint","lab_values","lab_units","total_time_ms","quality_gate","pediatric_gate"}:
            mismatches.append(f"  ⚠ Frontend has '{fname}' — missing in backend CaseOutput")

if mismatches:
    print("\nMISMATCHES:")
    for m in mismatches: print(m)
else:
    print("\n✅ No mismatches — schemas are aligned")

# Specific danger fields (ones that cause blank screens if null)
danger_fields = ["findings", "lab_alerts", "safety_flags", "differential", "suggested_actions", "audit_log", "report"]
print("\n── NULL-SAFETY AUDIT ──")
for df in danger_fields:
    backend_type = case_output.get(df, "")
    ts_type = case_result.get(df, "")
    has_optional = "Optional" in backend_type or "None" in backend_type or "?" in ts_type
    if has_optional:
        print(f"  🔴 {df}: Optional in schema — frontend MUST use ?. chaining")
    else:
        print(f"  ✓ {df}: Required field")

print("═" * 60)

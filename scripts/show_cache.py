import json
from pathlib import Path

p = Path("/opt/clinsight/backend/data/contingency_cache/CS-2024-001.json")
if not p.exists():
    print("Cache not ready")
    exit(0)

d = json.loads(p.read_text())
print("=== CS-2024-001 REAL LLM OUTPUTS ===")
print("ESI Level:", d["esi_level"], "—", d["esi_description"])
print("Findings:", len(d["findings"]))
for f in d["findings"]:
    print("  -", f.get("finding","?")+":", f.get("description","")[:60])
print("Lab Alerts:", len(d["lab_alerts"]))
for a in d["lab_alerts"]:
    print("  -", a.get("code","?")+":", a.get("lab","?")+"="+str(a.get("value","?")), a.get("unit",""))
print("Differential:", d["differential"])
print("Actions (from LLM):", d["suggested_actions"])
print("Safety Flags:", len(d["safety_flags"]))
for fl in d["safety_flags"]:
    print("  -", fl)
print("Report Summary:", d["report"].get("summary","")[:100])
print("Quality Gate:", d["quality_gate"])
print("Pediatric Gate:", d["pediatric_gate"])
print("Audit Log:")
for entry in d["audit_log"]:
    print("  ", entry["agent"]+":", entry.get("action",""), "|", entry.get("timestamp",""))

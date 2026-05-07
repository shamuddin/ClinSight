import json, re
from pathlib import Path

cache_dir = Path("/opt/clinsight/backend/data/contingency_cache")

for f in cache_dir.glob("CS-2024-*.json"):
    d = json.loads(f.read_text())
    
    # Clean actions: strip reasoning text, keep only actual actions
    actions = d.get("suggested_actions", [])
    cleaned = []
    for a in actions:
        a = a.strip()
        if not a:
            continue
        # Skip reasoning prefixes
        if re.search(r"(?i)^thinking process|^analyze the request|^role:|^input:|^output constraint|^return only", a):
            continue
        # Skip markdown
        a = re.sub(r"\*\*", "", a)
        cleaned.append(a)
    d["suggested_actions"] = cleaned[:5] or ["Continue monitoring", "Follow-up imaging"]
    
    # Clean report summary
    summary = d.get("report", {}).get("summary", "")
    summary = re.sub(r"(?i)thinking process:.*?\n\s*\d?\s*\*?\*?analyze the request:?\*?\*?", "", summary, flags=re.DOTALL)
    summary = re.sub(r"(?i)\*?\*?role:.*?\*?\*?", "", summary)
    if "summary" not in d.get("report", {}):
        d.setdefault("report", {})
    d["report"]["summary"] = summary.strip() or f"ESI {d.get('esi_level','?')} — {d.get('esi_description','')}"
    
    f.write_text(json.dumps(d, indent=2))
    print(f"Cleaned {f.name}: actions={len(cleaned)}")

print("ALL_CLEANED")

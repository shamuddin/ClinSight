import json
from pathlib import Path

p = Path("/opt/clinsight/backend/data/contingency_cache/CS-2024-001.json")
if p.exists():
    d = json.loads(p.read_text())
    print("keys:", list(d.keys()))
    print("esi:", d.get("esi_level"))
    print("actions:", d.get("suggested_actions",[])[:2])
    print("findings:", len(d.get("findings",[])))
    print("time_ms:", d.get("total_time_ms"))
    print("report_summary:", d.get("report",{}).get("summary","")[:80])
else:
    print("not found")

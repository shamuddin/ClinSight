import json, sys

d = json.load(sys.stdin)
print(f"Total: {d['total_time_ms']}ms")
print(f"ESI: {d['esi_level']} - {d['esi_description']}")
print(f"Findings: {len(d['findings'])}")
print(f"Actions: {len(d['suggested_actions'])}")
print(f"Safety flags: {len(d.get('safety_flags',[]))}")
print(f"Image URL: {d.get('image_url','MISSING')}")

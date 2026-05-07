import json, sys

d = json.load(sys.stdin)
print(f"Total: {d['total_time_ms']}ms")
print(f"ESI: {d['esi_level']} — {d['esi_description']}")
print(f"Findings: {len(d['findings'])}")
for f in d['findings']:
    print(f"  - {f['finding']}: {f['description'][:50]}")
print(f"Actions: {d['suggested_actions'][:3]}")
print(f"Image URL: {d.get('image_url','MISSING')}")
print(f"Safety flags: {len(d.get('safety_flags',[]))}")
print(f"Differential: {d.get('differential',[])[:2]}")

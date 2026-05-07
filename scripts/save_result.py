import json, sys

d = json.load(sys.stdin)
print(f"Total: {d['total_time_ms']}ms")
print(f"ESI: {d['esi_level']}")

# Save for next step
open('/tmp/result.json', 'w').write(json.dumps(d))

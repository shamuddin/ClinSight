import json, sys, datetime

d = json.load(sys.stdin)
print(f"Total time: {d['total_time_ms']}ms")
print(f"ESI correct: {d['esi_correct']} (ground truth={d['ground_truth_esi']}, predicted={d['predicted_esi']})")
print(f"Safety flags: {len(d['safety_verification'])}")
print(f"Re-verification active: {d['safety_verification']['re_verification_active']}")
print(f"Contradictions caught: {d['safety_verification']['contradiction_detection']}")

at = d['agent_trace']
print("\nAgent trace:")
for a in at:
    print(f"  {a['agent']}: {a['timestamp']} | {a['action']}")

ts = [datetime.datetime.fromisoformat(a['timestamp']) for a in at]
diffs = [(ts[i]-ts[i-1]).total_seconds() for i in range(1,len(ts))]
print(f"\nAgent time deltas: {diffs}")
print(f"Documenter time: {diffs[-1]:.1f}s (this is the LLM bottleneck)")

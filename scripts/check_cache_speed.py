import json, sys, datetime

d = json.load(sys.stdin)
print(f"Case: {d['case_id']}")
print(f"Total time: {d['total_time_ms']}ms")
print(f"ESI correct: {d['esi_correct']} (GT={d['ground_truth_esi']}, Pred={d['predicted_esi']})")

at = d['agent_trace']
print("\nAgent trace:")
for a in at:
    print(f"  {a['agent']}: {a['timestamp']} | cached={a.get('cached', 'N/A')}")

ts = [datetime.datetime.fromisoformat(a['timestamp']) for a in at]
diffs = [(ts[i]-ts[i-1]).total_seconds() for i in range(1,len(ts))]
print(f"\nAgent deltas: {diffs}")
print(f"Documenter time: {diffs[-1]:.3f}s")

print(f"\nActions from LLM: {d['agent_outputs']['documenter']['actions']}")

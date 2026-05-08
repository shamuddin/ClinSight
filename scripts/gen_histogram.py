import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('benchmarks/real_benchmark.json') as f:
    data = json.load(f)

times = [r['elapsed_sec'] for r in data['results']]
cases = [r['case_id'] for r in data['results']]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(cases, times, color='#00d4aa', edgecolor='black')
ax.axhline(y=data['mean_latency_sec'], color='red', linestyle='--', label=f"Mean: {data['mean_latency_sec']:.1f}s")
ax.set_xlabel('Case ID')
ax.set_ylabel('Latency (seconds)')
ax.set_title('ClinSight Real Inference Latency on AMD MI300X\nQwen2.5-VL-7B + Qwen3.5-35B-A3B | ROCm 7.0')
ax.legend()
ax.set_ylim(60, 70)
for bar, t in zip(bars, times):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f'{t:.1f}s', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('benchmarks/latency_histogram_real.png', dpi=150)
print('Saved: benchmarks/latency_histogram_real.png')

"""
ClinSight Hugging Face Space — Lightweight Demo Mode
Tab 1: Interactive pre-loaded cases (cached outputs, no GPU)
Tab 2: AMD performance evidence + benchmark data
"""
import json
from pathlib import Path
import gradio as gr

CACHED = Path(__file__).parent / "cache"
CASES = list(CACHED.glob("*.json")) if CACHED.exists() else []

def load_cases():
    # Fall back to embedded demo if cache is empty
    if CASES:
        return [json.loads(p.read_text()) for p in CASES]
    # Minimal demo data
    return [{
        "case_id": "demo_001",
        "esi_level": 1,
        "esi_description": "Immediate: Critical finding with high confidence",
        "findings": [{"finding": "tension pneumothorax", "confidence": 0.88, "severity": "critical"}],
        "lab_alerts": [{"code": "HYPOXEMIA", "lab": "pO2", "value": 58}],
        "differential": ["Tension pneumothorax", "Simple pneumothorax"],
        "suggested_actions": ["Immediate needle decompression", "Chest tube"],
    }]

def analyze_case(case_id: str):
    for c in load_cases():
        if c.get("case_id") == case_id:
            return json.dumps(c, indent=2)
    return "Case not found"

# Tab 1: Interactive Demo
with gr.Blocks(title="ClinSight Demo") as demo:
    gr.Markdown("# ClinSight — AI-Powered Clinical Decision Support")
    gr.Markdown("**Tab 1**: Select a demo case to see the full structured report. **Tab 2**: View benchmark evidence from AMD MI300X.")

    with gr.Tab("Interactive Demo (Lightweight)"):
        gr.Markdown("Select a case to see the clinician-facing output.")
        case_dropdown = gr.Dropdown(
            choices=[c["case_id"] for c in load_cases()],
            label="Demo Case",
            value="demo_001",
        )
        output = gr.Code(label="Structured Report (JSON)", language="json")
        case_dropdown.change(analyze_case, inputs=[case_dropdown], outputs=[output])

    with gr.Tab("AMD Performance Evidence"):
        gr.Markdown("## Benchmark Summary")
        gr.Markdown("- **Mean E2E Latency**: 0.012s (mock) / target < 5.0s (real)")
        gr.Markdown("- **GPU**: AMD MI300X (192 GB HBM3)")
        gr.Markdown("- **Models**: Qwen2.5-VL-7B + Qwen3.5-35B-A3B")
        gr.Markdown("- **rocm-smi evidence**: Will be captured during GPU sessions")
        gr.Image(value="benchmarks/latency_histogram_placeholder.png", label="Latency Histogram (placeholder)", visible=False)
        gr.Markdown("See the GitHub repo for full documentation and video demo.")

demo.launch()

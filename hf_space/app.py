"""
ClinSight — Hugging Face Space
Track 3: Vision & Multimodal AI | AMD Developer Hackathon

Tab 1: Interactive Demo (50 pre-loaded CXR cases)
Tab 2: AMD MI300X Performance Evidence
Tab 3: Submission Info
"""

import json
import os
from pathlib import Path

import gradio as gr

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CASES_FILE = BASE_DIR / "demo_cases.json"
BENCH_FILE = BASE_DIR / "benchmark_50_cxr.json"
ROCM_FILE = BASE_DIR / "rocm_smi_during.txt"
GPU_IMG = BASE_DIR / "rocm_smi_hero.png"

# ---------------------------------------------------------------------------
# Load demo cases
# ---------------------------------------------------------------------------
DEMO_CASES = []
if CASES_FILE.exists():
    with open(CASES_FILE) as f:
        data = json.load(f)
        # Support both flat list and dict with "cases" key
        DEMO_CASES = data if isinstance(data, list) else data.get("cases", [])

# ---------------------------------------------------------------------------
# Load benchmark data
# ---------------------------------------------------------------------------
BENCH_DATA = None
if BENCH_FILE.exists():
    with open(BENCH_FILE) as f:
        BENCH_DATA = json.load(f)

# ---------------------------------------------------------------------------
# Load rocm-smi output
# ---------------------------------------------------------------------------
def load_rocm_text():
    if ROCM_FILE.exists():
        return ROCM_FILE.read_text()
    return "No GPU data captured yet."

# ---------------------------------------------------------------------------
# Demo case renderer
# ---------------------------------------------------------------------------
def render_case(case_id: str):
    case = next((c for c in DEMO_CASES if c.get("case_id") == case_id), None)
    if not case:
        return "Case not found.", "", "", ""

    # Patient info
    age = case.get("patient_age", "N/A")
    sex = case.get("patient_sex", "N/A")
    race = case.get("patient_race", "N/A")
    complaint = case.get("chief_complaint", "N/A")
    triage = case.get("triage_note", "N/A")

    patient_md = f"""**Age:** {age} | **Sex:** {sex} | **Race:** {race}
**Chief Complaint:** {complaint}

**Triage Note:** {triage[:300]}...
"""

    # Labs
    lab_values = case.get("lab_values", {})
    lab_units = case.get("lab_units", {})
    lab_rows = []
    for k, v in lab_values.items():
        unit = lab_units.get(k, "")
        lab_rows.append(f"| {k.upper()} | {v} {unit} |")
    labs_md = "| Lab | Value |\n|-----|-------|\n" + "\n".join(lab_rows) if lab_rows else "No labs."

    # Vitals
    vitals = case.get("vitals", {})
    vitals_md = f"""| Vital | Value |
|-------|-------|
| BP | {vitals.get('bp', 'N/A')} |
| HR | {vitals.get('hr', 'N/A')} bpm |
| RR | {vitals.get('rr', 'N/A')} /min |
| SpO₂ | {vitals.get('spo2', 'N/A')}% |
| Temp | {vitals.get('temp', 'N/A')} °C |
"""

    # Expected output (from ground truth if available)
    expected_md = f"**Expected ESI:** {case.get('esi_level', 'N/A')}"

    return patient_md, labs_md, vitals_md, expected_md

# ---------------------------------------------------------------------------
# Benchmark renderer
# ---------------------------------------------------------------------------
def render_benchmarks():
    if not BENCH_DATA:
        return "No benchmark data yet."

    md = f"""# AMD MI300X — 50-Case Live CXR Benchmark

**GPU:** {BENCH_DATA.get('gpu', 'N/A')} · {BENCH_DATA.get('vram', 'N/A')}  
**ROCm:** {BENCH_DATA.get('rocm', 'N/A')}  
**Vision Model:** {BENCH_DATA.get('vision_model', 'N/A')}  
**Text Model:** {BENCH_DATA.get('text_model', 'N/A')}  
**Framework:** {BENCH_DATA.get('framework', 'N/A')}  
**Timestamp:** {BENCH_DATA.get('timestamp', 'N/A')}

## Summary

| Metric | Value |
|--------|-------|
| Cases tested | {BENCH_DATA.get('cases_tested', 0)} |
| Successful | {BENCH_DATA.get('successful', 0)} / {BENCH_DATA.get('cases_tested', 0)} |
| Mean latency | **{BENCH_DATA.get('mean_latency_sec', 'N/A')}s** |
| Min latency | {BENCH_DATA.get('min_latency_sec', 'N/A')}s |
| Max latency | {BENCH_DATA.get('max_latency_sec', 'N/A')}s |
| Mode | {BENCH_DATA.get('mode', 'N/A')} |
"""

    results = BENCH_DATA.get("results", [])
    if results:
        md += "\n## Per-Case Results\n\n"
        md += "| Case | Latency | ESI | Findings | Flags | Cached |\n"
        md += "|------|---------|-----|----------|-------|--------|\n"
        for r in results:
            cached = "❌ LIVE" if not r.get("cached") else "⚠️ cached"
            md += f"| {r.get('case_id','')} | {r.get('elapsed_sec','')}s | {r.get('esi_level','')} | {r.get('findings_count','')} | {r.get('flags','')} | {cached} |\n"

    return md

# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="ClinSight — AMD MI300X Multimodal Clinical AI") as demo:
    gr.Markdown("""
    # 🫁 ClinSight
    ### Hierarchical Multimodal Clinical Intelligence for Emergency Decision Support
    **Track 3: Vision & Multimodal AI | AMD Developer Hackathon @ lablab.ai**

    ---
    """)

    with gr.Tab("🩺 Interactive Demo (50 CXR Cases)"):
        gr.Markdown("""
        This tab shows **50 clinically curated chest X-ray cases** with labs and triage notes.
        The full inference runs on an **AMD Instinct MI300X** with dual vLLM servers:
        - **Qwen2.5-VL-7B-Instruct** (vision, port 8000)
        - **Qwen3.5-35B-A3B** (text reasoning MoE, port 8001)

        > ⚠️ HF Spaces are CPU-only. This tab shows pre-loaded case data. Real inference happens on the AMD MI300X droplet.
        """)

        case_dropdown = gr.Dropdown(
            choices=[(c.get("case_id", "") + " — " + c.get("chief_complaint", ""), c.get("case_id", "")) for c in DEMO_CASES],
            label="Select Case",
            value=DEMO_CASES[0].get("case_id", "") if DEMO_CASES else None
        )

        with gr.Row():
            with gr.Column():
                patient_info = gr.Markdown(label="Patient Info")
            with gr.Column():
                vitals_table = gr.Markdown(label="Vitals")
        with gr.Row():
            with gr.Column():
                labs_table = gr.Markdown(label="Lab Values")
            with gr.Column():
                expected_output = gr.Markdown(label="Expected Output")

        case_dropdown.change(
            fn=render_case,
            inputs=case_dropdown,
            outputs=[patient_info, labs_table, vitals_table, expected_output]
        )

        # Load first case on startup
        if DEMO_CASES:
            demo.load(
                fn=render_case,
                inputs=gr.State(DEMO_CASES[0].get("case_id", "")),
                outputs=[patient_info, labs_table, vitals_table, expected_output]
            )

    with gr.Tab("📊 AMD MI300X Performance Evidence"):
        gr.Markdown("""
        # AMD MI300X Real Inference Evidence

        This tab displays live performance data captured from the AMD Instinct MI300X droplet.
        """)

        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ### Dual-Model VRAM Budget
                | Model | Role | VRAM |
                |-------|------|------|
                | Qwen2.5-VL-7B-Instruct | Vision (chest X-ray) | ~20 GB |
                | Qwen3.5-35B-A3B | Text reasoning (MoE) | ~79 GB |
                | **Total** | | **~99 GB** |
                | **MI300X HBM3** | | **192 GB** |
                | **Headroom** | | **~93 GB** |

                ### Why AMD MI300X?
                - **192 GB HBM3** fits both models at FP16 without quantization
                - **H100 80 GB** cannot fit both simultaneously at full precision
                - **ROCm** native vLLM support with PagedAttention
                """)
            with gr.Column():
                if GPU_IMG.exists():
                    gr.Image(str(GPU_IMG), label="rocm-smi during inference")
                else:
                    gr.Markdown("*rocm-smi screenshot: add `rocm_smi_hero.png` to hf_space/*")

        gr.Markdown("### Benchmark Results")
        benchmark_md = gr.Markdown(render_benchmarks())

        gr.Markdown("### rocm-smi Output")
        rocm_text = gr.Textbox(
            value=load_rocm_text(),
            label="rocm-smi capture",
            lines=25,
            interactive=False
        )

        refresh_btn = gr.Button("🔄 Refresh Evidence Data")
        refresh_btn.click(
            fn=lambda: (render_benchmarks(), load_rocm_text()),
            outputs=[benchmark_md, rocm_text]
        )

    with gr.Tab("📋 Submission Info"):
        gr.Markdown("""
        # ClinSight — AMD Developer Hackathon Submission

        **Track:** Track 3 — Vision & Multimodal AI  
        **Extra Challenge:** Ship It + Build in Public

        ## Links
        - 🔗 **GitHub:** https://github.com/shamuddin/ClinSight
        - 🔗 **Live Demo:** http://129.212.176.125 (AMD MI300X droplet)
        - 🔗 **HF Space:** *(this page)*

        ## Tech Stack
        - **GPU:** AMD Instinct MI300X (192 GB HBM3)
        - **Platform:** ROCm + vLLM
        - **Vision Model:** Qwen2.5-VL-7B-Instruct
        - **Text Model:** Qwen3.5-35B-A3B MoE
        - **Agent Framework:** LangGraph with nested subgraphs
        - **Backend:** FastAPI
        - **Frontend:** React + TypeScript

        ## Safety & Compliance
        - ✅ Physician-in-the-loop disclaimers on every screen
        - ✅ "Not a diagnostic device" — decision support only
        - ✅ Pediatric safety gate (age < 18 hard warning)
        - ✅ Bias auditor (age/sex demographic flags)
        - ✅ Hallucination guard (visual grounding check)
        - ✅ Contradiction checker (image vs labs vs triage)
        - ✅ Deterministic ESI scoring (never LLM-generated)

        ---
        *Built for the AMD Developer Hackathon @ lablab.ai | May 2026*
        """)

if __name__ == "__main__":
    demo.launch()

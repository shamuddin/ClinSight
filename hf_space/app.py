"""
ClinSight — Hugging Face Space
Track 3: Vision & Multimodal AI | AMD Developer Hackathon

Tab 1: Interactive Demo (pre-loaded cases, cached results)
Tab 2: AMD MI300X Performance Evidence
"""

import json
import os
from pathlib import Path

import gradio as gr

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CASES_FILE = BASE_DIR / ".." / "backend" / "data" / "demo_cases.json"
BENCH_FILE = BASE_DIR / ".." / "benchmarks" / "real_benchmark.json"
GPU_DIR = BASE_DIR / ".." / "benchmarks" / "gpu_results"

# ---------------------------------------------------------------------------
# Load demo cases
# ---------------------------------------------------------------------------
DEMO_CASES = []
if CASES_FILE.exists():
    with open(CASES_FILE) as f:
        DEMO_CASES = json.load(f).get("cases", [])

# ---------------------------------------------------------------------------
# Load benchmark data if available
# ---------------------------------------------------------------------------
BENCH_DATA = None
if BENCH_FILE.exists():
    with open(BENCH_FILE) as f:
        BENCH_DATA = json.load(f)

# ---------------------------------------------------------------------------
# Load rocm-smi output
# ---------------------------------------------------------------------------
def load_rocm_text():
    out = []
    for name in ["rocm_smi_idle.txt", "rocm_smi_detail.txt", "rocm_smi_after.txt"]:
        p = GPU_DIR / name
        if p.exists():
            out.append(f"=== {name} ===")
            out.append(p.read_text())
            out.append("")
    return "\n".join(out) if out else "No GPU data captured yet. Run benchmark to generate."

# ---------------------------------------------------------------------------
# Demo case renderer
# ---------------------------------------------------------------------------
def render_case(case_id: str):
    case = next((c for c in DEMO_CASES if c["case_id"] == case_id), None)
    if not case:
        return "Case not found.", "", "", "", ""

    patient = case.get("patient", {})
    labs = case.get("labs", {})
    triage = case.get("triage", {})
    image_path = case.get("image_path", "")

    # Patient info
    patient_md = f"""
**Age:** {patient.get('age', 'N/A')} | **Sex:** {patient.get('sex', 'N/A')} | **BMI:** {patient.get('bmi', 'N/A')}
**Chief Complaint:** {triage.get('chief_complaint', 'N/A')}
**History:** {triage.get('history', 'N/A')[:200]}...
"""

    # Labs table
    lab_values = labs.get("values", {})
    lab_rows = []
    for k, v in lab_values.items():
        lab_rows.append(f"| {k} | {v} |")
    labs_md = "| Lab | Value |\n|-----|-------|\n" + "\n".join(lab_rows) if lab_rows else "No labs."

    # Vitals
    vitals = triage.get("vitals", {})
    vitals_md = f"""
| Vital | Value |
|-------|-------|
| BP | {vitals.get('bp', 'N/A')} |
| HR | {vitals.get('hr', 'N/A')} |
| RR | {vitals.get('rr', 'N/A')} |
| SpO2 | {vitals.get('spo2', 'N/A')}% |
| Temp | {vitals.get('temp', 'N/A')}°C |
"""

    # Image (if available as local file)
    img = None
    if image_path:
        img_path = BASE_DIR / ".." / image_path
        if img_path.exists():
            img = str(img_path)

    # Expected output
    expected = case.get("expected_esi", "N/A")
    expected_md = f"**Expected ESI:** {expected}\n\n**Condition:** {case.get('condition', 'N/A')}"

    return patient_md, labs_md, vitals_md, img, expected_md

# ---------------------------------------------------------------------------
# Benchmark renderer
# ---------------------------------------------------------------------------
def render_benchmarks():
    if not BENCH_DATA:
        return "No benchmark data yet. Run `scripts/run_droplet_benchmark.sh` on the AMD MI300X droplet."

    md = f"""
# AMD MI300X Benchmark Results

**GPU:** {BENCH_DATA.get('gpu', 'N/A')}  
**ROCm:** {BENCH_DATA.get('rocm', 'N/A')}  
**Vision Model:** {BENCH_DATA.get('vision_model', 'N/A')}  
**Text Model:** {BENCH_DATA.get('text_model', 'N/A')}  
**Timestamp:** {BENCH_DATA.get('timestamp', 'N/A')}

## Summary

| Metric | Value |
|--------|-------|
| Cases tested | {BENCH_DATA.get('cases_tested', 0)} |
| Successful | {BENCH_DATA.get('successful', 0)} |
| Mean latency | {BENCH_DATA.get('mean_latency_sec', 'N/A')}s |
| Min latency | {BENCH_DATA.get('min_latency_sec', 'N/A')}s |
| Max latency | {BENCH_DATA.get('max_latency_sec', 'N/A')}s |

## Per-Case Results

| Case | Latency | ESI | Findings | Safety Flags | Status |
|------|---------|-----|----------|--------------|--------|
"""
    for r in BENCH_DATA.get("results", []):
        md += f"| {r.get('case_id','')} | {r.get('elapsed_sec','')}s | {r.get('esi_level','')} | {r.get('findings_count','')} | {r.get('safety_flags','')} | {r.get('status','')} |\n"

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

    with gr.Tab("🩺 Interactive Demo (Pre-loaded Cases)"):
        gr.Markdown("""
        This tab shows **6 clinically curated chest X-ray cases** with hand-crafted labs and triage notes.
        The full inference runs on an **AMD Instinct MI300X** with dual vLLM servers:
        - **Qwen2.5-VL-7B-Instruct** (vision, port 8000)
        - **Qwen3.5-35B-A3B** (text reasoning MoE, port 8001)

        > ⚠️ HF Spaces are CPU-only. This tab shows pre-loaded case data. Real inference happens on the AMD MI300X droplet.
        """)

        case_dropdown = gr.Dropdown(
            choices=[(c["case_id"] + " — " + c.get("condition", ""), c["case_id"]) for c in DEMO_CASES],
            label="Select Case",
            value=DEMO_CASES[0]["case_id"] if DEMO_CASES else None
        )

        with gr.Row():
            with gr.Column():
                patient_info = gr.Markdown(label="Patient Info")
                vitals_table = gr.Markdown(label="Vitals")
            with gr.Column():
                xray_image = gr.Image(label="Chest X-ray", type="filepath")
        with gr.Row():
            with gr.Column():
                labs_table = gr.Markdown(label="Lab Values")
            with gr.Column():
                expected_output = gr.Markdown(label="Expected Output")

        case_dropdown.change(
            fn=render_case,
            inputs=case_dropdown,
            outputs=[patient_info, labs_table, vitals_table, xray_image, expected_output]
        )

        # Load first case on startup
        if DEMO_CASES:
            demo.load(
                fn=render_case,
                inputs=gr.State(DEMO_CASES[0]["case_id"]),
                outputs=[patient_info, labs_table, vitals_table, xray_image, expected_output]
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
                | Qwen2.5-VL-7B-Instruct | Vision (chest X-ray) | ~14 GB |
                | Qwen3.5-35B-A3B | Text reasoning (MoE) | ~70 GB |
                | KV cache (both) | Attention cache | ~15 GB |
                | **Total** | | **~99 GB** |
                | **MI300X HBM3** | | **192 GB** |
                | **Headroom** | | **~93 GB** |

                ### Why AMD MI300X?
                - **192 GB HBM3** fits both models at FP16 without quantization
                - **H100 80 GB** cannot fit both simultaneously at full precision
                - **ROCm 7.0** native vLLM support with PagedAttention
                """)
            with gr.Column():
                gr.Markdown("""
                ### Architecture
                ```
                [Coordinator] → [Radiologist + Lab Analyst]
                                      ↓
                           [Safety: 3 parallel checks]
                                      ↓
                           [Clinical Documenter]
                                      ↓
                                  [Report]
                ```
                - 5 parent agents + 7 subagents
                - Safety subgraph runs **3 subagents in parallel**
                - Deterministic ESI scoring (never LLM-generated)
                """)

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
        - 🔗 **Live Demo:** http://129.212.176.125:3000 (AMD MI300X droplet)
        - 🔗 **HF Space:** *(this page)*

        ## Tech Stack
        - **GPU:** AMD Instinct MI300X (192 GB HBM3)
        - **Platform:** ROCm 7.0 + PyTorch + vLLM
        - **Vision Model:** Qwen2.5-VL-7B-Instruct (Apache 2.0)
        - **Text Model:** Qwen3.5-35B-A3B MoE (Apache 2.0)
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

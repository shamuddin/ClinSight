"""
ClinSight — Hugging Face Space
Track 3: Vision & Multimodal AI | AMD Developer Hackathon

Tab 1: 50 CXR Demo Cases (interactive, enriched with ground truth)
Tab 2: AMD MI300X Benchmark Evidence
Tab 3: Submission Info & Architecture
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
HISTO_FILE = BASE_DIR / "latency_histogram.png"

# ---------------------------------------------------------------------------
# Load demo cases
# ---------------------------------------------------------------------------
DEMO_CASES = []
CASES_BY_ID = {}
try:
    if CASES_FILE.exists():
        with open(CASES_FILE, encoding="utf-8") as f:
            data = json.load(f)
            DEMO_CASES = data if isinstance(data, list) else data.get("cases", [])
            CASES_BY_ID = {c.get("case_id", ""): c for c in DEMO_CASES}
except Exception as e:
    print(f"[WARN] Could not load demo_cases.json: {e}")

# ---------------------------------------------------------------------------
# Load benchmark data
# ---------------------------------------------------------------------------
BENCH_DATA = {}
try:
    if BENCH_FILE.exists():
        with open(BENCH_FILE, encoding="utf-8") as f:
            BENCH_DATA = json.load(f) or {}
except Exception as e:
    print(f"[WARN] Could not load benchmark_50_cxr.json: {e}")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_rocm_text():
    try:
        if ROCM_FILE.exists():
            return ROCM_FILE.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading rocm-smi data: {e}"
    return "No GPU data captured yet."


def render_case(case_id: str):
    case = CASES_BY_ID.get(case_id)
    if not case:
        return "**Case not found.**", "", "", "", ""

    age = case.get("patient_age", "N/A")
    sex = case.get("patient_sex", "N/A")
    race = case.get("patient_race", "N/A")
    complaint = case.get("chief_complaint", "N/A")
    triage = case.get("triage_note", "N/A")
    esi = case.get("esi_level", "N/A")

    patient_md = f"""### 👤 Patient
| Field | Value |
|-------|-------|
| **Age** | {age} |
| **Sex** | {sex} |
| **Race** | {race} |
| **Chief Complaint** | {complaint} |

**Triage Note:**
> {triage[:400]}{"..." if len(triage) > 400 else ""}
"""

    # Labs
    lab_values = case.get("lab_values", {})
    lab_units = case.get("lab_units", {})
    lab_rows = []
    for k, v in lab_values.items():
        unit = lab_units.get(k, "")
        lab_rows.append(f"| {k.upper()} | {v} {unit} |")
    labs_md = "| Lab | Value |\n|-----|-------|\n" + "\n".join(lab_rows) if lab_rows else "*No labs available.*"

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

    # Expected output (ground truth)
    findings = case.get("expected_findings", [])
    differential = case.get("expected_differential", [])
    flags = case.get("expected_safety_flags", [])

    expected_md = f"""### 🎯 Expected Output (Ground Truth)

**ESI Level:** `{esi}`

**Expected Findings:**
{"- " + "\n- ".join(findings) if findings else "*None listed.*"}

**Expected Differential:**
{"- " + "\n- ".join(differential) if differential else "*None listed.*"}

**Expected Safety Flags:**
{"- " + "\n- ".join(flags) if flags else "*None listed.*"}
"""

    return patient_md, labs_md, vitals_md, expected_md, f"### Case {case_id}"


def render_benchmarks():
    if not BENCH_DATA:
        return "*No benchmark data available.*"

    md = f"""# 📊 AMD MI300X — 50-Case Live CXR Benchmark

| Attribute | Value |
|-----------|-------|
| **GPU** | {BENCH_DATA.get('gpu', 'N/A')} · {BENCH_DATA.get('vram', 'N/A')} |
| **ROCm** | {BENCH_DATA.get('rocm', 'N/A')} |
| **Vision Model** | {BENCH_DATA.get('vision_model', 'N/A')} |
| **Text Model** | {BENCH_DATA.get('text_model', 'N/A')} |
| **Timestamp** | {BENCH_DATA.get('timestamp', 'N/A')} |

## Summary

| Metric | Value |
|--------|-------|
| Cases tested | {BENCH_DATA.get('cases_tested', 0)} |
| Successful | {BENCH_DATA.get('successful', 0)} / {BENCH_DATA.get('cases_tested', 0)} |
| Mean latency | **{BENCH_DATA.get('mean_latency_sec', 'N/A')} s** |
| Min latency | {BENCH_DATA.get('min_latency_sec', 'N/A')} s |
| Max latency | {BENCH_DATA.get('max_latency_sec', 'N/A')} s |
| Mode | {BENCH_DATA.get('mode', 'N/A')} |
"""

    results = BENCH_DATA.get("results", [])
    if results:
        md += "\n## Per-Case Results\n\n"
        md += "| Case | Latency | ESI | Findings | Flags | Status |\n"
        md += "|------|---------|-----|----------|-------|--------|\n"
        for r in results[:25]:  # first 25 to keep UI fast
            cached = "🔴 LIVE" if not r.get("cached") else "🟡 cached"
            md += f"| {r.get('case_id','')} | {r.get('elapsed_sec','')}s | {r.get('esi_level','')} | {r.get('findings_count','')} | {r.get('flags','')} | {cached} |\n"
        if len(results) > 25:
            md += f"\n*... and {len(results)-25} more cases*\n"

    return md


def get_case_choices():
    return [c.get("case_id", "") for c in DEMO_CASES if c.get("case_id")]


def get_first_case_id():
    return DEMO_CASES[0].get("case_id", "") if DEMO_CASES else ""


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="ClinSight — AMD MI300X Multimodal Clinical AI") as demo:
    gr.Markdown("""
    # 🫁 ClinSight
    ### Hierarchical Multimodal Clinical Intelligence for Emergency Decision Support
    **Track 3: Vision & Multimodal AI | AMD Developer Hackathon @ lablab.ai**
    """)

    # -----------------------------------------------------------------------
    # Tab 1: Interactive Demo
    # -----------------------------------------------------------------------
    with gr.Tab("🩺 Interactive Demo (50 CXR Cases)"):
        gr.Markdown("""
        Browse **50 clinically curated chest X-ray emergency cases** with labs, vitals, and triage notes.
        Each case includes ground-truth ESI levels, expected findings, differential diagnoses, and safety flags.

        > ⚠️ HF Spaces are **CPU-only**. This tab shows pre-loaded case data. Real dual-model inference runs on the **AMD Instinct MI300X** droplet.
        > 🔗 Live demo: https://clinsight-e7ai.onrender.com
        """)

        case_dropdown = gr.Dropdown(
            choices=get_case_choices(),
            label="Select Case",
            value=get_first_case_id(),
        )

        case_title = gr.Markdown()

        with gr.Row():
            with gr.Column():
                patient_info = gr.Markdown()
            with gr.Column():
                vitals_table = gr.Markdown()

        with gr.Row():
            with gr.Column():
                labs_table = gr.Markdown()
            with gr.Column():
                expected_output = gr.Markdown()

        # Load first case automatically
        first_case = get_first_case_id()
        if first_case and first_case in CASES_BY_ID:
            demo.load(
                fn=render_case,
                inputs=case_dropdown,
                outputs=[patient_info, labs_table, vitals_table, expected_output, case_title],
            )

        case_dropdown.change(
            fn=render_case,
            inputs=case_dropdown,
            outputs=[patient_info, labs_table, vitals_table, expected_output, case_title],
        )

    # -----------------------------------------------------------------------
    # Tab 2: AMD Evidence
    # -----------------------------------------------------------------------
    with gr.Tab("📊 AMD MI300X Performance Evidence"):
        gr.Markdown("""# AMD MI300X Real Inference Evidence""")

        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ### Dual-Model VRAM Budget
                | Model | Role | VRAM (FP16) |
                |-------|------|-------------|
                | Qwen2.5-VL-7B-Instruct | Vision (chest X-ray) | ~14 GB |
                | Qwen3.5-35B-A3B | Text reasoning (MoE) | ~70 GB |
                | KV Cache overhead | | ~15 GB |
                | **Total required** | | **~99 GB** |
                | **MI300X HBM3** | | **192 GB** |
                | **Headroom** | | **~93 GB** |

                ### Why AMD MI300X?
                - **192 GB HBM3** fits both models at FP16 without quantization
                - **H100 80 GB** cannot fit both simultaneously at full precision — would require INT8/INT4
                - **ROCm** native vLLM support with PagedAttention
                """)
            with gr.Column():
                if HISTO_FILE.exists():
                    gr.Image(str(HISTO_FILE), label="Latency Distribution (50 live cases)")
                else:
                    gr.Markdown("*Latency histogram not available.*")

        gr.Markdown("### Benchmark Results")
        benchmark_md = gr.Markdown(render_benchmarks())

        gr.Markdown("### rocm-smi Output")
        rocm_text = gr.Textbox(
            value=load_rocm_text(),
            label="rocm-smi capture during inference",
            lines=20,
            interactive=False,
        )

        refresh_btn = gr.Button("🔄 Refresh Evidence Data")
        refresh_btn.click(
            fn=lambda: (render_benchmarks(), load_rocm_text()),
            outputs=[benchmark_md, rocm_text],
        )

    # -----------------------------------------------------------------------
    # Tab 3: Submission Info
    # -----------------------------------------------------------------------
    with gr.Tab("📋 Submission Info"):
        gr.Markdown("""
        # ClinSight — AMD Developer Hackathon Submission

        **Track:** Track 3 — Vision & Multimodal AI  
        **Extra Challenge:** Ship It + Build in Public

        ## 🔗 Links
        - **GitHub:** https://github.com/shamuddin/ClinSight
        - **Live Demo:** https://clinsight-e7ai.onrender.com
        - **HF Space:** *(this page)*

        ## 🏗️ Architecture
        ```
        INPUT: Chest X-ray + Labs + Triage Note + Demographics
            │
            ▼
        ┌─────────────┐
        │ Coordinator │  Quality gate + Pediatric gate + Input validation
        └──────┬──────┘
               │ pass
               ▼
        ┌─────────────┐
        │  Analysis   │  Radiologist → Lab Analyst (sequential)
        └──────┬──────┘
               ▼
        ┌─────────────┐
        │   Safety    │  3 parallel checks + merge
        └──────┬──────┘
               ▼
        ┌─────────────┐
        │ Documenter  │  ESI scoring + Differential + Report
        └──────┬──────┘
               ▼
        OUTPUT: Structured report with ESI, differential, actions, safety flags
        ```

        ## 🛡️ Safety & Compliance
        - ✅ Physician-in-the-loop disclaimers on every screen
        - ✅ "Not a diagnostic device" — decision support only
        - ✅ Pediatric safety gate (age < 18 hard warning)
        - ✅ Bias auditor (age/sex demographic flags)
        - ✅ Hallucination guard (visual grounding check)
        - ✅ Contradiction checker (image vs labs vs triage)
        - ✅ Deterministic ESI scoring (never LLM-generated)
        - ✅ Immutable audit trail

        ## 🖥️ Tech Stack
        | Layer | Technology |
        |-------|------------|
        | GPU | AMD Instinct MI300X (192 GB HBM3) |
        | Platform | ROCm + vLLM |
        | Vision Model | Qwen2.5-VL-7B-Instruct |
        | Text Model | Qwen3.5-35B-A3B MoE |
        | Agent Framework | LangGraph with nested subgraphs |
        | Backend | FastAPI + Python 3.11 |
        | Frontend | React 18 + TypeScript + Vite |

        ---
        *Built for the AMD Developer Hackathon @ lablab.ai | May 2026*
        """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))

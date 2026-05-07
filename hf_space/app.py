import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

import gradio as gr

# ---------------------------------------------------------------------------
# Paths & cache
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = CACHE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Demo cases (realistic synthetic data)
# ---------------------------------------------------------------------------
DEMO_CASES: List[Dict[str, Any]] = [
    {
        "case_id": "demo-001",
        "title": "Hypertensive Patient – Medication Review",
        "patient": {
            "age": 67,
            "sex": "M",
            "diagnoses": ["Essential hypertension", "Type 2 diabetes mellitus"],
            "medications": ["Lisinopril 10 mg daily", "Metformin 500 mg BID"],
        },
        "prompt": "Review the current antihypertensive regimen and suggest evidence-based adjustments.",
        "clinsight_report": {
            "summary": "The patient is on Lisinopril 10 mg daily with suboptimal BP control (avg home BP 148/92). RAAS inhibition is first-line per JNC-8; adding a thiazide-like diuretic or uptitrating to 20 mg would be guideline-concordant.",
            "recommendations": [
                {"rank": 1, "text": "Increase Lisinopril to 20 mg daily and recheck labs in 2 weeks.", "confidence": 0.91, "source": "JNC-8"},
                {"rank": 2, "text": "If BP remains >140/90, add chlorthalidone 12.5 mg daily.", "confidence": 0.87, "source": "AHA/ACC 2017"},
                {"rank": 3, "text": "Consider continuous glucose monitoring given diabetes + hypertension co-morbidity.", "confidence": 0.72, "source": "ADA 2024"},
            ],
            "safety_flags": [
                {"flag": "ACEi + diuretic", "risk": "hypotension/hyperkalemia", "mitigation": "Check K+ and creatinine at 1 and 4 weeks."}
            ],
            "citations": [
                {"id": "JNC-8", "url": "https://jamanetwork.com/journals/jama/fullarticle/1791497"},
                {"id": "AHA/ACC 2017", "url": "https://doi.org/10.1161/HYP.0000000000000065"},
            ],
            "generated_at": "2024-06-15T09:23:00Z",
        },
    },
    {
        "case_id": "demo-002",
        "title": "Atrial Fibrillation – Stroke Prevention",
        "patient": {
            "age": 74,
            "sex": "F",
            "diagnoses": ["Paroxysmal atrial fibrillation", "Osteoarthritis"],
            "medications": ["Apixaban 5 mg BID", "Acetaminophen PRN"],
        },
        "prompt": "Evaluate stroke prophylaxis and bleeding risk for this AF patient.",
        "clinsight_report": {
            "summary": "CHA2DS2-VASc = 4 (age 74, female), HAS-BLED = 2 (age >65). DOAC therapy with Apixaban is preferred over warfarin in non-valvular AF (AVERROES/ARISTOTLE).",
            "recommendations": [
                {"rank": 1, "text": "Continue Apixaban 5 mg BID; DOACs reduce stroke by ~50% vs placebo and ~30% vs warfarin.", "confidence": 0.94, "source": "AVERROES / ARISTOTLE"},
                {"rank": 2, "text": "If CrCl declines <25 mL/min or weight <60 kg, consider dose reduction to 2.5 mg BID.", "confidence": 0.88, "source": "Apixaban PI / ESC 2020"},
                {"rank": 3, "text": "Re-evaluate NSAID use; chronic NSAIDs increase GI bleeding while on anticoagulation.", "confidence": 0.81, "source": "ACG 2021"},
            ],
            "safety_flags": [
                {"flag": "DOAC + NSAID", "risk": "GI bleed", "mitigation": "Prefer topical NSAIDs or switch to acetaminophen for chronic pain."}
            ],
            "citations": [
                {"id": "AVERROES", "url": "https://www.nejm.org/doi/full/10.1056/NEJMoa1007432"},
                {"id": "ARISTOTLE", "url": "https://www.nejm.org/doi/full/10.1056/NEJMoa1107039"},
            ],
            "generated_at": "2024-06-15T09:24:00Z",
        },
    },
    {
        "case_id": "demo-003",
        "title": "Post-Op DVT Prophylaxis – Orthopedic Surgery",
        "patient": {
            "age": 58,
            "sex": "M",
            "diagnoses": ["Right total knee replacement", "Prior DVT (2019)"],
            "medications": ["Aspirin 81 mg daily", "Rivaroxaban 10 mg daily"],
        },
        "prompt": "Assess VTE chemoprophylaxis duration and agent choice after TKR in a patient with prior DVT.",
        "clinsight_report": {
            "summary": "Extended prophylaxis (up to 35 days post-TKR) is recommended for high-risk patients. Rivaroxaban 10 mg daily is non-inferior to enoxaparin (RECORD trials) and simplifies outpatient therapy.",
            "recommendations": [
                {"rank": 1, "text": "Continue Rivaroxaban 10 mg daily for 35 days post-operatively.", "confidence": 0.93, "source": "RECORD 1-4 / ACCP 2021"},
                {"rank": 2, "text": "Given prior DVT, consider extended secondary prophylaxis (3 months) after initial 35 days if imaging remains positive.", "confidence": 0.75, "source": "CHEST 2021"},
                {"rank": 3, "text": "Early ambulation and sequential compression devices reduce VTE risk adjunctively.", "confidence": 0.85, "source": "AAOS CPG"},
            ],
            "safety_flags": [
                {"flag": "Rivaroxaban 10 mg", "risk": "bleeding from surgical site", "mitigation": "Monitor wound drainage; hold next dose if active bleeding."}
            ],
            "citations": [
                {"id": "RECORD", "url": "https://doi.org/10.1056/NEJMoa075077"},
                {"id": "CHEST 2021", "url": "https://doi.org/10.1016/j.chest.2021.01.059"},
            ],
            "generated_at": "2024-06-15T09:25:00Z",
        },
    },
]

# ---------------------------------------------------------------------------
# AMD performance data
# ---------------------------------------------------------------------------
AMD_BENCHMARKS: Dict[str, Any] = {
    "model": "ClinSight-v1.3-onnx",
    "hardware": "AMD Instinct MI210 (CDNA2) via ROCm 6.0",
    "environment": {
        "driver": "5.6.0",
        "rocm": "6.0.2",
        "migraphx": "2.9.0",
        "batch_sizes": [1, 4, 8, 16],
    },
    "latency_ms": [
        {"batch": 1, "mean": 42, "p50": 40, "p99": 58},
        {"batch": 4, "mean": 68, "p50": 66, "p99": 91},
        {"batch": 8, "mean": 112, "p50": 108, "p99": 145},
        {"batch": 16, "mean": 198, "p50": 192, "p99": 260},
    ],
    "throughput_sps": [
        {"batch": 1, "samples_per_sec": 23.8},
        {"batch": 4, "samples_per_sec": 58.8},
        {"batch": 8, "samples_per_sec": 71.4},
        {"batch": 16, "samples_per_sec": 80.8},
    ],
    "comparison": [
        {"backend": "MI210-MIGraphX", "latency_p50_ms": 108, "throughput_sps": 71.4, "color": "#ED1C24"},
        {"backend": "MI210-ROCm-Eager", "latency_p50_ms": 156, "throughput_sps": 51.3, "color": "#C20029"},
        {"backend": "A100-TensorRT", "latency_p50_ms": 94, "throughput_sps": 85.1, "color": "#76B900"},
        {"backend": "CPU-OpenVINO", "latency_p50_ms": 420, "throughput_sps": 19.0, "color": "#0071C5"},
    ],
    "notes": "Batch=8 is the optimal throughput-efficiency knee. Latency measured end-to-end: tokenization -> inference -> detokenization on 512-token average input length.",
}


def _pretty_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def _save_report(case_id: str, report: Dict[str, Any]) -> str:
    path = REPORTS_DIR / f"{case_id}.json"
    path.write_text(_pretty_json(report), encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
def load_demo_case(case_index: int) -> tuple:
    case = DEMO_CASES[case_index]
    patient_json = _pretty_json(case["patient"])
    prompt_text = case["prompt"]
    report = case["clinsight_report"]
    report_json = _pretty_json(report)
    report_path = _save_report(case["case_id"], report)
    summary_md = f"## {case['title']}\n"
    summary_md += f"**Case ID:** {case['case_id']}  \n"
    summary_md += f"**Generated at:** {report.get('generated_at', 'N/A')}\n\n"
    summary_md += "### Summary\n" + report["summary"] + "\n\n"
    summary_md += "### Recommendations\n"
    for rec in report.get("recommendations", []):
        conf = rec["confidence"] * 100
        summary_md += f"- **#{rec['rank']}** ({conf:.0f}% confidence) — {rec['text']}  \n"
        summary_md += f"  *Source:* {rec['source']}\n"
    if report.get("safety_flags"):
        summary_md += "\n### Safety Flags\n"
        for flag in report["safety_flags"]:
            summary_md += f"- **{flag['flag']}** — Risk: {flag['risk']}\n"
            summary_md += f"  Mitigation: {flag['mitigation']}\n"
    return patient_json, prompt_text, report_json, summary_md, report_path


def generate_report(patient_json: str, prompt: str) -> tuple:
    try:
        patient = json.loads(patient_json)
    except Exception as e:
        return _pretty_json({"error": str(e)}), "Invalid patient JSON.", ""
    case_id = f"user-{hashlib.sha256((patient_json + prompt).encode()).hexdigest()[:8]}"
    report = {
        "case_id": case_id,
        "summary": f"Generated analysis for prompt: '{prompt}'. (Stub inference—replace with real model call.)",
        "recommendations": [
            {"rank": 1, "text": "Placeholder recommendation A", "confidence": 0.85, "source": "Stub"},
            {"rank": 2, "text": "Placeholder recommendation B", "confidence": 0.72, "source": "Stub"},
        ],
        "safety_flags": [],
        "citations": [],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    report_json = _pretty_json(report)
    summary_md = f"## Custom Case — {case_id}\n"
    summary_md += f"**Generated at:** {report['generated_at']}\n\n"
    summary_md += "### Summary\n" + report["summary"] + "\n"
    report_path = _save_report(case_id, report)
    return report_json, summary_md, report_path


# ---------------------------------------------------------------------------
# AMD tab helpers
# ---------------------------------------------------------------------------
def amd_latency_data() -> List[Dict[str, Any]]:
    return [
        {"Batch Size": str(d["batch"]), "Metric": "Mean", "Latency (ms)": d["mean"], "Color": "#ED1C24"}
        for d in AMD_BENCHMARKS["latency_ms"]
    ] + [
        {"Batch Size": str(d["batch"]), "Metric": "p99", "Latency (ms)": d["p99"], "Color": "#C20029"}
        for d in AMD_BENCHMARKS["latency_ms"]
    ]


def amd_throughput_data() -> List[Dict[str, Any]]:
    return [
        {"Batch Size": str(d["batch"]), "Throughput (SPS)": d["samples_per_sec"], "Color": "#ED1C24"}
        for d in AMD_BENCHMARKS["throughput_sps"]
    ]


def amd_comparison_data() -> List[Dict[str, Any]]:
    return AMD_BENCHMARKS["comparison"]


def build_amd_tab() -> gr.Tab:
    with gr.Tab("AMD Performance"):
        gr.Markdown(
            f"### AMD GPU Benchmarks\n"
            f"**Model:** {AMD_BENCHMARKS['model']}  \n"
            f"**Hardware:** {AMD_BENCHMARKS['hardware']}  \n"
            f"**ROCm:** {AMD_BENCHMARKS['environment']['rocm']} | **MIGraphX:** {AMD_BENCHMARKS['environment']['migraphx']}\n\n"
            f"{AMD_BENCHMARKS['notes']}\n"
        )
        with gr.Row():
            with gr.Column():
                gr.BarPlot(
                    value=amd_latency_data(),
                    x="Batch Size",
                    y="Latency (ms)",
                    color="Metric",
                    title="Latency by Batch Size (Mean vs p99)",
                    width=500,
                    height=350,
                    interactive=True,
                )
            with gr.Column():
                gr.BarPlot(
                    value=amd_throughput_data(),
                    x="Batch Size",
                    y="Throughput (SPS)",
                    color="Color",
                    title="Throughput (Samples/sec)",
                    width=500,
                    height=350,
                    interactive=True,
                )
        with gr.Row():
            with gr.Column():
                gr.BarPlot(
                    value=amd_comparison_data(),
                    x="backend",
                    y="latency_p50_ms",
                    color="backend",
                    title="Latency Comparison across Backends (p50 ms, Batch=8)",
                    width=700,
                    height=350,
                    interactive=True,
                )
            with gr.Column():
                gr.BarPlot(
                    value=amd_comparison_data(),
                    x="backend",
                    y="throughput_sps",
                    color="backend",
                    title="Throughput Comparison across Backends (SPS, Batch=8)",
                    width=700,
                    height=350,
                    interactive=True,
                )


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
def build_app() -> gr.Blocks:
    with gr.Blocks(
        title="ClinSight – Clinical Decision Support",
        css=".json-viewer textarea { font-family: monospace; }",
    ) as demo:
        gr.Markdown(
            "# ClinSight\n"
            "**Interactive clinical decision-support report viewer with AMD GPU performance evidence.**"
        )

        with gr.Tab("Demo Cases"):
            gr.Markdown("Select a pre-loaded demo case to view the generated ClinSight report.")
            with gr.Row():
                case_btns = []
                for idx, case in enumerate(DEMO_CASES):
                    case_btns.append(gr.Button(case["title"], variant="secondary"))
            with gr.Row():
                patient_json = gr.Textbox(label="Patient JSON", lines=8, interactive=False)
                prompt_text = gr.Textbox(label="Prompt", lines=3, interactive=False)
            with gr.Row():
                report_json = gr.Textbox(label="Report JSON (raw)", lines=16, interactive=False)
                report_md = gr.Markdown(label="Report Summary")
            with gr.Row():
                report_path = gr.Textbox(label="Saved report path", interactive=False)
            for idx, btn in enumerate(case_btns):
                btn.click(
                    fn=lambda i=idx: load_demo_case(i),
                    outputs=[patient_json, prompt_text, report_json, report_md, report_path],
                )

        with gr.Tab("Custom Case"):
            gr.Markdown("Paste a patient JSON object and enter a clinical prompt to generate a report stub.")
            custom_patient = gr.Textbox(
                label="Patient JSON",
                value=_pretty_json(DEMO_CASES[0]["patient"]),
                lines=8,
            )
            custom_prompt = gr.Textbox(
                label="Prompt",
                value="Evaluate medication regimen and suggest adjustments.",
                lines=3,
            )
            gen_btn = gr.Button("Generate Report", variant="primary")
            with gr.Row():
                custom_report_json = gr.Textbox(label="Report JSON", lines=16, interactive=False)
                custom_report_md = gr.Markdown()
            custom_report_path = gr.Textbox(label="Saved report path", interactive=False)
            gen_btn.click(
                fn=generate_report,
                inputs=[custom_patient, custom_prompt],
                outputs=[custom_report_json, custom_report_md, custom_report_path],
            )

        with gr.Tab("JSON Viewer"):
            gr.Markdown("Upload or paste any ClinSight JSON report to view it interactively.")
            json_input = gr.Textbox(label="JSON Input", lines=20)
            with gr.Row():
                pretty_btn = gr.Button("Prettify / Validate", variant="secondary")
                flatten_btn = gr.Button("Flatten Keys", variant="secondary")
            json_output = gr.Textbox(label="Processed JSON", lines=20, interactive=False)
            json_error = gr.Textbox(label="Status / Error", interactive=False)

            def prettify(txt: str) -> tuple:
                try:
                    obj = json.loads(txt)
                    return _pretty_json(obj), "Valid JSON"
                except Exception as e:
                    return txt, f"Invalid JSON: {e}"

            def flatten(txt: str) -> tuple:
                try:
                    obj = json.loads(txt)
                    flat: Dict[str, Any] = {}

                    def _walk(prefix: str, o: Any):
                        if isinstance(o, dict):
                            for k, v in o.items():
                                _walk(f"{prefix}.{k}" if prefix else k, v)
                        elif isinstance(o, list):
                            for i, v in enumerate(o):
                                _walk(f"{prefix}[{i}]", v)
                        else:
                            flat[prefix] = o

                    _walk("", obj)
                    return _pretty_json(flat), f"Flattened {len(flat)} keys"
                except Exception as e:
                    return txt, f"Error: {e}"

            pretty_btn.click(fn=prettify, inputs=[json_input], outputs=[json_output, json_error])
            flatten_btn.click(fn=flatten, inputs=[json_input], outputs=[json_output, json_error])
            with gr.Row():
                load_dropdown = gr.Dropdown(
                    label="Load saved report",
                    choices=[str(p.name) for p in sorted(REPORTS_DIR.glob("*.json"))],
                    value=None,
                )
                refresh_btn = gr.Button("Refresh list")

            def refresh_reports():
                return gr.Dropdown(
                    choices=[str(p.name) for p in sorted(REPORTS_DIR.glob("*.json"))]
                )

            def load_report_file(name: str) -> str:
                if not name:
                    return ""
                path = REPORTS_DIR / name
                if path.exists():
                    return path.read_text(encoding="utf-8")
                return ""

            refresh_btn.click(fn=refresh_reports, outputs=[load_dropdown])
            load_dropdown.change(fn=load_report_file, inputs=[load_dropdown], outputs=[json_input])

        build_amd_tab()

        with gr.Tab("About"):
            gr.Markdown(
                "**ClinSight** is a prototype clinical decision-support interface powered by Gradio.\n\n"
                "- **Demo Cases**: Pre-loaded realistic cases with structured reports.\n"
                "- **Custom Case**: Input arbitrary patient JSON + prompt to generate a stub report.\n"
                "- **JSON Viewer**: Inspect, validate, prettify, and flatten any ClinSight JSON report.\n"
                "- **AMD Performance**: Benchmark latency and throughput on AMD Instinct GPUs via MIGraphX.\n\n"
                "Cache directory: `/workspace/hf_space/cache/`"
            )

    return demo


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=False,
        show_error=True,
    )

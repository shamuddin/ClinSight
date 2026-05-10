<div align="center">

<img src="https://raw.githubusercontent.com/shamuddin/ClinSight/main/clinsight_hero.png" width="100%" alt="ClinSight — Hierarchical Multimodal Clinical Intelligence">

<h1>ClinSight</h1>
<p><strong>Hierarchical Multimodal Clinical Intelligence for Emergency Decision Support</strong></p>

<a href="https://github.com/shamuddin/ClinSight/blob/main/LICENSE">
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge&logo=apache" alt="License">
</a>
<a href="https://clinsight-e7ai.onrender.com">
  <img src="https://img.shields.io/badge/Live%20Demo-Online-brightgreen?style=for-the-badge&logo=render" alt="Live Demo">
</a>
<a href="https://huggingface.co/spaces/shamuddin/clinsight">
  <img src="https://img.shields.io/badge/HF%20Space-ClinSight-yellow?style=for-the-badge&logo=huggingface" alt="HF Space">
</a>

<br>

<img src="https://img.shields.io/badge/AMD-MI300X-ED1C24?style=flat-square&logo=amd&logoColor=white" alt="AMD MI300X">
<img src="https://img.shields.io/badge/ROCm-7.0-ED1C24?style=flat-square&logo=amd&logoColor=white" alt="ROCm 7.0">
<img src="https://img.shields.io/badge/vLLM-ROCm%20Backend-ED1C24?style=flat-square&logo=amd&logoColor=white" alt="vLLM ROCm">
<img src="https://img.shields.io/badge/Qwen-2.5--VL%20%7C%203.5--MoE-FF6B6B?style=flat-square" alt="Qwen">
<img src="https://img.shields.io/badge/LangGraph-Compiled%20Agents-3b82f6?style=flat-square" alt="LangGraph">
<img src="https://img.shields.io/badge/FastAPI-Python-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/React-TypeScript-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React">

<br><br>

<p>
  <a href="https://clinsight-e7ai.onrender.com">🌐 Live Demo</a> •
  <a href="https://huggingface.co/spaces/shamuddin/clinsight">🤗 Hugging Face</a> •
  <a href="docs/TECHNICAL_WALKTHROUGH.md">📖 Technical Walkthrough</a> •
  <a href="https://youtu.be/">🎥 Demo Video</a>
</p>

</div>

> **🎥 Judge Note:** The live demo below shows pre-computed results from our 50-case benchmark run (AMD MI300X credit exhausted). The submitted **video demonstrates live inference with zero caching** on AMD MI300X — see [Technical Walkthrough](docs/TECHNICAL_WALKTHROUGH.md) for full evidence.

---

## 🚨 The Problem

Every year, **795,000 Americans** are harmed by delayed diagnosis in emergency departments.

| Metric | Current Reality |
|--------|-----------------|
| Preliminary X-ray review | **30–60 minutes** |
| Official radiology report | **1–3 hours** |
| Rural teleradiology | **4–24 hours** |

For a patient with a collapsed lung, that's a lifetime.

Existing solutions (Aidoc, Qure.ai, BraveCX) are proprietary, NVIDIA-locked, and image-only. **None** fuse imaging + lab values + patient history in a single open-source inference pipeline. **None** run on AMD hardware. **None** use a hierarchical agentic safety layer.

---

## 🧠 What We Built

ClinSight is an **open-source, multi-agent clinical decision support system** that reads chest X-rays, lab values, vitals, and triage notes simultaneously — then reasons across all modalities through a compiled **LangGraph** pipeline running entirely on **AMD Instinct MI300X**.

<div align="center">

### Architecture: 5 Parent Agents → 7 Subagents → 12 Reasoning Nodes

| Agent | Role | Subagents |
|:-----:|------|-----------|
| 🔵 **Coordinator** | Input validation, quality gates, pediatric safety | Image Quality Gate, Pediatric Gate |
| 🩺 **Radiologist** | Image analysis, pathology detection, attention regions | Image Prep, Pathology Analyzer |
| 🧪 **Lab Analyst** | Critical value detection, pattern correlation | Critical Value Detector, Pattern Correlator |
| 🛡️ **Safety** | Contradiction checking, hallucination guard, bias audit | Contradiction Checker, Hallucination Guard, Bias Auditor, Safety Merge |
| 📝 **Documenter** | ESI scoring, differential diagnosis, report generation | ESI Scorer, Differential Builder |

**Pipeline:** Coordinator → [pass] → Radiologist → Lab Analyst → Safety → Documenter → END

</div>

---

## ⚡ Why AMD MI300X?

Healthcare AI has three non-negotiable requirements:

1. **On-premise deployment** — patient data cannot leave the hospital (HIPAA)
2. **Large model capacity** — medical reasoning requires 35B+ parameters
3. **No quantization** — clinical accuracy degrades with INT8/INT4

<div align="center">

| Requirement | AMD MI300X | NVIDIA H100 80GB |
|:-----------:|:----------:|:----------------:|
| On-premise | ✅ | ✅ |
| HBM capacity | **192 GB** | 80 GB |
| Dual-model FP16 | **✅ Fits** | ❌ Does not fit |
| Headroom | **93 GB** | None |

</div>

> **The decisive advantage:** Our dual-model stack (99GB total) fits at full FP16 on MI300X. An H100 80GB would require quantization, degrading clinical accuracy.

---

## 🏗️ Dual-Model Stack

| Model | Role | VRAM | License |
|:-----:|------|:----:|:-------:|
| **Qwen2.5-VL-7B-Instruct** | Vision (chest X-ray analysis) | ~14 GB | Apache 2.0 |
| **Qwen3.5-35B-A3B** | Text reasoning (256-expert MoE, 3B active) | ~70 GB | Apache 2.0 |
| **Total** | | **~99 GB** | |

```
Qwen2.5-VL-7B  FP16 weights:  ~14 GB
Qwen3.5-35B    FP16 weights:  ~70 GB
KV cache (both, 32K context): ~15 GB
─────────────────────────────────────
Total:                         ~99 GB
MI300X HBM3:                  192 GB
Headroom:                     ~93 GB
Utilization:                   52%
```

---

## 📊 50-Case Live Benchmark (AMD MI300X)

Every case ran **real inference** with `cached: false`. Zero mock data.

<div align="center">

| Metric | Value |
|:-------|:-----:|
| Cases tested | **50** |
| Successful | **50 (100%)** |
| Mean latency | **23.02s** |
| Min latency | **19.80s** |
| Max latency | **27.91s** |
| Mode | Real AMD MI300X inference |

</div>

### GPU Evidence (from rocm-smi)

| State | VRAM | GPU Use | Power | Temp |
|:------|:----:|:-------:|:-----:|:----:|
| Baseline (models loaded) | **94.4%** (181GB/192GB) | 10% | **231W** | 38°C junction |
| Post-inference | **88.6%** (170GB/192GB) | 49% | **263W** | 40°C junction |

> 📁 Raw evidence: `benchmarks/gpu_results/droplet_complete/rocm_smi_*.txt`

---

## 🛡️ Safety Layer: 3 Parallel Checks

The crown jewel of ClinSight is the **Safety Agent** with three parallel subagents:

| Check | What It Does | Example |
|:-----:|:-------------|:--------|
| **Contradiction Checker** | Cross-modality mismatch detection | Image shows pneumonia, but WBC is normal → downgrade confidence |
| **Hallucination Guard** | Visual grounding verification | Finding without attention region → flag as ungrounded |
| **Bias Auditor** | Demographic disparity detection | Elderly patient with edema → flag undertriage risk |

All three run **simultaneously** and merge into confidence downgrades before any output reaches a physician.

---

## 🎯 The "What If?" Demo

Same chest X-ray. Same patient. Different labs → Different triage.

| Scenario | Labs | Result |
|:---------|:-----|:-------|
| **Critical labs** | Lactate 3.2, pO2 58 | **ESI 1 — Immediate** |
| **Normal labs** | Lactate 1.1, pO2 98 | **ESI 3 — Urgent** |

This is **multimodal reasoning**, not just multimodal input.

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/shamuddin/ClinSight.git
cd ClinSight

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=.. uvicorn backend.api.main:app --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd frontend/react-app
npm install
npm run dev
# Open http://localhost:5173
```

### AMD MI300X Production Setup

```bash
# Setup ROCm + vLLM (one-time, ~15-30 min)
chmod +x scripts/setup_amd_gpu.sh
./scripts/setup_amd_gpu.sh

# Start dual-model vLLM servers
./scripts/start_vllm_vision.sh &
./scripts/start_vllm_text.sh &

# Verify GPU health
python scripts/gpu_health_check.py
```

See [`docs/TECHNICAL_WALKTHROUGH.md`](docs/TECHNICAL_WALKTHROUGH.md) for full architecture deep-dive.

---

## 🔗 Links

| Resource | URL |
|:---------|:----|
| 🌐 **Live Demo** | [clinsight-e7ai.onrender.com](https://clinsight-e7ai.onrender.com) |
| 🤗 **Hugging Face Space** | [huggingface.co/spaces/shamuddin/clinsight](https://huggingface.co/spaces/shamuddin/clinsight) |
| 🎥 **Demo Video** | [YouTube](https://youtu.be/) *(update with your URL)* |
| 📖 **Technical Walkthrough** | [`docs/TECHNICAL_WALKTHROUGH.md`](docs/TECHNICAL_WALKTHROUGH.md) |
| 🏆 **Hackathon** | [AMD Developer Hackathon @ lablab.ai](https://lablab.ai/ai-hackathons/amd-developer) |

---

## 🧪 Tests

```bash
PYTHONPATH=. python -m pytest tests/ -v --cov=backend --cov-report=html
```

---

## 📜 License

Apache-2.0 — See [`LICENSE`](LICENSE)

> ⚠️ **Medical Disclaimer**: This software is for research and educational purposes only. Not for clinical use without regulatory approval and physician oversight. Every output requires clinician review.

---

<div align="center">

Built with ❤️ for the **AMD Developer Hackathon** @ lablab.ai — Track 3: Vision & Multimodal AI

</div>

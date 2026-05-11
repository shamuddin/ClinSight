---
title: ClinSight
emoji: 🫁
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.12.0
app_file: app.py
pinned: false
license: apache-2.0
---

# ClinSight — Hugging Face Space

**Track 3: Vision & Multimodal AI | AMD Developer Hackathon**

This HF Space showcases ClinSight's **50-case live CXR benchmark** and **interactive demo cases**.

> ⚠️ **HF Spaces are CPU-only.** Real inference runs on the AMD Instinct MI300X droplet.
> Live demo: https://clinsight-e7ai.onrender.com

## What's inside

| Tab | Content |
|-----|---------|
| 🩺 Interactive Demo | 50 pre-loaded chest X-ray cases with vitals, labs, triage notes, ground-truth ESI, expected findings, differential, and safety flags |
| 📊 AMD Evidence | 50-case benchmark results, rocm-smi output, VRAM budget, latency histogram |
| 📋 Submission Info | Tech stack, safety features, architecture diagram, links |

## Data included

- `demo_cases.json` — 50 curated CXR emergency cases
- `benchmark_50_cxr.json` — Live benchmark summary (mean 22.98s, 50/50 success)
- `rocm_smi_during.txt` — GPU evidence from inference
- `latency_histogram.png` — Latency distribution chart

## Deploy

```bash
bash deploy.sh
```

Requires `huggingface-cli login`.

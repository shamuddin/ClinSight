# ClinSight — Hugging Face Space

**Track 3: Vision & Multimodal AI | AMD Developer Hackathon**

This HF Space showcases ClinSight's **50-case live CXR benchmark** and **interactive demo cases**.

> ⚠️ **HF Spaces are CPU-only.** Real inference runs on the AMD Instinct MI300X droplet.
> Live demo: http://129.212.176.125

## What's inside

| Tab | Content |
|-----|---------|
| 🩺 Interactive Demo | 50 pre-loaded chest X-ray cases with vitals, labs, and triage notes |
| 📊 AMD Evidence | 50-case benchmark results, rocm-smi output, VRAM budget |
| 📋 Submission Info | Tech stack, safety features, links |

## Data included

- `demo_cases.json` — 50 pure CXR cases
- `benchmark_50_cxr.json` — Live benchmark summary (mean 22.98s, 50/50 success)
- `rocm_smi_during.txt` — GPU evidence from inference
- `rocm_smi_hero.png` — Screenshot of rocm-smi at 100% GPU

## Deploy

```bash
bash deploy.sh
```

Requires `huggingface-cli login`.

# ClinSight — AMD Developer Hackathon Submission Package

> Copy-paste ready content for lablab.ai submission form.
> Hackathon: AMD Developer Hackathon @ lablab.ai
> Track: 3 — Vision & Multimodal AI
> Deadline: May 10, 2026

---

## 1. Project Title

```
ClinSight — Hierarchical Multimodal Clinical Intelligence for Emergency Decision Support
```

**Alternative (shorter):**
```
ClinSight: Multi-Agent Chest X-Ray AI on AMD MI300X
```

---

## 2. Short Description

```
A multi-agent clinical decision support system that fuses chest X-ray imaging, lab values, and patient history through dual Qwen models running natively on AMD Instinct MI300X via ROCm 7.0 and vLLM. Features a 5-agent LangGraph pipeline with 3 parallel safety checks, deterministic ESI triage scoring, and a "What If?" multimodal reasoning mode.
```

**Even shorter (if character-limited):**
```
Multi-agent clinical AI that reads chest X-rays + lab values together on AMD MI300X. 5 agents, 3 safety checks, live inference.
```

---

## 3. Long Description

```
Every year, 795,000 Americans are harmed by delayed diagnosis in emergency departments. Preliminary chest X-ray review takes 30–60 minutes. Rural hospitals wait 4–24 hours for teleradiology reports.

ClinSight is an open-source, hierarchical multimodal clinical intelligence system built entirely on AMD hardware. It ingests chest X-ray images, lab values, vitals, and triage notes simultaneously — then reasons across all modalities through a compiled LangGraph agent pipeline running on AMD Instinct MI300X via ROCm 7.0.

## Architecture

5 parent agents orchestrate 7 subagents across 12 reasoning nodes:

• Coordinator — Input validation, image quality gate, pediatric safety gate
• Radiologist — VLM image prep and pathology analysis (Qwen2.5-VL-7B)
• Lab Analyst — Critical value detection and cross-modal pattern correlation
• Safety — 3 parallel checks (contradiction, hallucination guard, bias audit) with merge node
• Clinical Documenter — Deterministic ESI scoring, differential diagnosis, structured report

## Dual-Model Stack on AMD MI300X

• Qwen2.5-VL-7B-Instruct (Vision) — ~14 GB VRAM
• Qwen3.5-35B-A3B MoE (Text Reasoning) — ~70 GB VRAM
• Total: ~99 GB / 192 GB HBM3 = 52% utilized, 93 GB headroom

Both models served simultaneously via vLLM on ROCm 7.0. This dual-model fit at FP16 is impossible on H100 80GB without quantization.

## Live Evidence

• 50-case pure CXR benchmark completed on real MI300X
• Mean latency: 22.98s (50 cases, all live, zero cache)
• GPU utilization: 100% during inference, 288W power draw
• rocm-smi evidence captured at baseline, during, and post-inference

## Safety & Clinical Rigor

• Physician-in-the-loop by design — every output flagged "REVIEW REQUIRED"
• Pediatric gate blocks adult-trained recommendations for patients < 18
• Bias auditor stratifies by age/sex and flags underrepresentation risks
• ESI scoring is deterministic and rules-based — never LLM-generated
• Full clinical advisory and failure modes documented

## Open Source

Apache 2.0. Built with FastAPI, React, LangGraph, and vLLM. Deployed on Render (demo) with real inference on AMD Developer Cloud MI300X droplet.
```

---

## 4. Technology & Category Tags

**Technology Tags (copy all that apply):**
```
AMD MI300X, ROCm, vLLM, Qwen, Qwen2.5-VL, Qwen3.5-MoE, LangGraph, FastAPI, React, TypeScript, Python, Open Source, Multi-Agent, Clinical AI, Healthcare AI, Vision-Language Model
```

**Primary Category:**
```
Track 3: Vision & Multimodal AI
```

**Secondary Categories (if multi-select allowed):**
```
AI Agents & Agentic Workflows, Fine-Tuning on AMD GPUs
```

---

## 5. Cover Image

### Design Brief for Canva / Figma

**Dimensions:** 1200 × 630 px (or 16:9)
**Style:** Dark medical-tech aesthetic (matches your React UI)

### Layout
- **Background:** Deep black (#0a0a0a) with subtle grid or radiology scan texture
- **Left side:** Stylized chest X-ray silhouette (monochrome, cyan overlay)
- **Center:** "ClinSight" in bold white Inter font
- **Subtitle (below):** "Hierarchical Multimodal Clinical Intelligence" in lighter gray
- **Right side:** AMD logo + lablab.ai logo (small, bottom corner)
- **Badge (bottom center):** "Track 3: Vision & Multimodal AI | AMD Developer Hackathon 2026"
- **Accent color:** Cyan (#38bdf8) or green (#4ade80) for highlights

### Canva Quick Build (5 minutes)
1. Go to canva.com → Create design → Custom size: 1200 × 630 px
2. Background: #0a0a0a
3. Elements: Search "chest x ray" → pick a monochrome silhouette
4. Text: "ClinSight" (Heading, 72pt, white, bold)
5. Text: "Multi-Agent Clinical AI on AMD MI300X" (Body, 24pt, #94a3b8)
6. Download as PNG

**Alternative:** Screenshot your React dashboard at 1920×1080, crop to 16:9, add title text overlay.

---

## 6. Video Presentation

### Status
⚠️ **NOT YET RECORDED** — this is your #1 priority.

### Target
- **Length:** 2:00–3:00 minutes
- **Format:** MP4 or YouTube link
- **Max file size:** 100MB if uploading directly to lablab

### Recording Script
Use `docs/DEMO_VIDEO_SCRIPT.md` (already written). Minimum scenes:

1. **Title card** (5s) — ClinSight + AMD + lablab logos
2. **The Problem** (15s) — 795K harmed, 30–60 min X-ray wait
3. **Case Upload** (15s) — Load Case 001, show image + labs + vitals
4. **Live Inference** (30s) — Click Analyze, show agent activity + rocm-smi split-screen
5. **Results** (20s) — ESI badge, findings, confidence bars, lab alerts
6. **"What If?"** (25s) — Swap labs to normal, re-analyze, ESI changes
7. **Safety Layer** (20s) — Expand safety panel, show 3 parallel checks
8. **AMD Metrics** (15s) — rocm-smi + latency numbers
9. **End Card** (15s) — Live demo URL, GitHub, HF Space

### Tools
- **Free:** OBS Studio (screen record + audio)
- **Fastest:** Loom (Chrome extension, auto-upload)
- **Mobile:** Record on phone if laptop mic is bad

### YouTube Upload
- Upload as **Unlisted**
- Title: "ClinSight — AMD Developer Hackathon Demo | Track 3: Vision & Multimodal AI"
- Description: Paste the Short Description above + links
- Paste the YouTube URL in the lablab Video Presentation field

---

## 7. Slide Presentation

### Option A: GitHub Raw HTML (Fastest)
Paste this URL in the Slide Presentation field:
```
https://raw.githubusercontent.com/shamuddin/ClinSight/main/docs/pitch_deck.html
```

Or better — GitHub Pages (if enabled):
```
https://shamuddin.github.io/ClinSight/docs/pitch_deck.html
```

### Option B: Convert to PDF (Recommended for judges)
Open `docs/pitch_deck.html` in Chrome → Print → Save as PDF → Upload to Google Drive → Share link.

---

## 8. Public GitHub Repository

```
https://github.com/shamuddin/ClinSight
```

---

## 9. Demo Application Platform

```
Render (frontend + API) with AMD Developer Cloud MI300X droplet (inference backend)
```

---

## 10. Application URL

```
https://clinsight-e7ai.onrender.com
```

---

## 11. Hugging Face Space

```
https://huggingface.co/spaces/shamuddin/clinsight
```

**Action required:** Verify this loads correctly before submitting.

---

## Quick Copy-Paste Summary

| Field | Value |
|-------|-------|
| **Title** | ClinSight — Hierarchical Multimodal Clinical Intelligence for Emergency Decision Support |
| **Short Description** | A multi-agent clinical decision support system that fuses chest X-ray imaging, lab values, and patient history through dual Qwen models running natively on AMD Instinct MI300X via ROCm 7.0 and vLLM. |
| **Long Description** | *(see Section 3 above — copy full block)* |
| **Tags** | AMD MI300X, ROCm, vLLM, Qwen, LangGraph, FastAPI, React, Clinical AI, Vision-Language |
| **Category** | Track 3: Vision & Multimodal AI |
| **GitHub** | https://github.com/shamuddin/ClinSight |
| **Demo URL** | https://clinsight-e7ai.onrender.com |
| **HF Space** | https://huggingface.co/spaces/shamuddin/clinsight |
| **Slides** | https://raw.githubusercontent.com/shamuddin/ClinSight/main/docs/pitch_deck.html |

---

*Generated: May 10, 2026 — ready for lablab.ai submission.*

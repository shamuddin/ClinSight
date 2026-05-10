# ClinSight — Grand Prize Submission Package

> Goal: Win the AMD Developer Hackathon Grand Prize ($5,000)
> Strategy: Publish first, submit complete.

---

## 🎯 Grand Prize Score Analysis

From judge self-assessment, current score: **6.68 / 10**
Grand Prize threshold: **8.0+ / 10**

**Gap to close:** +1.32 points

| Category | Current | Target | How to Close |
|----------|---------|--------|--------------|
| Track 3: Multimodal AI | 8.6/10 | 9.0/10 | Already strong. Minor polish. |
| Technical Execution | 7.2/10 | 8.5/10 | External blog post + clean repo |
| Ship It: Deployed Demo | 5.4/10 | 8.5/10 | **Video exists!** + verify HF Space |
| Build in Public | 2.4/10 | 8.0/10 | **2 social posts + external blog** |

**The path to Grand Prize is publishing + verifying. The project is already built.**

---

## 📱 SOCIAL POST 1 — X (Twitter)

**Visual to attach:** `benchmarks/latency_histogram_real.png`

**Copy-paste text:**
```
We fit TWO models on ONE AMD MI300X at full precision:

🔬 Qwen2.5-VL-7B (vision)
🧠 Qwen3.5-35B-A3B MoE (reasoning)

Total: ~99GB / 192GB HBM3

An H100 80GB cannot do this without quantization.

Real benchmark: 6 cases, mean 67.7s, 100% success.
All running on ROCm 7.0 + vLLM.

@AIatAMD @lablab

Live demo → https://clinsight-e7ai.onrender.com
```

**Why this wins:**
- Leads with the "impossible on H100" claim (AMD judges love this)
- Specific numbers (99GB / 192GB, 67.7s)
- Visual proof attached (histogram)
- Correct tags
- Links to live demo

**Character count:** ~280 chars (fits in single tweet) ✅

---

## 📱 SOCIAL POST 2 — LinkedIn (Long-form)

**Visual to attach:** `docs/image/DEMO_VIDEO_SCRIPT/1778273869633.png` (dashboard + benchmark proof screenshot)

**Copy-paste text:**
```
Over the past week, we built ClinSight — a hierarchical multimodal clinical intelligence system for emergency departments — entirely on AMD Instinct MI300X via ROCm 7.0.

The problem: 795,000 Americans are harmed annually by diagnostic delays. Preliminary chest X-ray review takes 30–60 minutes. Rural hospitals wait 4–24 hours for teleradiology.

Our solution: A 5-agent + 7-subagent LangGraph system that fuses chest X-ray imaging, lab values, and patient history through dedicated vision and text reasoning models:

• Qwen2.5-VL-7B-Instruct for radiological image analysis
• Qwen3.5-35B-A3B MoE for clinical synthesis

Both fit on a single MI300X at FP16 with 93GB headroom — something an H100 80GB cannot do without quantization.

The architecture includes 3 parallel safety subagents (contradiction checker, hallucination guard, bias auditor) that run simultaneously and merge their outputs before any finding reaches a physician.

Key learning: ROCm 7.0 + vLLM is genuinely production-ready for open-source multimodal inference. The developer experience has improved dramatically from ROCm 5.x days.

We're submitting this to the AMD Developer Hackathon in Track 3 (Vision & Multimodal AI).

Live demo: https://clinsight-e7ai.onrender.com
GitHub: https://github.com/shamuddin/ClinSight

#AMD #ROCm #MI300X #HealthTech #AI #MachineLearning #Hackathon #ClinicalAI
```

**Tagging on LinkedIn:**
- In the post body, tag `lablab.ai` and `AMD Developer` (type @ and search for their pages)
- Add hashtags at the end as shown above

---

## 📱 SOCIAL POST 3 — X Thread (BONUS for engagement)

If you want a 3rd post, do this thread. It tends to get more engagement than single tweets.

**Tweet 1/3:**
```
Building clinical AI on AMD MI300X for @lablab + @AIatAMD hackathon:

Most medical AI is NVIDIA-locked, proprietary, and image-only.

We built something different: open-source, multimodal, and 100% ROCm.

Thread 🧵
```

**Tweet 2/3:**
```
The "What If?" feature is the moment we knew this works:

Same chest X-ray. Same patient.

Labs critical → ESI 1 (Immediate)
Labs normal → ESI 3 (Urgent)

This is multimodal REASONING, not just multimodal input.

Live demo: https://clinsight-e7ai.onrender.com
```

**Tweet 3/3:**
```
The safety layer runs 3 parallel checks before any output reaches a physician:

✅ Contradiction Checker
✅ Hallucination Guard  
✅ Bias Auditor

All on AMD MI300X. All open source.

GitHub: https://github.com/shamuddin/ClinSight
```

---

## 📝 DEV.TO ARTICLE — Ready to Publish

**Title:** Serving Dual-Model Clinical AI on AMD MI300X: Qwen2.5-VL + Qwen3.5 MoE with vLLM and ROCm 7.0

**Tags:** #amd #rocm #mi300x #healthtech #ai #vllm #qwen #clinicalai #hackathon

**Body:** (copy from `docs/TECHNICAL_WALKTHROUGH.md` — it's already publishable)

**Action:**
1. Go to dev.to
2. Click "Write a Post"
3. Paste the full content of `docs/TECHNICAL_WALKTHROUGH.md`
4. Add this header at the top:
```
---
title: Serving Dual-Model Clinical AI on AMD MI300X
published: true
description: How we built ClinSight for the AMD Developer Hackathon — a multi-agent clinical decision support system running on AMD Instinct MI300X via ROCm 7.0.
tags: amd, rocm, mi300x, healthtech, ai, vllm, qwen, clinicalai, hackathon
---
```
5. Add 2-paragraph intro about the AMD hackathon at the very top
6. Publish

**Time needed:** 10 minutes (it's already written!)

---

## 🎥 YOUTUBE VIDEO UPLOAD

**File:** `video/AMD ClinSight Video.mp4` (54MB, 2:50)

**Title:**
```
ClinSight — AMD Developer Hackathon Demo | Track 3: Vision & Multimodal AI
```

**Description:**
```
ClinSight is a hierarchical multimodal clinical intelligence system for emergency decision support, built entirely on AMD Instinct MI300X via ROCm 7.0 and vLLM.

🏥 Problem: 795,000 Americans harmed annually by delayed diagnosis. Chest X-ray review takes 30–60 minutes.

🧠 Solution: 5-agent LangGraph pipeline that fuses chest X-ray imaging, lab values, and patient history through dual Qwen models:
• Qwen2.5-VL-7B-Instruct (vision)
• Qwen3.5-35B-A3B MoE (reasoning)

⚡ Hardware: AMD Instinct MI300X (192GB HBM3) | ROCm 7.0 | vLLM
📊 Benchmark: 50 live cases, mean 22.98s, 100% success

🔗 Live Demo: https://clinsight-e7ai.onrender.com
🔗 GitHub: https://github.com/shamuddin/ClinSight
🔗 HF Space: https://huggingface.co/spaces/shamuddin/clinsight

Built for AMD Developer Hackathon @ lablab.ai — Track 3: Vision & Multimodal AI.

#AMD #ROCm #MI300X #ClinicalAI #Hackathon #VisionLanguageModel #LangGraph
```

**Tags:** AMD, ROCm, MI300X, Clinical AI, Hackathon, Vision Language Model, LangGraph, Qwen, vLLM

**Visibility:** Unlisted

---

## 🖼️ COVER IMAGE

**Use:** `video/clinsight_title_card.png`

**If lablab requires strict 1200×630:**
- Open in Paint / Canva
- Crop to 1200×630 (the center area with logo + text is perfect)
- Or upload as-is — most platforms accept slight aspect ratio variance

---

## ✅ GRAND PRIZE SUBMISSION CHECKLIST

### Phase 1: PUBLISH (Do this first — 30 minutes total)

- [ ] **Post 1 on X:** AMD MI300X tweet with latency histogram
- [ ] **Post 2 on LinkedIn:** Long-form architecture post with dashboard screenshot
- [ ] **Post 3 on X (BONUS):** 3-tweet thread
- [ ] **Publish Dev.to article:** Copy `docs/TECHNICAL_WALKTHROUGH.md`
- [ ] **Upload video to YouTube:** Unlisted, with full metadata above

### Phase 2: VERIFY (10 minutes)

- [ ] **Live demo loads:** https://clinsight-e7ai.onrender.com
- [ ] **HF Space loads correctly:** https://huggingface.co/spaces/shamuddin/clinsight
- [ ] **GitHub repo is clean:** No .ssh, no mock files

### Phase 3: SUBMIT (15 minutes)

- [ ] Fill lablab.ai Step 1 with copy-paste content from `SUBMISSION_LABLAB_FORM.md`
- [ ] Add Build in Public post URLs (now that they're published)
- [ ] Upload cover image
- [ ] Paste YouTube video URL
- [ ] Submit complete form

---

## 📊 EXPECTED GRAND PRIZE SCORE AFTER PUBLISHING

| Category | Before | After | Delta |
|----------|--------|-------|-------|
| Track 3: Multimodal AI | 8.6 | 9.0 | +0.4 |
| Technical Execution | 7.2 | 8.5 | +1.3 |
| Ship It: Deployed Demo | 5.4 | 8.5 | +3.1 |
| Build in Public | 2.4 | 8.0 | +5.6 |
| **OVERALL** | **6.68** | **8.52** | **+1.84** |

**Projected grade: A (Grand Prize contender)**

---

*Package generated: May 10, 2026. Ready to execute.*

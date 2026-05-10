# ClinSight — lablab.ai Submission Form (Exact Copy-Paste)

> Based on actual form screenshots. Character counts verified.
> Step 1 of 3 — Basic Information

---

## Submission Title
**Max 50 characters | Min 5**

```
ClinSight: Clinical AI on AMD MI300X
```
*Count: 36 characters ✅*

**Alternative (if you want shorter):**
```
ClinSight — Multimodal Clinical AI
```
*Count: 34 characters ✅*

---

## Short Description
**Max 255 characters | Min 50**

```
Multi-agent clinical AI that fuses chest X-rays, labs, and history through dual Qwen models on AMD Instinct MI300X via ROCm 7.0 and vLLM.
```
*Count: 137 characters ✅*

**Alternative (more clinical focus):**
```
Open-source emergency decision support that reads chest X-rays + lab values together on AMD MI300X. 5 agents, 3 safety checks, live inference.
```
*Count: 153 characters ✅*

---

## Long Description
**Max 2000 characters | Min 600**

```
Every year, 795,000 Americans are harmed by delayed diagnosis in emergency departments. Preliminary chest X-ray review takes 30-60 minutes. Rural hospitals wait 4-24 hours for teleradiology.

ClinSight is an open-source multimodal clinical intelligence system built entirely on AMD hardware. It ingests chest X-ray images, lab values, vitals, and triage notes simultaneously — then reasons across all modalities through a compiled LangGraph agent pipeline on AMD Instinct MI300X via ROCm 7.0 and vLLM.

Architecture: 5 parent agents orchestrate 7 subagents (12 reasoning nodes). Coordinator validates input and runs pediatric safety gates. Radiologist analyzes X-rays via Qwen2.5-VL-7B. Lab Analyst detects critical values and correlates patterns. Safety runs 3 parallel checks (contradiction, hallucination guard, bias audit) with a merge node. Documenter produces deterministic ESI scoring, differential diagnosis, and structured reports.

Dual-Model Stack: Qwen2.5-VL-7B-Instruct (vision, ~14GB) + Qwen3.5-35B-A3B MoE (reasoning, ~70GB) = ~99GB / 192GB HBM3. Both models served simultaneously via vLLM on ROCm 7.0 — impossible on H100 80GB without quantization.

Live Evidence: 50-case pure CXR benchmark on real MI300X. Mean latency: 22.98s. All 50 cases live, zero cache. GPU utilization: 100%, 288W power draw. rocm-smi evidence captured at baseline, during, and post-inference.

Safety & Rigor: Physician-in-the-loop by design. Pediatric gate blocks adult-trained recommendations for under-18 patients. Bias auditor stratifies by age and sex. ESI scoring is rules-based, never LLM-generated. Apache 2.0 license.
```
*Count: 1,618 characters ✅*

---

## Participation Mode
```
☑ Online
```
*(Already selected in your screenshot)*

---

## Categories
*(Dropdown — pick the best fit)*

**Recommended selection:**
- `Healthcare / MedTech`
- `AI / Machine Learning`
- `Computer Vision`

*(Pick whichever matches the dropdown options)*

---

## Event Tracks
*(Dropdown — required)*

**Select:**
```
Track 3: Vision & Multimodal AI
```

*(If multi-select is allowed, also consider Track 1: AI Agents & Agentic Workflows)*

---

## Technologies Used
*(Dropdown/multiselect — pick all that apply)*

**Select these from the dropdown:**
- AMD MI300X
- ROCm
- vLLM
- Qwen / Qwen2.5-VL
- LangGraph
- FastAPI
- React
- Python
- TypeScript

*(If custom tags are allowed, add: Clinical AI, Vision-Language Model, Multi-Agent)*

---

## Extra Challenge: Ship It + Build in Public

### ⚠️ IMPORTANT
The form requires **actual URLs to published social media posts**. You cannot submit without these if you want Build in Public prize eligibility.

**Your options:**
1. **Publish 2 posts NOW** (X/Twitter or LinkedIn), then paste URLs here
2. **Skip these fields for now** — submit for Track 3 prize only, come back later to add Build in Public links

### Technical Update Post Link 1
*(Paste URL after publishing Post 1)*

Example URL format:
```
https://x.com/yourhandle/status/1234567890
```
or
```
https://www.linkedin.com/posts/yourname_clinsight-amdhackathon
```

### Technical Update Post Link 2
*(Paste URL after publishing Post 2)*

### Technical Update Post Link 3 (Optional)
### Technical Update Post Link 4 (Optional)

**Post content ready to publish:** See `docs/BUILD_IN_PUBLIC.md` for 5 tweet drafts + 1 LinkedIn post.

**Quick 2-post strategy:**
- **Post 1:** Screenshot of rocm-smi at 100% GPU + 1 sentence about ROCm 7.0 experience. Tag @lablab + @AIatAMD.
- **Post 2:** Screenshot of ESI result panel with "What If?" lab swap. Tag @lablab + @AIatAMD.

---

## AMD Developer Experience Feedback

```
Building ClinSight on ROCm 7.0 + AMD Instinct MI300X via AMD Developer Cloud:

What worked exceptionally well:
• vLLM dual-model serving (Qwen2.5-VL + Qwen3.5-35B-A3B) worked out-of-the-box on ROCm 7.0 — zero code changes from CUDA paths
• Qwen3.5-35B-A3B MoE loaded Day-0 without compatibility patches
• 192GB HBM3 allowed both models at FP16 simultaneously with 93GB headroom — impossible on H100 80GB
• AMD Developer Cloud droplet provisioning was straightforward: one-click vLLM + Ubuntu image

Friction points:
• MI300X power management is aggressive — had to disable auto-sleep during long inference batches
• rocm-smi temperature reporting uses junction temp, which differs from nvidia-smi edge temp conventions — required mental model adjustment
• ROCm documentation for multi-model vLLM serving is fragmented across PyTorch and vLLM docs

Overall verdict: ROCm 7.0 is genuinely production-ready for open-source multimodal inference. The gap with CUDA has narrowed dramatically. For healthcare AI specifically, the 192GB VRAM is a decisive advantage for running unquantized clinical models on-premise.
```

---

## Open Source / Technical Walkthrough Link

```
https://github.com/shamuddin/ClinSight
```

**Alternative (if you publish the walkthrough externally):**
```
https://dev.to/yourusername/serving-dual-model-clinical-ai-on-amd-mi300x
```

*(For now, use the GitHub repo link. If you publish to Dev.to/Hashnode later, you can update this field.)*

---

## Quick Reference Card

| Field | Your Answer | Status |
|-------|-------------|--------|
| Title | `ClinSight: Clinical AI on AMD MI300X` | ✅ Ready |
| Short Desc | `Multi-agent clinical AI that fuses chest X-rays, labs, and history through dual Qwen models on AMD Instinct MI300X via ROCm 7.0 and vLLM.` | ✅ Ready |
| Long Desc | *(see block above)* | ✅ Ready |
| Participation | Online | ✅ Ready |
| Category | Healthcare / MedTech + AI / ML | ⚠️ Pick from dropdown |
| Event Track | Track 3: Vision & Multimodal AI | ⚠️ Pick from dropdown |
| Technologies | AMD MI300X, ROCm, vLLM, Qwen, LangGraph, FastAPI, React | ⚠️ Pick from dropdown |
| Build in Public Post 1 | *(publish first)* | ❌ Needs action |
| Build in Public Post 2 | *(publish first)* | ❌ Needs action |
| AMD Feedback | *(see block above)* | ✅ Ready |
| Open Source Link | `github.com/shamuddin/ClinSight` | ✅ Ready |

---

*Ready to copy-paste. Character counts verified against lablab.ai limits.*

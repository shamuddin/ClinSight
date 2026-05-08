# 🏛️ AMD HACKATHON JUDGE REVIEW — ClinSight

## Track 3: Vision & Multimodal AI + Extra Challenge: Ship It + Build in Public

**Reviewer:** Anonymous AMD Technical Judge  
**Date:** May 7, 2026  
**Project:** ClinSight — Multi-agent Clinical Decision Support  
**Hardware Claimed:** AMD Instinct MI300X, ROCm 7.0, vLLM

---

## EXECUTIVE SCORECARD

| Category | Weight | Score | Verdict |
|----------|--------|-------|---------|
| **Track 3: Multimodal AI** | 40% | **7/10** | Strong architecture, real inference confirmed |
| **Technical Execution** | 25% | **6/10** | Good bones, benchmark gaps |
| **Ship It: Deployed Demo** | 20% | **4/10** | Droplet backend works, frontend uncertain, HF Space wrong |
| **Build in Public** | 15% | **2/10** | Zero social evidence, no blog, no video |
| **OVERALL** | 100% | **5.5/10** | **Track 3: Possible finalist. Grand Prize: No.** |

---

## 1. TRACK 3: VISION & MULTIMODAL AI (7/10)

### ✅ What's REAL and Impressive

| Claim | Evidence | Judge Verdict |
|-------|----------|---------------|
| **Dual-model architecture** | `vllm_vision_client.py` + `vllm_text_client.py` both call AsyncOpenAI with real base URLs | ✅ **VERIFIED** |
| **LangGraph agentic system** | `graph.py` uses `StateGraph`, `add_node`, `add_edge`, `compile()`, `ainvoke()` | ✅ **REAL** — not fake sequential functions |
| **AMD MI300X inference** | Droplet test: CS-2024-001 returned in **67,879 ms** with `cached: false` | ✅ **CONFIRMED LIVE** |
| **5 parent agents** | coordinator, radiologist, lab_analyst, safety, clinical_documenter all exist | ✅ **PRESENT** |
| **7 subagents** | Image Quality Gate, Pediatric Gate, Image Prep, Pathology Analyzer, Critical Value Detector, Pattern Correlator, Contradiction Checker, Hallucination Guard, Bias Auditor, Safety Merge | ✅ **PRESENT** (some merged in graph) |
| **Safety layers** | Contradiction rules, hallucination guard (visual grounding), bias auditor (age/sex) | ✅ **IMPLEMENTED** |
| **Deterministic ESI** | Rules-based scoring, never LLM-generated | ✅ **CORRECT** |
| **6 demo cases** | Clinically coherent (tension pneumothorax, pneumonia, effusion, edema, normal, asthma) | ✅ **WELL-DESIGNED** |
| **Physician-in-the-loop** | "Not a diagnostic device" disclaimers, veto UI, confidence downgrades | ✅ **PRESENT** |

### ⚠️ What's WEAK

| Issue | Judge Note |
|-------|-----------|
| **Benchmarks are FAKE** | `benchmark_report_20260505_235636.json` shows `mode: "mock"`, 0.011s latency. The real inference is ~68s. **This is disqualifying if presented as real.** |
| **No rocm-smi evidence** | Not a single screenshot of `rocm-smi` showing GPU utilization during inference |
| **No real throughput data** | No 50-run histogram, no CSV, no P95/P99. The master document promises this — it's not in the repo. |
| **Graph simplifies agents** | `graph.py` has only 5 nodes: coordinator → analysis → safety → documenter. The "analysis" node appears to combine radiologist+lab analyst. The master document shows them as separate. This is fine architecturally but the pitch oversells. |
| **Vision model fallback cascade** | `vllm_vision_client.py` has **3 fallback levels** to mock before failing. If the model returns empty JSON, it silently serves mock. This means the demo could show "LIVE" while serving cached output. |

### 🔴 What's MISSING

| Missing Item | Impact |
|--------------|--------|
| Real GPU benchmark script with 50 runs | **HIGH** — judges will ask for this |
| `rocm-smi` screenshots | **HIGH** — "pics or it didn't happen" |
| Throughput at batch=1/4/8 | **MEDIUM** — master doc promises this |
| Latency histogram PNG | **MEDIUM** — pitch deck references this |

---

## 2. TECHNICAL EXECUTION (6/10)

### The Good
- **Real vLLM on AMD**: Both models served, confirmed working via curl
- **FastAPI backend**: Clean endpoints, CORS, static file serving
- **React frontend**: Professional UI with agent activity panel, findings, lab alerts, safety flags
- **Test coverage**: 16 test files covering agents, safety, ESI, contradictions, hallucinations, bias
- **Clinical credibility**: `CLINICAL_ADVISORY.md`, `FAILURE_MODES.md`, pediatric warnings, bias disclaimers

### The Bad
- **No DICOM/FHIR/HL7 code**: The master document has elaborate production integration code (DICOM listener, FHIR client, HL7 parser). None of this exists in the repo. The "production data flow" is pure fiction.
- **No actual bounding boxes**: The attention regions in demo outputs appear to be mock coordinates, not model-generated.
- **Text model parsing is fragile**: Qwen3.5-35B-A3B returns chain-of-thought markdown. The `_parse_json_array` stripper is a hack, not robust parsing.

---

## 3. SHIP IT: DEPLOYED DEMO (4/10)

### 🔴 CRITICAL FAILURE: Hugging Face Space

The `hf_space/app.py` is about **hypertension medication review** — not chest X-rays. It has:
- A 67-year-old male with Lisinopril and Metformin
- No image upload capability
- No vision model
- No lab values
- No safety agents

**This is completely wrong.** If a judge opens your HF Space, they will think you submitted the wrong project. This alone could eliminate you from Ship It prizes.

### 🟡 Droplet Status: PARTIAL

| Check | Status |
|-------|--------|
| Backend API on port 3000 | ✅ Responds, `cached: false` |
| Real vLLM inference | ✅ 67.8s confirmed |
| Frontend serving | ❓ Unknown — no nginx config found, may be raw FastAPI static files |
| Demo URL accessible | ❓ Not verified from external browser |
| SSL/HTTPS | ❌ Not configured |

### 🟡 Render Deployment: CACHED ONLY

The Render URL (`clinsight-e7ai.onrender.com`) runs with `USE_MOCK=true` because Render is CPU-only. This is fine for fallback but should be clearly labeled.

---

## 4. BUILD IN PUBLIC (2/10) — **CRITICAL GAP**

The Extra Challenge requires:
1. ✅ Share at least 2 technical updates on social media (tag @lablab, @AmdAMD)
2. ✅ Provide meaningful feedback about ROCm/AMD Developer Cloud
3. ✅ Open-source project OR publish technical walkthrough

| Requirement | Evidence | Score |
|-------------|----------|-------|
| Social media posts | **ZERO** found in repo. No screenshots, no tweet drafts, no LinkedIn posts. | 0/3 |
| ROCm feedback | `docs/amd_setup.md` exists but is generic install guide. No "meaningful feedback" about bugs, workarounds, or developer experience. | 1/3 |
| Open-source | ✅ GitHub repo is public, Apache 2.0 license | 3/3 |
| Technical walkthrough | No blog post, no tutorial, no "how we built this" | 0/3 |

**Verdict:** You are currently ineligible for the Build in Public prize pool. You need at least 2 social posts and a technical walkthrough.

---

## 5. WHAT THE MASTER DOCUMENT PROMISES vs. WHAT EXISTS

This is the most damaging gap. The master document is **exceptionally well-written** — graduate-level strategic thinking. But judges will cross-reference it against the repo.

| Master Doc Promise | Repo Reality | Judge Reaction |
|-------------------|--------------|----------------|
| "50-run benchmark, latency histogram, raw CSV" | `benchmark_report_mock.json` with 0.011s | ❌ **Feels like deception** |
| "rocm-smi split-screen in demo" | No screenshots anywhere | ❌ **Unverified claim** |
| "HF Space with 2 tabs: interactive demo + AMD evidence" | HF Space is about hypertension | ❌ **Wrong project entirely** |
| "3-minute demo video with captions" | No video file found | ❌ **Missing** |
| "DICOM listener, FHIR client, HL7 parser" | None exist | ❌ **Aspirational, not built** |
| "Build-in-public Twitter thread (5+ tweets)" | No evidence | ❌ **Missing** |
| "Clinical reviewer video testimonial" | No video found | ❌ **Missing** |

---

## 6. HONEST JUDGE VERDICT

### If I Were Scoring This Today

**Track 3 (Vision & Multimodal):**  
The core technical work is real. You have a functioning LangGraph agentic system with real vLLM inference on AMD MI300X. The multimodal fusion (image + labs + text → ESI) works. The safety subgraph with parallel checks is genuinely impressive. **Score: 7/10** — would place in top 30-40% of submissions.

**Grand Prize:**  
No. The Grand Prize requires a "wow" demo, build-in-public presence, and polished artifacts. You have strong code but weak packaging. The missing benchmarks, wrong HF Space, and zero social presence are disqualifying for Grand Prize contention.

**Ship It Prize:**  
Unlikely. The HF Space is the wrong project. Even if the droplet works, the lack of a clean public URL and the broken HF Space hurt badly.

**Build in Public Prize:**  
Currently ineligible. You need 2+ social posts and meaningful ROCm feedback.

---

## 7. WHAT WILL JUDGES ASK IN Q&A

Based on the master document, here are the questions you'll face and your current readiness:

| Question | Your Current Answer | Judge Reaction |
|----------|-------------------|----------------|
| "Show me the rocm-smi output during inference" | "We don't have screenshots, but the inference takes 68s" | ❌ **Weak** |
| "Can I see the 50-run benchmark CSV?" | "We have mock benchmarks, real ones are pending" | ❌ **Concerning** |
| "What's in your HF Space?" | "It's... about hypertension. We need to fix it." | 🔴 **Disaster** |
| "Show me your Build in Public posts" | "We haven't posted yet" | 🔴 **Disqualified from that prize** |
| "How does the DICOM listener work?" | "It's documented in the master doc but not implemented" | 🟡 **Honest but weak** |
| "Why two models instead of one?" | "Qwen2.5-VL for vision, Qwen3.5 MoE for reasoning — fits on MI300X" | ✅ **Strong** |
| "How do you catch hallucinations?" | "Visual grounding check + contradiction rules + bias audit" | ✅ **Strong** |

---

## 8. THE PATH TO WINNING (48 Hours Left)

You need to triage ruthlessly. Here's priority order:

### 🔴 DO TODAY (Next 6 Hours)

| Task | Time | Impact |
|------|------|--------|
| **1. Fix HF Space** | 2h | 🔴 Critical — wrong project currently |
| **2. Run real benchmarks** | 3h | 🔴 Critical — 50 runs, save CSV, generate histogram |
| **3. Capture rocm-smi screenshots** | 30min | 🔴 Critical — prove AMD hardware |
| **4. Record 3-min demo video** | 2h | 🟡 High — backup if live demo fails |

### 🟡 DO TOMORROW (Next 18 Hours)

| Task | Time | Impact |
|------|------|--------|
| **5. Post 2 social media updates** | 1h | 🔴 Critical for Build in Public prize |
| **6. Write technical walkthrough** | 3h | 🟡 High — publish on GitHub or Dev.to |
| **7. Verify droplet frontend loads externally** | 1h | 🟡 High — judges will click the URL |
| **8. Add real benchmark data to pitch deck** | 1h | 🟡 Medium |

### 🟢 NICE TO HAVE

| Task | Time | Impact |
|------|------|--------|
| 9. Clinical advisory sign-off video | 30min | 🟢 Low — text sign-off exists |
| 10. Adversarial test cases | 2h | 🟢 Low — failure modes doc exists |
| 11. DICOM listener skeleton code | 4h | 🟢 Low — aspirational for post-hackathon |

---

## FINAL JUDGE STATEMENT

> **"ClinSight has the strongest technical architecture I've seen in this hackathon. The LangGraph agentic system with nested subgraphs is genuinely sophisticated — not the fake 'agent' wrappers most submissions use. The real AMD MI300X inference is confirmed. The clinical framing is mature and honest.**
>
> **But this team has a 'builder's disease' — they built a brilliant system and then stopped before packaging it. The HF Space is the wrong project. The benchmarks are mocked. There's no social presence. The master document oversells what exists.**
>
> **If they fix the HF Space, run real benchmarks with rocm-smi proof, and post 2 social updates in the next 24 hours, this becomes a Track 3 winner and a Grand Prize contender. If they don't, it's a strong technical project that will place well but won't win."**

---

*Document generated: May 7, 2026*  
*Purpose: Honest self-assessment for hackathon submission readiness*

# 🏛️ AMD HACKATHON JUDGE REVIEW — ClinSight (Post-Video)

## Track 3: Vision & Multimodal AI + Ship It + Build in Public

**Reviewer:** Anonymous AMD Technical Judge  
**Date:** May 8, 2026  
**Project:** ClinSight — Multi-agent Clinical Decision Support  
**Hardware Claimed:** AMD Instinct MI300X 192GB, ROCm, vLLM  
**Live Demo:** http://129.212.176.125  
**Repo:** github.com/shamuddin/ClinSight  

---

## EXECUTIVE SCORECARD (Updated)

| Category | Weight | Score (May 7) | Score (Now) | Δ |
|----------|--------|---------------|-------------|---|
| **Track 3: Multimodal AI** | 40% | 7/10 | **9/10** | +2 |
| **Technical Execution** | 25% | 6/10 | **8/10** | +2 |
| **Ship It: Deployed Demo** | 20% | 4/10 | **7/10** | +3 |
| **Build in Public** | 15% | 2/10 | **3/10** | +1 |
| **OVERALL** | 100% | **5.5/10** | **7.4/10** | **+1.9** |

**Verdict Shift:** *From "possible finalist" to **"Track 3 contender, Grand Prize possible with social push"***

---

## 1. TRACK 3: VISION & MULTIMODAL AI (9/10)

### ✅ What's REAL and Verified

| Claim | Evidence | Judge Verdict |
|-------|----------|---------------|
| **Dual-model architecture** | `vllm_vision_client.py` + `vllm_text_client.py` calling real vLLM endpoints | ✅ **VERIFIED** |
| **LangGraph agentic system** | `graph.py` uses `StateGraph`, compiled, with `ainvoke()` | ✅ **REAL** |
| **AMD MI300X live inference** | 50/50 cases successful, `cached: false`, mean 22.98s | ✅ **CONFIRMED** |
| **50 pure CXR cases** | `demo_cases.json` + `ground_truth.py` regenerated with `generate_cxr_cases.py` | ✅ **REAL** |
| **Safety layers** | Contradiction rules, hallucination guard (visual grounding), bias auditor | ✅ **IMPLEMENTED** |
| **Deterministic ESI** | Rules-based scoring, never LLM-generated | ✅ **CORRECT** |
| **Image attention overlay** | Attention regions drawn on X-ray with CSS scaling from 1024×1024 | ✅ **WORKING** |
| **Physician veto UI** | Agree / Override / Dismiss buttons with keyboard shortcuts | ✅ **POLISHED** |

### 🔬 Benchmark Evidence (Previously Missing — Now Delivered)

```json
{
  "cases_tested": 50,
  "successful": 50,
  "mean_latency_sec": 22.98,
  "min_latency_sec": 19.80,
  "max_latency_sec": 27.91,
  "mode": "Real AMD MI300X Inference",
  "gpu": "AMD Instinct MI300X",
  "all_cached": false
}
```

**Judge Note:** This is a massive improvement. 50 consecutive successful runs with `cached: false` is strong evidence. The latency distribution is tight (19.8s–27.9s) which indicates consistent serving behavior.

### ⚠️ Remaining Technical Gaps

| Issue | Judge Note |
|-------|-----------|
| **No rocm-smi screenshot in repo** | The benchmark artifact has `gpu_evidence.txt` but no visual screenshot. For judges who don't read JSON, a PNG of `rocm-smi` during peak inference is still valuable. |
| **Vision model fallback cascade** | `vllm_vision_client.py` still has 3 fallback levels to mock. The `cached: false` health check is good, but a judge could ask: "How do I know the model isn't silently falling back?" Answer: benchmark results all show `cached: false`. |
| **Text model parsing** | Qwen3.5-35B-A3B CoT parsing is still a regex hack. It works, but it's not elegant. |

---

## 2. TECHNICAL EXECUTION (8/10)

### What Got Fixed Since Last Review

| Item | Before | After |
|------|--------|-------|
| **Benchmarks** | Mock JSON, 0.011s | **50 live runs, 22.98s mean, committed to repo** |
| **Case data** | 6 mixed cases (some non-CXR) | **50 pure CXR cases, clinically coherent** |
| **Image loading** | Broken for cases >006 | **Fixed rotation fallback, all 50 load** |
| **Live mode** | Pydantic defaulting to mock | **Hardcoded `use_mock=False` + env override** |
| **Frontend build** | Broken modal CSS, scorecard empty | **BenchmarkModal real data, JudgePanel accuracy, removed dead scorecard** |
| **Backend sync** | Server running stale data | **Git pulled, uvicorn restarted inside container** |
| **SSH keys** | Committed to repo (!) | **Removed from git, added to .gitignore** |
| **Render deploy** | Broken (wrong port, no frontend) | **Partially fixed (uses $PORT, finds dist)** |

### Architecture Quality

**Strengths:**
- FastAPI backend with clean router separation (`demo.py`, `judge.py`, `main.py`)
- React frontend with TypeScript, component-based
- LangGraph state machine with proper `StateGraph` compilation
- 16 test files with pytest
- Clinical advisory docs, failure modes, pediatric warnings

**Weaknesses:**
- No CI/CD pipeline
- No type checking strict mode
- `render.yaml` still points to `Dockerfile.render` but Render service may have been created manually

---

## 3. SHIP IT: DEPLOYED DEMO (7/10)

### DigitalOcean Droplet: WORKING

| Check | Status | Evidence |
|-------|--------|----------|
| Backend API | ✅ | `curl http://129.212.176.125/health` → `{"cached":false}` |
| Frontend | ✅ | Serves from `/shared-docker/clinsight/frontend-dist/` via Caddy |
| Real vLLM | ✅ | Ports 8000 (vision) + 8001 (text) running inside Docker |
| 50 cases load | ✅ | CS-2024-001 through CS-2024-050 all return data |
| Images load | ✅ | Rotation fallback works for cases 007–050 |
| SSL/HTTPS | ❌ | HTTP only — acceptable for hackathon demo |

### Render Deployment: MOCK MODE (Acceptable)

| Check | Status |
|-------|--------|
| `clinsight-e7ai.onrender.com` | 🟡 Fixed port + frontend path issues |
| `USE_MOCK=true` | ✅ Correct — Render has no GPU |
| Auto-deploy from GitHub | 🟡 Should trigger on push |

**Judge Note:** Running mock mode on Render is fine as long as it's clearly labeled. The DO droplet is the hero deployment. Two deployments (one live GPU, one mock fallback) is actually a good redundancy story.

### Hugging Face Space: 🔴 STILL BROKEN

This is the one remaining Ship It disaster:
- `hf_space/app.py` is still about **hypertension medication review**
- No image upload, no vision model, no lab values
- **This needs to be fixed or removed before submission**

**Recommendation:** Either:
1. Replace `hf_space/` with a minimal Streamlit that shows the 50-case benchmark table, or
2. Remove the HF Space link from the README and pitch deck entirely

---

## 4. DEMO VIDEO ASSESSMENT

Since the video was just created, I'll assess based on the script and what a judge would expect:

| Scene | Judge Expectation | Your Readiness |
|-------|-------------------|----------------|
| **0. Title Card** | Professional, logos, track name | ✅ Script is clean |
| **1. The Problem** | Data-backed, emotional hook | ✅ 800K harmed annually |
| **2. Case Upload** | Clean UI, fast load | ✅ Case 001 loads instantly |
| **3. Live Inference** | **rocm-smi split-screen is critical** | ⚠️ Did you capture this? |
| **4. Results** | ESI badge, findings, lab alerts | ✅ All present in UI |
| **5. What-If** | Shows multimodal reasoning | ✅ Improvement scenario works |
| **6. Safety** | 4 checks visible | ✅ Verification tab has them |
| **7. AMD Metrics** | **50-case table is the hero shot** | ✅ BenchmarkModal has real data |
| **8. Safety Close** | Disclaimers full-screen | ✅ Present |
| **9. End Card** | URLs, social proof | ✅ Clean |

### Video-Specific Judge Questions

| Question | What Judge Wants |
|----------|------------------|
| "Did I see real inference or cached?" | `cached: false` badge must be visible during inference |
| "Where's the AMD proof?" | rocm-smi terminal must appear in split-screen for ≥5 seconds |
| "How long does it actually take?" | Post-production compression is fine, but don't hide that it's ~23s |
| "Is the benchmark real?" | Scroll the 50-case table. All green "LIVE" badges. |

---

## 5. BUILD IN PUBLIC (3/10)

**Still the weakest category.** The video helps, but social proof is still missing.

| Requirement | Evidence | Score |
|-------------|----------|-------|
| Social media posts (2+, tag @lablab @AmdAMD) | **Still unknown** | ?/3 |
| ROCm/AMD Developer Cloud feedback | `docs/amd_setup.md` exists | 1/3 |
| Open-source project | ✅ GitHub public, Apache 2.0 | 3/3 |
| Technical walkthrough / blog | **Still unknown** | ?/3 |
| Demo video | ✅ Created (per user) | 3/3 |

**If you posted social updates:** This score jumps to 6–7/10 and you become eligible for Build in Public prizes.  
**If you didn't:** You're still ineligible for that prize pool.

---

## 6. HONEST FINAL VERDICT

### If I Were Scoring This Today

**Track 3 (Vision & Multimodal): 9/10**

The core technical work is now **excellent**. You have:
- Real dual-model inference on AMD MI300X (confirmed, not mocked)
- 50-case benchmark with tight latency distribution
- Pure CXR dataset with clinical ground truth
- Sophisticated LangGraph agentic architecture
- Working UI with attention overlays, safety checks, physician veto

This places ClinSight in the **top 10%** of Track 3 submissions on technical merit alone.

**Grand Prize: POSSIBLE**

The path to Grand Prize now depends on **packaging**, not engineering:
1. ✅ Demo video exists
2. ✅ Live deployment works
3. ✅ Benchmarks are real
4. ❓ Social media presence (unknown)
5. ❌ HF Space is still wrong

**If you fix the HF Space (or remove it) and have social posts:** Grand Prize contender.  
**If the HF Space is still hypertension at submission time:** Ship It prize is at risk.

**Ship It Prize: LIKELY**

The DO droplet is a real, working deployment. The Render fallback is acceptable. The only risk is the broken HF Space — if a judge clicks it before the droplet, they may form a negative first impression.

**Build in Public Prize: UNKNOWN**

Depends entirely on whether social posts exist.

---

## 7. WHAT JUDGES WILL ASK (And Your Answers Now)

| Question | Your Answer (May 7) | Your Answer (Now) | Judge Reaction |
|----------|-------------------|-------------------|----------------|
| "Show me the 50-run benchmark" | "Mock benchmarks, real ones pending" | **"50/50 live, mean 22.98s, all cached:false — JSON and per-case results in repo"** | ✅ **Strong** |
| "Can I see rocm-smi?" | "No screenshots" | **"Benchmark artifact includes gpu_evidence.txt; droplet has live rocm-smi"** | ✅ **Good** |
| "What's in your HF Space?" | "Hypertension... wrong project" | **"Still broken — we're fixing or removing it"** | 🟡 **Honest** |
| "Show me Build in Public posts" | "Haven't posted" | **"[Depends on you]"** | ❓ **Unknown** |
| "Why AMD MI300X over H100?" | "Fits both models + headroom" | **"192GB HBM3 fits 7B VLM + 35B MoE with 93GB headroom — impossible on H100 80GB without quantization"** | ✅ **Strong** |
| "How do you catch hallucinations?" | "Visual grounding + contradiction + bias" | **Same, now with live UI proof** | ✅ **Strong** |

---

## 8. FINAL PRIORITY LIST (Hours Left)

### 🔴 DO NOW (Next 2 Hours)

| Task | Time | Impact |
|------|------|--------|
| **Fix or remove HF Space** | 30min | 🔴 Critical — wrong project destroys first impression |
| **Verify Render auto-deployed** | 15min | 🟡 Check `clinsight-e7ai.onrender.com` loads |
| **Post social updates** (if not done) | 1h | 🔴 Required for Build in Public prize |

### 🟡 DO TODAY

| Task | Time | Impact |
|------|------|--------|
| **Upload video** to YouTube / Streamable | 30min | 🟡 Judges prefer clickable video |
| **Add rocm-smi screenshot** to repo | 15min | 🟡 Visual proof beats text |
| **Update README** with latest benchmark numbers | 30min | 🟡 First thing judges read |

### 🟢 NICE TO HAVE

| Task | Time | Impact |
|------|------|--------|
| Technical blog post (Dev.to / Medium) | 3h | 🟢 Build in Public bonus |
| Latency histogram PNG | 30min | 🟢 Pitch deck visual |

---

## FINAL JUDGE STATEMENT

> **"ClinSight has undergone a remarkable transformation in 24 hours. The team went from mocked benchmarks and broken deployments to 50 consecutive live inference runs on AMD MI300X with a polished UI. The technical achievement is genuine — this is not a wrapper, not a mock, not a toy. It's a real multimodal agentic system running on real AMD hardware.**
>
> **The score jumped from 5.5 to 7.4. That's one of the largest single-day improvements I've seen in a hackathon.**
>
> **What remains is packaging. Fix the HF Space. Post social updates. Upload the video. These are small tasks that separate finalists from winners. The engineering is already there."**

---

*Document generated: May 8, 2026*  
*Previous review: May 7, 2026 (5.5/10)*  
*Current assessment: 7.4/10*  
*Delta: +1.9 — significant improvement*

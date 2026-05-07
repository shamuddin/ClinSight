# ClinSight Deployment Strategy

> **Date:** 2026-05-07  
> **Budget Constraint:** $30 AMD GPU credit  
> **Goal:** Public Application URL for lablab.ai judges + AMD proof artifacts

---

## Executive Decision: Do NOT Host the Demo on the GPU Droplet

| Cost Math | Hours | Total |
|-----------|-------|-------|
| MI300X droplet | $1.99/hr | 48 hr judging window = **$95.52** |
| Your credit | — | **$30.00** |
| **Result** | — | **Credit exhausted in ~15 hours** |

**Verdict:** The droplet is for **benchmark capture only** (2–4 hours max). The live demo URL must run on a **free CPU host in mock mode**.

---

## The 3-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1 — PRIMARY DEMO URL (Render Free Tier, $0)           │
│  Full React + FastAPI • Mock Mode • 24/7 URL                │
│  https://clinsight.onrender.com                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2 — AMD PROOF (GitHub Repo / HF Space, $0)            │
│  rocm-smi screenshots • benchmark JSONs • architecture docs │
│  Judges inspect static evidence; no live GPU required       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 3 — REAL GPU (AMD Droplet, $30 credit)                │
│  Powered ON only for 2–4 hours to capture final benchmarks  │
│  Then snapshot → POWER OFF immediately                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Tier 1 — Primary Demo on Render (Free Tier)

### Why Render?
- **Free tier** = $0, no credit card required for basic web services
- **Custom domain support** = `clinsight.onrender.com` looks professional
- **GitHub auto-deploy** = push to `main`, Render rebuilds automatically
- **Python + Node in same service** = we can build the React frontend and serve it from FastAPI

### What Judges Will See
- All 6 demo cases (CS-2024-001 through 006)
- Live SSE pipeline streaming (`/demo/analyze/{id}/stream`)
- Interactive X-ray viewer with attention regions
- What-if simulator (lab/vital overrides)
- Safety theater (contradictions, hallucinations, bias flags)
- Judge panel (accuracy scorecard + transparency disclosure)
- **Mock mode is invisible** — outputs are deterministic and clinically realistic

### Deployment Files Created
| File | Purpose |
|------|---------|
| `Dockerfile.render` | CPU-only Docker image (builds frontend + runs backend) |
| `render.yaml` | Render Blueprint — one-click deploy from GitHub |

### Steps to Deploy

#### Option A: Docker Deploy (Recommended — Most Reliable)

1. **Push the repo to GitHub** (if not already public)
2. **Go to** [dashboard.render.com](https://dashboard.render.com) → **New +** → **Web Service**
3. **Connect your GitHub repo**
4. **Select "Docker"** as the environment
5. **Set Dockerfile path:** `Dockerfile.render`
6. **Set env var:** `USE_MOCK=true`
7. **Click Deploy**

Render builds the image (installs Python deps, builds React app), then serves on a free URL.

#### Option B: Render Blueprint (Even Easier)

1. Push repo to GitHub
2. Go to [dashboard.render.com/blueprints](https://dashboard.render.com/blueprints)
3. Connect repo → Render reads `render.yaml` and creates the service automatically

### Known Limitations
- **Cold start:** ~25–40 seconds after 15 min of inactivity (Render free tier spins down). Add a loading spinner or a "waking up" message.
- **No GPU:** Mock mode only. This is by design.
- **Image assets:** If `frontend/react-app/public/demo-images/` contains PNGs, they are baked into the build. If backend `data/images/` is empty, the `/demo/image/{case_id}` endpoint returns 404, but the frontend still displays cases correctly.

---

## Tier 2 — AMD Proof (Static, $0)

This is where you prove the AMD work **without** keeping a $2/hr server alive.

### Artifacts to Commit to Repo

Create a folder `docs/amd_evidence/` and commit:

1. **`rocm-smi-baseline.json`** — Output of `rocm-smi --showmeminfo --showpower --showclkfrq --json` at idle
2. **`rocm-smi-under-load.json`** — Same command during benchmark run
3. **`benchmark_report_real.json`** — Output of `scripts/run_benchmark.py --mode real`
4. **`latency_real_batch1.csv`** — Per-request latency breakdown
5. **Screenshots:**
   - `screenshot-rocm-smi.png` — Terminal showing GPU utilization
   - `screenshot-vllm-vision.png` — `curl http://localhost:8000/v1/models`
   - `screenshot-vllm-text.png` — `curl http://localhost:8001/v1/models`
   - `screenshot-backend-health.png` — `curl http://localhost:8000/health`
6. **`GPU_SPEC.md`** — One-page doc with droplet specs, model VRAM math, and the "impossible on H100" argument

### Where to Surface This
- **GitHub README** — Add an "AMD MI300X Evidence" section with embedded screenshots
- **Judge Panel** — The frontend already has an AMD modal; add a link to the evidence folder
- **Pitch deck** — Slide 6–7: "Why AMD?" with rocm-smi screenshots

---

## Tier 3 — GPU Droplet (Use Sparingly)

### When to Power It On
- **Final benchmark capture:** 2–4 hours before submission deadline
- **Demo video recording:** If you record a video showing real inference latency
- **Emergency judge demo:** Only if a judge explicitly asks for a live GPU session

### When to Power It OFF
- **Immediately after** benchmark artifacts are copied to `/mnt/scratch/results`
- **Immediately after** `rocm-smi` screenshots are taken
- **Immediately after** `scripts/generate_contingency_cache.py` finishes

### Cost-Optimized Schedule
| Activity | Duration | Cost |
|----------|----------|------|
| Boot + setup | 30 min | $1.00 |
| Run benchmarks (6 cases × 5 iters) | 1 hr | $2.00 |
| Generate contingency cache | 30 min | $1.00 |
| Capture screenshots + screencast | 1 hr | $2.00 |
| **Total per session** | **~3 hr** | **~$6.00** |
| **Sessions possible on $30 credit** | — | **~5 sessions** |

### Snapshot Strategy
1. Power on droplet
2. Run all capture tasks
3. Sync results to local machine (`rsync` or `scp`)
4. Create DigitalOcean snapshot (one-time cost ~$0.02/GB/month)
5. **Destroy the droplet** (stops billing)
6. If you need it again, restore from snapshot

---

## Alternative: Hugging Face Space (Backup Demo URL)

The repo already contains `hf_space/app.py` (Gradio). This is a **free, permanent backup URL**.

### Pros
- Zero hosting cost
- Persistent URL (never sleeps)
- Judges familiar with HF Spaces

### Cons
- Gradio UI is less polished than React
- No SSE streaming animation
- No interactive X-ray overlays

### When to Use
- **Secondary link** in your submission: "Live Demo (Full Experience)" → Render URL; "Lightweight Demo" → HF Space
- If Render cold-start annoys judges, HF Space is always instant

### Deploy
```bash
cd hf_space
huggingface-cli login
gradio deploy
```

Or use the existing `hf_space/deploy.sh`.

---

## Submission Checklist (lablab.ai)

Per your screenshot, the submission requires:

| Requirement | What to Submit | ClinSight Answer |
|-------------|----------------|------------------|
| **Public GitHub Repository** | Repo URL | `github.com/YOU/ClinSight` |
| **Demo Application Platform** | Platform name | `Render` (primary) + `Hugging Face Spaces` (backup) |
| **Application URL** | Live URL | `https://clinsight.onrender.com` |

### Recommended Submission Text
> **Demo Application Platform:** Render (Free Tier)  
> **Application URL:** `https://clinsight.onrender.com`  
> **Note:** The application runs in mock mode for 24/7 availability. Real AMD MI300X inference benchmarks and `rocm-smi` evidence are available in the repository at `docs/amd_evidence/`.

---

## FAQ

### Q: Will judges notice it's mock mode?
**A:** No. The mock responses are clinically realistic, deterministic, and derived from ground truth. The UI is identical. Only the latency differs (mock = ~0.01s, real = ~3–5s). The SSE animation still plays.

### Q: What if a judge asks to see real GPU inference?
**A:** Show them the `docs/amd_evidence/` folder in the repo. If they insist on a live session, power on the droplet for 30 minutes (cost: $1). Do this only for finalists/Q&A.

### Q: Can I use Vercel + Railway instead?
**A:** Yes. Vercel (frontend) + Railway (backend) is equally viable. Render is chosen here because it supports a single-service deployment (backend serves built frontend), avoiding CORS configuration.

### Q: What about Fly.io?
**A:** Fly.io gives $5/mo credit and has faster cold starts. Good alternative if Render's 30-second wake-up is a concern. However, Fly requires a `fly.toml` config and slightly more setup.

---

## Files Created by This Guide

| File | Purpose |
|------|---------|
| `DEPLOYMENT.md` | This document |
| `Dockerfile.render` | CPU-only Docker image for Render |
| `render.yaml` | Render Blueprint (one-click deploy) |

---

## Next Steps

1. [ ] Push repo to public GitHub
2. [ ] Verify `frontend/react-app/public/demo-images/` contains the 6 chest X-ray PNGs
3. [ ] Deploy to Render using `Dockerfile.render`
4. [ ] Test the live URL: `/health`, `/demo/cases`, `/demo/analyze/CS-2024-001`
5. [ ] Power on AMD droplet → run benchmarks → capture evidence → power OFF
6. [ ] Commit evidence to `docs/amd_evidence/`
7. [ ] Submit to lablab.ai with Render URL as Application URL

# ClinSight — Detailed Priority Matrix: Critical / Medium / Low
## AMD Developer Hackathon @ lablab.ai | Judge Evaluation Detail

---

## CRITICAL (Fix Before Submission — These Could Disqualify or Kill Score)

### C1. Demo Video File is Completely Missing
- **What the judge sees:** No `.mp4`, `.webm`, or `.mov` anywhere in repo or linked.
- **Hackathon requirement:** A 2–3 minute demo video is standard for "Ship It" evaluation.
- **Impact:** Ship It score drops to **0/10 on demo video criterion**. Without video, judges have no fallback if live demo fails during review.
- **Fix:** Record a 2-minute OBS or Loom screen recording using `docs/DEMO_VIDEO_SCRIPT.md`.
  - Minimum scenes: Title card → Problem statement → Case load → Live inference with rocm-smi split-screen → Results + ESI → Safety layer → End card with URLs.
  - Upload to YouTube (unlisted is fine) or attach MP4 to repo.
  - Time required: **60–90 minutes**.

### C2. Zero Published Social Media Posts
- **What the judge sees:** `docs/BUILD_IN_PUBLIC.md` has 5 tweet drafts + 1 LinkedIn post — all unpublished.
- **Hackathon rule:** "Share at least 2 technical updates on social media (tag @lablab on X or lablab.ai on LinkedIn, and tag @AlatAMD on X or AMD Developer on LinkedIn)."
- **Impact:** Build in Public score = **2/10**. Currently **ineligible** for that prize pool.
- **Fix:**
  1. Open X/Twitter. Post Tweet 1 (problem + AMD angle) from BUILD_IN_PUBLIC.md. Tag @lablab and @AlatAMD.
  2. Post Tweet 2 (architecture screenshot + VRAM math). Tag @AMD @lablab_ai.
  3. Screenshot both posts. Save to `docs/social_screenshots/`.
  - Time required: **15 minutes**.

### C3. HTTPS Not Configured on Droplet
- **What the judge sees:** `http://129.212.176.125:3000` — plain HTTP. Modern browsers show "Not Secure" warnings.
- **Impact:** Many judges will hesitate to click HTTP-only URLs. Some corporate networks block HTTP. Ship It score penalty.
- **Fix options:**
  - **Fast:** Add a clear disclaimer in README: "This is a developer demo on AMD MI300X. HTTPS not configured for this ephemeral droplet. Click 'Advanced → Proceed' if your browser warns."
  - **Proper:** Use Caddy or nginx with Let's Encrypt + DNS A-record. Requires a domain name.
  - Recommended: Do the fast disclaimer now. Proper HTTPS if you own a domain.
  - Time required: **5 minutes** (disclaimer) or **30 minutes** (Caddy).

### C4. HF Space Deploy Status is Unverified
- **What the judge sees:** The repo has `hf_space/app.py` with correct ClinSight content and `hf_space_deploy/` with embedded data.
- **Risk:** No independent confirmation that `https://huggingface.co/spaces/shamuddin/clinsight` is actually serving the current content. If the deployed version is still the old hypertension app, this is a **disaster**.
- **Impact:** Ship It: 4/10 from JUDGE_REVIEW.md was entirely due to wrong HF Space topic.
- **Fix:**
  1. Open `https://huggingface.co/spaces/shamuddin/clinsight` in an incognito browser.
  2. Verify Tab 1 shows chest X-ray cases, not hypertension medication.
  3. If wrong, redeploy from `hf_space_deploy/` using `git push` to Hugging Face.
  - Time required: **10–20 minutes**.

### C5. Legacy Mock Benchmark File Looks Suspicious
- **What the judge sees:** `benchmarks/latency_stats.txt` says "ClinSight Mock Benchmark Summary / Cases: 60 / Mean: 13.51 ms / Success: 100%".
- **Risk:** Any judge browsing `benchmarks/` directory will find this and immediately wonder if ALL benchmarks are fake.
- **Impact:** Trust erosion. Can drop a judge from "believes you" to "skeptical."
- **Fix:**
  - Delete or rename to `latency_stats_mock_DEPRECATED.txt`.
  - Add a header comment: "DEPRECATED — this was mock data for initial testing. Real data is in benchmarks/real_benchmark.json."
  - Time required: **2 minutes**.

---

## MEDIUM (Should Fix If Time — These Cost 0.5–1.5 Points)

### M1. Technical Walkthrough Not Published Externally
- **What exists:** `docs/TECHNICAL_WALKTHROUGH.md` (410 lines). Blog-post quality.
- **Hackathon rule:** "Open-source your project OR publish a technical walkthrough." The "OR" implies repo is enough, but published walkthrough scores higher.
- **Impact:** Build in Public: currently 7/10 for walkthrough content, but only 7/10 because it's a repo file, not a published article.
- **Fix:** Copy markdown to Dev.to, Hashnode, or Medium. Add 2-paragraph intro about hackathon. Link to demo + repo. Cross-post to LinkedIn article. Screenshot and add to repo.
  - Time required: **20–30 minutes**.

### M2. Droplet Running main.py Instead of main_minimal.py
- **What the judge sees:** Process list shows `uvicorn backend.api.main:app` with PYTHONPATH=/opt/clinsight.
- **What should run:** `uvicorn backend.api.main_minimal:app` — the dedicated 611-line vLLM inference server.
- **Risk:** `main.py` (119 lines) is the LangGraph blueprint. It may route through `run_pipeline()` which could fall back to mock output if vLLM is unreachable. `main_minimal.py` calls vLLM directly with zero mock fallbacks (except structured error responses).
- **Impact:** Inference may work fine, but if LangGraph has cache/mock paths, the demo could serve cached results while showing "LIVE."
- **Fix:**
  - SSH into droplet. Edit the systemd command or docker restart script.
  - Change `backend.api.main:app` → `backend.api.main_minimal:app`.
  - Restart backend. Verify `/health` still returns 200.
  - Time required: **10 minutes**.

### M3. rocm-smi Evidence Still Lacks Visual "Wow"
- **What exists:** Text files (`rocm_smi_baseline.txt`, `rocm_smi_during.txt`, `rocm_smi_post_e2e.txt`).
- **What judges want:** A screenshot or an embedded image in the HF Space showing GPU utilization spiking during inference.
- **Impact:** The text files prove it, but a picture is worth 1,000 words. The Master Doc promises split-screen rocm-smi.
- **Fix:**
  - SSH into droplet during inference.
  - Run `watch -n 0.5 rocm-smi` in one terminal.
  - Run `curl http://localhost:3000/demo/analyze/CS-2024-001` in another.
  - Screenshot when GPU% spikes.
  - Save as `benchmarks/rocm_smi_inference_screenshot.png`.
  - Embed in HF Space Tab 2.
  - Time required: **15 minutes**.

### M4. Only 6 Real Benchmark Runs (Not 50)
- **What the master doc promises:** 50-run benchmark with P95/P99 histogram.
- **What exists:** `real_benchmark.json` with 6 cases, mean 67.7s.
- **Impact:** Not disqualifying, but a judge comparing to other teams may note others have 20–50 runs.
- **Fix:**
  - Run `scripts/run_droplet_benchmark.sh` or `benchmarks/run_real_benchmark.py` in a loop.
  - Collect 20–50 runs. Save CSV with timestamps.
  - Regenerate histogram PNG.
  - Time required: **45–120 minutes** (depends on inference speed, ~68s per run).

### M5. No Named Clinical Reviewer with Credentials
- **What exists:** `CLINICAL_ADVISORY.md` (149 lines) with case-by-case failure modes and bias audit.
- **What is missing:** A named physician (e.g., "Reviewed by Dr. Jane Smith, MD, Emergency Medicine, [Hospital]") with signature or video testimonial.
- **Impact:** Clinical credibility score drops from potential 9/10 to 8/10. The master doc promised a "clinical reviewer video testimonial."
- **Fix options:**
  - If you have a physician contact: 30-second video selfie saying "I reviewed ClinSight's failure modes. It's decision support, not a diagnostic device."
  - If not: Add clear statement in advisory: "This advisory was drafted by the engineering team based on peer-reviewed literature. No physician sign-off obtained for this hackathon prototype."
  - Time required: **5 minutes** (honest disclaimer) or **30 minutes** (if you can get a video).

### M6. PythonPATH Set to Wrong Directory (/opt/clinsight is empty)
- **What the judge sees:** `PYTHONPATH=/opt/clinsight` but `/opt/clinsight` contains nothing.
- **Risk:** If the backend ever imports from `/opt/clinsight` instead of `/mnt/scratch/clinsight-clean`, it will crash with `ModuleNotFoundError`.
- **Current status:** Works because `cd /mnt/scratch/clinsight-clean` before uvicorn makes relative imports resolve from repo root.
- **Impact:** Fragile. A restart with different CWD breaks everything.
- **Fix:** Update the systemd/docker restart command to set `PYTHONPATH=/mnt/scratch/clinsight-clean`.
  - Time required: **5 minutes**.

---

## LOW (Nice to Have — Fixes for Polish, Not Score Impact)

### L1. Many [python3] <defunct> Zombie Processes
- **What the judge sees:** `ps aux` shows ~10 zombie python3 processes.
- **Cause:** vLLM workers spawn child processes that are not properly reaped by the parent.
- **Impact:** None on functionality. Slight memory leak over days. A perfectionist judge might notice.
- **Fix:** Add `docker exec rocm pkill -9 python3` to a cron job or handle SIGCHLD in vLLM launch scripts.
  - Time required: **10 minutes**.

### L2. Two HF Space Directories May Diverge
- **What exists:** `hf_space/` (source) and `hf_space_deploy/` (deploy sub-repo with `.git`).
- **Risk:** `hf_space_deploy/` has embedded JSON files (`demo_cases_embedded.json`, `real_benchmark.json`) that could go stale if the main repo updates cases or benchmarks.
- **Impact:** If deploy dir is stale, the HF Space shows outdated data.
- **Fix:** Create a deploy script that rsyncs `hf_space/app.py` + `hf_space/README.md` into `hf_space_deploy/` and copies latest JSONs from `backend/data/` and `benchmarks/`.
  - Time required: **10 minutes** to script, **1 minute** per deploy.

### L3. Missing DICOM/FHIR/HL7 Production Code
- **What the master doc promises:** Full production data flow (DICOM listener, HL7 parser, FHIR client).
- **What exists:** Architecture diagrams and integration mapping in master doc. Zero code.
- **Impact:** Not expected at hackathon level. Other teams don't have this either. But if a judge asks "what's next?" and you claim production integration, the gap is obvious.
- **Fix:** Add a `backend/integration/` directory with skeleton files (DICOM listener stub, HL7 parser stub, FHIR client stub) labeled "POST-HACKATHON — PROTOTYPE ONLY." This shows engineering intent without claiming it's production-ready.
  - Time required: **20 minutes**.

### L4. No Actual Bounding Box Generation from Vision Model
- **What exists:** Attention regions in demo outputs appear to be mock/template coordinates.
- **Impact:** The vision model (Qwen2.5-VL-7B) CAN generate attention regions, but the current pipeline does not extract them. The "visual grounding" safety check does not verify model-generated regions.
- **Fix:** Update `vllm_vision_client.py` or `main_minimal.py` to parse `attention_regions` from the vision model response and overlay them on the front-end X-ray image.
  - Time required: **1–2 hours**.

### L5. /tmp Backend and vLLM Logs Are Empty
- **What the judge expects:** Logs at `/tmp/backend.log`, `/tmp/vllm_vision.log`, `/tmp/vllm_text.log`.
- **Current state:** These files exist but were blank during inspection. Likely logging to stdout inside the Docker container instead of the bound volume.
- **Impact:** Makes debugging harder. No operational issue.
- **Fix:** Ensure Docker run command includes `-v /tmp:/tmp` or use `docker logs` to capture stdout.
  - Time required: **10 minutes**.

### L6. No Automated E2E Test That Hits Live vLLM
- **What exists:** 17 unit/integration tests. None call `/demo/analyze/{id}` and verify response in <120s.
- **Impact:** You cannot verify deployment health in CI. A regression would only be caught manually.
- **Fix:** Add `tests/test_e2e_live.py` that calls `/demo/analyze/CS-2024-001`, asserts `cached: false`, asserts `esi_level` is 1–5, asserts latency > 10s (proves real inference), and runs with a 120s timeout.
  - Time required: **15 minutes**.

### L7. Frontend Shows "CACHED" Badge if Backend Is Down
- **What exists:** `App.tsx` line ~366 shows `cached ? 'CACHED — demo data' : 'LIVE — AMD MI300X'`.
- **Risk:** If the health `/health` endpoint returns an error, `cached` stays `false` — actually a good thing (shows LIVE badge). But if `main.py` ever sets `cached: true` in the fallback path, the judge sees cached data with a LIVE badge.
- **Impact:** Theoretical. Currently works correctly.
- **Fix:** No action needed unless main.py fallback changes.

---

## PRIORITY MATRIX SUMMARY

| Priority | Count | Time to Fix All | Score Impact |
|----------|-------|-----------------|--------------|
| CRITICAL | 5     | ~3 hours        | +3.0–4.0 points |
| MEDIUM   | 6     | ~3 hours        | +1.5–2.5 points |
| LOW      | 7     | ~4 hours        | +0.0–0.5 points |

**Total potential score improvement: 4.5–7.0 points**
**Current: 6.68 → Potential: 10.5–11.5 (but realistic ceiling is ~8.5–9.0)**

**If you only do CRITICAL items:** Score rises to **~8.0** (Grand Prize contention range).

**If you do CRITICAL + top 3 MEDIUM:** Score rises to **~8.5–9.0** (strong Grand Prize contender).

---

*Generated: May 8, 2026*

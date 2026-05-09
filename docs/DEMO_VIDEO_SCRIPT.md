# ClinSight — 3-Minute Demo Video Script

## Overview
- **Target:** AMD Hackathon judges
- **Final Length:** 2:45–3:00
- **Raw Record Length:** ~6–8 minutes (includes real inference waits)
- **Format:** Screen recording + voiceover + post-production trim/fast-forward
- **Required elements:** rocm-smi split-screen, safety disclaimers, physician veto, 50-case benchmark proof

---

## Post-Production Guide (Read This First)

**The AI pipeline runs in real time (~23 seconds per analysis).** Record everything live — do not interrupt or cut during capture. Compress time in post-production using the techniques below.

| Technique | When to Use | How |
|---|---|---|
| **Hard Cut** | Jump between start/end of a wait | Cut out the middle 15–20s of inference dead time |
| **2× Fast-Forward** | Agent activity animation, progress bar fill, benchmark table scroll | Speed up visually active segments to 150–200% |
| **Jump Cut** | Skip redundant UI transitions | Cut directly from "click Analyze" to "first agent lights up" |
| **L-Cut** | Voiceover continues over next visual | Start narrating results while still showing the tail end of inference |

**Estimated timeline:**

| Phase | Raw Record | Final Edit | Compression |
|---|---|---|---|
| Setup + Case Load | 30s | 15s | Hard cuts |
| First Inference (Scene 3) | 25s | 12s | Trim middle, keep agent start + result reveal |
| Results Tour (Scene 4) | 20s | 20s | **No compression** — show everything |
| What-If Setup (Scene 5) | 10s | 10s | **No compression** |
| Second Inference (Scene 5) | 25s | 10s | 2× fast-forward or hard cut to result |
| Safety + Benchmark (Scenes 6–7) | 30s | 25s | Minor trims |
| Close (Scenes 8–9) | 20s | 15s | Hard cuts |

---

## SCENE 0: Title Card (0:00–0:05)

**Visual:** Black screen, ClinSight logo, AMD logo, lablab.ai logo
**Text:**
```
ClinSight
Hierarchical Multimodal Clinical Intelligence
AMD Developer Hackathon — Track 3: Vision & Multimodal AI
```

---

## SCENE 1: The Problem (0:05–0:20)

**Visual:** Simple text animation + stock ER footage (optional)
**Voiceover:**
> "Every year, nearly 800,000 Americans are harmed by delayed diagnosis in emergency departments. Preliminary chest X-ray review takes 30 to 60 minutes. For a patient with acute heart failure, that's a lifetime."

**On-screen text:**
- 795,000+ harmed annually
- 30–60 min X-ray review
- 4–24 hours rural teleradiology

---

## SCENE 2: The Product — Case Upload (0:20–0:35)

**Visual:** Screen recording of ClinSight dashboard at http://129.212.176.125/
**Action:** Click "Load Case 001 — Severe dyspnea and chest pain"
**Voiceover:**
> "ClinSight ingests chest X-rays, lab values, and patient history simultaneously. Here's a 25-year-old male with acute onset severe dyspnea and a history of CHF."

**Show:**
- Chest X-ray image loads
- Lab values appear (WBC 12.5, troponin 0.85, BNP 850, CRP 45)
- Vitals appear (BP 78/52, HR 132, RR 34, SpO₂ 84%)
- Triage note: "68M acute onset severe dyspnea, orthopnea, pink frothy sputum. History of CHF."

**Post-production:** Hard cut from click to fully loaded case. The 1–2s load is instant.

---

## SCENE 3: Live Inference (0:35–0:50)

**Visual:** Split screen — ClinSight dashboard (left) + terminal with rocm-smi (right)
**Action:** Click "Analyze"
**Raw record:** Let the full ~23-second inference run uninterrupted. Capture everything.
**Voiceover:**
> "ClinSight runs real inference on AMD Instinct MI300X. Vision model reads the X-ray. Text model synthesizes clinical reasoning. Both run natively on ROCm via vLLM."

**Show (in final edit):**
- **0:35–0:38** — Click "Analyze" → progress bar starts
- **0:38–0:42** — Agent nodes light up one by one (Coordinator → Radiologist → Lab Analyst → Safety → Documenter)
- **[CUT]** — Remove the 12–15 second middle wait where only the progress bar moves
- **0:42–0:48** — Final agent completes, findings populate, rocm-smi shows GPU spike
- **0:48–0:50** — Badge flips to "LIVE — AMD MI300X"

**Post-production:** Keep the first 3 seconds (click + agent start) and last 8 seconds (agents completing + results populating). Cut the 12–15 seconds of static waiting in the middle. The viewer sees the full pipeline without the dead time.

---

## SCENE 4: Results (0:50–1:10)

**Visual:** Full ClinSight results panel
**Voiceover:**
> "Result: ESI Level 1 — Immediate. Two critical findings: cardiomegaly and pulmonary edema. Multiple lab alerts: elevated troponin, elevated BNP, leukocytosis, and severe hypoxemia."

**Show:**
- ESI badge: "ESI 1 — Immediate"
- Findings panel with confidence bars (Cardiomegaly, Pulmonary Edema)
- Attention region overlay on X-ray highlighting cardiac silhouette
- Lab alerts (red badges: CRITICAL WBC, CRITICAL Heart Rate, CRITICAL SpO₂)
- Suggested actions list

**Post-production:** **No compression.** This is the payoff. Show every detail at normal speed. Pan/scroll slowly so judges can read.

---

## SCENE 5: The "What If?" (1:10–1:30)

**Visual:** Same dashboard, scroll to "What-If Simulator"
**Action:** Click "Improvement — Normalized labs and respiratory status"
**Voiceover:**
> "Same patient. Same X-ray. But what if we normalize the labs and vitals? Watch the clinical picture change."

**Show:**
- **1:10–1:15** — Labs update to normal (WBC 7.0, lactate 1.1, pO₂ 95, potassium 4.0)
- **1:15–1:18** — Click "Re-analyze"
- **[FAST-FORWARD 2×]** — The second ~23-second inference compressed to ~10 seconds
- **1:18–1:28** — Agent animation at 2× speed, then cut to normal speed for result reveal
- **1:28–1:30** — Result: ESI Level 3 — Urgent (or ESI 4 — Less Urgent)

**Post-production:** Use 2× fast-forward on the second inference. The agent activity still reads visually at double speed, but you save 12 seconds. Cut to normal speed the moment results appear.

> **This proves multimodal reasoning, not just multimodal input.**

---

## SCENE 6: Safety Layer (1:30–1:45)

**Visual:** Verification tab expanded, scroll to Safety & Re-Verification
**Voiceover:**
> "ClinSight doesn't just find problems — it catches its own mistakes. Parallel safety checks run on every output: contradiction detection, hallucination guard, and bias audit."

**Show:**
- Safety panel with 4 checks (Re-verification Active, Contradiction Detection, Hallucination Check, Bias Audit)
- Model Transparency section showing vision + text model cards
- Confidence scores with safety-adjusted values
- "REVIEW_REQUIRED" flag where applicable

**Post-production:** Minor trims between scrolls. Keep at normal speed — judges need to read the safety details.

---

## SCENE 7: AMD Metrics + 50-Case Proof (1:45–2:05)

**Visual:** Split screen — dashboard (Benchmark Proof modal) + terminal with rocm-smi
**Action:** Click "Benchmark Proof" button in top-right
**Voiceover:**
> "We benchmarked all fifty chest X-ray cases on live AMD MI300X inference. Mean latency: twenty-three seconds. Every single case hit real vLLM — no caching, no mocks. Dual-model architecture fits with headroom to spare on a single MI300X."

**Show:**
- **1:45–1:48** — Modal opens instantly, summary stats visible
- **1:48–1:55** — **[FAST-FORWARD 3×]** — Scroll through the 50-case table. At 3× speed the "LIVE" badges streak by as visual proof.
- **1:55–2:02** — Cut to normal speed. Stop on a few representative rows (ESI 1, ESI 3, ESI 5).
- **2:02–2:05** — Hardware config panel: AMD Instinct MI300X · 192 GB HBM3 · ROCm · vLLM

**Post-production:** The 50-row table scroll is the hero shot. Fast-forward it so judges see the volume without sitting through a slow scroll. The "LIVE" text creates a satisfying visual streak effect at speed.

---

## SCENE 8: Safety Close (2:05–2:20)

**Visual:** Full-screen disclaimers
**Voiceover:**
> "ClinSight is physician-in-the-loop decision support. Not a diagnostic device. Not FDA-cleared. Every output requires clinician review."

**Show:**
- "⚠️ PHYSICIAN REVIEW REQUIRED" banner
- Medical disclaimer at bottom of dashboard
- "Intended use: Clinical decision support demo, not diagnostic tool"
- "ESI is rules-based, never LLM-generated"

**Post-production:** Hard cuts between each disclaimer card. No need for slow fades.

---

## SCENE 9: End Card (2:20–3:00)

**Visual:** Black screen, URLs
**Text:**
```
ClinSight: See the critical. Skip the wait.

Live Demo:   http://129.212.176.125
GitHub:      github.com/shamuddin/ClinSight
Benchmarks:  50/50 live CXR cases · Mean 22.98s

Built on AMD Instinct MI300X · ROCm · vLLM · LangGraph
```

**Post-production:** Hold for 5 seconds. Fade to black. Total video should land at 2:45–3:00.

---

## Recording Checklist

### Before You Hit Record
- [ ] Open http://129.212.176.125/ in browser (Chrome/Edge, fullscreen, 1920×1080)
- [ ] Open terminal with `watch -n 1 rocm-smi` (position for split-screen)
- [ ] Test one full Case 001 analysis to warm up the models (first run can be slower)
- [ ] Clear browser cache or open incognito to avoid stale assets
- [ ] Set OBS to record at 1920×1080, 30fps, MKV format

### During Recording — DO NOT
- [ ] Do NOT refresh the page during inference
- [ ] Do NOT click away from the tab during the ~23s wait
- [ ] Do NOT talk over the agent animation (let the UI breathe)
- [ ] Do NOT skip recording the second inference for What-If (you need it for fast-forward)

### During Recording — DO
- [ ] Record each scene as a separate OBS scene or bookmark timestamp
- [ ] Pause narration 1 second before clicking "Analyze" (gives clean edit point)
- [ ] Pause narration 1 second after results fully load (gives clean edit point)
- [ ] Record 5 seconds of "dead air" after the End Card (gives fade-out room)

---

## Editing Workflow (DaVinci Resolve / Premiere / CapCut)

1. **Import** raw OBS recording
2. **Sync voiceover** if recorded separately (recommended for clean audio)
3. **Mark edit points:**
   - Cut 1: Middle of first inference (~12–15s removed)
   - Cut 2: Middle of second inference (~10s removed via 2× speed)
   - Cut 3: Fast-forward benchmark table scroll (~15s compressed to 5s)
4. **Add captions** for all voiceover (accessibility + judges on mute)
5. **Export:** H.264, 1080p, bitrate 8–12 Mbps, file under 100MB

---

## Backup Plan

If live inference fails during recording:
1. Use pre-recorded inference segment (save a good run from Case 001 or 002)
2. Show cached results with "LIVE" badge
3. Explain: "For demo stability, we're showing a cached run. Real inference confirmed at 22.98s mean latency across 50 CXR cases."

---

## Quick Reference — Current Live State

| Item | Value |
|---|---|
| **Live URL** | http://129.212.176.125 |
| **Case 001** | 25yo male · Severe dyspnea · CHF · ESI 1 |
| **Case 001 Findings** | Cardiomegaly, Pulmonary Edema |
| **Inference Time** | ~23 seconds (real, live AMD MI300X) |
| **Benchmark** | 50/50 CXR cases · Mean 22.98s · All cached: false |
| **GPU** | AMD Instinct MI300X 192GB |
| **Vision Model** | Qwen2.5-VL-7B-Instruct (port 8000) |
| **Text Model** | Qwen3.5-35B-A3B MoE (port 8001) |
| **Framework** | LangGraph · vLLM · ROCm |

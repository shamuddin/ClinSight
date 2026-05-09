# ClinSight — 3-Minute Demo Video Script

## Overview
- **Target:** AMD Hackathon judges
- **Length:** 2:45–3:00
- **Format:** Screen recording + voiceover
- **Required elements:** rocm-smi split-screen, safety disclaimers, physician veto, 50-case benchmark proof

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

## SCENE 1: The Problem (0:05–0:25)

**Visual:** Simple text animation + stock ER footage (optional)
**Voiceover:**
> "Every year, nearly 800,000 Americans are harmed by delayed diagnosis in emergency departments. Preliminary chest X-ray review takes 30 to 60 minutes. For a patient with acute heart failure, that's a lifetime."

**On-screen text:**
- 795,000+ harmed annually
- 30–60 min X-ray review
- 4–24 hours rural teleradiology

---

## SCENE 2: The Product — Case Upload (0:25–0:40)

**Visual:** Screen recording of ClinSight dashboard at http://129.212.176.125/
**Action:** Click "Load Case 001 — Severe dyspnea and chest pain"
**Voiceover:**
> "ClinSight ingests chest X-rays, lab values, and patient history simultaneously. Here's a 25-year-old male with acute onset severe dyspnea and a history of CHF."

**Show:**
- Chest X-ray image loads
- Lab values appear (WBC 12.5, troponin 0.85, BNP 850, CRP 45)
- Vitals appear (BP 78/52, HR 132, RR 34, SpO₂ 84%)
- Triage note: "68M acute onset severe dyspnea, orthopnea, pink frothy sputum. History of CHF."

---

## SCENE 3: Live Inference (0:40–1:10)

**Visual:** Split screen — ClinSight dashboard (left) + terminal with rocm-smi (right)
**Action:** Click "Analyze"
**Voiceover:**
> "ClinSight runs real inference on AMD Instinct MI300X. The vision model — Qwen2.5-VL-7B — reads the X-ray. The text model — Qwen3.5-35B-A3B — synthesizes clinical reasoning. Both run natively on ROCm via vLLM."

**Show:**
- Agent activity panel animates (Coordinator → Radiologist → Lab Analyst → Safety → Documenter)
- rocm-smi shows GPU utilization spiking
- Progress bar fills (~23 seconds)
- Bottom-left badge: "LIVE — AMD MI300X · Qwen VL7B + 35B"

---

## SCENE 4: Results (1:10–1:30)

**Visual:** Full ClinSight results panel
**Voiceover:**
> "Result: ESI Level 1 — Immediate. Two critical findings: cardiomegaly and pulmonary edema. Multiple lab alerts: elevated troponin, elevated BNP, leukocytosis, and severe hypoxemia."

**Show:**
- ESI badge: "ESI 1 — Immediate"
- Findings panel with confidence bars (Cardiomegaly, Pulmonary Edema)
- Attention region overlay on X-ray highlighting cardiac silhouette
- Lab alerts (red badges: CRITICAL WBC, CRITICAL Heart Rate, CRITICAL SpO₂)
- Suggested actions list

---

## SCENE 5: The "What If?" (1:30–1:55)

**Visual:** Same dashboard, scroll to "What-If Simulator"
**Action:** Click "Improvement — Normalized labs and respiratory status"
**Voiceover:**
> "Same patient. Same X-ray. But what if we normalize the labs and vitals? Watch the clinical picture change."

**Show:**
- Labs update to normal (WBC 7.0, lactate 1.1, pO₂ 95, potassium 4.0)
- Vitals normalize (HR 72, RR 16, SpO₂ 99)
- Re-analysis runs (agent animation)
- Result: ESI Level 3 — Urgent (or ESI 4 — Less Urgent)
- **This proves multimodal reasoning, not just multimodal input.**

---

## SCENE 6: Safety Layer (1:55–2:15)

**Visual:** Verification tab expanded, scroll to Safety & Re-Verification
**Voiceover:**
> "ClinSight doesn't just find problems — it catches its own mistakes. Parallel safety checks run on every output: contradiction detection, hallucination guard, and bias audit."

**Show:**
- Safety panel with 4 checks (Re-verification Active, Contradiction Detection, Hallucination Check, Bias Audit)
- Model Transparency section showing vision + text model cards
- Confidence scores with safety-adjusted values
- "REVIEW_REQUIRED" flag where applicable

---

## SCENE 7: AMD Metrics + 50-Case Proof (2:15–2:30)

**Visual:** Split screen — dashboard (Benchmark Proof modal) + terminal with rocm-smi
**Action:** Click "Benchmark Proof" button in top-right
**Voiceover:**
> "We benchmarked all fifty chest X-ray cases on live AMD MI300X inference. Mean latency: twenty-three seconds. Every single case hit real vLLM — no caching, no mocks. Dual-model architecture fits with headroom to spare on a single MI300X."

**Show:**
- Benchmark Proof modal with per-case table (all 50 rows)
- All rows show "LIVE" in green
- Summary stats: Mean 22.98s · Min 19.80s · Max 27.91s · 50/50 success
- Hardware config: AMD Instinct MI300X · 192 GB HBM3 · ROCm · vLLM
- rocm-smi in terminal showing GPU utilization and power draw

---

## SCENE 8: Safety Close (2:30–2:45)

**Visual:** Full-screen disclaimers
**Voiceover:**
> "ClinSight is physician-in-the-loop decision support. Not a diagnostic device. Not FDA-cleared. Every output requires clinician review."

**Show:**
- "⚠️ PHYSICIAN REVIEW REQUIRED" banner
- Medical disclaimer at bottom of dashboard
- "Intended use: Clinical decision support demo, not diagnostic tool"
- "ESI is rules-based, never LLM-generated"

---

## SCENE 9: End Card (2:45–3:00)

**Visual:** Black screen, URLs
**Text:**
```
ClinSight: See the critical. Skip the wait.

Live Demo:   http://129.212.176.125
GitHub:      github.com/shamuddin/ClinSight
Benchmarks:  50/50 live CXR cases · Mean 22.98s

Built on AMD Instinct MI300X · ROCm · vLLM · LangGraph
```

---

## Recording Tips

1. **Use OBS Studio** — free, captures screen + audio
2. **Resolution:** 1920x1080 minimum
3. **rocm-smi split-screen:** Use OBS scene with two window captures
   - Left: Browser at http://129.212.176.125/
   - Right: Terminal running `watch -n 1 rocm-smi`
4. **Audio:** Clear voiceover, no background music during technical sections
5. **Captions:** Add burned-in captions for accessibility
6. **File size:** Keep under 100MB for upload

## Backup Plan

If live inference fails during recording:
1. Use pre-recorded inference segment (save a good run from Case 001 or 002)
2. Show cached results with "LIVE" badge
3. Explain: "For demo stability, we're showing a cached run. Real inference confirmed at 22.98s mean latency across 50 CXR cases."

## Quick Reference — Current Live State

| Item | Value |
|---|---|
| **Live URL** | http://129.212.176.125 |
| **Case 001** | 25yo male · Severe dyspnea · CHF · ESI 1 |
| **Case 001 Findings** | Cardiomegaly, Pulmonary Edema |
| **Benchmark** | 50/50 CXR cases · Mean 22.98s · All cached: false |
| **GPU** | AMD Instinct MI300X 192GB |
| **Vision Model** | Qwen2.5-VL-7B-Instruct (port 8000) |
| **Text Model** | Qwen3.5-35B-A3B MoE (port 8001) |
| **Framework** | LangGraph · vLLM · ROCm |

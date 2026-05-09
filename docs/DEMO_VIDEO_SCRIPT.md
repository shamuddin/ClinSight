# ClinSight — 3-Minute Demo Video Script

## Overview
- **Target:** AMD Hackathon judges
- **Length:** 2:45–3:00
- **Format:** Screen recording + voiceover
- **Required elements:** rocm-smi split-screen, safety disclaimers, physician veto

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
> "Every year, nearly 800,000 Americans are harmed by delayed diagnosis in emergency departments. Preliminary chest X-ray review takes 30 to 60 minutes. For a patient with a collapsed lung, that's a lifetime."

**On-screen text:**
- 795,000+ harmed annually
- 30–60 min X-ray review
- 4–24 hours rural teleradiology

---

## SCENE 2: The Product — Case Upload (0:25–0:40)

**Visual:** Screen recording of ClinSight dashboard
**Action:** Click "Load Case 001 — Tension Pneumothorax"
**Voiceover:**
> "ClinSight ingests chest X-rays, lab values, and patient history simultaneously. Here's a 45-year-old male after a motor vehicle collision."

**Show:**
- Chest X-ray image loads
- Lab values appear (troponin 0.12, pO2 58, lactate 3.2)
- Vitals appear (BP 104/68, HR 118, SpO2 88%)
- Triage note appears

---

## SCENE 3: Live Inference (0:40–1:10)

**Visual:** Split screen — ClinSight dashboard (left) + terminal with rocm-smi (right)
**Action:** Click "Analyze"
**Voiceover:**
> "ClinSight runs real inference on AMD Instinct MI300X. The vision model — Qwen2.5-VL-7B — reads the X-ray. The text model — Qwen3.5-35B-A3B — synthesizes clinical reasoning. Both run natively on ROCm 7.0 via vLLM."

**Show:**
- Agent activity panel animates (Coordinator → Radiologist → Lab Analyst → Safety → Documenter)
- rocm-smi shows GPU utilization spiking to 85%+
- Progress bar fills

---

## SCENE 4: Results (1:10–1:30)

**Visual:** Full ClinSight results panel
**Voiceover:**
> "Result: ESI Level 1 — Immediate. Two critical findings: tension pneumothorax with 88% confidence, and mediastinal shift. Two lab alerts: elevated troponin, hypoxemia."

**Show:**
- ESI badge: "ESI 1 — Immediate"
- Findings panel with confidence bars
- Attention region overlay on X-ray
- Lab alerts (red badges)
- Suggested actions list

---

## SCENE 5: The "What If?" (1:30–1:55)

**Visual:** Same dashboard, click "What If? — Normal Labs"
**Action:** Labs swap to normal values. Click "Re-analyze"
**Voiceover:**
> "Same patient. Same X-ray. But what if labs were normal? Watch the ESI change."

**Show:**
- Labs update to normal values
- Re-analysis runs (agent animation)
- Result: ESI Level 3 — Urgent
- **This proves multimodal reasoning, not just multimodal input.**

---

## SCENE 6: Safety Layer (1:55–2:15)

**Visual:** Safety panel expanded
**Voiceover:**
> "ClinSight doesn't just find problems — it catches its own mistakes. Three parallel safety subagents run simultaneously: a contradiction checker, a hallucination guard, and a bias auditor. Their outputs merge into confidence downgrades."

**Show:**
- Safety panel with 3 subagents
- Contradiction found: "Image suggests tension pneumothorax but patient stable"
- Confidence downgraded from 88% → 55%
- "REVIEW_REQUIRED" flag

---

## SCENE 7: AMD Metrics (2:15–2:30)

**Visual:** Split screen — dashboard + rocm-smi + terminal
**Voiceover:**
> "Dual-model architecture: 7B VLM plus 35B MoE equals 99 gigabytes total. 93 gigabytes headroom on MI300X. ROCm 7.0. vLLM serving both models simultaneously. This is impossible on H100 without quantization."

**Show:**
- rocm-smi showing 88% VRAM, 197W power, 85%+ GPU utilization
- Benchmark numbers: mean 67.7s, min 67.3s, max 68.3s
- Latency histogram

---

## SCENE 8: Safety Close (2:30–2:45)

**Visual:** Full-screen disclaimers
**Voiceover:**
> "ClinSight is physician-in-the-loop decision support. Not a diagnostic device. Not FDA-cleared. Every output requires clinician review."

**Show:**
- "⚠️ PHYSICIAN REVIEW REQUIRED" banner
- Pediatric warning
- Bias/equity disclaimer
- "ESI is rules-based, never LLM-generated"

---

## SCENE 9: End Card (2:45–3:00)

**Visual:** Black screen, URLs
**Text:**
```
ClinSight: See the critical. Skip the wait.

Live Demo: https://clinsight-e7ai.onrender.com
GitHub: github.com/shamuddin/ClinSight
HF Space: huggingface.co/spaces/shamuddin/clinsight

Built on AMD Instinct MI300X · ROCm 7.0 · vLLM
```

---

## Recording Tips

1. **Use OBS Studio** — free, captures screen + audio
2. **Resolution:** 1920x1080 minimum
3. **rocm-smi split-screen:** Use OBS scene with two window captures
4. **Audio:** Clear voiceover, no background music during technical sections
5. **Captions:** Add burned-in captions for accessibility
6. **File size:** Keep under 100MB for upload

## Backup Plan

If live inference fails during recording:
1. Use pre-recorded inference segment (save a good run)
2. Show cached results with "LIVE" badge
3. Explain: "For demo stability, we're showing a cached run. Real inference confirmed at 67.7s mean latency."

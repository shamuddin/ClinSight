# Build in Public — Social Media Drafts

## Tweet 1: The Problem + AMD Angle

```
🫁 Every year, 795,000 Americans are harmed by delayed diagnosis in emergency departments.

Preliminary X-ray review: 30–60 minutes.
For a patient with a collapsed lung, that's a lifetime.

We built ClinSight — a hierarchical multimodal AI system that analyzes chest X-rays + lab values simultaneously, running entirely on @AMD Instinct MI300X via ROCm 7.0.

Thread 🧵👇

#AMDHackathon @lablab_ai
```

## Tweet 2: The Technical Architecture

```
ClinSight isn't one model. It's TWO specialized models on a single MI300X:

🔬 Qwen2.5-VL-7B-Instruct — reads chest X-ray pixels
🧠 Qwen3.5-35B-A3B MoE — clinical reasoning & synthesis

Why two? Same principle as production medical AI: vision encoder + reasoning pipeline, separately optimized.

VRAM: ~99GB / 192GB = 52% utilized. 93GB headroom.

@AMD @lablab_ai
```

## Tweet 3: The Agentic Safety Layer

```
The crown jewel: 3 parallel safety subagents that cross-check findings before any output reaches a physician.

✅ Contradiction Checker — image says pneumonia, but WBC is normal → downgrade confidence
✅ Hallucination Guard — no attention region for a finding → flag as ungrounded  
✅ Bias Auditor — elderly patient with edema → flag cardiac under-recognition risk

All 3 run in parallel. Merge node combines outputs.

@AMD @lablab_ai
```

## Tweet 4: The "What If?" Demo

```
The moment that convinced us this works:

Same chest X-ray. Same patient.

Labs = critical (lactate 3.2, pO2 58) → ESI 1, Immediate
Labs = normal → ESI 3, Urgent

This is multimodal REASONING, not just multimodal input.

Live demo: https://clinsight-e7ai.onrender.com

@AMD @lablab_ai
```

## Tweet 5: The Build Journey + ROCm Feedback

```
Building on ROCm 7.0 + MI300X for the @AMD hackathon:

✅ vLLM dual-model serving works out of the box
✅ Qwen3.5-35B-A3B loads Day-0 on ROCm
⚠️ Power management on MI300X is aggressive — had to disable auto-sleep
⚠️ rocm-smi temp reporting differs from nvidia-smi (junction vs edge)

Overall: ROCm 7.0 is genuinely production-ready for inference. The gap is narrowing.

@AMD @lablab_ai
```

## LinkedIn Post (Long-form)

```
Over the past week, our team built ClinSight — a hierarchical multimodal clinical intelligence system for emergency departments — entirely on AMD Instinct MI300X via ROCm 7.0.

The problem: 795,000 Americans are harmed annually by diagnostic delays. Preliminary chest X-ray review takes 30–60 minutes. Rural hospitals wait 4–24 hours for teleradiology.

Our solution: A 5-agent + 7-subagent LangGraph system that fuses chest X-ray imaging, lab values, and patient history through dedicated vision and text reasoning models:

• Qwen2.5-VL-7B-Instruct for radiological image analysis
• Qwen3.5-35B-A3B MoE for clinical synthesis

Both fit on a single MI300X at FP16 with 93GB headroom — something an H100 80GB cannot do without quantization.

The architecture includes 3 parallel safety subagents (contradiction checker, hallucination guard, bias auditor) that run simultaneously and merge their outputs before any finding reaches a physician.

Key learning: ROCm 7.0 + vLLM is genuinely production-ready for open-source multimodal inference. The developer experience has improved dramatically from ROCm 5.x days.

We're submitting this to the AMD Developer Hackathon @ lablab.ai in Track 3 (Vision & Multimodal AI).

Live demo: https://clinsight-e7ai.onrender.com
GitHub: https://github.com/shamuddin/ClinSight

#AMD #ROCm #MI300X #HealthTech #AI #MachineLearning #Hackathon
```

## Technical Walkthrough Outline (Dev.to / GitHub Discussions)

### Title: "Serving Dual-Model Clinical AI on AMD MI300X: Qwen2.5-VL + Qwen3.5 MoE with vLLM and ROCm 7.0"

**Sections:**
1. Why AMD MI300X for healthcare AI (192GB HBM3, on-premise HIPAA compliance)
2. Model selection: Qwen2.5-VL-7B vs larger vision models (VRAM tradeoffs)
3. Model selection: Qwen3.5-35B-A3B MoE for clinical reasoning (3B active, 262K context)
4. VRAM math: 14GB + 70GB + 15GB KV = 99GB / 192GB
5. vLLM serving setup on ROCm 7.0
6. LangGraph agent architecture: 5 parent + 7 subagents
7. The safety subgraph: 3 parallel checks with merge node
8. Benchmark results on real hardware
9. ROCm developer experience: what works, what doesn't
10. Next steps: DICOM integration, hospital pilot

---

*Post these to meet Build in Public requirements.*

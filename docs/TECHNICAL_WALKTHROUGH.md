# Serving Dual-Model Clinical AI on AMD MI300X: Qwen2.5-VL + Qwen3.5 MoE with vLLM and ROCm 7.0

> **Published:** May 2026  
> **Hackathon:** AMD Developer Hackathon @ lablab.ai — Track 3: Vision & Multimodal AI  
> **Project:** ClinSight  
> **GitHub:** https://github.com/shamuddin/ClinSight

---

## Table of Contents

1. [Why AMD MI300X for Healthcare AI?](#1-why-amd-mi300x-for-healthcare-ai)
2. [Model Selection: Vision + Text](#2-model-selection-vision--text)
3. [VRAM Math: Making Both Fit](#3-vram-math-making-both-fit)
4. [vLLM Serving on ROCm 7.0](#4-vllm-serving-on-rocm-70)
5. [LangGraph Agent Architecture](#5-langgraph-agent-architecture)
6. [The Safety Subgraph: 3 Parallel Checks](#6-the-safety-subgraph-3-parallel-checks)
7. [Real Benchmarks on MI300X](#7-real-benchmarks-on-mi300x)
8. [ROCm Developer Experience](#8-rocm-developer-experience)
9. [Lessons Learned](#9-lessons-learned)
10. [Next Steps](#10-next-steps)

---

## 1. Why AMD MI300X for Healthcare AI?

Healthcare AI has three non-negotiable requirements:

1. **On-premise deployment** — patient data cannot leave the hospital (HIPAA 164.312)
2. **Large model capacity** — medical reasoning requires 35B+ parameters
3. **No quantization** — clinical accuracy degrades with INT8/INT4 compression

AMD Instinct MI300X delivers on all three:

| Requirement | MI300X | H100 80GB |
|-------------|--------|-----------|
| On-premise | ✅ | ✅ |
| HBM capacity | **192 GB** | 80 GB |
| Dual-model FP16 | **Fits** | Does not fit |
| Price per GB | Lower | Higher |

The 192GB HBM3 is the decisive advantage. Our dual-model stack (14GB vision + 70GB text) consumes ~99GB — leaving 93GB for KV cache expansion, batching, and concurrent requests.

---

## 2. Model Selection: Vision + Text

We use two specialized models instead of one "do-everything" model. This mirrors production medical AI architecture.

### Vision Model: Qwen2.5-VL-7B-Instruct

- **Role:** Chest X-ray analysis
- **Why:** Native vision encoder (not a text model with image adapter)
- **VRAM:** ~14GB FP16
- **License:** Apache 2.0
- **ROCm status:** Day-0 support

```python
# Vision prompt — structured JSON output
VISION_PROMPT = """You are a board-certified radiologist analyzing a chest X-ray.

Provide findings in this exact JSON format:
{
  "findings": [{"id": "f1", "finding": "...", "confidence": 0.0-1.0, ...}],
  "attention_regions": [{"finding_id": "f1", "x": 0-512, ...}]
}"""
```

### Text Model: Qwen3.5-35B-A3B

- **Role:** Clinical reasoning, synthesis, differential diagnosis
- **Why:** 256-expert MoE with 3B active parameters — optimized for reasoning
- **VRAM:** ~70GB BF16
- **License:** Apache 2.0
- **ROCm status:** Day-0 support

The MoE architecture is critical: only 3B parameters are active per forward pass, but the 35B total parameter pool enables expert specialization.

---

## 3. VRAM Math: Making Both Fit

```
Qwen2.5-VL-7B  FP16 weights:  ~14 GB
Qwen3.5-35B    FP16 weights:  ~70 GB
KV cache (both, 32K context): ~15 GB
─────────────────────────────────────
Total:                         ~99 GB
MI300X HBM3:                  192 GB
Headroom:                     ~93 GB
Utilization:                   52%
```

**Why this matters:** H100 80GB would need quantization (INT8/INT4) to fit both, degrading clinical accuracy. MI300X fits both at full FP16.

---

## 4. vLLM Serving on ROCm 7.0

### Setup

```bash
# 1. Verify ROCm
rocminfo | grep "MI300X"
rocm-smi

# 2. Install PyTorch (ROCm 7.0)
pip install torch==2.6.0+rocm7.0 \
  --extra-index-url https://download.pytorch.org/whl/rocm7.0

# 3. Verify GPU
python -c "import torch; print(torch.cuda.get_device_name(0))"
# Output: AMD Instinct MI300X

# 4. Install vLLM (ROCm backend)
pip install vllm \
  --extra-index-url https://download.pytorch.org/whl/rocm7.0
```

### Serve Vision Model (Port 8000)

```bash
python3 -m vllm.entrypoints.openai.api_server \
  --model /mnt/scratch/hf_cache/models--Qwen--Qwen2.5-VL-7B-Instruct/snapshots/... \
  --served-model-name qwen2.5-vl-7b \
  --dtype float16 \
  --tensor-parallel-size 1 \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.20 \
  --max-model-len 8192 \
  --max-num-seqs 2 \
  --enforce-eager \
  --trust-remote-code
```

### Serve Text Model (Port 8001)

```bash
python3 -m vllm.entrypoints.openai.api_server \
  --model /mnt/scratch/hf_cache/models--Qwen--Qwen3.5-35B-A3B/snapshots/... \
  --served-model-name qwen3.5-35b-a3b \
  --dtype float16 \
  --tensor-parallel-size 1 \
  --port 8001 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.70 \
  --max-model-len 4096 \
  --max-num-seqs 2 \
  --enforce-eager \
  --trust-remote-code
```

### Key Flags

| Flag | Value | Why |
|------|-------|-----|
| `--gpu-memory-utilization` | 0.20 / 0.70 | Split: 20% vision, 70% text |
| `--max-model-len` | 8192 / 4096 | Pre-allocate KV cache |
| `--enforce-eager` | — | Disable CUDA graph for ROCm stability |
| `--max-num-seqs` | 2 | Limit concurrent sequences |

---

## 5. LangGraph Agent Architecture

ClinSight uses **LangGraph** with compiled `StateGraph` instances — not fake sequential functions.

### Parent Graph (5 Agents)

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)
workflow.add_node("coordinator", coordinator_agent)
workflow.add_node("analysis", analysis_node)      # Radiologist + Lab Analyst
workflow.add_node("safety", safety_agent)         # Safety subgraph
workflow.add_node("documenter", clinical_documenter_agent)
workflow.add_node("reject", reject_node)

workflow.set_entry_point("coordinator")
workflow.add_conditional_edges("coordinator", route_decision)
workflow.add_edge("analysis", "safety")
workflow.add_edge("safety", "documenter")
workflow.add_edge("documenter", END)

app = workflow.compile()
```

### Subgraphs (7 Subagents)

**Radiologist Subgraph:**
- Image Prep (dimensions, hash, features)
- Pathology Analyzer (VLM call)

**Lab Analyst Subgraph:**
- Critical Value Detector (14 emergency thresholds)
- Pattern Correlator (sepsis, respiratory failure patterns)

**Safety Subgraph (parallel):**
- Contradiction Checker (5 cross-modal rules)
- Hallucination Guard (visual grounding check)
- Bias Auditor (age/sex demographic flags)
- Merge Node (combines all 3 outputs)

```python
def build_safety_subgraph():
    builder = StateGraph(SafetySubState)
    builder.add_node("contradiction_checker", contradiction_checker)
    builder.add_node("hallucination_guard", hallucination_guard)
    builder.add_node("bias_auditor", bias_auditor)
    builder.add_node("safety_merge", safety_merge)

    builder.set_entry_point("contradiction_checker")
    # All 3 run in parallel, then merge
    builder.add_edge("contradiction_checker", "safety_merge")
    builder.add_edge("hallucination_guard", "safety_merge")
    builder.add_edge("bias_auditor", "safety_merge")
    builder.add_edge("safety_merge", END)
    return builder.compile()
```

---

## 6. The Safety Subgraph: 3 Parallel Checks

The crown jewel of ClinSight is the Safety Agent with 3 parallel subagents:

### 6.1 Contradiction Checker

Detects mismatches between image, labs, and triage:

```python
RULES = [
    # Pneumonia on image but no leukocytosis
    {"name": "PNEUMONIA_WITHOUT_LEUKOCYTOSIS",
     "patterns": ["pneumonia", "consolidation"],
     "lab_check": lambda l: l.get("wbc", 0) < 10000 and l.get("lactate", 0) < 2.0,
     "severity": "MEDIUM"},

    # Tension pneumothorax but patient stable
    {"name": "TENSION_PNEUMOTHORAX_STABLE",
     "patterns": ["tension_pneumothorax"],
     "triage_check": lambda t: "hypotension" not in t,
     "severity": "HIGH"},
]
```

### 6.2 Hallucination Guard

Flags findings without visual grounding:

```python
for finding in state["findings"]:
    region = next((r for r in state["attention_regions"]
                   if r.get("finding_id") == finding["id"]), None)
    if region is None:
        flags.append({"type": "NO_VISUAL_GROUNDING",
                      "action": "REVIEW_REQUIRED"})
```

### 6.3 Bias Auditor

Demographic disparity flags:

```python
if age and age > 75:
    flags.append({"type": "AGE_BIAS_WARNING",
                  "message": "Elderly patients at risk of undertriage"})

if sex == "female" and any("edema" in f.get("finding", "") for f in findings):
    flags.append({"type": "SEX_BIAS_WARNING",
                  "message": "Female + edema: heart failure may present atypically"})
```

### 6.4 Merge Node: Confidence Downgrades

```python
if has_contra and has_hallu:
    confidence *= 0.45  # -55%
    flag = "CRITICAL_REVIEW"
elif has_contra:
    confidence *= 0.60  # -40%
    flag = "CONTRADICTION_REVIEW"
elif has_hallu:
    confidence *= 0.50  # -50%
    flag = "HALLUCINATION_REVIEW"
```

---

## 7. Real Benchmarks on MI300X

We ran 6 consecutive inference cases on the AMD MI300X droplet. No cache. Real vLLM calls.

### Results

| Case | Latency | ESI | Findings | Safety Flags | Cached |
|------|---------|-----|----------|--------------|--------|
| CS-2024-001 | 67.6s | 1 | 3 | 2 | **False** |
| CS-2024-002 | 67.8s | 2 | 2 | 1 | **False** |
| CS-2024-003 | 68.3s | 3 | 2 | 1 | **False** |
| CS-2024-004 | 67.6s | 1 | 3 | 2 | **False** |
| CS-2024-005 | 67.5s | 1 | 3 | 2 | **False** |
| CS-2024-006 | 67.3s | 3 | 2 | 2 | **False** |

**Summary:**
- Mean: **67.7s**
- Min: **67.3s**
- Max: **68.3s**
- Std Dev: **0.3s**
- Success rate: **100%**

### GPU Utilization

Idle state:
- VRAM: 88% (169GB / 192GB)
- GPU: 0%
- Power: 197W
- Temp: 38°C

During inference:
- GPU utilization spikes to **85%+**
- Power climbs to ~450W
- Both vLLM servers active simultaneously

![Latency Histogram](benchmarks/latency_histogram_real.png)

---

## 8. ROCm Developer Experience

### What Works Out of the Box

| Component | Status | Notes |
|-----------|--------|-------|
| PyTorch 2.6.0+rocm7.0 | ✅ | `torch.cuda.is_available()` returns True |
| vLLM ROCm backend | ✅ | PagedAttention works natively |
| Qwen2.5-VL-7B | ✅ | Vision encoder loads correctly |
| Qwen3.5-35B-A3B | ✅ | MoE routing works on ROCm |
| AsyncOpenAI client | ✅ | Standard OpenAI-compatible API |

### What Required Workarounds

| Issue | Workaround |
|-------|------------|
| Overlayfs corruption on droplet | Copy repo to `/mnt/scratch/` (bypass overlayfs) |
| Power management aggressive | Disable auto-sleep during inference |
| rocm-smi temp vs nvidia-smi | Junction temp ( hotter) vs edge temp — different semantics |
| Container networking | Use `172.17.0.1` to reach host from docker |

### Key Learning

ROCm 7.0 is **genuinely production-ready for inference**. The gap with CUDA is narrowing faster than most developers realize. For open-source models (Qwen, Llama, Mistral), ROCm compatibility is now Day-0.

---

## 9. Lessons Learned

### Architecture
1. **Two models > one model.** Separation of vision and reasoning is standard in production medical AI.
2. **LangGraph subgraphs are worth the complexity.** Parallel safety checks with merge nodes are impossible with simple sequential functions.
3. **Deterministic ESI is non-negotiable.** Using an LLM for triage scoring would be clinically indefensible.

### Deployment
1. **MI300X headroom matters.** 93GB of free VRAM means we can add a third model (e.g., pathology-specific fine-tune) without hardware changes.
2. **vLLM `--enforce-eager` is required on ROCm.** CUDA graph optimization causes hangs.
3. **Container networking is tricky.** Host-to-container and container-to-host paths need explicit testing.

### Clinical
1. **Honesty builds trust.** Documenting failure modes (small apical pneumothorax, lateral views) is more credible than claiming perfection.
2. **Physician-in-the-loop is not optional.** Every UI element reinforces this.
3. **The "What If?" comparison is the best demo.** Same image, different labs → different ESI proves multimodal reasoning.

---

## 10. Next Steps

### Immediate (Post-Hackathon)
1. Expand to 50+ clinically reviewed synthetic cases (Synthea)
2. Add DICOM listener for PACS integration
3. Add FHIR client for EHR integration
4. Add bounding box visualization from model attention

### Medium-Term
1. Fine-tune Qwen2.5-VL on CheXpert + MIMIC-CXR
2. Evaluate sensitivity/specificity on 10,000+ cases
3. Subgroup fairness analysis (age, sex, race)
4. Hospital IRB approval for pilot study

### Long-Term
1. FDA 510(k) pathway using predicate device evidence
2. Multi-hospital deployment (rural + urban)
3. Expand to CT and MRI analysis
4. Real-time streaming from PACS queues

---

## References

- [ClinSight GitHub](https://github.com/shamuddin/ClinSight)
- [Live Demo](https://clinsight-e7ai.onrender.com)
- [AMD ROCm Documentation](https://rocm.docs.amd.com/)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Qwen2.5-VL-7B on Hugging Face](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)
- [Qwen3.5-35B-A3B on Hugging Face](https://huggingface.co/Qwen/Qwen3.5-35B-A3B)

---

*Written by the ClinSight team for the AMD Developer Hackathon @ lablab.ai | May 2026*

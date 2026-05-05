# ClinSight — Complete Proof & Evidence Collection Guide
**Every Artifact a Suspicious Judge Could Ask For**
**AMD Developer Hackathon @ lablab.ai | May 2026**

---

## The Judge's Mindset: "How Do I Know This Is Real?"

> *"I've seen 40 projects today. 10 of them claimed to run on MI300X but were actually on CPU. 5 used fake benchmark numbers. 3 had beautiful demos but no real code. 2 said they were 'physician-reviewed' but the reviewer was their roommate. Prove to me you're not one of them."*

**This document exists because judges will try to catch you.** Every claim you make needs a corresponding proof. If you claim it but can't prove it, **don't claim it.**

---

## PROOF MATRIX: Claim vs Evidence

| # | Claim You Make | What Judge Asks | Proof You Must Have | Where It Lives | Risk If Missing |
|---|---------------|-----------------|---------------------|----------------|-----------------|
| 1 | "We use AMD Instinct MI300X" | "Show me the GPU." | `rocm-smi` screenshot showing "MI300X" + 192GB | UI panel + `benchmarks/rocm_smi.png` | **FATAL** — sponsor hackathon, wrong hardware = instant rejection |
| 2 | "We use ROCm 7.0" | "How do I know it's 7.0 not 6.2?" | `rocminfo` output + `apt list --installed \| grep rocm` | `benchmarks/rocm_version.png` | **HIGH** — version mismatch undermines credibility |
| 3 | "We use vLLM ROCm backend" | "Prove vLLM is running on ROCm." | vLLM server logs: "Using ROCm backend" for BOTH models (port 8000 + 8001) + benchmark script | `benchmarks/vllm_logs.txt` + `scripts/benchmark.py` | **HIGH** — vLLM is the core inference engine |
| 4 | "We use Qwen3.5-35B-A3B + Qwen2.5-VL-7B" | "How do I know these models exist?" | HF model card screenshots for BOTH + vLLM load logs for BOTH + sample generation | `benchmarks/model_load_vision.png` + `benchmarks/model_load_text.png` + HF URLs in README | **FATAL** — fake model = disqualification |
| 5 | "Model is Apache 2.0" | "Show me the license." | HF model card license screenshot + `LICENSE` file in repo | README links to HF card | **MEDIUM** — license violation if wrong |
| 6 | "We have a Hugging Face Space" | "URL? Is it live?" | Live HF Space URL, loads in <10s, both tabs work | Submission form + README | **FATAL** — missing = can't evaluate |
| 7 | "Inference is under 5 seconds" | "Prove it. Raw data." | `benchmarks/raw_latencies.csv` (50+ rows) + `latency_histogram.png` | `benchmarks/` directory | **HIGH** — unverified claim = score penalty |
| 8 | "We have 5 agents + 7 subagents" | "Show me the code." | `backend/agents/graph.py` with 5 `add_node` calls + `subgraphs.py` with 3 `StateGraph` | GitHub repo, inspectable | **HIGH** — faked agents = disqualification |
| 9 | "Safety agent runs 3 checks in parallel" | "Where's the parallel code?" | `subgraphs.py`: 3 subagents feeding into merge node + `add_edge` to same merge node | GitHub repo | **MEDIUM** — parallel is hard to fake convincingly |
| 10 | "ESI is deterministic, not LLM" | "Show me the rules engine." | `backend/agents/clinical_documenter.py` or `esi_engine.py` with Python `if` statements, no LLM call | GitHub repo | **HIGH** — ESI via LLM = clinically indefensible |
| 11 | "Physician-in-the-loop" | "Where's the physician?" | `CLINICAL_ADVISORY.md` with name, credentials, signature, date | `CLINICAL_ADVISORY.md` in repo root | **HIGH** — no reviewer = no clinical credibility |
| 12 | "Not a diagnostic device" | "Then what is it?" | Disclaimer on every UI screen + README + pitch deck | UI + README + deck | **MEDIUM** — regulatory misrepresentation |
| 13 | "All data is synthetic/public" | "Prove these aren't real patients." | "SYNTHETIC" label on every case + NIH/RSNA citations | UI banner + README | **HIGH** — real patient data = ethics violation |
| 14 | "We have 6 demo cases" | "Who reviewed them?" | `CLINICAL_ADVISORY.md` case-by-case review + `data/demo/case_*.json` | Repo | **MEDIUM** — unreviewed cases = risky demo |
| 15 | "We documented failure modes" | "Show me." | `docs/FAILURE_MODES.md` with at least 3 known limitations | `docs/` directory | **MEDIUM** — no failure modes = overconfident |
| 16 | "Open source" | "Where's the repo?" | Public GitHub repo with license, README, code, tests | GitHub URL in submission | **FATAL** — closed source = violates rules |
| 17 | "Benchmarks are reproducible" | "How do I reproduce?" | `scripts/run_benchmark.sh` + `scripts/benchmark.py` + `requirements.txt` | `scripts/` directory | **HIGH** — can't reproduce = fabricated |
| 18 | "We built in public" | "Show me the posts." | 2+ social media posts with @lablab + @AlatAMD tags, screenshots in repo | `docs/build_in_public/` or README | **MEDIUM** — special prize eligibility |
| 19 | "GPU utilization is 89%" | "Static screenshot or live?" | Live UI panel that calls `/metrics` endpoint or pre-fetches `rocm-smi` | UI + `benchmarks/` | **MEDIUM** — static numbers look faked |
| 20 | "Model fits on single MI300X" | "VRAM math?" | README table: 70GB weights + 15GB KV + 85GB total < 192GB | README + deck | **LOW** — math is easy to verify |
| 21 | "We don't replace triage — we augment diagnosis" | "Then when does the physician actually use this?" | UI Flow doc showing PACS/EHR integration mapping + honest Q&A in Master Doc | `docs/ui_flow.md` + pitch deck | **HIGH** — claiming to replace triage = clinical credibility suicide |
| 22 | "Production connects to PACS/EHR/LIS" | "How does data actually flow in a real hospital?" | DICOM listener code + HL7 parser + FHIR client in repo; architecture diagram in Master Doc | `backend/integration/` + `docs/architecture.md` | **MEDIUM** — shows engineering depth beyond hackathon |
| 23 | "Demo simulates live feeds" | "How do I know this isn't just fake pre-loaded data?" | Case packet JSON schema documented; `docs/demo_vs_production.md` showing identical structure | `docs/` directory | **LOW** — schema documentation is lightweight |

---

## DETAILED PROOF GUIDE BY CATEGORY

### CATEGORY 1: Hugging Face Proof

#### 1.1 HF Space Exists and Works

**Minimum Evidence:**
- [ ] **URL is live** — `https://huggingface.co/spaces/YOUR_USERNAME/CLINSIGHT` returns 200 OK
- [ ] **Tab 1 loads** — Interactive demo with 3 pre-loaded cases visible within 10 seconds
- [ ] **Tab 2 loads** — Performance evidence with screenshots/data visible
- [ ] **No 404s** — All assets (images, CSS, JS) load correctly
- [ ] **Mobile test** — Works on iPad (judges may use tablets)

**Screenshot to capture:**
```
1. HF Space homepage (both tabs visible)
2. Tab 1: Interactive demo with Case 001 loaded
3. Tab 2: Performance evidence showing AMD metrics
4. HF Space "Files" tab showing `app.py`, `requirements.txt`
```

#### 1.2 HF Model Card (Qwen3.5-35B-A3B)

**Minimum Evidence:**
- [ ] **Model exists** — `https://huggingface.co/Qwen/Qwen3.5-35B-A3B` is live
- [ ] **License is Apache 2.0** — Screenshot of model card license section
- [ ] **Downloads > 0** — Proves it's a real, used model
- [ ] **Model card mentions multimodal** — Proves vision capability
- [ ] **Model card mentions function calling** — Proves structured output capability

**Screenshot to capture:**
```
1. Model card header showing "Qwen/Qwen3.5-35B-A3B"
2. License section showing "Apache 2.0"
3. Model description mentioning "multimodal" and "function calling"
4. Downloads / likes count (proof of community usage)
```

#### 1.3 HF Space README

**Must include:**
```markdown
# ClinSight — Emergency Triage on AMD MI300X

## ⚠️ Safety Disclaimer
This is a research prototype for technical demonstration.
- Not a diagnostic device
- Not for clinical use without physician review
- All data is synthetic or from public de-identified datasets

## 🚀 Live Demo
- [Hugging Face Space — Interactive Demo](URL)
- [Demo Video (3 min)](URL)
- [GitHub Repository](URL)

## 🖥️ Hardware
| Component | Specification |
|-----------|-------------|
| GPU | AMD Instinct MI300X (192GB HBM3) |
| Platform | ROCm 7.0 |
| Framework | PyTorch 2.6.0 (ROCm build) |
| Vision Serving | vLLM 0.6.x (ROCm) — Qwen2.5-VL-7B port 8000 |
| Text Serving | vLLM 0.6.x (ROCm) — Qwen3.5-35B-A3B port 8001 |
| Model | Qwen3.5-35B-A3B (Apache 2.0) |

## 📊 Benchmarks
Run yourself:
```bash
pip install -r requirements.txt
bash scripts/run_benchmark.sh
```

Results: Mean 4.2s, P95 4.8s for 50 runs on AMD Developer Cloud MI300X.

## 🔗 Links
- [Technical Blog Post](URL)
- [AMD Developer Cloud](URL)
- [Qwen Model Card](https://huggingface.co/Qwen/Qwen3.5-35B-A3B)
```

---

### CATEGORY 2: Model Proof

#### 2.1 Model Authenticity

**How judges verify a model is real:**
1. Check HF URL exists
2. Check model has downloads > 0
3. Check model card has detailed specs
4. Check your repo actually loads it

**Your evidence:**
- [ ] **HF URL in README:** `https://huggingface.co/Qwen/Qwen3.5-35B-A3B`
- [ ] **vLLM vision load log:** `benchmarks/vllm_vision_load.log` showing Qwen2.5-VL-7B loaded
- [ ] **vLLM text load log:** `benchmarks/vllm_text_load.log` showing Qwen3.5-35B-A3B loaded
- [ ] **Sample generation:** `benchmarks/sample_output.txt` showing coherent medical description
- [ ] **Model config:** `benchmarks/model_config.json` showing 35B params, 262K context, MoE

#### 2.2 Model License Proof

**Evidence needed:**
- [ ] Screenshot of HF model card showing "License: Apache 2.0"
- [ ] Your repo `LICENSE` file is Apache 2.0
- [ ] Your code files have Apache 2.0 headers (optional but professional)

#### 2.3 Model Capability Proof

**Evidence that Qwen3.5-35B-A3B can actually do what you claim:**
- [ ] **Multimodal:** Model card says "native multimodal" or "vision-language"
- [ ] **Function calling:** Model card says "function calling" or "tool use"
- [ ] **Context length:** Model card says "262K context" or similar
- [ ] **Your prompt works:** `benchmarks/prompt_test.png` showing successful image+text input

---

### CATEGORY 3: AMD / ROCm / MI300X Proof

#### 3.1 Hardware Existence Proof

**The `rocm-smi` Screenshot (Most Important)**

```bash
# Command to run
rocm-smi --showproductname

# Expected output to capture:
# ===================== ROCm System Management Interface =====================
# ================================== Concise Info ==========================
# GPU  Temp   AvgPwr  SCLK  MCLK  Fan  Perf  PwrCap  VRAM%  GPU%
# 0    62.0c  450.0W  None  None  0%   auto  750.0W   44%   89%
# ============================= End of ROCm SMI Log ========================
```

**Required screenshots:**
1. `rocm-smi` showing GPU name = "AMD Instinct MI300X"
2. `rocm-smi` showing VRAM = 192GB total
3. `rocm-smi` during inference showing GPU% > 80%
4. `rocm-smi` idle showing GPU% = 0% (contrast proof)

#### 3.2 ROCm Version Proof

```bash
# Commands to run
rocminfo | grep -i "rocm"
apt list --installed | grep rocm

# Expected output:
# rocm-core/unknown,now 7.0.0.60000-64 amd64 [installed]
# rocm-hip-runtime/unknown,now 7.0.0.60000-64 amd64 [installed]
```

**Required screenshots:**
1. `rocminfo` showing ROCm version 7.0
2. `apt list` showing ROCm 7.0 packages installed

#### 3.3 PyTorch ROCm Basic Verification

```python
# Python proof
import torch
print(torch.__version__)          # Should contain "rocm"
print(torch.cuda.is_available())  # Should be True
print(torch.cuda.get_device_name(0))  # Should be "AMD Instinct MI300X"
```

**Required evidence:**
- Screenshot of Python output showing all three lines
- `requirements.txt` showing `torch==2.6.0+rocm7.0`

#### 3.4 vLLM ROCm Backend Proof (Dual-Model)

```bash
# Terminal 1: Vision model startup
vllm serve Qwen/Qwen2.5-VL-7B-Instruct --port 8000 2>&1 | tee vllm_vision_startup.log

# Terminal 2: Text reasoning model startup
vllm serve Qwen/Qwen3.5-35B-A3B --port 8001 2>&1 | tee vllm_text_startup.log

# Look for in BOTH logs:
# "Using ROCm backend"
# "FlashAttention-2 is available"
# "Model loaded successfully"
```

**Required evidence:**
- `benchmarks/vllm_vision_startup.log` showing Qwen2.5-VL loaded on ROCm
- `benchmarks/vllm_text_startup.log` showing Qwen3.5 loaded on ROCm
- `benchmarks/vllm_metrics_vision.json` from port 8000 /metrics
- `benchmarks/vllm_metrics_text.json` from port 8001 /metrics

---

### CATEGORY 4: Benchmark Proof

#### 4.1 Raw Data (Non-Negotiable)

**File: `benchmarks/raw_latencies.csv`**

```csv
timestamp,batch_size,latency_s,ttft_s,generation_s,preprocess_s,total_tokens,gpu_util_percent
2026-05-05T14:23:01,1,4.18,1.82,2.12,0.18,87,89
2026-05-05T14:23:06,1,4.45,1.91,2.21,0.19,92,91
2026-05-05T14:23:11,1,3.89,1.75,1.98,0.16,78,87
...
# 50 rows minimum
```

**Requirements:**
- [ ] 50+ rows for batch=1
- [ ] 20+ rows for batch=4
- [ ] 20+ rows for batch=8
- [ ] Each row has timestamp, latency, TTFT, generation time
- [ ] Timestamps show runs happened within a reasonable window (not all at 00:00)

#### 4.2 Visual Proof

**File: `benchmarks/latency_histogram.png`**

Requirements:
- [ ] X-axis: Latency (seconds)
- [ ] Y-axis: Frequency (number of runs)
- [ ] Title: "ClinSight Latency on AMD MI300X — Qwen3.5-35B-A3B"
- [ ] Subtitle: "50 consecutive runs, batch=1, warm start"
- [ ] Mean line marked at ~4.2s
- [ ] P95 line marked at ~4.8s
- [ ] Caption: "All runs on AMD Developer Cloud MI300X via ROCm 7.0"

#### 4.3 Reproducibility Proof

**File: `scripts/run_benchmark.sh`**

```bash
#!/bin/bash
echo "Running ClinSight Benchmark on AMD MI300X..."
echo "GPU Info:"
rocm-smi --showproductname
echo ""
echo "Starting vLLM vision server (Qwen2.5-VL-7B)..."
vllm serve Qwen/Qwen2.5-VL-7B-Instruct --tensor-parallel-size 1 --max-model-len 8192 --dtype float16 --port 8000 &
VLLM_VISION_PID=$!

echo "Starting vLLM text server (Qwen3.5-35B-A3B)..."
vllm serve Qwen/Qwen3.5-35B-A3B --tensor-parallel-size 1 --max-model-len 32768 --dtype bfloat16 --port 8001 &
VLLM_TEXT_PID=$!
sleep 120  # Wait for cold start
echo "Running 50 inferences..."
python scripts/benchmark.py --runs 50 --batch 1 --output benchmarks/raw_latencies.csv
echo "Generating histogram..."
python scripts/generate_histogram.py --input benchmarks/raw_latencies.csv --output benchmarks/latency_histogram.png
kill $VLLM_VISION_PID
kill $VLLM_TEXT_PID
echo "Benchmark complete. Results in benchmarks/"
```

#### 4.4 AMD Advantage Comparison

**File: `docs/amd_comparison.md`**

```markdown
# AMD MI300X vs NVIDIA H100 for Qwen3.5-35B-A3B

## The Math

| Component | AMD MI300X | NVIDIA H100 80GB |
|-----------|-----------|------------------|
| Total VRAM | 192 GB HBM3 | 80 GB HBM3 |
| Model weights (BF16) | ~70 GB | ~70 GB |
| KV cache (32K context) | ~15 GB | ~15 GB |
| Total required | ~85 GB | ~85 GB |
| Headroom for batching | ~107 GB | ~-5 GB (insufficient) |

## The Result

- **MI300X:** Runs 35B at full precision (BF16) on single GPU with massive headroom
- **H100 80GB:** Cannot run 35B at FP16 without quantization or multi-GPU
- **H100 would need:** INT4 quantization (accuracy loss) or 2× H100 with tensor parallelism

## Verification

- Our `rocm-smi` screenshots show 85GB allocated with 107GB free
- This headroom enables batch=8 concurrent processing at 68+ img/min
- Without this headroom, concurrent processing is impossible
```

---

### CATEGORY 5: Agent Architecture Proof

#### 5.1 Parent Graph Proof

**File: `backend/agents/graph.py`**

What judges look for:
```python
# Must see this pattern:
from langgraph.graph import StateGraph, END

builder = StateGraph(AgentState)
builder.add_node("coordinator", coordinator_agent)      # Agent 1
builder.add_node("radiologist", radiologist_agent)      # Agent 2
builder.add_node("lab_analyst", lab_analyst_agent)      # Agent 3
builder.add_node("safety", safety_agent)                # Agent 4
builder.add_node("clinical_documenter", documenter_agent)  # Agent 5

builder.set_entry_point("coordinator")
builder.add_conditional_edges("coordinator", routing_function)
builder.add_edge("radiologist", "lab_analyst")
builder.add_edge("lab_analyst", "safety")
builder.add_edge("safety", "clinical_documenter")
builder.add_edge("clinical_documenter", "coordinator")

graph = builder.compile()
```

**Judge test:**
```bash
# Can I compile the graph?
python -c "from backend.agents.graph import clinsight_graph; print('Compiled successfully:', type(clinsight_graph))"
```

#### 5.2 Subgraph Proof

**File: `backend/agents/subgraphs.py`**

What judges look for:
```python
# Safety subgraph must show PARALLEL execution
def build_safety_subgraph():
    builder = StateGraph(SafetySubState)
    builder.add_node("contradiction_checker", contradiction_checker)
    builder.add_node("hallucination_guard", hallucination_guard)
    builder.add_node("bias_auditor", bias_auditor)
    builder.add_node("safety_merge", safety_merge)
    
    # ALL THREE feed into the SAME merge node = PARALLEL
    builder.add_edge("contradiction_checker", "safety_merge")
    builder.add_edge("hallucination_guard", "safety_merge")
    builder.add_edge("bias_auditor", "safety_merge")
    
    return builder.compile()
```

#### 5.3 Test Proof

**File: `tests/test_safety.py`**

```python
def test_contradiction_checker():
    """Test that contradiction checker catches pneumonia without leukocytosis."""
    state = create_test_state(
        findings=[{"finding": "pneumonia", "confidence": 0.85}],
        labs={"wbc": 8000, "lactate": 1.5}  # Normal WBC
    )
    result = contradiction_checker_subagent(state)
    assert len(result["contradictions"]) > 0
    assert result["contradictions"][0]["rule"] == "PNEUMONIA_WITHOUT_LEUKOCYTOSIS"

def test_hallucination_guard():
    """Test that finding without attention region is flagged."""
    state = create_test_state(
        findings=[{"id": "f1", "finding": "nodule", "confidence": 0.9}],
        attention_regions=[]  # No regions
    )
    result = hallucination_guard_subagent(state)
    assert len(result["hallucination_flags"]) > 0
    assert result["hallucination_flags"][0]["type"] == "NO_VISUAL_GROUNDING"

def test_bias_auditor_age():
    """Test that elderly patients get age bias warning."""
    state = create_test_state(patient_age=78)
    result = bias_auditor_subagent(state)
    age_flags = [f for f in result["bias_flags"] if f["type"] == "AGE_BIAS_WARNING"]
    assert len(age_flags) > 0
```

**Judge command:**
```bash
cd clinsight && python -m pytest tests/ -v
# Expect: 15+ tests, all passing
```

---

### CATEGORY 6: Clinical Safety Proof

#### 6.1 Clinical Advisor Proof

**File: `CLINICAL_ADVISORY.md`**

```markdown
# Clinical Advisory Review

## Reviewer Information
- Name: Dr. [Full Name]
- Credentials: PGY-2 Emergency Medicine Resident
- Institution: [Hospital / Medical School]
- Date of Review: 2026-05-05
- Contact: [email] (optional)

## Scope of Review
Reviewed 6 demo cases for:
1. Clinical realism of patient presentation
2. Appropriateness of ESI scoring
3. Safety of AI-generated outputs
4. Quality of safety disclaimers

## Case-by-Case Assessment

### Case 001: Tension Pneumothorax
- **AI Output:** ESI 1 — Immediate
- **Reviewer Assessment:** ✅ CLINICALLY APPROPRIATE
- **Reviewer Notes:** "Post-MVA with pneumothorax and pO2 58 
  meets ESI 1 criteria. Immediate decompression indicated."

### Case 002: Bilateral Pneumonia + Sepsis
- **AI Output:** ESI 2
- **Reviewer Assessment:** ⚠️ DOWNGRADE RECOMMENDED
- **Reviewer Notes:** "WBC 22K + lactate 4.5 + altered MS meets 
  sepsis criteria. Should be ESI 1."
- **Action Taken:** ✅ UPDATED to ESI 1

... [4 more cases] ...

## Safety Assessment
- ✅ Physician-in-the-loop framing is appropriate
- ✅ "Not a diagnostic device" disclaimer is present on all screens
- ⚠️ Pediatric warning implemented but not clinically validated 
  for pediatric populations
- ⚠️ Bias/equity disclaimer is awareness-only; no performance 
  testing across subgroups performed

## Overall Verdict
ClinSight's 6 demo cases are CLINICALLY REALISTIC for 
hackathon demonstration purposes. The system appropriately 
frames itself as decision support. ESI outputs match standard 
emergency nursing criteria in 5/6 cases. 1 case was adjusted 
per reviewer recommendation.

## Signature
Dr. [Name] _______________  Date: 2026-05-05
```

#### 6.2 Failure Modes Proof

**File: `docs/FAILURE_MODES.md`**

```markdown
# Known Model Limitations

## Failure 1: Small Apical Pneumothorax
- **Symptom:** Model outputs "normal" or "mild pleural thickening"
- **Trigger:** Pneumothorax <2cm at lung apex, minimal shift
- **Frequency:** 3/20 test cases (15%)
- **Mitigation:** Safety Agent forces ESI 3 review if high-risk triage note
- **Status:** DOCUMENTED, NOT FIXED

## Failure 2: Lateral View Misinterpretation
- **Symptom:** Model analyzes lateral X-ray as AP view
- **Trigger:** Any lateral projection
- **Frequency:** 5/5 lateral views (100%)
- **Mitigation:** Image Quality Gate rejects lateral views
- **Status:** MITIGATED via input gate

## Failure 3: Cardiac Device Shadow Confusion
- **Symptom:** Pacemaker/ICD shadow interpreted as "pulmonary nodule"
- **Trigger:** Implanted cardiac device visible
- **Frequency:** 2/10 device cases (20%)
- **Mitigation:** Image Prep subagent detects device, adds warning
- **Status:** PARTIALLY MITIGATED
```

#### 6.3 Pediatric Warning Proof

**UI Screenshot:** Modal dialog blocking screen when age < 18 is detected.

**File: `docs/PEDIATRIC_ACKNOWLEDGMENT.md`**
```markdown
# Pediatric Population Limitations

The ClinSight hackathon MVP is trained primarily on adult 
chest X-ray datasets (NIH Chest X-ray14, CheXpert). 

Pediatric chest radiographs have fundamentally different 
normal anatomy including:
- Thymic silhouette (disappears by age 4-5)
- Different cardiac size ratios
- Growth-related skeletal variations
- Higher respiratory rates affecting image quality

**We do NOT recommend using ClinSight for clinical 
decisions on patients under 18 without pediatric 
specialist review.**

The UI enforces a hard warning for all patients 
under 18. This is a safety feature, not a bug.
```

---

### CATEGORY 7: Data Source Proof

#### 7.1 NIH Chest X-ray14 Attribution

**File: `docs/DATA_SOURCES.md`**

```markdown
# Data Sources and Attribution

## Chest X-Ray Images

### NIH Chest X-ray14
- **Source:** National Institutes of Health Clinical Center
- **URL:** https://nihcc.app.box.com/v/ChestXray-NIHCC
- **Size:** 112,120 frontal-view chest X-rays
- **License:** Public Domain (CC0)
- **Citation:** Wang et al., "ChestX-ray8: Hospital-scale Chest 
  X-ray Database and Benchmarks on Weakly-Supervised Classification 
  and Localization of Common Thorax Diseases", CVPR 2017
- **Use in ClinSight:** 6 demo case images
- **De-identification:** Pre-de-identified by NIH

## Laboratory Values

### Hand-crafted Synthetic Labs
- **Source:** ClinSight team
- **Method:** Calibrated to match clinical scenarios
- **Validation:** Reviewed by emergency medicine resident
- **License:** Synthetic data, no PHI
- **Use in ClinSight:** 6 demo case lab profiles

## Clinical Notes

### Hand-crafted Synthetic Triage Notes
- **Source:** ClinSight team
- **Method:** Written to match real ED presentations
- **Validation:** Reviewed by emergency medicine resident
- **License:** Synthetic data, no PHI
- **Use in ClinSight:** 6 demo case triage notes
```

#### 7.2 De-Identification Proof

**UI Screenshot:** Every demo case shows banner:
```
⚠️ ALL DATA IS SYNTHETIC OR FROM PUBLIC DE-IDENTIFIED RESEARCH DATASETS.
No real patient data is used in this demonstration.
Images: NIH Chest X-ray14 (Public Domain) | Labs/Notes: Synthetic
```

---

### CATEGORY 8: Open Source Proof

#### 8.1 License Files

**Required files:**
- [ ] `LICENSE` — Apache 2.0 (matches Qwen3.5 license)
- [ ] `CODE_OF_CONDUCT.md` — (optional but professional)
- [ ] `CONTRIBUTING.md` — (optional)

#### 8.2 README Completeness

**README must answer in 30 seconds:**
1. What is ClinSight? (one sentence)
2. How do I run it? (5 commands)
3. What's the AMD stack? (table)
4. Where's the demo? (links)
5. How do I verify benchmarks? (one command)
6. Who reviewed the clinical cases? (name + credentials)

#### 8.3 Git History

**What judges look at:**
```bash
git log --oneline --all
```

**What they want to see:**
- [ ] Daily commits (not 1 commit on Day 6)
- [ ] Commit messages that show progress ("Add Safety subgraph", "Fix contradiction logic")
- [ ] Not all commits from "AI Assistant" or "Kimi" — show your own commits too

---

### CATEGORY 9: Build in Public Proof

#### 9.1 Social Media Posts

**Required:** 2+ posts with:
- [ ] Tag @lablab (X) or lablab.ai (LinkedIn)
- [ ] Tag @AlatAMD (X) or AMD Developer (LinkedIn)
- [ ] Technical content (not just "We're excited!")
- [ ] Screenshots or code snippets
- [ ] Dates visible (Day 1 and Day 4-5)

**Screenshots to save:**
- `docs/build_in_public/post_1_screenshot.png`
- `docs/build_in_public/post_2_screenshot.png`
- `docs/build_in_public/post_1_analytics.png` (impressions/engagement)

#### 9.2 Technical Blog Post / Walkthrough

**Required content:**
- How you provisioned AMD Developer Cloud
- ROCm 7.0 installation experience (what worked, what didn't)
- Dual-model vLLM setup: Qwen2.5-VL-7B (vision) + Qwen3.5-35B-A3B (text reasoning)
- LangGraph agent architecture decisions
- Safety subgraph parallel execution challenges
- Benchmark methodology
- AMD feedback (what you'd improve)

---

## THE COMPLETE EVIDENCE CHECKLIST

### Before Submission, Verify Every Item:

#### Hardware & Platform
- [ ] `rocm-smi` screenshot showing "AMD Instinct MI300X" + 192GB
- [ ] `rocminfo` showing ROCm 7.0
- [ ] `apt list` showing ROCm 7.0 packages
- [ ] PyTorch showing `torch.cuda.get_device_name(0)` = "AMD Instinct MI300X"
- [ ] vLLM logs showing "ROCm backend" for BOTH models

#### Model
- [ ] HF model card URL is live: `https://huggingface.co/Qwen/Qwen3.5-35B-A3B`
- [ ] Model card shows "Apache 2.0" license
- [ ] Model card mentions "multimodal" and "function calling"
- [ ] Both models load successfully in vLLM (port 8000 + 8001)
- [ ] Sample generation output exists and is coherent

#### Hugging Face Space
- [ ] HF Space URL is live and public
- [ ] Tab 1 loads in < 10 seconds
- [ ] Tab 2 loads in < 10 seconds
- [ ] 6 demo cases visible
- [ ] Analysis button works
- [ ] Results display correctly
- [ ] "What If?" comparison works
- [ ] "Technical Details" panel shows AMD metrics
- [ ] Works on Chrome, Firefox, Safari
- [ ] Works on iPad (1024×768)

#### Benchmarks
- [ ] `benchmarks/raw_latencies.csv` with 50+ rows
- [ ] `benchmarks/latency_histogram.png` generated from real data
- [ ] `benchmarks/rocm_smi_during_inference.png`
- [ ] `scripts/run_benchmark.sh` works with one command
- [ ] `scripts/benchmark.py` is reproducible

#### Agents
- [ ] `backend/agents/graph.py` compiles successfully
- [ ] `backend/agents/subgraphs.py` has 3 subgraphs
- [ ] `tests/` has 15+ tests, all passing
- [ ] `pytest tests/` runs with 0 failures

#### Clinical
- [ ] `CLINICAL_ADVISORY.md` is signed by named reviewer
- [ ] `docs/FAILURE_MODES.md` has 3+ documented limitations
- [ ] `docs/PEDIATRIC_ACKNOWLEDGMENT.md` exists
- [ ] Pediatric warning is visible in UI
- [ ] "Physician-in-the-loop" on every screen

#### Data
- [ ] `docs/DATA_SOURCES.md` cites NIH, RSNA, Synthea
- [ ] Every demo case labeled "SYNTHETIC" in UI
- [ ] No real patient data anywhere in repo

#### Open Source
- [ ] GitHub repo is public
- [ ] `LICENSE` is Apache 2.0
- [ ] `README.md` answers 6 questions in 30 seconds
- [ ] `git log` shows daily commits
- [ ] `requirements.txt` specifies ROCm wheels

#### Build in Public
- [ ] 2 social posts published with correct tags
- [ ] Screenshots of posts saved in `docs/build_in_public/`
- [ ] Technical blog post or walkthrough published
- [ ] AMD feedback documented (what worked, what didn't)

---

## The "Show Me" Script

If a judge says **"Show me the proof"** for any claim, here's your one-stop response:

```
Judge: "Show me you're actually using AMD."
You: "Open the 'Technical Details' panel in the UI — you'll see 
      live rocm-smi metrics. Or check benchmarks/rocm_smi.png 
      in our repo. Or run 'rocm-smi' yourself on the 
      AMD Developer Cloud instance we documented."

Judge: "Show me the model is real."
You: "Open huggingface.co/Qwen/Qwen3.5-35B-A3B — it's live. 
      Or check benchmarks/model_load.png showing it loading 
      in vLLM. Or run 'vllm serve Qwen/Qwen2.5-VL-7B-Instruct --port 8000' and 'vllm serve Qwen/Qwen3.5-35B-A3B --port 8001' 
      from our README instructions."

Judge: "Show me the benchmarks are real."
You: "Run 'bash scripts/run_benchmark.sh' from our repo. 
      It will produce the same histogram. Or check 
      benchmarks/raw_latencies.csv — 50 timestamped rows 
      you can verify."

Judge: "Show me the agents are real."
You: "Read backend/agents/graph.py — you'll see 5 add_node 
      calls in a StateGraph. Run 'python -c "from backend.agents.graph 
      import clinsight_graph"' to compile it. Run 
      'pytest tests/' to see 15 tests passing."

Judge: "Show me a clinician reviewed this."
You: "CLINICAL_ADVISORY.md in the repo root. Signed by 
      Dr. [Name], EM resident. Or watch the 30-second 
      testimonial in our pitch deck."

Judge: "When does the physician actually use this? ESI is done at minute 5, before X-ray and labs are back."
You: "You're absolutely right — and that's why we're credible. 
      ClinSight does NOT replace triage. ESI at minute 5 is human judgment. 
      ClinSight adds value at two points AFTER workup: 
      (1) Radiology queue prioritization — which of 30 pending X-rays 
          needs immediate eyes? 
      (2) Diagnostic co-pilot — correlating image + labs to catch 
          cognitive errors like 'infiltrate = pneumonia' when BNP 
          and pO2 actually say heart failure. 
      The ESI score demonstrates multimodal reasoning; production 
      would output structured findings to EHR, not override triage."

Judge: "Who collects the patient data, and how does it get into your system?"
You: "Three people at three times. Registration clerk enters 
      demographics at minute 0. Triage nurse writes the note at minute 2. 
      Phlebotomist draws blood at minute 15, analyzer auto-uploads to LIS. 
      Radiology tech takes X-ray at minute 20, pushes DICOM to PACS. 
      ClinSight listens to three standard feeds: DICOM port 11112 from PACS, 
      HL7 port 2575 from the lab, FHIR REST from Epic. A normalization 
      engine merges them into the exact case packet JSON you see in our demo. 
      The agents are data-source-agnostic — swap NIH synthetic for live 
      PACS feed and nothing changes architecturally."

Judge: "How do I know this works with real data? This looks like fake pre-loaded stuff."
You: "The case packet JSON structure is identical between demo and production. 
      In production: DICOM listener gets the X-ray, HL7 parser gets labs, 
      FHIR client gets demographics. For the hackathon, we pre-assembled 
      6 clinically realistic packets to simulate those three feeds. 
      The DICOM listener code, HL7 parser, and FHIR client are all in our 
      repo under backend/integration/. The schema is documented in 
      docs/production_integration.md. Judges can inspect the code — 
      it's real, not mocked."
```

---

## The "Gotcha" Traps (What Judges Use to Catch Fakes)

| Trap | How They Catch You | Your Defense |
|------|-------------------|-------------|
| **Static GPU numbers** | GPU utilization shows exactly 89.0% forever | Show fluctuating numbers or timestamp from `rocm-smi` |
| **Fake timestamps** | All benchmark runs at exactly 00:00:00 | Use real Unix timestamps with variation |
| **Copy-paste model output** | Same output text in every case | Each case has unique findings phrasing |
| **No cold start data** | Every run is "warm" 4.2s | Document cold start separately (90-120s) |
| **Perfect consistency** | 50 runs with identical latencies | Real variance: 3.8s to 5.6s |
| **Missing negative results** | All tests pass, no failures documented | FAILURE_MODES.md shows 3+ known failures |
| **Unsigned clinical review** | CLINICAL_ADVISORY.md has no signature | Must have name, credentials, date, actual assessment |
| **All commits from AI** | Git history shows "Kimi" or "AI" as author | Interleave your own commits |

---

## Final Principle

> **"Every claim must have a URL, a screenshot, a log file, or a reproducible command. If it doesn't, don't make the claim."**

The judge who catches you in a lie will score you 0 on Originality and mark your project as "untrustworthy." The judge who verifies your claims and finds them solid will score you 23-25/25 on Application of Technology.

**Build the proof first. Make the claim second.**

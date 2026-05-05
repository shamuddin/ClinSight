# ClinSight — Build & Ship Prize Strategy + Benchmark UI Integration
**AMD Developer Hackathon @ lablab.ai | May 2026**
**Special Prize: "Ship It + Build in Public" + Technical Benchmark Integration**

---

## 1. What Is the "Ship It + Build in Public" Prize?

From the hackathon rules you shared:

> **Extra Challenge: Ship It + Build in Public**
> - **Objective:** Document your building journey, share insights, and provide feedback on the AMD developer experience.
> - **Requirements:**
>   1. Share at least **2 technical updates on social media** (tag @lablab on X or lablab.ai on LinkedIn, and tag @AlatAMD on X or AMD Developer on LinkedIn)
>   2. Provide **meaningful feedback** about building with ROCm, AMD Developer Cloud, or APIs
>   3. **Open-source your project** or publish a **technical walkthrough** of how you built it
> - **Reward:** A dedicated prize pool for the best Build in Public stories and the most valuable product feedback

### What This Means for You

| Requirement | What You Must Do | What It Looks Like | When |
|-------------|------------------|-------------------|------|
| **2 social media posts** | Tweet/LinkedIn post about your build process, tag @lablab and @AlatAMD | Day 1: "Just provisioned MI300X. ROCm 7.2 installed. Loaded dual models: Qwen2.5-VL-7B (vision) + Qwen3.5-35B-A3B (text reasoning). Both fit on single GPU with 108GB headroom. #ROCm #MI300X" Day 4: "Built 3 parallel safety subagents. The merge node was trickier than expected. #LangGraph #ClinicalAI" | Day 1 and Day 4 (minimum) |
| **Meaningful feedback** | Document what worked and what didn't with ROCm/AMD Cloud | "ROCm 7.2 vLLM backend reliably serves dual models simultaneously: Qwen2.5-VL-7B for vision + Qwen3.5-35B-A3B for clinical reasoning. 192GB HBM3 makes this possible on a single GPU. Here's what we learned..." | In README or blog post |
| **Open-source or walkthrough** | Public GitHub repo + technical blog post | GitHub repo with full code + blog post: "How We Built a Hierarchical Agentic Medical AI on AMD MI300X" | Day 6 (submission) |

### Do You Need a Separate UI for This?

**No.** The "Build in Public" prize is about **documentation, social media, and community engagement** — not a separate UI.

**But** — having a polished product UI makes your "Build in Public" story stronger. The judges for this special prize will check:
1. Your social media posts (engagement, technical depth)
2. Your GitHub repo (code quality, README)
3. Your technical blog/walkthrough (did you actually teach something?)
4. Your HF Space (does it work?)

**The HF Space is your "ship it" proof.** If your product UI is live and functional, it proves you didn't just blog — you actually built something.

---

## 2. Do You Need Benchmarks? (Short Answer: YES, ABSOLUTELY)

### Why Benchmarks Are Non-Negotiable

| Without Benchmarks | With Benchmarks |
|-------------------|-----------------|
| "We claim under 5 seconds" — judge thinks: *"Prove it."* | "Mean latency 4.2s, P95 4.8s, 50 runs" — judge thinks: *"Credible."* |
| "We use AMD MI300X" — judge thinks: *"Where's the proof?"* | "GPU 89% utilized, VRAM 85GB/192GB, `rocm-smi` screenshot" — judge thinks: *"Real."* |
| "Our model fits on one GPU" — judge thinks: *"H100 can do that too."* | "H100 80GB would OOM at FP16. MI300X 192GB runs with 107GB headroom." — judge thinks: *"AMD advantage is real."* |

### What Judges Will Ask

**Q: "How do I know you're actually running on AMD MI300X and not your laptop?"**

**Your answer:** *"Open the 'Technical Details' panel in the UI. It shows real-time `rocm-smi` data: GPU temperature, utilization, VRAM usage, and model info. The benchmark histogram is generated from 50 live runs on the AMD Developer Cloud instance. You can verify by checking the `rocm-smi` output against AMD's spec sheet."*

**Q: "What if I don't believe your 'under 5 seconds' claim?"**

**Your answer:** *"The benchmark script is in our repo at `scripts/benchmark.py`. You can provision your own AMD Developer Cloud MI300X, run `bash scripts/run_benchmark.sh`, and reproduce the exact same histogram. The raw CSV with 50 latency measurements is in `benchmarks/raw_latencies.csv`."*

---

## 3. Where to Show Benchmarks in the UI

### Option A: "Technical Details" Button (Recommended)

```
┌────────────────────────────────────────────────────────────────────┐
│  CLINSIGHT > Results: Case 001                           [< Back]   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  [Results content: ESI, findings, safety, veto...]                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  🔍 TECHNICAL DETAILS  [Click to expand]                       ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
```

**When clicked, expands to:**

```
┌────────────────────────────────────────────────────────────────────┐
│  🔍 TECHNICAL DETAILS                                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  HARDWARE & PLATFORM                                         ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ││
│  │  GPU: AMD Instinct MI300X (192GB HBM3)                      ││
│  │  Platform: ROCm 7.0 + PyTorch 2.6.0 (ROCm build)            ││
│  │  Serving: vLLM 0.6.4 (ROCm backend, PagedAttention)        ││
│  │  Vision Model: Qwen2.5-VL-7B-Instruct (port 8000)         ││
│  │  Text Model: Qwen3.5-35B-A3B (port 8001)                   ││
│  │  Model: Qwen2.5-VL-7B-Instruct (Apache 2.0)               ││
│  │  Agents: LangGraph 0.2.x (5 parents + 7 subagents)         ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  REAL-TIME GPU METRICS (from rocm-smi)                       ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ││
│  │  GPU Utilization:     ████████████████████░░  89%           ││
│  │  GPU Memory Used:     ██████████░░░░░░░░░░  99GB / 192GB    ││
│  │  GPU Temperature:       62°C (normal)                        ││
│  │  Power Draw:           450W (typical for MI300X inference)  ││
│  │  ROCm Version:        7.0.0                                  ││
│  │  Driver Version:       6.8.5                                  ││
│  │                                                              ││
│  │  [Refresh Metrics]  [View Full rocm-smi Output →]          ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  PERFORMANCE BENCHMARKS (50 runs, this session)              ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ││
│  │                                                              ││
│  │  Latency Distribution:                                       ││
│  │  ┌────────────────────────────────────────┐                  ││
│  │  │    ▓▓▓▓▓▓▓▓▓▓▓▓                       │  0-3s: 8 runs   ││
│  │  │    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓              │  3-4s: 22 runs  ││
│  │  │    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓          │  4-5s: 15 runs  ││
│  │  │    ▓▓▓▓▓▓▓▓                           │  5-6s: 4 runs   ││
│  │  │    ▓▓                                  │  6s+:  1 run    ││
│  │  └────────────────────────────────────────┘                  ││
│  │                                                              ││
│  │  Mean Latency:        4.24 seconds                           ││
│  │  P95 Latency:         4.81 seconds                           ││
│  │  P99 Latency:         5.63 seconds                           ││
│  │  Cold Start:          92 seconds                             ││
│  │  Throughput (batch=1): 14.2 images/minute                    ││
│  │  Throughput (batch=8): 68.5 images/minute                    ││
│  │                                                              ││
│  │  [Download Raw CSV →]  [Reproduce on Your Hardware →]        ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  INFERENCE BREAKDOWN (last analysis)                           ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ││
│  │  Image Preprocessing:        0.18s  (resize, normalize)      ││
│  │  vLLM Queue Wait:            0.05s  (batching overhead)        ││
│  │  Time to First Token (TTFT):   1.85s  (model initial response) ││
│  │  Token Generation:           2.12s  (100 tokens @ 47 tok/s)    ││
│  │  JSON Parsing:               0.04s  (structured output)        ││
│  │  Safety Agent (parallel):    0.12s  (3 subagents + merge)    ││
│  │  ESI Scoring + Report:       0.08s  (deterministic rules)    ││
│  │  ──────────────────────────────────────────────────────────   ││
│  │  TOTAL:                      4.44s                           ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  AMD ADVANTAGE COMPARISON                                    ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ││
│  │                                                              ││
│  │  ┌──────────────────┐  ┌──────────────────┐               ││
│  │  │  AMD MI300X       │  │  NVIDIA H100 80GB │               ││
│  │  │  192GB HBM3       │  │  80GB HBM3        │               ││
│  │  │  ───────────────  │  │  ───────────────  │               ││
│  │  │  35B @ FP16       │  │  35B @ INT4       │               ││
│  │  │  + 107GB headroom │  │  + 0GB headroom   │               ││
│  │  │  for batching     │  │  (at limit)       │               ││
│  │  │  ───────────────  │  │  ───────────────  │               ││
│  │  │  Single GPU       │  │  Requires 2 GPUs   │               ││
│  │  │  or TP=1          │  │  or quantization │               ││
│  │  └──────────────────┘  └──────────────────┘               ││
│  │                                                              ││
│  │  [View Memory Calculation →]  [AMD Developer Cloud Specs →]││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  [Collapse Technical Details ↑]                                    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Why This UI Design Wins

| Section | Why It Matters |
|---------|---------------|
| **Hardware & Platform** | Proves you're using the exact stack the hackathon requires |
| **Real-Time GPU Metrics** | Live `rocm-smi` data proves this is running on real AMD hardware, not CPU simulation |
| **Performance Benchmarks** | Histogram + numbers make the "under 5 seconds" claim undeniable |
| **Inference Breakdown** | Shows you understand WHERE the latency comes from (not just a magic number) |
| **AMD Advantage Comparison** | Explicitly answers "why AMD over NVIDIA?" — the question every AMD judge wants answered |

### Option B: Split-Screen During Demo

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ┌────────────────────────────┐  ┌────────────────────────────┐   │
│  │                            │  │  AMD MI300X GPU METRICS   │   │
│  │  CLINSIGHT DASHBOARD       │  │                            │   │
│  │                            │  │  GPU: 89% ████████████░   │   │
│  │  [Case results showing]    │  │  VRAM: 85GB/192GB          │   │
│  │                            │  │  Model: Qwen3.5-35B-A3B    │   │
│  │                            │  │  ROCm: 7.0                 │   │
│  │                            │  │                            │   │
│  │                            │  │  Last latency: 4.2s        │   │
│  │                            │  │  Avg latency: 4.4s         │   │
│  │                            │  │                            │   │
│  └────────────────────────────┘  └────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**This is the split-screen you show during the live demo.** It proves AMD utilization in real-time while the analysis runs.

---

## 4. Benchmarks You MUST Have (No Exceptions)

### The Non-Negotiable List

| Benchmark | Target | Where Shown | Evidence File |
|-----------|--------|-------------|---------------|
| **End-to-end latency (warm, batch=1)** | < 5.0s mean | UI Technical Details + video | `benchmarks/latency_histogram.png` |
| **End-to-end latency (warm, batch=4)** | < 6.0s mean | UI Technical Details (expand) | `benchmarks/throughput_batch4.png` |
| **End-to-end latency (warm, batch=8)** | < 8.0s mean | UI Technical Details (expand) | `benchmarks/throughput_batch8.png` |
| **TTFT (Time to First Token)** | < 2.5s | UI Inference Breakdown | vLLM `/metrics` endpoint |
| **Token generation speed** | > 25 tok/s | UI Inference Breakdown | vLLM `/metrics` endpoint |
| **GPU utilization during inference** | > 85% | UI Real-Time Metrics | `rocm-smi` screenshot |
| **GPU memory allocated** | ~85GB | UI Real-Time Metrics | `rocm-smi` screenshot |
| **GPU memory headroom** | > 90GB free | UI AMD Advantage Comparison | VRAM math in README |
| **Cold start time** | < 120s | UI Performance Benchmarks | Timer log |
| **Throughput (batch=1)** | > 12 img/min | UI Performance Benchmarks | Calculated from latency |
| **Throughput (batch=8)** | > 60 img/min | UI Performance Benchmarks | vLLM metrics |
| **Contingency mode response** | < 0.2s | Not in UI (emergency only) | Cached JSON retrieval |

### What Judges Will Ask About Benchmarks

**Q: "How do I know these numbers are real and not made up?"**

**A:** *"Three ways to verify: (1) The raw CSV with 50 timestamped measurements is in `benchmarks/raw_latencies.csv` — each row has a Unix timestamp and latency. (2) The benchmark script `scripts/benchmark.py` is reproducible — run it on any AMD Developer Cloud MI300X and you'll get similar results. (3) The `rocm-smi` screenshots in `benchmarks/` show GPU utilization during the actual benchmark runs, not idle states."*

**Q: "Why should I care about batch=8 throughput? You said batch=1 in the demo."**

**A:** *"Batch=1 is what the judge sees in the demo — one patient at a time. But in a real ED, the system would process multiple cases simultaneously. Batch=8 throughput at 68 img/min shows the MI300X's headroom is real — we're using only 85GB of 192GB. The remaining 107GB enables concurrent processing without quantization or multi-GPU complexity."*

---

## 5. Where Benchmarks Live in Your Repo

```
clinsight/
├── benchmarks/
│   ├── latency_histogram.png              # 50-run distribution chart
│   ├── latency_histogram_batch4.png         # 20-run batch=4 chart
│   ├── latency_histogram_batch8.png         # 20-run batch=8 chart
│   ├── rocm_smi_during_inference.png      # Screenshot showing 89% util
│   ├── rocm_smi_idle.png                  # Screenshot showing 0% util (contrast)
│   ├── vllm_metrics_endpoint.json          # Raw /metrics output
│   ├── raw_latencies.csv                  # 50 rows: timestamp, latency, batch_size
│   ├── raw_latencies_batch4.csv           # 20 rows
│   ├── raw_latencies_batch8.csv           # 20 rows
│   └── benchmark_report.md                # Human-readable summary
│
├── scripts/
│   ├── run_benchmark.sh                   # One-shot: runs all benchmarks
│   └── benchmark.py                       # Python benchmark script
│
└── docs/
    ├── benchmark_methodology.md           # How we benchmarked (controlled conditions)
    └── hardware_spec.md                   # Exact AMD Cloud instance specs
```

---

## 6. The "Build & Ship" Prize Deliverables

### What You Need to Submit for This Special Prize

| Deliverable | Description | Format | Where |
|-------------|-------------|--------|-------|
| **Social Post #1** | Day 1-2 update: Provisioning, first model load, initial thoughts on ROCm | X/Tweet or LinkedIn | Tag @lablab + @AlatAMD |
| **Social Post #2** | Day 4-5 update: Dual-model architecture working — Qwen2.5-VL for vision + Qwen3.5 MoE for clinical reasoning on single MI300X | X/Tweet or LinkedIn | Tag @lablab + @AlatAMD |
| **GitHub Repo** | Open-source code with full README | Public GitHub | Link in submission |
| **Technical Walkthrough** | Blog post or README section explaining HOW you built it | Markdown / Blog | Link in submission |
| **AMD Feedback** | Meaningful feedback about ROCm/AMD Cloud experience | In README or blog | "What worked, what didn't, what we'd improve" |

### Social Media Post Templates

**Post 1 (Day 1-2):**
```
Day 1 of building @lablab hackathon project on AMD MI300X:
✅ Provisioned AMD Developer Cloud instance
✅ Installed ROCm 7.0 + PyTorch 2.6.0 (ROCm build)
✅ Loaded dual models on MI300X via vLLM: Qwen2.5-VL-7B (vision) + Qwen3.5-35B-A3B (text reasoning)
✅ First inference: 4.8s for chest X-ray + labs

Early thought: The 192GB HBM3 on MI300X is a game-changer.
Running 35B at FP16 with 107GB headroom? H100 can't do that.

#AMD #ROCm #MI300X #LangGraph #MedicalAI
@lablab @AlatAMD
```

**Post 2 (Day 4-5):**
```
Day 4: Built the crown jewel — a parallel Safety Agent with 3 subagents:
🔍 Contradiction Checker (image vs labs)
👁️ Hallucination Guard (visual grounding)
⚖️ Bias Auditor (demographic disparities)

All 3 run in parallel and merge into a single confidence score.
The merge node was the trickiest part — state synchronization
across parallel LangGraph nodes isn't well documented.

Latency impact? Only +120ms for 3 safety checks vs. single-pass.
Worth it for the safety gain.

#AMD #ROCm #LangGraph #AgenticAI #HealthcareAI
@lablab @AlatAMD
```

**LinkedIn Post (Day 6):**
```
Just submitted our hackathon project: ClinSight — a hierarchical
multimodal agentic system for emergency triage, built entirely on
AMD Instinct MI300X via ROCm 7.0.

What we built:
• 5 parent agents + 7 subagents in LangGraph
• 3 parallel safety checks (contradiction + hallucination + bias)
• Sub-5s inference for chest X-ray + labs + history
• 50-run benchmarked latency with reproducible script

What we learned about ROCm:
✅ vLLM backend serves dual-model clinical AI simultaneously on single MI300X
✅ PagedAttention on MI300X handles 262K context smoothly
⚠️ Multimodal image preprocessing docs need more examples
⚠️ AITER kernel compilation takes 3-5 min on first run

Full write-up: [link to blog]
Open-source repo: [link to GitHub]

#AMD #ROCm #MI300X #HealthcareAI #LangChain
@AMD Developer @lablab.ai
```

---

## 7. The AMD Proof Strategy

### Judges Will Ask: "How Do I Know You're Actually Using AMD?"

**Your answer must have 3 layers:**

**Layer 1: UI Proof (Immediate)**
- Real-time `rocm-smi` metrics panel in the UI
- GPU utilization fluctuates during inference (not static fake numbers)
- ROCm version 7.0 explicitly stated

**Layer 2: Screenshot Proof (In Deck)**
- `rocminfo` output showing "AMD Instinct MI300X"
- `rocm-smi` showing 192GB total memory
- vLLM logs showing "ROCm backend loaded" for BOTH models (port 8000 + 8001)
- PyTorch showing `torch.cuda.get_device_name(0)` = "AMD Instinct MI300X"

**Layer 3: Reproducible Proof (In Repo)**
- Benchmark script that any judge can run
- Raw CSV with timestamped measurements
- `requirements.txt` with `torch-rocm7.0` wheels
- `docs/amd_setup.md` with exact install commands

### The "AMD Advantage" Slide (For Pitch Deck)

```
┌────────────────────────────────────────────────────────────────────┐
│  WHY AMD MI300X?                                                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────┐  ┌─────────────────────┐                   │
│  │  AMD Instinct       │  │  NVIDIA H100 80GB   │                   │
│  │  MI300X 192GB       │  │  (closest comp)     │                   │
│  │                     │  │                     │                   │
│  │  Qwen3.5-35B-A3B    │  │  Qwen3.5-35B-A3B    │                   │
│  │  @ bfloat16         │  │  @ INT4 quantized   │                   │
│  │                     │  │  (accuracy loss)    │                   │
│  │  Single GPU         │  │  2 GPUs or          │                   │
│  │  No quantization    │  │  quantization       │                   │
│  │                     │  │                     │                   │
│  │  85GB used          │  │  ~75GB used         │                   │
│  │  107GB headroom     │  │  ~5GB headroom      │                   │
│  │  for batching       │  │  (no batching room) │                   │
│  │                     │  │                     │                   │
│  │  Latency: 4.2s      │  │  Latency: 4.5s*     │                   │
│  │  (batch=1, FP16)    │  │  (batch=1, INT4)    │                   │
│  │                     │  │  *estimated         │                   │
│  │                     │  │                     │                   │
│  │  ✅ Full precision  │  │  ⚠️ Quantized      │                   │
│  │  ✅ Single GPU      │  │  ⚠️ Multi-GPU      │                   │
│  │  ✅ Massive headroom│  │  ❌ Limited headroom│                   │
│  └─────────────────────┘  └─────────────────────┘                   │
│                                                                    │
│  *H100 comparison based on published specs and VRAM math.        │
│   We did not have access to H100 for direct benchmarking.          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Important note:** If you didn't actually benchmark on H100, **say so honestly.** "Estimated based on VRAM math" is fine. Claiming you benchmarked on H100 when you didn't is disqualifying.

---

## 8. Final Checklist: Build & Ship + Benchmarks

### Build & Ship Prize
- [ ] **Social Post #1** published (Day 1-2), tagged @lablab + @AlatAMD
- [ ] **Social Post #2** published (Day 4-5), tagged @lablab + @AlatAMD
- [ ] **GitHub repo** public with Apache 2.0 license
- [ ] **Technical walkthrough** in README or blog post (how you built it, not just what)
- [ ] **AMD feedback** section: what worked, what didn't, suggestions for improvement
- [ ] **HF Space** live and public (proves you "shipped")

### Benchmarks (In UI)
- [ ] **"Technical Details" button** on Results screen
- [ ] **Expands to show:** Hardware specs, GPU metrics, latency histogram, inference breakdown, AMD comparison
- [ ] **Real-time metrics** actually call `rocm-smi` or read from cached endpoint
- [ ] **Histogram** is from real 50-run benchmark (not mock data)
- [ ] **Inference breakdown** shows TTFT + generation + preprocessing separately

### Benchmarks (In Repo)
- [ ] `scripts/benchmark.py` — reproducible
- [ ] `scripts/run_benchmark.sh` — one-shot runner
- [ ] `benchmarks/raw_latencies.csv` — 50+ timestamped rows
- [ ] `benchmarks/latency_histogram.png` — matplotlib chart
- [ ] `benchmarks/rocm_smi_during_inference.png` — screenshot proof
- [ ] `docs/benchmark_methodology.md` — how you tested

### AMD Proof (3 Layers)
- [ ] **UI Layer:** Real-time GPU metrics panel
- [ ] **Deck Layer:** `rocm-smi` + `rocminfo` screenshots
- [ ] **Repo Layer:** Reproducible benchmark script + setup docs

---

## Bottom Line

| Question | Answer |
|----------|--------|
| **Do I need a separate UI for Build & Ship?** | No. But your main UI must work (HF Space = "shipped"). |
| **Should benchmarks be in the UI?** | **YES.** "Technical Details" expandable panel. Non-negotiable. |
| **Do I need benchmarks at all?** | **YES.** Without them, "under 5 seconds" is just a claim. With them, it's proof. |
| **Will judges want to see AMD usage?** | **YES.** The entire hackathon is about proving AMD's stack. If you don't show GPU metrics, judges assume you're not using AMD. |
| **How much AMD proof is enough?** | 3 layers: UI real-time metrics + deck screenshots + repo reproducible script. |

**The "Technical Details" button in your UI is the single most important AMD proof element.** Judges who click it see real numbers. Judges who don't click it see it exists. Both are wins.

**Build it. Benchmark it. Show it. Ship it.**

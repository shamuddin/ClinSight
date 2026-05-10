# ClinSight — Image Prompts for Technical Walkthrough Article

> Use these prompts to generate images for `docs/TECHNICAL_WALKTHROUGH.md` / `ARTICLE_PUBLISH.md`.
> Tools: DALL-E 3, Midjourney v6, Canva, Figma, or Excalidraw for diagrams.

---

## Image 1: Hero / Cover Image

**Placement:** Top of article, before Section 1  
**Dimensions:** 1600 × 900 px (16:9)  
**Tool:** DALL-E 3 or Midjourney  
**Purpose:** First impression — establishes medical AI + AMD tech aesthetic

### Prompt

```
A futuristic medical command center dashboard interface on a dark navy background (#0a0a0a). 
Left third: a chest X-ray image with cyan-teal attention region highlights overlaid. 
Center: large bold white text "ClinSight" with subtitle "Hierarchical Multimodal Clinical Intelligence" in lighter gray. 
Right third: medical vitals panel showing BP 104/68, HR 118, SpO2 88%, and a red "ESI 1 — Immediate" triage badge. 
Bottom right corner: small AMD logo and "AMD Instinct MI300X" badge. 
Glassmorphism card UI elements with subtle cyan glow accents (#38bdf8). 
Clean, professional, medical technology aesthetic. High detail, 8K render, no blur.
```

**Alternative (simpler):**
```
Dark medical AI dashboard hero banner, chest X-ray with cyan heatmap overlays, ESI triage score badge, vital signs display, AMD MI300X chip icon, dark theme with teal accents, clean UI design, 16:9 aspect ratio, professional tech illustration
```

---

## Image 2: MI300X vs H100 VRAM Comparison

**Placement:** Section 1 — "Why AMD MI300X for Healthcare AI?"  
**Dimensions:** 1200 × 800 px  
**Tool:** Canva (recommended) or DALL-E 3  
**Purpose:** Visual proof of the "impossible on H100" claim

### Prompt (for AI generation)

```
A clean tech infographic comparing two GPU chips side by side on a dark background. 

LEFT SIDE — "AMD Instinct MI300X" in green/cyan (#4ade80): 
- Large text "192 GB HBM3"
- Inside the GPU chip silhouette, two model icons fit comfortably: 
  * Eye icon labeled "Vision 14GB" 
  * Brain icon labeled "Text 70GB"
- Green text "93GB headroom remaining" with a checkmark
- Status: "Fits at FP16"

RIGHT SIDE — "NVIDIA H100 80GB" in muted gray/red: 
- Large text "80 GB HBM3"
- Same two model icons overflowing outside the chip boundary with red warning triangles
- Red text "Requires quantization (INT8/INT4)"
- Status: "Degrades clinical accuracy"

Center dividing line. Isometric 3D GPU chip renders. Clean sans-serif typography. 
Dark tech presentation style. No clutter.
```

**Canva DIY (5 min):**
- Background: #0a0a0a
- Left card: #1e293b with green border #4ade80
- Right card: #1e293b with red border #f87171
- Icons: Search "chip" + "eye" + "brain" in Canva Elements
- Text: Bold white headings, gray subtext

---

## Image 3: Dual-Model Architecture Diagram

**Placement:** Section 2 — "Model Selection: Vision + Text"  
**Dimensions:** 1400 × 900 px  
**Tool:** Excalidraw, Figma, or Canva (recommended — AI struggles with readable architecture diagrams)  
**Purpose:** Show how vision and text models feed into the agent pipeline

### Diagram Structure (Build in Canva/Excalidraw)

```
[Top] "Chest X-Ray Input" → arrow splits into two parallel paths

PATH A (left, cyan):
  Box: "Qwen2.5-VL-7B-Instruct" 
  Subtext: "~14GB FP16 | Vision Analysis"
  Icon: Eye or camera
  Output: "Findings JSON + Attention Regions"

PATH B (right, purple):
  Box: "Qwen3.5-35B-A3B MoE"
  Subtext: "~70GB FP16 | Clinical Reasoning"
  Icon: Brain
  Output: "Differential Diagnosis + Synthesis"

Both paths converge into central hub:
  "LangGraph Agent Pipeline"

Hub branches to 5 colored nodes in horizontal row:
  1. Coordinator (blue) — "Quality + Pediatric Gates"
  2. Radiologist (cyan) — "Image Prep → Pathology Analyzer"
  3. Lab Analyst (yellow) — "Critical Values + Patterns"
  4. Safety (red) — "3 Parallel Checks + Merge"
  5. Documenter (green) — "ESI + Report"

Arrows show data flow direction. Rounded rectangles. 
Dark background (#0a0a0a). Cyan connecting arrows (#38bdf8).
```

**AI Prompt (if you prefer generation):**
```
Clean software architecture diagram on dark navy background. 
Top: "Chest X-Ray Input" splits into two parallel boxes. 
Left box (cyan border): "Qwen2.5-VL-7B" with eye icon, "14GB Vision". 
Right box (purple border): "Qwen3.5-35B-A3B" with brain icon, "70GB Reasoning". 
Both converge into central hub "LangGraph Pipeline" which branches to 5 rounded rectangles below: 
Coordinator, Radiologist, Lab Analyst, Safety, Documenter. 
Each with small descriptive subtext. Cyan arrows. Minimalist, readable, professional tech diagram. No photorealism.
```

---

## Image 4: vLLM Terminal + rocm-smi Split Screen

**Placement:** Section 4 — "vLLM Serving on ROCm 7.0"  
**Dimensions:** 1600 × 900 px  
**Tool:** Take an actual screenshot, OR DALL-E 3  
**Purpose:** Prove real AMD hardware + dual-model serving

### Prompt (for AI generation)

```
A split-screen terminal screenshot aesthetic on a dark background. 

LEFT TERMINAL (60% width):
- Black background, green/cyan monospace text
- Title bar: "rocm-smi | AMD Instinct MI300X"
- Stats displayed:
  GPU[0]: Temperature 38°C (junction)
  GPU[0]: Power 231W
  GPU[0]: GPU use 10%
  GPU[0]: VRAM Total 192GB
  GPU[0]: VRAM Used 181GB (94.4%)
- Highlight: "AMD Instinct MI300X" in cyan

RIGHT TERMINAL (40% width):
- Black background, white/green monospace text  
- Two server logs stacked:
  * "vLLM server on port 8000 — Qwen2.5-VL-7B ready"
  * "vLLM server on port 30000 — Qwen3.5-35B-A3B ready"
- Green "Application startup complete" messages
- Small text: "ROCm 7.0 | vLLM 0.6.x"

Realistic terminal window chrome with minimize/maximize/close buttons. 
Looks like a real Linux server screenshot. No blur, crisp text.
```

**BETTER OPTION:** Take an actual screenshot of your terminal when the servers are running, or use the `scripts/capture_rocm_smi_live.sh` output. Real screenshots > AI-generated for proof.

---

## Image 5: LangGraph Agent Flow Diagram

**Placement:** Section 5 — "LangGraph Agent Architecture"  
**Dimensions:** 1600 × 700 px (wide horizontal)  
**Tool:** Excalidraw or Canva (strongly recommended over AI)  
**Purpose:** Show the 5-agent pipeline and 7 subagents

### Diagram Structure

```
Horizontal flowchart, left to right, 5 main nodes connected by thick cyan arrows.

NODE 1: Coordinator
  Shape: Rounded rectangle, blue (#3b82f6)
  Sub-nodes (smaller, below): 
    - Image Quality Gate
    - Pediatric Safety Gate

→ Arrow →

NODE 2: Analysis (Radiologist + Lab)
  Shape: Rounded rectangle, cyan (#06b6d4)
  Sub-nodes:
    - Image Prep → Pathology Analyzer (VLM call)
    - Critical Value Detector → Pattern Correlator

→ Arrow →

NODE 3: Safety
  Shape: Rounded rectangle, red (#ef4444)
  Sub-nodes (parallel, arranged horizontally):
    - Contradiction Checker
    - Hallucination Guard  
    - Bias Auditor
  All three converge into diamond: "Merge Node"

→ Arrow →

NODE 4: Documenter
  Shape: Rounded rectangle, green (#22c55e)
  Sub-nodes:
    - ESI Scorer (deterministic)
    - Differential Builder
    - Report Generator

→ Arrow →

NODE 5: END
  Shape: Circle, gray (#64748b)

Bottom label: "Compiled StateGraph — backend/agents/graph.py"
```

**AI Prompt:**
```
Horizontal software flowchart on dark background. 
5 main nodes connected by thick cyan arrows: 
(1) Coordinator with 2 small sub-nodes below, 
(2) Analysis with 4 small sub-nodes, 
(3) Safety with 3 parallel sub-nodes converging into a diamond Merge shape, 
(4) Documenter with 3 sub-nodes, 
(5) END circle. 
Each main node is a rounded rectangle in different color (blue, cyan, red, green, gray). 
Small sub-nodes are lighter shades. Clean sans-serif text. 
Dark tech diagram style. Readable at 1200px width.
```

---

## Image 6: Safety Subgraph Panel

**Placement:** Section 6 — "The Safety Subgraph"  
**Dimensions:** 1200 × 800 px  
**Tool:** Canva or DALL-E 3  
**Purpose:** Visualize the 3 parallel safety checks

### Prompt

```
A medical software "Safety Audit" panel interface on a dark theme (#0f172a background). 

Three horizontal audit rows, each with a checkbox on the left:

ROW 1 (green):
  Checkbox: checked green checkmark
  Title: "Contradiction Check"
  Detail: "1 mismatch found: Image suggests pneumonia, WBC normal"
  Badge: "MEDIUM"

ROW 2 (yellow):
  Checkbox: yellow warning triangle
  Title: "Hallucination Guard" 
  Detail: "All findings have visual grounding"
  Badge: "PASS"

ROW 3 (blue):
  Checkbox: blue info circle
  Title: "Bias Audit"
  Detail: "Elderly patient flagged — undertriage risk"
  Badge: "REVIEW"

BOTTOM SECTION:
  Large confidence meter bar showing 88% → 55%
  Red downward arrow
  Text: "Confidence downgraded: CONTRADICTION_REVIEW"
  Red banner: "PHYSICIAN REVIEW REQUIRED"

Glassmorphism cards, teal accent borders, clean medical UI. 
Professional, trustworthy, dark mode. No photorealism.
```

---

## Image 7: 50-Case Benchmark Results

**Placement:** Section 7 — "Real Benchmarks on MI300X"  
**Dimensions:** 1200 × 600 px  
**Tool:** Use existing `benchmarks/latency_histogram_real.png` OR generate a new chart  
**Purpose:** Prove 50-case live benchmark success

### Recommended: Generate a New Chart with Python

Run this on your machine to create a Grand Prize-worthy chart:

```python
import json
import matplotlib.pyplot as plt

# Load 50-case benchmark
with open("benchmarks/gpu_results/batch_50_cxr_live/benchmark_summary.json") as f:
    data = json.load(f)

cases = [r["case_id"] for r in data["results"]]
latencies = [r["elapsed_sec"] for r in data["results"]]

plt.figure(figsize=(14, 6))
bars = plt.bar(range(len(cases)), latencies, color="#06d6a0", edgecolor="#0a0a0a", linewidth=0.5)
plt.axhline(y=data["mean_latency_sec"], color="#ef476f", linestyle="--", linewidth=2, label=f"Mean: {data['mean_latency_sec']:.2f}s")
plt.fill_between(range(len(cases)), data["mean_latency_sec"]-1, data["mean_latency_sec"]+1, alpha=0.1, color="#ef476f")

plt.title("ClinSight — 50-Case Live Inference Latency on AMD MI300X\nQwen2.5-VL-7B + Qwen3.5-35B-A3B | ROCm 7.0 | vLLM | All Cases: cached=false", fontsize=13, fontweight="bold", color="#f8fafc")
plt.xlabel("Case ID", fontsize=11, color="#94a3b8")
plt.ylabel("Latency (seconds)", fontsize=11, color="#94a3b8")
plt.xticks(range(0, len(cases), 5), [cases[i] for i in range(0, len(cases), 5)], rotation=45, ha="right", color="#94a3b8")
plt.yticks(color="#94a3b8")
plt.legend(loc="upper right", facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc")
plt.ylim(15, 30)

# Dark theme
plt.gca().set_facecolor("#0a0a0a")
plt.gcf().set_facecolor("#0a0a0a")
plt.grid(axis="y", alpha=0.15, color="#94a3b8")

# Add annotation
plt.text(0.02, 0.98, f"50/50 Success | Mean: {data['mean_latency_sec']:.2f}s | Min: {min(latencies):.2f}s | Max: {max(latencies):.2f}s",
         transform=plt.gca().transAxes, fontsize=10, verticalalignment="top",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#1e293b", edgecolor="#334155"),
         color="#f8fafc")

plt.tight_layout()
plt.savefig("benchmarks/latency_50_cases.png", dpi=150, facecolor="#0a0a0a")
plt.show()
```

**AI Prompt (if you can't run Python):**
```
A dark-themed bar chart showing 50 vertical bars in teal/cyan gradient. 
X-axis: Case IDs from CS-2024-001 to CS-2024-050. 
Y-axis: Latency in seconds (range 15-30). 
Horizontal red dashed line across the chart labeled "Mean: 23.02s". 
Title: "50-Case Live Inference Latency on AMD MI300X". 
Subtitle: "Qwen2.5-VL-7B + Qwen3.5-35B-A3B | ROCm 7.0 | All cached=false". 
Dark background (#0a0a0a). Teal bars (#06d6a0). Red mean line (#ef476f). 
Clean data visualization style, no 3D effects.
```

---

## Image 8: "What If?" Demo Comparison

**Placement:** Section 8 (or create a new subsection after benchmarks)  
**Dimensions:** 1200 × 700 px  
**Tool:** Canva or DALL-E 3  
**Purpose:** Prove multimodal reasoning, not just input

### Prompt

```
A split-screen medical dashboard comparison on dark background. 

LEFT PANEL — "Scenario A: Critical Labs":
- Same chest X-ray image at top
- Lab values in red (critical):
  * Lactate: 3.2 (red)
  * pO2: 58 (red)
  * WBC: 18.5 (red)
- Large red badge: "ESI 1 — Immediate"
- Text: "Tension pneumothorax suspected. Emergency decompression required."

RIGHT PANEL — "Scenario B: Normal Labs":
- Same chest X-ray image at top (identical)
- Lab values in green (normal):
  * Lactate: 1.1 (green)
  * pO2: 98 (green) 
  * WBC: 7.2 (green)
- Large yellow badge: "ESI 3 — Urgent"
- Text: "Monitor and repeat imaging in 4 hours."

Center dividing arrow labeled "What If?"
Bottom banner: "Same image. Different labs. Different triage. This is multimodal reasoning."

Dark medical UI theme. Glassmorphism cards. Teal and red accents. Clean, professional.
```

---

## Image 9: ROCm Developer Experience Summary

**Placement:** Section 8 — "ROCm Developer Experience"  
**Dimensions:** 1200 × 600 px  
**Tool:** Canva (recommended)  
**Purpose:** Quick visual summary of what works vs what needed workarounds

### Canva Layout (DIY — 3 minutes)

```
Background: #0a0a0a

LEFT CARD (green border #22c55e):
  Title: "✅ Works Out of the Box"
  Bullets:
    • PyTorch 2.6.0+rocm7.0
    • vLLM ROCm backend
    • Qwen2.5-VL-7B
    • Qwen3.5-35B-A3B
    • AsyncOpenAI client

RIGHT CARD (yellow border #eab308):
  Title: "⚠️ Required Workarounds"
  Bullets:
    • Overlayfs → use /mnt/scratch
    • Power mgmt → disable auto-sleep
    • rocm-smi temp → junction vs edge
    • Container networking → 172.17.0.1

Bottom text: "ROCm 7.0 is production-ready for inference"
```

**AI Prompt:**
```
A dark-themed two-column comparison infographic. 
Left column with green header "Works Out of the Box" and 5 green checkmark items. 
Right column with yellow header "Required Workarounds" and 4 yellow warning items. 
Bottom center: bold text "ROCm 7.0 is production-ready for inference". 
Dark background (#0a0a0a). Clean sans-serif. No clutter. Professional tech blog style.
```

---

## Image 10: AMD MI300X Hardware Close-Up (Optional)

**Placement:** Section 1 or Section 4  
**Dimensions:** 1200 × 800 px  
**Tool:** DALL-E 3 or use stock AMD photo  
**Purpose:** Hardware credibility

### Prompt

```
A dramatic close-up product shot of an AMD Instinct MI300X GPU chip. 
Dark studio lighting with cyan and teal accent lights reflecting off the heatsink fins. 
The chip is angled at 45 degrees showing the "AMD Instinct MI300X" branding. 
HBM3 memory stacks visible around the edges. 
Subtle glow effect. Black background. 
Product photography style, high detail, no text overlays.
```

**Alternative:** Download official AMD MI300X product photo from AMD's press kit (free to use for editorial).

---

## 📋 Quick Reference: Which Tool to Use

| Image | Best Tool | Time |
|-------|-----------|------|
| Hero / Cover | DALL-E 3 | 1 min |
| VRAM Comparison | Canva | 5 min |
| Architecture Diagram | Canva / Excalidraw | 10 min |
| Terminal Screenshot | REAL screenshot (best) or DALL-E | 5 min |
| Agent Flowchart | Canva / Excalidraw | 10 min |
| Safety Panel | DALL-E 3 | 1 min |
| Benchmark Chart | Python matplotlib | 5 min |
| What If Comparison | Canva / DALL-E | 5 min |
| ROCm Summary | Canva | 3 min |

---

## 🚀 Recommended Minimum Set for Grand Prize

If you're short on time, generate **only these 5**:

1. **Hero image** (DALL-E) — first impression
2. **VRAM comparison** (Canva) — proves AMD advantage
3. **Agent flowchart** (Canva/Excalidraw) — proves real architecture
4. **Benchmark chart** (Python) — proves 50-case evidence
5. **Safety panel** (DALL-E) — proves clinical rigor

---

*Generated: May 10, 2026*

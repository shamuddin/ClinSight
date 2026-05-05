# ClinSight — Final UI Flow Specification (Judge-Corrected)
**AMD Developer Hackathon @ lablab.ai | May 2026**
**Version: Production-Ready, Judge-Proof, 6-Click Demo**

---

## The Judge-First Design Philosophy

> *"The judge has 12 minutes. They will spend 30–60 seconds clicking your HF Space. If any click fails, confuses, or delays — they score you down and move on. Every pixel, every click, every word must earn its place."*

**Rules:**
1. **Zero friction entry** — URL opens dashboard, not a landing page
2. **One clear action per screen** — never make the judge guess what to click
3. **No hidden functionality** — if it doesn't work or isn't tested, it's not visible
4. **Mobile-first thinking** — judges use 13-inch laptops and iPads
5. **Error states are features** — contingency mode, validation gates, and kill switches prove engineering maturity

---

## The 5-Screen Demo Flow (Reduced from 7)

```
┌────────────────────────────────────────────────────────────────────┐
│  1. DASHBOARD (Entry Point — No Landing Page)                     │
│     ├─ 6 case cards visible immediately                            │
│     ├─ "All data synthetic / public domain" banner                  │
│     └─ Click Case 001 → Case Detail                                │
│                                                                    │
│  2. CASE DETAIL (Pre-Inference)                                    │
│     ├─ X-ray dominates (60% width)                                 │
│     ├─ Labs as collapsible drawer                                  │
│     ├─ One safety banner (expandable)                              │
│     └─ Click "Analyze" → Inference                                 │
│                                                                    │
│  3. INFERENCE (Real-Time Animation)                                │
│     ├─ 3 visible steps (not 12)                                    │
│     ├─ Progress bars (not spinners)                                │
│     ├─ GPU metrics panel (20% of screen)                           │
│     ├─ NO cancel button (judge can't accidentally kill it)       │
│     └─ Complete → Results                                          │
│                                                                    │
│  4. RESULTS (Post-Inference)                                       │
│     ├─ ESI score dominates (20% of screen height)                  │
│     ├─ X-ray + findings side-by-side                              │
│     ├─ Safety banner (one, collapsible)                            │
│     ├─ Differential hidden behind "Show differential →"           │
│     ├─ Physician veto bar STICKY (always visible)                   │
│     ├─ "Technical Details" button (expandable benchmark panel)      │
│     └─ Click "What If?" → Comparison                               │
│                                                                    │
│  5. "WHAT IF?" (Demo Killer Feature)                             │
│     ├─ 3 pre-computed scenario buttons (not live editing)        │
│     ├─ Side-by-side or toggle comparison                           │
│     ├─ "Key insight" text explains WHY model changed               │
│     └─ Return to Results or Dashboard                              │
└────────────────────────────────────────────────────────────────────┘
```

**Total clicks in happy path: 6**
1. Open URL → Dashboard loads
2. Click Case 001 card
3. Click "Analyze"
4. Wait for inference → Results show
5. Click "What If?"
6. Click "Scenario B"

---

## Real-World Workflow Mapping

**Critical context for judges:** The UI you see is a **technical demonstration** of multimodal reasoning. In production deployment, these screens map to real clinical workflow as follows:

| Demo Screen | Real-World Deployment | Who Uses It | When |
|-------------|----------------------|-------------|------|
| **Dashboard (ESI scores)** | **Radiology worklist prioritization** | Radiologist / ED physician | After X-ray taken, before read |
| **Case Detail (image + labs)** | **PACS + EHR integrated view** | Physician / PA / NP | After workup complete (min 60+) |
| **Inference animation** | **Background queue processing** | System (no UI) | Automatic on imaging queue |
| **Results (differential + actions)** | **Structured report in EHR** | Physician | During chart review |
| **"What If?" comparison** | **Clinical decision support** | Physician / trainee | When diagnosis is uncertain |

**Pitch deck line to add:** *"This UI demonstrates multimodal reasoning capability. Production deployment would embed as a PACS/EHR plugin, not a standalone triage interface."*

### Why This Honesty Wins

Judges who know healthcare will immediately ask: *"Why would a physician use this after triage is done?"*

**Your answer:** *"You're right — ESI is assigned at minute 5 with almost no data. By minute 60, the patient is in a bed. ClinSight doesn't replace triage. It adds value at two points: first, it prioritizes the radiology queue — flagging which of 30 pending X-rays needs immediate eyes. Second, after workup, it acts as a diagnostic co-pilot — correlating image findings with lab patterns to catch cognitive errors like 'infiltrate = pneumonia' when BNP and pO2 actually suggest heart failure."*

**This framing is stronger than claiming to replace triage because it shows clinical sophistication, admits limitations, and positions the technical achievement correctly.**

---

## SCREEN 1: Dashboard (Entry Point)

### Design

```
┌────────────────────────────────────────────────────────────────────┐
│  🏥 CLINSIGHT    Physician-in-the-Loop Decision Support          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ ⚠️ All data is synthetic or from public de-identified         ││
│  │    research datasets. No real patient data is used.           ││
│  │    Images: NIH Chest X-ray14 (Public Domain)                  ││
│  │    Labs/Notes: Clinically reviewed synthetic data            ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  Active Cases (6)                                                  │
│                                                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ 🔴 CRITICAL     │  │ 🔴 CRITICAL     │  │ 🟡 URGENT       │   │
│  │                 │  │                 │  │                 │   │
│  │  Case 001       │  │  Case 002       │  │  Case 003       │   │
│  │  Tension Pneumo │  │  Sepsis + PNA   │  │  Large Effusion │   │
│  │  M, 34 y/o      │  │  F, 67 y/o      │  │  F, 45 y/o      │   │
│  │  Post-MVA       │  │  Fever 3 days   │  │  SOB 1 week     │   │
│  │  [Click to Analyze →]            │  │  [Click to Analyze →]            │  │  [Click to Analyze →]            │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ 🟡 URGENT       │  │ 🟢 NORMAL       │  │ 🟢 NORMAL       │   │
│  │                 │  │                 │  │                 │   │
│  │  Case 004       │  │  Case 005       │  │  Case 006       │   │
│  │  Focal Pneumonia│  │  Clear lungs    │  │  Cardiac Edema  │   │
│  │  M, 52 y/o      │  │  M, 28 y/o      │  │  F, 71 y/o      │   │
│  │  Productive cough│  │  Mild cough     │  │  CHF history    │   │
│  │  [Click to Analyze →]            │  │  [Click to Analyze →]            │  │  [Click to Analyze →]            │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                    │
│  Legend: 🔴 ESI 1–2 (Immediate/Emergent)  🟡 ESI 3–4 (Urgent)   │
│          🟢 ESI 5 (Non-urgent)                                     │
│                                                                    │
│  🔒 All processing on AMD Instinct MI300X — ROCm 7.0 — On-premise │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Behavior
- **URL opens directly to this screen** — no landing page, no login, no role selection
- **Synthetic data banner is always visible** — judges immediately know data source
- **No "New Case" button** — hidden by CSS (`display: none`) in demo mode
- **No timestamps** — removed to avoid "fake" appearance
- **Color + text labels** — "🔴 CRITICAL" not just red color (colorblind accessible)
- **All 6 cases pre-loaded** — zero delay on click

---

## SCREEN 2: Case Detail (Pre-Inference)

### Design

```
┌────────────────────────────────────────────────────────────────────┐
│  🏥 CLINSIGHT > Case 001: Tension Pneumothorax         [< Back]   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────┐  ┌──────────────┐  │
│  │                                          │  │ LABS          │  │
│  │     [CHEST X-RAY — 60% WIDTH]            │  │ ▼ Collapse   │  │
│  │                                          │  │               │  │
│  │    ┌──────────────────────────┐            │  │ WBC      9.5K │  │
│  │    │                          │            │  │ 🟡 HIGH      │  │
│  │    │   Right lung collapse    │            │  │               │  │
│  │    │   with tracheal shift    │            │  │ pO2      58   │  │
│  │    │   (original: NIH CXR14)  │            │  │ 🔴 CRITICAL  │  │
│  │    │                          │            │  │               │  │
│  │    │   [Click to zoom]        │            │  │ pH       7.32 │  │
│  │    │                          │            │  │ 🟡 ACIDOSIS  │  │
│  │    └──────────────────────────┘            │  │               │  │
│  │                                          │  │ Lactate  3.2   │  │
│  │   [🔍 Zoom] [↔️ Pan] [📏 Measure]        │  │ 🟡 ELEVATED  │  │
│  │                                          │  │               │  │
│  │                                          │  │ Troponin 0.04  │  │
│  │                                          │  │ 🟢 NORMAL    │  │
│  │                                          │  │               │  │
│  │                                          │  │ [View 9 more →]│  │
│  └──────────────────────────────────────────┘  └──────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  👤 M, 34 y/o  |  Vitals: HR 118, BP 94/62, RR 28, SpO2 88% │  │
│  │  📝 Triage: "Sudden onset dyspnea after MVA. Chest pain      │  │
│       right side. No loss of consciousness."                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  ⚠️ Safety checks active: Pediatric ✓ | Image Quality ✓      │  │
│  │     | Lab Range ✓ | Bias Audit ✓  [Expand details →]         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│           ┌────────────────────────────────────┐                 │
│           │      🤖 RUN CLINSIGHT ANALYSIS       │                 │
│           │      AI: 5 agents + 7 subagents      │                 │
│           │      GPU: AMD MI300X | ROCm 7.0      │                 │
│           └────────────────────────────────────┘                 │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Key Changes from Original
| Original | Corrected | Why |
|----------|-----------|-----|
| 3-column layout (patient/X-ray/labs) | 2-column (X-ray 60%, labs 20%) | Judge's 13-inch laptop can't fit 3 columns |
| 3 separate warning banners | 1 expandable banner | Visual noise reduction |
| Patient info as vertical column | Patient info as horizontal bar | Saves vertical space |
| Labs as full column | Labs as collapsible drawer | X-ray gets visual priority |
| "Estimated time: ~5s" on button | Button shows architecture, not time estimate | Underestimating = credibility suicide |
| Upload buttons visible | Hidden by CSS | Judge WILL try to upload cat photos |

### Backend Health Check
Before the "Analyze" button is shown:
```javascript
// On component mount
const [backendReady, setBackendReady] = useState(false);

useEffect(() => {
  fetch('/api/health')
    .then(r => r.ok)
    .then(ok => setBackendReady(ok))
    .catch(() => setBackendReady(false));
}, []);

// If backend down:
// Show "DEMO MODE" banner + "Analyze" still works via contingency cache
```

---

## SCREEN 3: Inference Overlay

### Design

```
┌────────────────────────────────────────────────────────────────────┐
│  🏥 CLINSIGHT > Analyzing Case 001...                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│              ⏱️ Elapsed: 2.3s                                       │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Analyzing...                                                │   │
│  │                                                              │   │
│  │  ✅  🫁 Reading X-ray          [████████░░] 80%            │   │
│  │      Finding: Right lung collapse detected                  │   │
│  │                                                              │   │
│  │  ✅  🧪 Checking labs          [██████████] DONE         │   │
│  │      Alert: pO2 critically low (58)                       │   │
│  │                                                              │   │
│  │  🔄  🛡️ Verifying safety        [████░░░░░░] 40%        │   │
│  │      Checking: Lab-image consistency                        │   │
│  │      3 parallel subagents active...                          │   │
│  │                                                              │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  🔒 AMD MI300X GPU METRICS                                  │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │   │
│  │  GPU Utilization:     ████████████████████░░  89%          │   │
│  │  GPU Memory:          ██████████░░░░░░░░░░  85GB / 192GB   │   │
│  │  Temperature:           62°C (normal)                        │   │
│  │  Power Draw:           450W                                    │   │
│  │  ROCm Version:         7.0.0                                  │   │
│  │  Model:                Qwen3.5-35B-A3B (Apache 2.0)            │   │
│  │                                                              │   │
│  │  [View full rocm-smi output →]                              │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  💡 The Safety Agent is running 3 checks in parallel:              │
│     Contradiction Checker | Hallucination Guard | Bias Auditor    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions
| Decision | Rationale |
|----------|-----------|
| **3 visible steps, not 12** | Judge can't process 12 items in 3 seconds. 3 is digestible. |
| **Progress bars, not spinners** | Spinners = "something is broken." Progress bars = "work is happening." |
| **GPU panel = 20% of screen** | AMD judges need to screenshot this. Make it impossible to miss. |
| **No cancel button** | Judge might click it accidentally. The demo must complete. |
| **No "skip to results"** | Undermines the real-time demo. If inference fails, contingency mode auto-activates silently. |
| **Subagent names hidden by default** | "Contradiction Checker" is technical. "Checking lab-image consistency" is medical. Translate. |

### Contingency Mode (Silent Activation)

```javascript
// In the inference component
const [mode, setMode] = useState("LIVE"); // or "CONTINGENCY"

useEffect(() => {
  const timer = setTimeout(() => {
    if (!responseReceived) {
      setMode("CONTINGENCY");
      loadContingencyCache(caseId);
    }
  }, 8000); // 8 second timeout

  return () => clearTimeout(timer);
}, []);

// If contingency activates:
// Don't show error. Don't show "Loading..." forever.
// Instantly populate results with pre-cached output.
// Show subtle banner: "Showing pre-validated reference output."
```

---

## SCREEN 4: Results Dashboard

### Design

```
┌────────────────────────────────────────────────────────────────────┐
│  🏥 CLINSIGHT > Results: Case 001                      [< Back]   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                                                                ││
│  │    🔴  ESI 1 — IMMEDIATE                                       ││
│  │                                                                ││
│  │    Life-threatening. Immediate intervention required.        ││
│  │                                                                ││
│  │    Confidence: 55%  (DOWNGRADED due to safety checks)         ││
│  │    Original: 84% → Adjusted: 55% (contradiction detected)     ││
│  │                                                                ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────┐  ┌──────────────────┐ │
│  │  [X-RAY WITH ATTENTION REGIONS]      │  │  FINDINGS        │ │
│  │                                      │  │                  │ │
│  │  ┌───┐  Tension Pneumothorax        │  │  1. Tension      │ │
│  │  │ 🟡│  (55% confidence)            │  │     Pneumothorax │ │
│  │  └───┘  Click to see details         │  │     Confidence:  │ │
│  │                                      │  │     55% 🔴       │ │
│  │  ┌───┐  Right lower lobe opacity    │  │     Flag: CONTRA-│ │
│  │  │ 🔴│  (62% confidence)            │  │     DICTION_REVIEW│ │
│  │  └───┘                              │  │                  │ │
│  │                                      │  │  2. Right lower  │ │
│  │                                      │  │     lobe opacity │ │
│  │                                      │  │     Confidence:  │ │
│  │                                      │  │     62% 🟡       │ │
│  │                                      │  │     Flag: AI_SUG-│ │
│  │                                      │  │     GESTION      │ │
│  │                                      │  │                  │ │
│  │                                      │  │ [View raw AI     │ │
│  │                                      │  │  output →]       │ │
│  └──────────────────────────────────────┘  └──────────────────┘ │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  🛡️ SAFETY CHECKS: 1 issue found                               ││
│  │  ┌────────────────────────────────────────────────────────────┐││
│  │  │ CONTRADICTION: Image suggests "tension pneumothorax" but │││
│  │  │ patient vitals show BP 94/62, SpO2 88% — hemodynamically │││
│  │  │ stable. May be large simple pneumothorax, not tension.   │││
│  │  │ Confidence adjusted: 84% → 55%.                           │││
│  │  └────────────────────────────────────────────────────────────┘││
│  │  [Expand full safety report (3 checks) →]                    ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  🔍 TECHNICAL DETAILS  [Click to expand →]                     ││
│  │  Hardware: AMD MI300X | ROCm 7.0 | vLLM                     ││
│  │  Models: Qwen2.5-VL-7B (vision, 14GB) + Qwen3.5-35B (70GB)   ││
│  │  Latency: 4.4s | GPU: 89% | VRAM: 99GB/192GB                ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  DIFFERENTIAL DIAGNOSIS  [Click to expand →]                 ││
│  │  (Hidden by default — reduces cognitive load)                  ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  SUGGESTED ACTIONS  [Click to expand →]                      ││
│  │  (Hidden by default — reduces cognitive load)                  ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ════════════════════════════════════════════════════════════════│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  ⚠️ PHYSICIAN REVIEW REQUIRED — STICKY BAR                    ││
│  │                                                                ││
│  │  AI Suggests: ESI 1 — Immediate intervention                   ││
│  │                                                                ││
│  │  [✅ AGREE WITH AI]  [⚠️ OVERRIDE ESI]  [❌ DISMISS]            ││
│  │                                                                ││
│  │  If overriding: _______________________________               ││
│  │                                                                ││
│  │  By proceeding, I acknowledge:                                  ││
│  │  • This is AI decision support, not a diagnosis                 ││
│  │  • I have reviewed all findings and safety flags               ││
│  │  • Final clinical decision is my responsibility             ││
│  │                                                                ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ⚠️ This system is not FDA-cleared. Research prototype only.      │
│  ⚠️ Not validated for pediatric populations (age < 18).          │
│  ⚠️ AI models may exhibit performance disparities across groups.   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Technical Details Expanded Panel

When judge clicks "Technical Details":

```
┌────────────────────────────────────────────────────────────────────┐
│  🔍 TECHNICAL DETAILS                                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ HARDWARE & PLATFORM                                          │  │
│  │ GPU: AMD Instinct MI300X (192GB HBM3)                        │  │
│  │ Platform: ROCm 7.0 + PyTorch 2.6.0 (ROCm build)            │  │
│  │ Serving: vLLM 0.6.4 (ROCm backend, PagedAttention)        │  │
│  │ Model: Qwen/Qwen3.5-35B-A3B (Apache 2.0)                   │  │
│  │ Agents: LangGraph 0.2.x (5 parents + 7 subagents)         │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ REAL-TIME GPU METRICS                                        │  │
│  │ GPU Utilization:     ████████████████████░░  89%          │  │
│  │ GPU Memory Used:     ██████████░░░░░░░░░░  85GB / 192GB    │  │
│  │ GPU Temperature:       62°C (normal)                        │  │
│  │ Power Draw:           450W                                  │  │
│  │ ROCm Version:         7.0.0                                 │  │
│  │ Driver Version:       6.8.5                                 │  │
│  │                                                              │  │
│  │ [Refresh Metrics]  [View Full rocm-smi Output →]           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ PERFORMANCE BENCHMARKS (50 runs, this session)             │  │
│  │                                                              │  │
│  │ Latency Distribution:                                        │  │
│  │ ┌────────────────────────────────────────┐                   │  │
│  │ │ ▓▓▓▓▓▓▓▓▓▓▓▓                         │  0-3s: 8 runs    │  │
│  │ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                 │  3-4s: 22 runs   │  │
│  │ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓             │  4-5s: 15 runs   │  │
│  │ │ ▓▓▓▓▓▓▓▓                               │  5-6s: 4 runs    │  │
│  │ │ ▓▓                                      │  6s+:  1 run     │  │
│  │ └────────────────────────────────────────┘                   │  │
│  │                                                              │  │
│  │ Mean: 4.24s | P95: 4.81s | P99: 5.63s                       │  │
│  │ Cold Start: 92s | Throughput: 14.2 img/min (batch=1)        │  │
│  │ Throughput: 68.5 img/min (batch=8)                         │  │
│  │                                                              │  │
│  │ [Download Raw CSV →]  [Reproduce on Your Hardware →]         │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ INFERENCE BREAKDOWN (this analysis)                          │  │
│  │ Image Preprocessing:         0.18s                           │  │
│  │ vLLM Queue Wait:             0.05s                           │  │
│  │ Time to First Token (TTFT):  1.85s                           │  │
│  │ Token Generation:           2.12s (100 tokens @ 47 tok/s)  │  │
│  │ JSON Parsing:                0.04s                           │  │
│  │ Safety Agent (parallel):    0.12s (3 subagents + merge)    │  │
│  │ ESI Scoring + Report:       0.08s (deterministic rules)    │  │
│  │ ─────────────────────────────────────────────────────────   │  │
│  │ TOTAL:                       4.44s                           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ AMD ADVANTAGE                                                │  │
│  │ ┌──────────────────┐  ┌──────────────────┐                │  │
│  │ │ AMD MI300X       │  │ NVIDIA H100 80GB │                │  │
│  │ │ 192GB HBM3       │  │ 80GB HBM3        │                │  │
│  │ │ ───────────────  │  │ ───────────────  │                │  │
│  │ │ 35B @ FP16       │  │ 35B @ INT4       │                │  │
│  │ │ + 107GB headroom │  │ + 0GB headroom   │                │  │
│  │ │ Single GPU       │  │ 2 GPUs or quant  │                │  │
│  │ └──────────────────┘  └──────────────────┘                │  │
│  │ [View Memory Calculation →]                                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  [Collapse Technical Details ↑]                                      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Physician Veto Behavior

```typescript
// PhysicianVetoBar.tsx

const [action, setAction] = useState<"agree" | "override" | "dismiss" | null>(null);
const [overrideReason, setOverrideReason] = useState("");
const [submitted, setSubmitted] = useState(false);

const handleAgree = () => {
  setAction("agree");
  submitToAuditLog({ caseId, action: "AGREE", esi: results.esi, timestamp: now() });
  setSubmitted(true);
};

const handleOverride = () => {
  if (overrideReason.length < 10) {
    showError("Please provide a reason for override (minimum 10 characters).");
    return;
  }
  setAction("override");
  submitToAuditLog({ caseId, action: "OVERRIDE", reason: overrideReason, timestamp: now() });
  setSubmitted(true);
};

// After submission:
// Show confirmation: "Physician acknowledgment recorded."
// Enable "Generate Report" button
// Enable "What If?" button
```

---

## SCREEN 5: "What If?" Comparison

### Design

```
┌────────────────────────────────────────────────────────────────────┐
│  🏥 CLINSIGHT > "What If?" Comparison                   [< Back]    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Same patient. Same X-ray. Different clinical context.            │
│                                                                    │
│  Select scenario:                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐      │
│  │ 🔴 SCENARIO A  │  │ 🟡 SCENARIO B  │  │ 🔴 SCENARIO C  │      │
│  │ Current labs   │  │ Normal labs    │  │ Critical sepsis│      │
│  │ (ESI 1)        │  │ (ESI 3)        │  │ labs (ESI 1)   │      │
│  │ [ACTIVE]       │  │                │  │                │      │
│  └────────────────┘  └────────────────┘  └────────────────┘      │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  SCENARIO A: Post-MVA with abnormal labs                     ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ││
│  │                                                              ││
│  │  Labs:  WBC 9,500 (HIGH) | pO2 58 (CRITICAL) | Lactate 3.2  ││
│  │         pH 7.32 (ACIDOSIS) | Troponin 0.04 (NORMAL)          ││
│  │                                                              ││
│  │  ┌─────────────────────┐                                     ││
│  │  │  🔴 ESI 1           │                                     ││
│  │  │  IMMEDIATE          │                                     ││
│  │  │  Confidence: 55%    │  (downgraded: contradiction found)  ││
│  │  └─────────────────────┘                                     ││
│  │                                                              ││
│  │  Findings: 2 (1 downgraded) | Contradictions: 1             ││
│  │  Hallucinations: 0 | Bias Flags: 2 (age, sex)               ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  [Compare with Scenario B →]                                        │
│                                                                    │
│  💡 KEY INSIGHT:                                                   │
│     Changing pO2 from 58 → 88 (normal) alone would downgrade     │
│     ESI from 1 → 3. The model weighs oxygenation heavily in        │
│     pneumothorax assessment — this is true multimodal reasoning,   │
│     not just image classification.                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  WHY THIS MATTERS                                              ││
│  │  Most AI systems process image and text separately.            ││
│  │  ClinSight fuses them: the same X-ray means different things   │
│  │  depending on whether the patient is hypoxic or not.           ││
│  │  This requires 192GB HBM3 on MI300X — H100 80GB would need     ││
│  │  quantization to fit the 35B model with context.               ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Behavior

```typescript
// WhatIfComparison.tsx
// ALL scenarios are pre-cached. NO live inference during demo.

const SCENARIOS = {
  A: { labs: { wbc: 9500, pO2: 58, lactate: 3.2, ... }, esi: 1, confidence: 0.55 },
  B: { labs: { wbc: 7200, pO2: 88, lactate: 1.1, ... }, esi: 3, confidence: 0.72 },
  C: { labs: { wbc: 22000, pO2: 52, lactate: 4.5, ... }, esi: 1, confidence: 0.91 },
};

// When judge clicks scenario button:
// 1. Swap labs in display (instant, no API call)
// 2. Swap ESI badge (instant)
// 3. Swap confidence (instant)
// 4. Update "Key Insight" text (instant)

// NO vLLM call. NO inference. All pre-computed.
```

---

## Error States & Contingency UI

### Backend Down (Before Analysis)

```
┌────────────────────────────────────────────────────────────────────┐
│  🏥 CLINSIGHT > Case 001: Tension Pneumothorax                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  ⚠️ DEMO MODE — Reference Output                               ││
│  │                                                                ││
│  │  Live AI inference is temporarily unavailable.                 ││
│  │  Showing pre-validated clinical analysis for demonstration.    ││
│  │                                                                ││
│  │  This output was clinically reviewed by:                       ││
│  │  Dr. [Name], Emergency Medicine Resident, 2026-05-05          ││
│  │                                                                ││
│  │  [Continue with Reference Output →]                            ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  (Rest of case detail loads normally)                               │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Image Quality Gate Rejection

```
┌────────────────────────────────────────────────────────────────────┐
│  ⚠️ IMAGE REJECTED                                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  The uploaded image cannot be analyzed:                            │
│                                                                    │
│  Reason: NOT_CHEST_XRAY                                          │
│  Details: The image appears to be a hand X-ray / skull film /    │
│           non-medical image. ClinSight only analyzes chest X-rays. │
│                                                                    │
│  Suggested action: Please upload a frontal chest X-ray (PA or AP).│
│                                                                    │
│  [Return to Dashboard]  [Try Another Image]                        │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Pediatric Warning (Hard Block)

```
┌────────────────────────────────────────────────────────────────────┐
│  👶 PEDIATRIC PATIENT DETECTED                                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Patient age: 12 years old                                        │
│                                                                    │
│  ⚠️ CRITICAL SAFETY WARNING                                       │
│                                                                    │
│  This AI model was trained primarily on adult chest X-rays.         │
│  Pediatric radiographs have fundamentally different anatomy:        │
│  • Thymic silhouette (normal in children, pathologic in adults)  │
│  • Different cardiac size ratios                                  │
│  • Growth-related skeletal variations                              │
│                                                                    │
│  ⚠️ Do NOT use this output for clinical decisions on children    │
│     without pediatric specialist review.                            │
│                                                                    │
│  [I Understand — Show Analysis Anyway]                            │
│  [Return to Dashboard]                                             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Responsive Breakpoints

| Screen Size | Layout Adjustment | Judge Device |
|-------------|-------------------|--------------|
| **≥ 1440px** (desktop) | Full 2-column, labs visible | Judge's external monitor |
| **1200–1440px** (laptop) | 2-column, labs collapsible | **Most common: 13-inch MacBook** |
| **768–1200px** (tablet) | Stacked: X-ray on top, labs below | iPad |
| **< 768px** (phone) | Mobile view: single column, simplified | Judge probably won't use |

**Test on:** Chrome 120, Firefox 121, Safari 17. All at 1280×800 (13-inch laptop).

---

## UI State Machine (Final)

```typescript
type DemoUIState = 
  | "DASHBOARD"
  | "CASE_DETAIL" 
  | "INFERENCE"
  | "RESULTS"
  | "WHAT_IF";

const transitions: Record<DemoUIState, DemoUIState[]> = {
  DASHBOARD: ["CASE_DETAIL"],
  CASE_DETAIL: ["INFERENCE", "DASHBOARD"],
  INFERENCE: ["RESULTS"],  // No cancel, no error in happy path
  RESULTS: ["WHAT_IF", "DASHBOARD"],
  WHAT_IF: ["RESULTS", "DASHBOARD"]
};

// Rules:
// - DASHBOARD → CASE_DETAIL: click card
// - CASE_DETAIL → INFERENCE: click "Analyze"
// - INFERENCE → RESULTS: inference completes (or contingency loads)
// - RESULTS → WHAT_IF: click "What If?"
// - WHAT_IF → RESULTS: click "Back to Results"
// - Any screen → DASHBOARD: click "< Back" or logo
```

---

## Component Architecture (React)

```
src/
├── App.tsx                    # Router + state machine
├── Layout.tsx                 # Header + sticky footer disclaimer
│
├── screens/
│   ├── Dashboard.tsx          # Screen 1: 6 case cards
│   ├── CaseDetail.tsx         # Screen 2: X-ray + labs + analyze
│   ├── InferenceOverlay.tsx   # Screen 3: 3-step animation + GPU
│   ├── ResultsDashboard.tsx   # Screen 4: ESI + findings + veto
│   └── WhatIfComparison.tsx   # Screen 5: Scenario buttons
│
├── components/
│   ├── CaseCard.tsx           # Dashboard card component
│   ├── ImageViewer.tsx        # Canvas + zoom/pan + attention overlay
│   ├── LabDrawer.tsx          # Collapsible lab panel
│   ├── AgentProgress.tsx      # 3-step inference animation
│   ├── GpuMetricsPanel.tsx    # rocm-smi display
│   ├── EsiDisplay.tsx         # Large color-coded ESI badge
│   ├── FindingsList.tsx       # Findings with confidence + flags
│   ├── SafetyBanner.tsx       # Single collapsible safety alert
│   ├── PhysicianVeto.tsx      # Sticky agree/override/dismiss bar
│   ├── TechnicalDetails.tsx   # Expandable benchmark panel
│   ├── DifferentialExpand.tsx # Hidden-by-default differential
│   ├── ActionsExpand.tsx      # Hidden-by-default actions
│   ├── AuditPreview.tsx       # Short audit summary
│   └── ScenarioButton.tsx     # What If? scenario selector
│
├── hooks/
│   ├── useBackendHealth.ts    # Ping /health on mount
│   ├── useInference.ts        # Call API with timeout → contingency
│   ├── useGpuMetrics.ts      # Poll /metrics endpoint
│   └── useContingency.ts     # Load pre-cached fallback
│
└── utils/
    ├── constants.ts           # ESI colors, thresholds
    └── formatters.ts        # Number formatting, time formatting
```

---

## The 6-Click Demo Path (Memorize This)

| Step | Action | Time | You Say |
|------|--------|------|---------|
| 1 | Open URL → Dashboard loads | 0s | "Welcome to ClinSight — 6 patients, 2 critical. This is a decision support demo; in production it integrates into PACS/EHR, not standalone triage." |
| 2 | Click Case 001 | 1s | "Case 001 — 34-year-old male, post-MVA, chest pain. X-ray + labs are back — this is where ClinSight adds value, after workup." |
| 3 | Click "Analyze" | 2s | "Watch — 5 agents, 7 subagents, running on MI300X. This is diagnostic synthesis, not triage replacement." |
| 4 | Inference completes | 5s | "ESI 1 — but notice confidence was downgraded. Safety caught a contradiction. Image says tension pneumo, but vitals are stable." |
| 5 | Click "What If?" | 1s | "Same patient. Same X-ray. What if labs were normal? This proves multimodal reasoning — not just image classification." |
| 6 | Click "Scenario B" | 1s | "ESI 3. The model uses labs to inform image reading — true multimodal reasoning. In production, this differential goes into the EHR." |

**Total: ~10 seconds of clicking + 5 seconds of waiting = fits in 3-minute demo.**

---

*UI Flow Specification — Final Judge-Corrected Version*
*Optimized for: 13-inch laptop, tired judges, 6-click happy path, zero friction*

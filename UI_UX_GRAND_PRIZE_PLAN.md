# ClinSight — Grand Prize MVP UI/UX Strategy
### Author: UI/UX Expert Analysis · Date: 2026-05-06

---

## What I Got Wrong in v1

| v1 Mistake | What Judges Actually Want |
|---|---|
| Designed a "workspace" | Should be a **cinematic story** — judge sees the AI think |
| Tabs hide the multi-agent magic | Judge clicks 1 tab, never sees the rest. Wrong. |
| Pipeline as decoration | Pipeline IS the product — must be **live-streaming** |
| 4 safety subagents not showcased | This is your **only** moat vs other AI demos. Front-and-center. |
| No narrative — just panels | Need before/after, "what would a doctor miss" |
| No AMD sponsor surface | $97 in MI300X credit ≠ free — show the iron |
| Static loading bar | Loading state IS the demo moment |
| No "why?" — just outputs | Trust = visible reasoning chains |
| Empty state = sad message | Empty state = hero architecture moment |

---

## The Grand Prize Mental Model

**A hackathon judge spends 90–180 seconds with you.** They:
1. **First 5s** — Decide if this looks "real" (production-grade vs hack)
2. **Next 30s** — Want a clear problem/solution narrative
3. **Next 60s** — Look for the "AI doing something only AI can do"
4. **Last 30s** — Memorize 1–2 phrases to argue for you in deliberation

**Your three winning phrases must be:**
1. *"12 reasoning agents catch what a single model misses"*
2. *"Every recommendation passes through hallucination, bias, and contradiction guards"*
3. *"129ms on AMD MI300X — 14× faster than the 30-minute ED standard"*

The UI exists to make those three phrases obvious without you saying them.

---

## Architecture Decision: Kill the Tabs, Build the Cinematic Scroll

```
┌────────────────────────────────────────────────────────────────┐
│ HEADER  Logo · "Powered by AMD MI300X 192GB" · GitHub · About │
├────────┬───────────────────────────────────────────────────────┤
│        │ ▮ HERO BAND ───────────────────────────────────────── │
│SIDEBAR │   ESI ① · 87% confidence · 129ms                      │
│        │   [Agree] [Override] [Dismiss]                        │
│Cases   │                                                       │
│ ●●●●●● │ ▮ LIVE PIPELINE ─── (the wow moment) ──────────────── │
│        │   5 agent cards animating in sequence,                │
│Patient │   outputs streaming in real-time                      │
│Snapshot│                                                       │
│        │ ▮ EVIDENCE ─── 3 column ───────────────────────────── │
│Vitals  │   X-Ray w/ attention   Findings + why  Lab evidence  │
│Demo    │                                                       │
│Sequence│ ▮ SAFETY THEATER ─── 4 metric badges ──────────────── │
│Button  │   ✓ 0 contradictions  ✓ 0 hallucinations              │
│        │   ✓ 0 bias flags      ✓ Quality gate passed           │
│        │                                                       │
│        │ ▮ CLINICAL REPORT ─────────────────────────────────── │
│        │   Differential w/ evidence | Actions | Print/Export   │
│        │                                                       │
│        │ ▮ COUNTERFACTUAL ─── What-If simulator ────────────── │
│        │   Current | Worse | Better — side-by-side ESI deltas │
│        │                                                       │
│        │ ▮ IMPACT ─── before vs after ──────────────────────── │
│        │   "Without ClinSight: ~30 min · 1 reviewer"           │
│        │   "With ClinSight: 129ms · 12 agents · audited"      │
│        │                                                       │
├────────┴───────────────────────────────────────────────────────┤
│  ▼ AUDIT TRAIL  (collapsed, expand for compliance demo)       │
└────────────────────────────────────────────────────────────────┘
```

Single scroll. Judge sees every feature without clicking. Every section is a screenshot for the pitch deck.

---

## Design System

### Color Palette

```
Background:      #030d1a   ← True clinical dark, nearly black-blue
Surface:         #071428   ← Subtle navy for panels
Card:            #0c1e38   ← Cards with depth
Card hover:      #112448   ← Gentle lift

Accent (AI):     #00c8e8   ← Electric cyan — AI presence
Clinical teal:   #14b8a6   ← Healthcare trust color
Muted:           #4a6a85   ← Secondary text

Critical/ESI-1:  #ef4444
Danger/ESI-2:    #f97316
Warning/ESI-3:   #f59e0b
Stable/ESI-4:    #22c55e
Routine/ESI-5:   #14b8a6

Border subtle:   rgba(255,255,255,0.05)
Border active:   rgba(0,200,232,0.35)
Glass bg:        rgba(255,255,255,0.03)
```

### Typography

```
Font:  Inter (via @fontsource/inter — self-hosted, no CDN)
Mono:  JetBrains Mono (IDs, vitals, values, timestamps)

Scale:
  --text-xs:   11px / 0.08em tracking / uppercase labels
  --text-sm:   13px / body copy
  --text-base: 15px / default
  --text-lg:   18px / card headings
  --text-xl:   24px / section headings
  --text-hero: 80px / ESI number

Weight:
  300 → dim/secondary
  400 → body
  500 → labels, panel headers
  700 → headings, values
  900 → ESI hero number
```

### Spacing & Shape

```
Radius:   6px cards / 4px badges / 12px major panels / 999px pills
Shadows:  0 1px 3px rgba(0,0,0,0.5) card
          0 0 0 1px var(--border-active) focus ring
          0 0 24px rgba(239,68,68,0.3) ESI-1 glow
Grid:     8px base unit
```

### Confidence Color Gradient

```
< 60%  → red    (#ef4444)
60–80% → amber  (#f59e0b)
> 80%  → teal   (#14b8a6)
```

### Severity Glow Rings (ESI badges)

```
ESI 1 → red glow, 2s pulse animation (urgent)
ESI 2 → orange glow, 3s pulse
ESI 3 → amber steady
ESI 4 → green steady
ESI 5 → teal steady
```

---

## Icons (Lucide React — tree-shakeable, zero runtime cost)

| Component | Icon |
|---|---|
| Coordinator agent | `ShieldCheck` |
| Radiologist agent | `ScanLine` |
| Lab Analyst agent | `FlaskConical` |
| Safety agent | `AlertTriangle` |
| Documenter agent | `FileText` |
| ESI 1 | `Zap` (red) |
| ESI 2 | `AlertOctagon` (orange) |
| ESI 3 | `Clock` (amber) |
| ESI 4 | `TrendingUp` (green) |
| ESI 5 | `Activity` (teal) |
| Lab alert | `TestTube` |
| Finding | `Eye` |
| Quality gate pass | `CheckCircle2` |
| Quality gate fail | `XCircle` |
| Pediatric warning | `Baby` |
| Pipeline | `GitBranch` |
| Report | `FileText` |
| What-If | `Sliders` |
| Audit | `History` |
| Physician Agree | `ThumbsUp` |
| Physician Override | `Pencil` |
| Physician Dismiss | `X` |
| AMD / Hardware | `Cpu` |
| Export PDF | `Download` |
| About | `Info` |

---

## The 7 Critical Additions

### 1. Live-Streaming Pipeline (BACKEND + FRONTEND)

**The single biggest demo upgrade.** Right now the endpoint returns the final result. Judge sees a spinner, then everything appears. Boring.

**Change:** Add `/demo/analyze/{case_id}/stream` — Server-Sent Events that emit each agent's output as it finishes:

```
event: agent_start    data: {"agent": "coordinator"}
event: agent_complete data: {"agent": "coordinator", "duration_ms": 12, "output": {...}}
event: agent_start    data: {"agent": "radiologist"}
event: agent_complete data: {"agent": "radiologist", "duration_ms": 45, "output": {...}}
...
event: pipeline_done  data: {"total_ms": 129, "esi": 1}
```

Frontend: pipeline cards illuminate one-by-one, outputs cascade in. **The judge watches the AI think.**

### 2. Reasoning Traces ("Why?" expanders)

Every output needs a "why" reveal:
- **Finding:** click → shows the VLM's evidence regions + confidence breakdown
- **ESI score:** click → shows which clinical rules triggered (`HYPOTENSION`, `TROPONIN_ELEVATED`)
- **Differential:** click → evidence weights for each diagnosis
- **Lab alert:** click → threshold reference + clinical pattern match

This is what separates "AI wrapper" from "trustworthy clinical AI."

### 3. Safety Theater Dashboard

The 4 safety subagents are your **single biggest moat**. Other hackathon projects have zero of this. Make it loud:

```
┌────────────────────────────────────────────────────┐
│  AI SAFETY GUARDS                                  │
├──────────────┬──────────────┬──────────────┬───────┤
│ ✓ 0          │ ✓ 0          │ ✓ 0          │ ✓PASS │
│ Contradict.  │ Hallucinat.  │ Bias flags   │Q.Gate │
│ Findings vs  │ vs reference │ Race/sex     │Image  │
│ labs vs hist │ pathology    │ patterns     │valid  │
└──────────────┴──────────────┴──────────────┴───────┘
```

When you induce a failure case, this lights up red. Demo gold.

### 4. Aggregated System Confidence

A single number combining all 12 nodes' confidences:

```
SYSTEM CONFIDENCE  ━━━━━━━━━━━━━━━━━━━━━━━━ 87%
                   findings · labs · safety · consensus
```

Compute client-side as weighted average of finding confidences minus safety penalties.

### 5. AMD Sponsor Surface

A proud strip in the header:

```
⚡ Powered by AMD MI300X · 192GB VRAM · Qwen2.5-VL-7B + Qwen3.5-35B-A3B · 99GB loaded
```

Click → modal with VRAM utilization, throughput stats from `benchmarks/`, AMD setup docs link.
**This wins sponsor-prize tracks** even if you miss grand prize.

### 6. Impact / Before-After Section

Below the report:

```
┌─────────────────────┬─────────────────────┐
│  STATUS QUO         │  WITH CLINSIGHT     │
│  ────────           │  ─────────          │
│  ⏱ ~30 min          │  ⏱ 129 ms           │
│  👁 1 reviewer      │  👁 12 agents       │
│  📋 No audit trail  │  📋 Cryptographic   │
│  ⚠ Bias unflagged   │  ✓ Bias audited    │
│  ⚠ No 2nd opinion   │  ✓ 4 safety guards │
└─────────────────────┴─────────────────────┘
```

This is the slide judges steal for their own pitch decks.

### 7. Demo Sequence Mode (auto-play)

**`▶ Run Grand Demo`** button in the sidebar:
- Plays through 3 hand-picked cases in sequence (10s each)
- CS-2024-001 → ESI 1, all safety green
- CS-2024-003 → pediatric gate triggers
- (synthetic case) → safety guard catches induced hallucination
- Subtle text overlays narrate each moment

If you can't be there to demo, this runs solo at the booth or in the recording.

---

## Component Redesigns (Detailed)

### A. Hero Band (`HeroBand.tsx` — NEW)

```
┌──────────────────────────────────────────────────────────────┐
│  CS-2024-001 · 67yo M · Chest Pain                           │
│                                                              │
│   ╭───╮                                                      │
│   │ ① │  RESUSCITATION                                       │
│   ╰───╯  Immediate life-saving intervention required         │
│                                                              │
│  Confidence ━━━━━━━━━━━━━━━━━━━━ 87%   ⏱ 129ms             │
│                                                              │
│  [✓ Agree (A)]  [⚡ Override (O)]  [✕ Dismiss (D)]          │
└──────────────────────────────────────────────────────────────┘
```

- ESI number is **80px**, glowing ring matching severity
- Confidence is a real computed bar
- Buttons show keyboard shortcuts in brackets
- After veto action: replaces buttons with `Physician: Agreed · 14:23:01` chip

### B. Live Pipeline (`LivePipeline.tsx` — replaces AgentActivity)

5 agent cards in a horizontal flow with animated connectors:
- **Pending state:** dim card, empty nodes
- **Running state:** pulsing cyan dot + indeterminate progress bar
- **Complete state:** checkmark + duration + collapsed output summary
- Click to expand: full subagent breakdown (Coordinator → Image Quality Gate + Pediatric Gate, etc.)
- During load: traveling-dot animation along connector lines

```
[Coord ✓ 12ms] ──●──▶ [Rad ✓ 45ms] ──●──▶ [Lab ✓ 23ms] ──●──▶ [Safety ✓ 31ms] ──●──▶ [Doc ✓ 18ms]
  ↓ expand                                                          ↓ expand
  · img quality gate                                                · 0 contradictions
  · pediatric gate                                                  · 0 hallucinations
                                                                    · 0 bias flags
```

**This is the most important component in the product.**

### C. Evidence Row (`EvidenceRow.tsx` — replaces Analysis tab)

Three equal columns:

**Column 1 — X-Ray Viewer:**
- Large canvas, fills height
- Modality chip: `CXR PA · DEMO`
- Attention regions: amber dashed rect, hover highlights
- Findings count pill at bottom

**Column 2 — Findings:**
- Cards with severity-colored left border
- Confidence bar (visual gradient, not just %)
- "Why?" collapse button → evidence regions + rule triggers
- `critical` border = red, `high` = orange, `moderate` = amber, `low` = teal

**Column 3 — Lab Evidence:**
Visual value-vs-range bars:
```
WBC  ════╸●══════  16.5 K/µL  [CRITICAL]
         ↑ threshold 11.0

Pattern chips: SEPSIS_PATTERN · INFLAMMATORY
```

### D. Safety Theater (`SafetyTheater.tsx` — NEW, replaces SafetyPanel)

4 metric hero cards in a 2×2 grid. Metrics, not lists. Lists go inside expanders.
Red state is a demo moment — induce it with a bad-labs scenario.

### E. Clinical Report (`ClinicalReport.tsx` — replaces ReportViewer)

Two-column layout:
- **Left:** Differential diagnosis numbered list, each entry with evidence weight bar
- **Right:** Suggested actions with category icons (🩺 Meds, 💉 IV, 📊 Labs, etc.)

Buttons:
- **`📄 Export PDF`** — triggers `window.print()` with a print CSS stylesheet
- **`📤 Send to EHR`** — opens a modal mockup (signals integration intent to judges)

### F. What-If Simulator (`WhatIfSimulator.tsx` — replaces WhatIfComparison, fix broken CSS)

Three scenario cards side-by-side. Each card:
- Scenario name + ESI badge
- Adjusted lab/vital deltas with `↑↓` color arrows
- `[Run Scenario]` button → re-fetches via API with override params (real call)
- Active/selected: glowing cyan border + `ACTIVE` chip

Fix needed: `.scenario-tabs`, `.scenario-card`, `.scenario-grid` CSS is missing today.

### G. Impact Block (`ImpactBlock.tsx` — NEW)

Static comparison card. No interactivity. Pure narrative. Lives just above audit drawer.

### H. Sidebar (refactored `Dashboard.tsx`)

```
┌─────────────────────────────┐
│  ⚕ ClinSight         ~~~~~  │  ← logo + EKG pulse SVG animation
│  12 agents · 99GB · MI300X  │  ← quick stats
├─────────────────────────────┤
│  CASES                      │
│  ┃ CS-2024-001              │  ← ESI-colored left border
│  ┃ ① 67yo M · Chest Pain   │
│  ┃ BP 145 · HR 110 · 94%   │
│                             │
│  ┃ CS-2024-002              │
│  ┃ ③ 34yo F · Head Trauma  │
│  ...                        │
├─────────────────────────────┤
│  PATIENT   (after select)   │
│  67yo · Male · Hispanic     │
│  Chief: Chest pain + SOB    │
│                             │
│  BP  145/95   HR  110 ●     │  ← ● = abnormal dot
│  RR  22 ●     SpO₂ 94% ●   │
│  Temp 37.1                  │
├─────────────────────────────┤
│  ▶ Run Grand Demo           │  ← auto-play button
├─────────────────────────────┤
│  About · GitHub · Pitch     │  ← footer links
└─────────────────────────────┘
```

### I. Audit Drawer (refactored `AuditLog.tsx`)

Collapsed by default — thin strip at very bottom:
```
▲  Audit Trail  ·  7 entries  ·  129ms total
```
Click → slide-up drawer with immutable table. Physician actions appended in real-time.

### J. About / Architecture Modal (`AboutModal.tsx` — NEW)

Accessed from header `Info` button:
- Full 5-agent → 7-subagent → 12-node architecture diagram (SVG)
- Model stack table
- AMD MI300X hardware specs
- Benchmark stats (from `benchmarks/` directory)
- Links: GitHub, Pitch Deck (`docs/pitch_deck.html`), AMD Setup docs

### K. Safety Disclaimer (refactored `SafetyBanner.tsx`)

**Not a red bar anymore.** A collapsed amber chip in sidebar footer:
```
⚠ Research Use Only — Not for clinical deployment  [▼]
```
Expands inline. Reduces visual noise while keeping regulatory compliance.

### L. Keyboard Shortcuts Layer (NEW — global)

| Key | Action |
|---|---|
| `1` – `6` | Load demo case 1–6 |
| `A` | Physician Agree |
| `O` | Physician Override |
| `D` | Physician Dismiss |
| `R` | Rerun current case |
| `←` / `→` | Cycle through cases |
| `Esc` | Close modal |
| `?` | Show keyboard shortcut help modal |

Press `?` shows a clean clinical-style help overlay. Judges who discover this think "production product."

---

## Backend Changes Required

| Change | File | Effort |
|---|---|---|
| Streaming pipeline via SSE | `backend/api/demo.py` | ~60 LOC |
| Override params on analyze endpoint | `backend/api/demo.py` | ~20 LOC |
| Reasoning trace fields in agent outputs | `backend/agents/subgraphs.py` | ~30 LOC |
| `system_confidence` aggregate in state | `backend/agents/clinical_documenter.py` | ~10 LOC |
| `/api/architecture` endpoint | new file | ~20 LOC |

**Total: ~140 LOC of backend work. Non-negotiable.**

---

## New Package Dependencies

```json
{
  "lucide-react": "^0.460.0",
  "@fontsource/inter": "^5.1.0",
  "@fontsource/jetbrains-mono": "^5.1.0"
}
```

No other new dependencies. Keep the bundle lean.

---

## Implementation Order

### Day 1 — Foundation
- [ ] `npm install lucide-react @fontsource/inter @fontsource/jetbrains-mono`
- [ ] Full `index.css` rewrite — new design system, CSS custom properties
- [ ] New `App.tsx` layout — sidebar + scroll main + audit drawer
- [ ] Global keyboard shortcuts (`useKeyboard.ts` hook)

### Day 2 — Hero Components (Wow Moments)
- [ ] `HeroBand.tsx` — ESI hero + confidence + physician actions
- [ ] `LivePipeline.tsx` — animated 5-agent flow (static first)
- [ ] Backend: SSE streaming endpoint
- [ ] Wire `LivePipeline` to consume SSE stream (real animation)

### Day 3 — Evidence + Safety
- [ ] `EvidenceRow.tsx` — 3-column X-Ray + Findings + Labs
- [ ] Add confidence bars to findings
- [ ] Add "Why?" expander stubs
- [ ] `SafetyTheater.tsx` — 4-metric dashboard
- [ ] Reasoning trace fields from backend

### Day 4 — Story Layer
- [ ] `ClinicalReport.tsx` — differential + actions + export
- [ ] Print CSS stylesheet for PDF export
- [ ] `WhatIfSimulator.tsx` — fix CSS, add real API call with overrides
- [ ] `ImpactBlock.tsx` — before/after static block
- [ ] `AboutModal.tsx` — architecture + hardware + links

### Day 5 — Polish + Demo Prep
- [ ] Demo Sequence auto-play feature
- [ ] AMD sponsor header strip with stats
- [ ] Empty-state hero architecture animation
- [ ] Keyboard shortcut help modal (`?` key)
- [ ] Sidebar EKG pulse animation
- [ ] Mobile/tablet responsive (tablet: 1024px, phone: 480px)
- [ ] Lighthouse audit → fix issues
- [ ] Zero console errors
- [ ] End-to-end demo rehearsal

---

## Files to Create / Modify

### New Files (Frontend)
- `src/components/HeroBand.tsx`
- `src/components/LivePipeline.tsx`
- `src/components/EvidenceRow.tsx`
- `src/components/SafetyTheater.tsx`
- `src/components/ClinicalReport.tsx`
- `src/components/WhatIfSimulator.tsx`
- `src/components/ImpactBlock.tsx`
- `src/components/AboutModal.tsx`
- `src/components/AuditDrawer.tsx`
- `src/hooks/useKeyboard.ts`
- `src/hooks/usePipelineStream.ts`

### Modified Files (Frontend)
- `src/App.tsx` — new layout, tab removal, scroll layout
- `src/index.css` — complete rewrite
- `src/components/Dashboard.tsx` → becomes sidebar case queue
- `src/components/AgentActivity.tsx` → replaced by `LivePipeline.tsx`
- `src/components/SafetyPanel.tsx` → replaced by `SafetyTheater.tsx`
- `src/components/ReportViewer.tsx` → replaced by `ClinicalReport.tsx`
- `src/components/WhatIfComparison.tsx` → replaced by `WhatIfSimulator.tsx`
- `src/components/AuditLog.tsx` → replaced by `AuditDrawer.tsx`
- `src/components/SafetyBanner.tsx` → becomes amber chip in sidebar
- `src/components/PhysicianVeto.tsx` → merged into `HeroBand.tsx`
- `src/types.ts` — add `system_confidence`, `reasoning_traces` fields

### Modified Files (Backend)
- `backend/api/demo.py` — SSE streaming endpoint + override params
- `backend/agents/subgraphs.py` — reasoning trace fields
- `backend/agents/clinical_documenter.py` — system_confidence aggregate
- `backend/core/state.py` — new state fields

---

## What Each Component Earns You With Judges

| Component | Judge takeaway |
|---|---|
| Hero Band | "This looks like a real product" |
| Live Pipeline (streaming) | "Holy shit, it's actually a multi-agent system doing work" |
| Evidence Row + Why? | "I can trust what this AI is saying" |
| Safety Theater | "Nobody else has this — 4 safety guards is a moat" |
| What-If + real API | "This is a clinical reasoning tool, not a screenshot" |
| Impact Block | "I can pitch this in one slide" |
| About Modal | "Real architecture, real models, real hardware" |
| AMD header strip | "They're using our hardware intentionally" (sponsor judges) |
| Demo Sequence | "Plays without them — they trust us" |
| Keyboard Shortcuts | "Built by people who've used real clinical software" |

---

## Cuts from Previous Plan

- **Tabs** — killed. Cinematic scroll instead.
- **Audit log as primary UI** — stays collapsed. Compliance demo, not feature.
- **Hex grid background** — de-prioritized. Subtle glass cards instead.

---

## Final Checklist Before Demo

- [ ] All 6 demo cases work offline (contingency cache)
- [ ] Pipeline streams in real-time (not just final result)
- [ ] ESI 1 glows red with pulse animation
- [ ] Safety theater shows green zeros (or red when failure induced)
- [ ] "Why?" expanders work on at least findings and ESI
- [ ] What-If runs real API calls with overrides
- [ ] PDF export opens print dialog cleanly
- [ ] About modal shows architecture + AMD hardware
- [ ] Demo Sequence auto-plays 3 cases
- [ ] Keyboard shortcuts work (especially `1`–`6`, `A`, `?`)
- [ ] Mobile view works at 768px (tablet)
- [ ] Zero console errors
- [ ] Lighthouse performance > 85
- [ ] `npm run build` succeeds, served from `:8000`

---

## Three Phrases Judges Will Remember

1. **"12 reasoning agents catch what a single model misses"**
2. **"Every recommendation passes through hallucination, bias, and contradiction guards"**
3. **"129ms on AMD MI300X — 14× faster than the 30-minute ED standard"**

Make these visible in the UI without the presenter saying them.

---

*This document is the source of truth for the ClinSight frontend redesign.*
*Backend changes are scoped to ~140 LOC — all other logic untouched.*

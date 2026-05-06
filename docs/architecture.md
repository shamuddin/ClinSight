# ClinSight Architecture

## Overview

**ClinSight** is a multi-agent clinical decision support system for chest X-ray analysis. It combines vision-language models (VLMs) with rules-based safety layers and structured clinical documentation.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              ClinSight Pipeline                            │
│                                                                          │
│  INPUT: Chest X-ray + Labs + Triage Note + Demographics                  │
│       │                                                                  │
│       ▼                                                                  │
│  ┌──────────────┐                                                        │
│  │ Coordinator│  Quality gate + Pediatric gate + Input validation       │
│  └──────┬───────┘  [REJECT if image quality fails]                       │
│         │                                                                │
│       pass                                                               │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ Analysis Node (Sequential)                                     │       │
│  │                                                                │       │
│  │  ┌──────────────┐    ┌────────────────────┐                     │       │
│  │  │ Radiologist  │───▶│ Lab Analyst        │                     │       │
│  │  │              │    │                    │                     │       │
│  │  │ Image Prep   │    │ Critical Value     │                     │       │
│  │  │ Pathology    │    │ Pattern Correlator │                     │       │
│  │  │ Analyzer     │    │                    │                     │       │
│  │  │ (VLM vision) │    │ (deterministic)    │                     │       │
│  │  └──────────────┘    └────────────────────┘                     │       │
│  └────────────────────────────┬───────────────────────────────────┘       │
│                               │                                          │
│                               ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ Safety Agent                                                  │       │
│  │                                                                │       │
│  │  ┌──────────────────┐                                        │       │
│  │  │ Contradiction    │                                        │       │
│  │  │ Checker          │                                        │       │
│  │  └──────────────────┘                                        │       │
│  │  ┌──────────────────┐                                        │       │
│  │  │ Hallucination    │                                        │       │
│  │  │ Guard            │                                        │       │
│  │  └──────────────────┘                                        │       │
│  │  ┌──────────────────┐                                        │       │
│  │  │ Bias Auditor     │                                        │       │
│  │  └──────────────────┘                                        │       │
│  │  ┌──────────────────┐                                        │       │
│  │  │ Safety Merge     │  Apply confidence penalties            │       │
│  │  └──────────────────┘                                        │       │
│  └────────────────────────────┬───────────────────────────────────┘       │
│                               │                                          │
│                               ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ Clinical Documenter                                           │       │
│  │                                                                │       │
│  │  ┌──────────────┐    ┌────────────────────┐                     │       │
│  │  │ ESI Scorer   │    │ Differential       │                     │       │
│  │  │ (deterministic)    │ Builder            │                     │       │
│  │  └──────────────┘    └────────────────────┘                     │       │
│  │                    Actions + Report (LLM fallback)             │       │
│  └────────────────────────────┬───────────────────────────────────┘       │
│                               │                                          │
│                               ▼                                          │
│  OUTPUT: Structured report with ESI, differential, actions, safety flags │
└──────────────────────────────────────────────────────────────────────────┘
```

## Agent Hierarchy

| Layer | Count | Name | Logic |
|-------|-------|------|-------|
| Parent | 5 | Coordinator, Radiologist, Lab Analyst, Safety, Documenter | Orchstrator: calls subagents |
| Subagent | 7+ | Image Quality Gate, Pediatric Gate, Image Prep, Pathology Analyzer, Critical Value Detector, Pattern Correlator, Contradiction Checker, Hallucination Guard, Bias Auditor, Safety Merge, ESI Scorer, Differential Builder | **Actual business logic** |

## State Machine

`AgentState` (TypedDict) carries data through the graph:
- **INPUTS**: `case_id`, `image_path`, `lab_values`, `lab_units`, `triage_note`, vitals
- **COORDINATOR**: `quality_gate`, `pediatric_gate`, `input_warnings`
- **RADIOLOGIST**: `findings`, `attention_regions`, `image_features`
- **LAB ANALYST**: `lab_alerts`, `lab_patterns`, `lab_correlation`
- **SAFETY**: `contradictions`, `hallucination_flags`, `bias_flags`, `merged_flags`, `safety_downgrades`
- **DOCUMENTER**: `esi_level`, `esi_description`, `differential`, `suggested_actions`, `report`
- **AUDIT**: `audit_log`, `total_time_ms`

## Dual Model Stack

| Model | Role | Port | VRAM | Provider |
|-------|------|------|------|----------|
| Qwen2.5-VL-7B-Instruct | Vision: chest X-ray analysis | 8000 | ~14 GB | vLLM (ROCm) |
| Qwen3.5-35B-A3B | Text: ESI + diagnosis + actions | 8001 | ~70 GB | vLLM (ROCm) |

**Total footprint**: ~84 GB on MI300X (192 GB VRAM) → 108 GB headroom.

## Fallback Chain (Resilience)

```
Real vLLM API
    ↓ Exception / timeout / unreachable
Mock Client (pre-cached outputs for 6 demo cases)
    ↓ case not in cache / file missing
ContingencyFallback (emergency safe output, ESI 3)
```

## Safety Architecture

1. **14 Lab thresholds** — deterministic (e.g., pO2 < 60 = HYPOXEMIA CRITICAL)
2. **5 Contradiction rules** — image-vs-lab mismatch (e.g., pneumonia without leukocytosis)
3. **Hallucination guard** — out-of-scope anatomy detection, missing visual grounding
4. **Bias auditor** — demographic-dependent confidence shifts (cardiomegaly audits)
5. **Safety merge** — multiplicative confidence penalties, downgrade counts
6. **Physician veto** — Agree / Override / Dismiss in UI
7. **Contingency mode** — system runs without GPU, returns safe defaults

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + Uvicorn |
| Agent Graph | LangGraph `StateGraph` |
| Models | vLLM + OpenAI-compatible API |
| Image | OpenCV + Pillow |
| Frontend | React + Vite + TypeScript |
| GPU | AMD MI300X, ROCm 6.x, HBM3 |
| Container | DigitalOcean GPU Droplet + Docker |

## Data Flow

1. Upload case JSON or select demo case
2. Coordinator validates image + warns on pediatrics
3. (Async) Radiologist calls vision VLM → findings + attention regions
4. (Async) Lab Analyst checks 14 emergency thresholds + cross-references into patterns
5. Safety runs contradiction + hallucination + bias checks in sequence
6. Documenter scores ESI (deterministic), builds differential (rules), generates actions (LLM fallback)
7. Frontend renders full report with audit trail, safety panels, physician veto

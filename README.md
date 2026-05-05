# ClinSight

Multi-agent clinical decision support system with vision-language models for chest X-ray analysis.

## Architecture

**5 Parent Agents → 7 Subagents → 12 Total Reasoning Nodes**

| Agent | Role | Subagents |
|---|---|---|
| **Coordinator** | Input validation, quality gates, pediatric safety | Image Quality Gate, Pediatric Gate |
| **Radiologist** | Image analysis, pathology detection, attention regions | Image Prep, Pathology Analyzer |
| **Lab Analyst** | Critical value detection, pattern correlation | Critical Value Detector, Pattern Correlator |
| **Safety** | Contradiction checking, hallucination guard, bias audit | Contradiction Checker, Hallucination Guard, Bias Auditor, Safety Merge |
| **Clinical Documenter** | ESI scoring, differential diagnosis, report generation | ESI Scorer, Differential Builder |

Graph: Coordinator → [pass] → Radiologist → Lab Analyst → Safety → Documenter → END

## Dual Model Stack

| Model | Role | VRAM |
|---|---|---|
| Qwen2.5-VL-7B-Instruct | Vision (chest X-ray) | ~14 GB |
| Qwen3.5-35B-A3B | Text reasoning (MoE) | ~70 GB |
| **Total** | | **~99 GB** |

Target platform: AMD MI300X (192 GB VRAM) — 93 GB headroom for concurrent requests.

## Quick Start (Full Stack)

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=.. uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend (dev mode)

```bash
cd frontend/react-app
npm install
npm run dev
# Open http://localhost:5173
```

### 3. Build for single-port deployment

```bash
cd frontend/react-app
npm run build

# Restart backend — it now serves the React app at /
PYTHONPATH=.. uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
# Open http://localhost:8000
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/analyze` | POST | Analyze a case with full JSON body |
| `/demo/cases` | GET | List 6 pre-built demo cases |
| `/demo/analyze/{case_id}` | GET | Run full pipeline on a demo case |

## Demo Cases

| ID | Scenario | ESI |
|---|---|---|
| CS-2024-001 | Chest pain + elevated troponin | 1 |
| CS-2024-002 | Head trauma (MVC) | 3 |
| CS-2024-003 | Pediatric fever + rash | 1 |
| CS-2024-004 | Sepsis + altered mental status | 1 |
| CS-2024-005 | Severe headache | 3 |
| CS-2024-006 | Peritoneal signs + elevated WBC | 1 |

## Run Tests

```bash
PYTHONPATH=. python -m pytest tests/ -v --cov=backend --cov-report=html
```

## License

Apache-2.0 — See [LICENSE](LICENSE)

**Medical Disclaimer**: This software is for research and educational purposes only. Not for clinical use without regulatory approval and physician oversight.

# ClinSight

Multi-agent clinical decision support system with vision-language models for chest X-ray analysis.

## Architecture

5 Parent Agents -> 7 Subagents -> 12 Total Reasoning Nodes

- **Coordinator**: Input validation, quality gates, pediatric safety
- **Radiologist**: Image analysis, pathology detection, attention regions
- **Lab Analyst**: Critical value detection, pattern correlation
- **Safety**: Contradiction checking, hallucination guard, bias audit (parallel)
- **Clinical Documenter**: ESI scoring, differential diagnosis, report generation

## Dual Model Stack

| Model | Role | VRAM |
|---|---|---|
| Qwen2.5-VL-7B-Instruct | Vision (chest X-ray) | ~14GB |
| Qwen3.5-35B-A3B | Text reasoning (MoE) | ~70GB |
| **Total** | | **~99GB** |

Target platform: AMD MI300X (192GB VRAM) — 93GB headroom for concurrent requests.

## Quick Start

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

```bash
cd frontend/react-app && npm install && npm run dev
```

## License

Apache-2.0 — See [LICENSE](LICENSE)

**Medical Disclaimer**: This software is for research and educational purposes only. Not for clinical use without regulatory approval and physician oversight.

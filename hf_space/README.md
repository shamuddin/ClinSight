# ClinSight HF Space

Interactive clinical decision-support report viewer powered by Gradio.

## Tabs
- **Demo Cases**: 3 pre-loaded realistic cases with generated ClinSight reports.
- **Custom Case**: Input patient JSON + prompt to generate a stub report.
- **JSON Viewer**: Inspect, validate, prettify, and flatten any ClinSight JSON report.
- **AMD Performance**: Benchmark latency and throughput on AMD Instinct GPUs via MIGraphX.
- **About**: Project info.

## Run locally
```bash
pip install -r requirements.txt
python app.py
```

## Deploy to HF Space
```bash
export SPACE_NAME="nousresearch/ClinSight"
bash deploy.sh
```

## Cache
Reports are saved to `/workspace/hf_space/cache/reports/`.

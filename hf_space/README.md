# ClinSight — Hugging Face Space

**Track 3: Vision & Multimodal AI | AMD Developer Hackathon @ lablab.ai**

## What is ClinSight?

ClinSight is a hierarchical multimodal clinical intelligence system for emergency decision support. It analyzes chest X-rays, lab values, and patient history simultaneously through a **5-parent-agent + 7-subagent LangGraph architecture**, running entirely on **AMD Instinct MI300X** via ROCm 7.0.

## Dual-Model Architecture

| Model | Role | VRAM |
|-------|------|------|
| Qwen2.5-VL-7B-Instruct | Vision (chest X-ray analysis) | ~14 GB |
| Qwen3.5-35B-A3B | Text reasoning (MoE, 3B active) | ~70 GB |
| **Total** | | **~99 GB** |
| **MI300X HBM3** | | **192 GB** |
| **Headroom** | | **~93 GB** |

H100 80GB cannot fit both simultaneously at full precision.

## Tabs

### Tab 1: Interactive Demo
Pre-loaded chest X-ray cases with clinically curated data. Since HF Spaces are CPU-only, this tab shows case data. Real inference runs on the AMD MI300X droplet.

### Tab 2: AMD MI300X Performance Evidence
- Real benchmark data (6 cases, mean 67.7s)
- Latency histogram
- rocm-smi output
- Architecture diagrams

## Links

- 🔗 **GitHub:** https://github.com/shamuddin/ClinSight
- 🔗 **Live Demo:** http://129.212.176.125:3000
- 🔗 **Benchmark Data:** See `benchmarks/real_benchmark.json`

## Safety

- ⚠️ Physician-in-the-loop decision support. NOT a diagnostic device.
- ⚠️ Not FDA-cleared.
- ⚠️ Pediatric warning: adult-trained models, increased correlation required for patients < 18.
- ⚠️ Bias disclaimer: AI models may exhibit performance disparities across demographic subgroups.

## License

Apache 2.0

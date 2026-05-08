#!/usr/bin/env python3
"""ClinSight Judge Readiness Verify Agent
Checks all 19 submission checklist items from Grand Prize Master Document.
Usage: python scripts/judge_readiness_verify.py
"""
import json, os, sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
REPORT = {}

def exists(path: str) -> bool:
    return (BASE / path).exists()

def read(path: str, limit=500) -> str:
    p = BASE / path
    if not p.exists(): return ""
    try:
        return p.read_text()[:limit]
    except:
        return ""

def check(name: str, condition: bool, note: str = ""):
    status = "PASS" if condition else "FAIL"
    REPORT[name] = {"status": status, "note": note}
    icon = "✓" if condition else "✗"
    print(f"  [{icon}] {name}: {status}" + (f" — {note}" if note else ""))

print("═" * 60)
print("JUDGE READINESS VERIFY AGENT")
print("═" * 60)
print(f"Repo: {BASE}")
print(f"Time: {datetime.utcnow().isoformat()}Z\n")

# ── TECHNICAL CHECKLIST ──
print("\n── TECHNICAL ──")
check("01. README.md exists", exists("README.md"))
check("02. LICENSE exists", exists("LICENSE"))
check("03. CLINICAL_ADVISORY.md exists", exists("CLINICAL_ADVISORY.md"), "Required for safety prize")
check("04. docs/architecture.md exists", exists("docs/architecture.md"))
check("05. docs/failure_modes.md exists", exists("docs/failure_modes.md"))
check("06. 5 parent agents in backend/agents/",
      all(exists(f"backend/agents/{f}") for f in ["coordinator.py","radiologist.py","lab_analyst.py","safety.py","clinical_documenter.py"]))
check("07. graph.py compiles LangGraph", "StateGraph" in read("backend/agents/graph.py"))
check("08. vllm_vision_client.py real client", "AsyncOpenAI" in read("backend/inference/vllm_vision_client.py"))
check("09. vllm_text_client.py real client", "AsyncOpenAI" in read("backend/inference/vllm_text_client.py"))
check("10. FastAPI main.py or main_minimal.py", exists("backend/api/main.py") or exists("backend/api/main_minimal.py"))
check("11. schemas.py with CaseInput/CaseOutput", "CaseInput" in read("backend/api/schemas.py"))
check("12. React frontend dist/ built", exists("frontend/react-app/dist/index.html"))
check("13. 6+ demo cases", len(list((BASE / "benchmarks").glob("CS-2024-*_meta.json"))) >= 6,
      f"Found {len(list((BASE / 'benchmarks').glob('CS-2024-*_meta.json')))} cases")
check("14. Tests directory", exists("tests/test_coordinator.py"))
check("15. Docker or compose file", exists("Dockerfile") or exists("docker-compose.yml"))

# ── BENCHMARKS ──
print("\n── BENCHMARKS ──")
real_bench = list((BASE / "benchmarks").glob("*latency*.csv")) or list((BASE / "benchmarks/gpu_results").glob("*.json"))
check("16. Real benchmark CSV/JSON exists", len(real_bench) > 0, f"Found {len(real_bench)} files")
rocm_smi = list((BASE / "benchmarks").glob("*rocm*")) + list((BASE / "benchmarks/gpu_results").glob("*rocm*"))
check("17. rocm-smi evidence exists", len(rocm_smi) > 0, f"Found {len(rocm_smi)} files")

# ── HUGGING FACE ──
print("\n── HUGGING FACE ──")
check("18. hf_space/ exists", exists("hf_space/app.py"))
hf_content = read("hf_space/app.py", 1000).lower()
if "clinsight" in hf_content or "chest" in hf_content or "xray" in hf_content or "radiologist" in hf_content:
    check("19. HF Space is about ClinSight", True)
else:
    check("19. HF Space is about ClinSight", False, f"Content hint: {hf_content[:80]}... WRONG TOPIC")

# ── BUILD IN PUBLIC ──
print("\n── BUILD IN PUBLIC ──")
check("20. Social media drafts exist", any(exists(p) for p in ["docs/social_posts.md","scripts/social_drafts.md","social/"]))

# ── DEMO VIDEO ──
check("21. Demo video file exists", any(exists(p) for p in ["docs/demo_video.mp4","demo_video.mp4","assets/demo.mp4"]))

# ── PITCH DECK ──
check("22. Pitch deck exists", exists("docs/pitch_deck.html") or exists("docs/pitch_deck.pdf"))

# ── SCORE ──
print("\n" + "═" * 60)
total = len(REPORT)
passed = sum(1 for v in REPORT.values() if v["status"] == "PASS")
pct = int(passed / total * 100) if total else 0
print(f"SCORE: {passed}/{total} ({pct}%)")
if pct >= 90:
    print("VERDICT: ✅ JUDGE-READY")
elif pct >= 70:
    print("VERDICT: 🟡 FINALIST-READY (fix failures)")
else:
    print("VERDICT: 🔴 NOT READY")
print("═" * 60)

# Save report
report_path = BASE / "benchmarks" / "judge_readiness_report.json"
report_path.write_text(json.dumps({"score": f"{passed}/{total}", "pct": pct, "checks": REPORT}, indent=2))
print(f"\nReport saved: {report_path}")

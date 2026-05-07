# ═══════════════════════════════════════════════════════════════════════
# MEDICAL KNOWLEDGE & MODEL TRANSPARENCY
# ═══════════════════════════════════════════════════════════════════════
#
# This file documents the exact medical training status of each model
# used in the ClinSight pipeline. It is designed for judge review and
# external audit.
#
# IMPORTANT: These are GENERAL-PURPOSE models, not medically fine-tuned.
# The clinical rigor comes from multi-agent architecture + safety layers,
# not from medical fine-tuning of the base models.
#
# ═══════════════════════════════════════════════════════════════════════

MODEL_MEDICAL_TRANSPARENCY = {
    "qwen2.5-vl-7b": {
        "model_name": "Qwen2.5-VL-7B-Instruct",
        "parameter_count": "7 billion",
        "training_status": "GENERAL PURPOSE (not medically fine-tuned)",
        "medical_knowledge_source": "Pre-training corpus includes: PubMed abstracts, medical textbooks, radiology atlases, clinical photography datasets (public web data)",
        "what_it_can_do": [
            "Identify anatomical structures in chest X-rays",
            "Recognize common radiological patterns (pneumothorax, effusion, consolidation)",
            "Describe image findings in clinical terminology",
        ],
        "what_it_cannot_do": [
            "Replace a board-certified radiologist",
            "Guarantee detection of subtle or rare findings",
            "Interpret imaging in full clinical context (history + labs + vitals)",
        ],
        "clinical_validation": "NONE — this is a proof-of-concept architecture demo",
        "used_for": "Image analysis agent — generates initial finding descriptions",
        "safety_compensation": "Findings are cross-validated by Lab Analyst + Safety Guard + Documenter agents",
    },
    "qwen3.5-35b-a3b": {
        "model_name": "Qwen3.5-35B-A3B",
        "parameter_count": "35 billion",
        "training_status": "GENERAL PURPOSE (not medically fine-tuned)",
        "medical_knowledge_source": "Pre-training corpus includes: medical textbooks, clinical guidelines, drug databases, medical Q&A forums, research papers (public web data)",
        "what_it_can_do": [
            "Generate structured clinical differentials",
            "Suggest evidence-based clinical actions",
            "Apply ESI triage protocols from training data",
            "Recognize drug interactions and contraindications",
        ],
        "what_it_cannot_do": [
            "Replace clinical judgment of trained physicians",
            "Account for institution-specific protocols",
            "Access real-time drug databases or patient-specific factors",
        ],
        "clinical_validation": "NONE — this is a proof-of-concept architecture demo",
        "used_for": "Documenter agent — generates differential, actions, and report",
        "safety_compensation": "Outputs are verified by Safety Guard for hallucinations and contradictions",
    },
}

# Human-readable summary for judge display
MEDICAL_TRANSPARENCY_SUMMARY = """
CLINSIGHT MEDICAL KNOWLEDGE DISCLOSURE

Models Used:
  • Vision:  Qwen2.5-VL-7B-Instruct (7B parameters, general multimodal)
  • Text:    Qwen3.5-35B-A3B (35B parameters, general reasoning)

Medical Training Status:
  • NEITHER model has been fine-tuned on medical datasets
  • Both are GENERAL-PURPOSE models that learned medical concepts
    during broad internet pre-training
  • This is analogous to how a medical student learns from textbooks
    — broad knowledge, not clinical practice

Where Clinical Rigor Comes From:
  1. MULTI-AGENT ARCHITECTURE — 5 specialized agents cross-validate
  2. STRUCTURED PROMPTING — clinical framing forces medical reasoning
  3. SAFETY VERIFICATION — contradiction/hallucination detection
  4. ESI PROTOCOL — hard-coded triage rules prevent severity errors
  5. ACCURACY SCORING — outputs compared against expert ground truth

Clinical Validation:
  • NONE — this is an architecture proof-of-concept
  • NOT FDA-approved or CE-marked
  • NOT a substitute for trained clinicians
  • Accuracy scores are based on 6 curated demo cases only

Intended Use:
  • Clinical DECISION SUPPORT, not diagnosis
  • Demonstrates how general AI can be structured for healthcare
  • Multi-agent approach compensates for lack of medical fine-tuning
"""

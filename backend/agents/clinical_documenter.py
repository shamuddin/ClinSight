from datetime import datetime
from backend.core.state import AgentState
from backend.agents.subgraphs import esi_scorer_sub, differential_builder
from backend.agents.documenter_cache import get_cached_documenter_outputs
from backend.inference.vllm_text_client import VLLMTextClient

_client: VLLMTextClient | None = None

def _text_client():
    global _client
    if _client is None:
        _client = VLLMTextClient()
    return _client


async def clinical_documenter_agent(state: AgentState) -> AgentState:
    """Agent 5: ESI scorer, differential builder, report generation.
    For demo cases: uses pre-cached real LLM outputs (instant).
    For new cases: calls LLM live (prove it's real).
    """
    # Delegate to subagents (deterministic)
    state = esi_scorer_sub(state)
    state = differential_builder(state)

    cid = state.get("case_id", "")
    cached = get_cached_documenter_outputs(cid)

    if cached:
        # Demo case: use pre-generated real LLM outputs (instant)
        actions = cached["suggested_actions"]
        report = cached["report"]
        # Override ESI if cached differs (rare)
        if cached.get("esi_level"):
            state["esi_level"] = cached["esi_level"]
            state["esi_description"] = cached["esi_description"]
        if cached.get("differential"):
            state["differential"] = cached["differential"]
    else:
        # New case: call LLM live (real-time inference)
        try:
            actions = await _text_client().generate_actions(state)
        except Exception:
            actions = suggest_actions_deterministic(state)
        try:
            report = await _text_client().generate_report(state)
        except Exception:
            report = generate_report_deterministic(state)

    state["suggested_actions"] = actions
    state["report"] = report

    audit_log = state.get("audit_log", [])
    audit_log.append({
        "agent": "clinical_documenter",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "report_generation",
        "esi": state["esi_level"],
        "differential_count": len(state["differential"]),
        "actions_count": len(actions),
        "cached": cached is not None,
    })
    state["audit_log"] = audit_log
    return state


def suggest_actions_deterministic(state: AgentState) -> list[str]:
    """Fallback deterministic action generator."""
    esi = state.get("esi_level", 5)
    if esi == 1:
        return ["Immediate bedside evaluation", "Contact trauma/critical care team", "Prepare for intervention"]
    elif esi == 2:
        return ["Urgent physician assessment", "Consider ICU admission", "Serial vitals and labs"]
    elif esi == 3:
        return ["Physician evaluation within 30 minutes", "Order follow-up imaging if indicated"]
    elif esi == 4:
        return ["Standard ED workup", "Follow-up imaging if needed"]
    return ["Routine workup and disposition"]


def generate_report_deterministic(state: AgentState) -> dict:
    return {
        "summary": f"ESI {state.get('esi_level', '?')} — {state.get('esi_description', '')}. "
                   f"{len(state.get('findings', []))} findings, {len(state.get('lab_alerts', []))} lab alerts, "
                   f"{len(state.get('merged_flags', []))} safety flags.",
        "esi": {
            "level": state.get("esi_level"),
            "description": state.get("esi_description"),
            "rules": state.get("esi_rules_triggered", []),
        },
        "differential": state.get("differential", []),
        "actions": state.get("suggested_actions", []),
        "safety_summary": {
            "flags": len(state.get("merged_flags", [])),
            "downgrades": state.get("safety_downgrades", 0),
        },
    }

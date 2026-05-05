"""Parent LangGraph compilation.

5 Parent Agents -> 12 Total Reasoning Nodes

Graph layout (sequential with conditional fail):
  Coordinator -(pass)-> Analysis (radiologist + lab) -> Safety -> Documenter -> END
  Coordinator -(fail)-> REJECT -> END
"""

from langgraph.graph import StateGraph, END
from backend.core.state import AgentState
from backend.agents.coordinator import coordinator_agent
from backend.agents.radiologist import radiologist_agent
from backend.agents.lab_analyst import lab_analyst_agent
from backend.agents.safety import safety_agent
from backend.agents.clinical_documenter import clinical_documenter_agent


def _coordinator_router(state: AgentState) -> str:
    """Route after coordinator: pass to analysis or fail to REJECT."""
    quality = state.get("quality_gate", {})
    if not quality.get("pass", True):
        return "reject"
    return "analyze"


async def _analysis_node(state: AgentState) -> AgentState:
    """Sequential aggregation of radiologist + lab analyst."""
    state = await radiologist_agent(state)
    state = await lab_analyst_agent(state)
    return state


def _reject_node(state: AgentState) -> AgentState:
    """Terminal node when image quality fails."""
    state["esi_level"] = -1
    state["esi_description"] = "REJECTED: Image quality insufficient"
    state["differential"] = ["N/A — input rejected"]
    state["suggested_actions"] = ["Resubmit with compliant image"]
    state["report"] = {
        "esi": {"level": -1, "description": state["esi_description"], "rules": []},
        "differential": state["differential"],
        "actions": state["suggested_actions"],
        "safety_summary": {},
    }
    return state


# Build graph
workflow = StateGraph(AgentState)

# Register nodes
workflow.add_node("coordinator", coordinator_agent)
workflow.add_node("analysis", _analysis_node)
workflow.add_node("safety", safety_agent)
workflow.add_node("documenter", clinical_documenter_agent)
workflow.add_node("reject", _reject_node)

# Entry point
workflow.set_entry_point("coordinator")

# Conditional edge: pass/fail routing
workflow.add_conditional_edges(
    "coordinator",
    _coordinator_router,
    {"reject": "reject", "analyze": "analysis"},
)

# Sequential edges
workflow.add_edge("analysis", "safety")
workflow.add_edge("safety", "documenter")
workflow.add_edge("documenter", END)
workflow.add_edge("reject", END)

# Compile
app = workflow.compile()


async def run_pipeline(state: AgentState) -> AgentState:
    """Execute the compiled graph from initial state."""
    return await app.ainvoke(state)

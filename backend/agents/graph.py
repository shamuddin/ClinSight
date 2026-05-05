"""Parent LangGraph compilation stub."""
from backend.core.state import AgentState
from backend.agents.coordinator import coordinator_agent
from backend.agents.radiologist import radiologist_agent
from backend.agents.lab_analyst import lab_analyst_agent
from backend.agents.safety import safety_agent
from backend.agents.clinical_documenter import clinical_documenter_agent

# TODO: compile into langgraph StateGraph with conditional edges
# This file will be fleshed out in Phase 1

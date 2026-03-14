from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.retriever import retriever_agent
from src.agents.parser import requirements_agent
from src.agents.evaluator import evaluator_agent
from src.agents.verification import verification_agent
from src.agents.synthesis import synthesis_agent

def create_orchestrator():
    """
    Creates the LangGraph StateGraph orchestration.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("retriever", retriever_agent)
    workflow.add_node("parser", requirements_agent)
    workflow.add_node("evaluator", evaluator_agent)
    workflow.add_node("verification", verification_agent)
    workflow.add_node("synthesis", synthesis_agent)

    # Set Entry Point
    workflow.set_entry_point("retriever")

    # Add Edges
    workflow.add_edge("retriever", "parser")
    workflow.add_edge("parser", "evaluator")
    workflow.add_edge("evaluator", "verification")
    workflow.add_edge("verification", "synthesis")
    workflow.add_edge("synthesis", END)

    return workflow.compile()

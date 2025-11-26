# graph/workflow.py

from langgraph.graph import StateGraph, END
from graph.state import UniversityState
from agents import payment_agent, reconciliation_agent
from orchestrator import orchestrator, router

def build_graph():
    """Build and compile the workflow graph"""
    
    workflow = StateGraph(UniversityState)
    
    # Add nodes
    workflow.add_node("orchestrator", orchestrator)
    workflow.add_node("payment_agent", payment_agent)
    workflow.add_node("reconciliation_agent", reconciliation_agent)
    # workflow.add_node("support_agent", support_agent)
    # workflow.add_node("appointment_agent", appointment_agent)
    
    # Set entry point
    workflow.set_entry_point("orchestrator")
    
    # Orchestrator routes to agents
    workflow.add_conditional_edges(
        "orchestrator",
        router,
        {
            "payment_agent": "payment_agent",
            "reconciliation_agent": "reconciliation_agent",
            "support_agent": "support_agent",
            "appointment_agent": "appointment_agent",
            "__end__": END
        }
    )
    
    # After agents, go back to orchestrator
    workflow.add_edge("payment_agent", "orchestrator")
    workflow.add_edge("reconciliation_agent", "orchestrator")
    workflow.add_edge("support_agent", "orchestrator")
    workflow.add_edge("appointment_agent", "orchestrator")
    
    # Compile and return
    return workflow.compile()
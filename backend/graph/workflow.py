# graph/workflow.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import UniversityState
from agents.payment_agent import payment_agent
from agents.reconciliation_agent import reconciliation_agent
from agents.info_agent import info_agent
from agents.orchestrator import orchestrator, router
from agents.appointment_agent import appointment_app

def build_graph():
    """Build and compile the workflow graph"""
    
    workflow = StateGraph(UniversityState)
    
    # Add nodes
    workflow.add_node("orchestrator", orchestrator)
    workflow.add_node("payment_agent", payment_agent)
    workflow.add_node("reconciliation_agent", reconciliation_agent)
    workflow.add_node("info_agent", info_agent)
    workflow.add_node("appointment_agent", appointment_app)
    
    # Set entry point
    workflow.set_entry_point("orchestrator")
    
    # Orchestrator routes to agents
    workflow.add_conditional_edges(
        "orchestrator",
        router,
        {
            "payment_agent": "payment_agent",
            "reconciliation_agent": "reconciliation_agent",
            "info_agent": "info_agent",
            "appointment_agent": "appointment_agent",
            "__end__": END
        }
    )
    
    # After agents, go back to orchestrator
    workflow.add_edge("payment_agent", END)
    workflow.add_edge("reconciliation_agent", END)
    workflow.add_edge("info_agent", END)
    workflow.add_edge("appointment_agent", END)
    
    memory = MemorySaver()
    # Compile and return
    return workflow.compile(checkpointer=memory)
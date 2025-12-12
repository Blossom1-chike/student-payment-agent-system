import os
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
from graph.state import UniversityState
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0)

# Define the classification schema
class AgentRoute(BaseModel):
    agent: Literal["payment", "reconciliation", "support", "appointment", "info"]
    reasoning: str  # Optional: why this agent was chosen

def orchestrator(state: UniversityState):
    """Classify which agent should handle this message"""
    
    message = state["messages"][-1]
    
    # Create classifier with structured output
    classifier_llm = llm.with_structured_output(AgentRoute)
    
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """
            You are a classfier who classifies queries of students at Northumbria University. 
            Review the CONVERSATION HISTORY.

            Classify the student message to route to the correct agent:

            - 'payment': If the student wants to make a NEW payment, needs payment link, asking about fees/costs, uploading student ID to validate identity before payment
            - 'reconciliation': If the student ALREADY paid but has access issues, missing payment reference, portal blocked despite payment
            - 'support': If the student has a problem, complaint, error, needs general help, frustrated
            - 'appointment': If the student wants to schedule a meeting, book appointment, talk to someone in person
            - 'info': General questions about the university, library hours, locations, gym, student union, courses, TFL or events.

            Choose the most appropriate agent based on the student's intent and return the key in quotes.
            Provide a brief reasoning for your choice.

            """
        },
        {
            "role": "user",
            "content": message.content
        }
    ])
    
    print(f"🤖 Orchestrator classified: {result.agent} - {result.reasoning}")
    
    return {"agent": result.agent}

def router(state: UniversityState):
    """Route to the classified agent"""
    
    agent_route = state.get("agent", "payment")
    
    print(f"📍 Router sending to: {agent_route}_agent")
    
    # Map to actual agent names in your graph
    agent_map = {
        "payment": "payment_agent",
        "reconciliation": "reconciliation_agent",
        "info": "info_agent",
        "appointment": "appointment_agent"
    }
    
    # Check if we're done
    if state.get('payment_link') and state.get('payment_matched'):
        return "__end__"
    
    return agent_map.get(agent_route, "payment_agent")


#   RULES:
#             - If the user is currently in the middle of a payment flow (e.g. just provided an ID card), route to 'payment'.
#             - If the user is answering an appointment question, route to 'appointment'.
#             - If the topic has CHANGED, route to the new topic.
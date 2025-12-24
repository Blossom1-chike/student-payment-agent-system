import os
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
from graph.state import UniversityState
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

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
    
    # 2. Get the LAST AI MESSAGE (Context)
    # We search backwards to find what the AI asked just before this.
    last_ai_text = "None"
    # Slice [:-1] to ignore the user's current message, reverse to find recent AI msg
    for msg in reversed(state["messages"][:-1]): 
        if isinstance(msg, AIMessage):
            last_ai_text = msg.content
            break

    # Create classifier with structured output
    classifier_llm = llm.with_structured_output(AgentRoute)
    
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": f"""
            You are a classfier who classifies queries of students at Northumbria University. 
            Review the CONVERSATION HISTORY.

            **CRITICAL CONTEXT:**
            The AI just asked the user: "{last_ai_text}"
            
            **YOUR JOB:**
            Classify the User's latest message to route it to the correct agent.
 
            **ROUTING RULES:**
            1. **CONTINUATION (High Priority):** If the User is answering the AI's specific question (e.g., providing email, ID, date, or confirming), **ROUTE BACK TO THE SAME INTENT.**
               - Example: AI asks "What date?" -> User says "Monday" -> Route to 'appointment'.
               - Example: AI asks "What is your email?" -> User says "me@gmail.com" -> Route to 'appointment'.

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
    agent_route = state.get("agent", "info")
    
    # 1. Get the last AI message
    last_ai_msg = ""
    for m in reversed(state["messages"]):
        if isinstance(m, AIMessage):
            last_ai_msg = m.content.lower()
            break
            
    # The Payment Agent says: "I have extracted...", "ID Card", "Biometric"
    payment_triggers = ["extracted", "id card", "biometric", "selfie", "payment", "stripe", "upload"]
    if any(word in last_ai_msg for word in payment_triggers):
        print(f"STICKY ROUTER: Context is 'Payment' (Found: '{last_ai_msg[:20]}...')")
        return "payment_agent"

    # The Appointment Agent says: "registry", "finance team", "schedule", "cohort", "roster"
    appointment_triggers = ["registry", "finance team", "schedule", "cohort", "roster", "calendar", "meeting", "book"]
    if any(word in last_ai_msg for word in appointment_triggers):
        print(f"STICKY ROUTER: Context is 'Appointment' (Found: '{last_ai_msg[:20]}...')")
        return "appointment_agent"
    
    # Check if we're done
    if state.get('payment_link') and state.get('payment_matched'):
        return "__end__"
    
    agent_map = {
        "payment": "payment_agent",
        "appointment": "appointment_agent",
        "info": "info_agent",
        "support": "info_agent" 
    }
    
    return agent_map.get(agent_route, "info_agent")

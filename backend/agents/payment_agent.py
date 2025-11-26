from typing import TypedDict, Optional, Annotated
import operator
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools.payment.create_payment_link import create_payment_link
from tools.payment.extract_name import extract_name_from_id
from graph.state import UniversityState

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0)

class PaymentState(TypedDict):
    messages: Annotated[list, operator.add]  # Accumulates messages
    student_id: Optional[str]
    student_name: Optional[str]
    amount: Optional[float]
    payment_link: Optional[str]
    has_student_image: bool
    image_bytes: bytes

payment_tools = [extract_name_from_id, create_payment_link]

def payment_agent(state: UniversityState):
    llm_with_tools = llm.bind_tools(payment_tools)
    system_message = {
        "role": "system",
        "content": f"""
        You are a friendly payment assistant at Northumbria University.

        You are expected to help student make payment for their tuition fee. If a student 
        requests to make payment, you have to check for

        1. If no student information is provided: Ask student to upload their student ID card image
        2. When image provided: Use extract_name_from_id tool to extract text from the image
        3. If have student information is provided but no amount: Ask the student how much they would want to pay
        4. When have all the student and amount information: Use create_stripe_payment_link tool to generate a payment link
        5. After link created: Share it with the student

        Note: if you do not understand, say you don't understand and suggest if they would want to pay

        Be warm, friendly, and don't mention any of these tools to the student"""
    }

    messages = [system_message].extend(state["messages"])

    response = llm_with_tools.invoke(messages)

    print(f"Payment agent response: {response}")

    if response.tool_calls:
        tool_messages = []
        updated_state = {}

        for tool_call in response.tool_calls:
            print(f"Tool call: {tool_call}")
            
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            if tool_name == "extract_name_from_id":
                # Extract from image in message history
                extracted = extract_name_from_id(state["image_bytes"])# come back here
                result = json.dumps(extracted)
                
                # Update state
                updated_state["student_id"] = extracted
                updated_state["student_name"] = extracted
                
            elif tool_name == "create_stripe_payment_link":
                # Create payment link
                result = create_stripe_payment_link.invoke(tool_args)
                
                # Update state
                updated_state["payment_link"] = result
                updated_state["amount"] = tool_args.get("amount")
                
            else:
                result = f"Unknown tool: {tool_name}"
            
            # Create tool message
            tool_message = ToolMessage(
                content=result,
                tool_call_id=tool_call["id"]
            )
            tool_messages.append(tool_message)
        
        # Get final response with tool results
        final_messages = messages + [response] + tool_messages
        final_response = llm.invoke(final_messages)
        
        # Return messages and state updates
        return {
            "messages": [response] + tool_messages + [final_response],
            **updated_state
        }
    else:
        # No tools needed
        return {"messages": [response]}
    


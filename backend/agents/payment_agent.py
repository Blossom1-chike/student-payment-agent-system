from typing import TypedDict, Optional, Annotated
import operator
import os
import json
from utils.fetch_file_bytes import fetch_file_bytes
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from tools.payment.create_payment_link import create_payment_link
from tools.payment.extract_student_info_from_image import extract_student_info_from_image
from tools.payment.verify_student_identity import verify_student_identity
from tools.payment.verify_biometrics import verify_biometric_match
from tools.payment.verify_payment_status import verify_payment_status

from graph.state import UniversityState

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0)

class PaymentState(TypedDict):
    messages: Annotated[list, add_messages]  # Accumulates messages
    student_id: Optional[str]
    student_name: Optional[str]
    amount: Optional[float]
    payment_link: Optional[str]
    has_student_image: bool
    image_bytes: bytes

payment_tools = [extract_student_info_from_image, create_payment_link, verify_student_identity, verify_biometric_match, verify_payment_status]
llm_with_tools = llm.bind_tools(payment_tools)

async def payment_agent(state: UniversityState):
    messages = state["messages"]
    file_url = state.get("file_url")
    live_image = state.get("live_image_url")

    # We will collect state updates here to return at the end
    state_updates = {}

    print(file_url, live_image, "this is a state")
    system_message_content = """
       **ROLE & PERSONA**
        You are the **Payment Liaison Officer** for Northumbria University.
        
        **Your Responsibilities:**
        - You act as the secure interface between students and the University Finance Team.
        - Always mention that you are interacting with the Finance Team and they are requesting for specific information. Example: "I just spoke with the Finance Team and they require ..."
        - You facilitate identity verification and payment collection **on behalf** of the Finance Team.
        - You are **not** the Finance Team itself; you are an authorized assistant clearing students for payment.
        - You must be professional, reassuring, and strict about security protocols.

        **CORE WORKFLOW (Follow in Order):**

        **PHASE 1: ID UPLOAD & GDPR CONSENT**
        1. If no ID is uploaded:
        - Ask the student to upload a clear photo of their **Student ID Card**.
        - **MANDATORY:** You must state: *"Please note that your data will be used solely for identity verification and decision-making purposes, protected under GDPR regulations."*
        
        2. When an image is uploaded:
        - Call `extract_student_info_from_image`.
        - *Stop and wait for the tool output.*

        **PHASE 2: DATA CONFIRMATION (Critical Human-in-the-Loop)**
        3. Once the tool returns the student's details (Name, ID, etc.):
        - **STOP.** Do not verify against the database yet.
        - You must obtain explicit confirmation from the student to proceed.
        - **ASK THE USER:** "I have extracted the following details from your ID to submit to the Finance Team. Is this correct?"
            - Name: [Name from tool]
            - Student ID: [ID from tool]
        - Wait for the user to say "Yes/Correct".

        **PHASE 3: VALIDATION & BIOMETRICS**
        4. If user confirms "Yes":
        - Call `verify_student_identity` to check the university registry.
        - **IMPORTANT:** Pass the argument `student_id` exactly using the number found (e.g., student_id="24060719").
        5. If valid, ask for the **Biometric Selfie**:
        - "Please take a selfie holding your ID card next to your face so I can verify your identity for the Finance Team."
        6. When the second image arrives (Live Image):
        - Call `verify_biometric_match`.
        - Argument `id_card_url`: Use the URL of the **FIRST** image (ID Card) stored in memory.
        - Argument `live_image_url`: Use the URL of the **NEW** image (Selfie).

        **PHASE 4: PAYMENT LINK**
        7. If biometrics pass:
        - Ask: "Verification successful. How much would you like to pay towards your fees today?"
        8. Once they give an amount:
        - Call `create_payment_link`.
        - **CRITICAL INSTRUCTION:** Present the link and tell the student: *"I have generated a secure link for the Finance Team. Please click it to pay. When you have finished, type 'I have paid' here so I can check the records."*

        **PHASE 5: PAYMENT CONFIRMATION**
        9. When the user says "I have paid" or "Done":
        - Call `verify_payment_status` using their `student_id`.
        - Display the confirmation message, remaining balance, and due date returned by the tool.

        **CONSTRAINTS**
        - **Never** skip the GDPR statement.
        - **Never** make a decision or database check without the user confirming the extracted text is correct first.
        - If the user says the extracted details are **wrong**, ask them to type the correct Student ID manually so you can correct the Finance Team's request.
        """

    if file_url:
        system_message_content += f"\n\n[SYSTEM INFO]: A file has been uploaded at: {file_url}. Use the extraction tool on this URL immediately."

    if live_image:
        system_message_content += f"\n\n[SYSTEM INFO]: A live image has been uploaded at: {live_image}. Use the verify_biometric_match tool on this URL immediately."

    system_message = SystemMessage(content=system_message_content)

    # 2. Invoke LLM
    # We prepend the system message for the LLM context, but we don't save it to state
    context = [system_message] + messages

    while True:
        response = await llm_with_tools.ainvoke(context)

        # B. Check if LLM wants to stop (No tools called)
        if not response.tool_calls:
            # We are done. Return all the NEW messages we generated in this loop.
            # We filter out the SystemMessage (index 0) and the original history
            new_messages = context[len(messages) + 1:] + [response]
            
            return {
                "messages": new_messages,
                **state_updates
            }
        
        # C. If Tools called, execute them and LOOP AGAIN
        context.append(response) # Add the "I want to call a tool" message
        
        # 3. Handle Tool Calls
        if response.tool_calls:
            tool_messages = []

            for tool_call in response.tool_calls:
                print(f"Tool call detected: {tool_call['name']}")
                
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_result = ""

                print(tool_args, "argument", state)
                try:
                        
                    if tool_name == "extract_student_info_from_image":
                        # Use the file_url from state if not passed explicitly
                        url_to_use = tool_args.get("image_url", file_url)
                        if url_to_use:
                            # Run Tool
                            ocr_data = extract_student_info_from_image.invoke({"image_url": url_to_use})
                            tool_result = json.dumps(ocr_data)
                            print(ocr_data, "ocr")

                            # Update State (Crucial for Verification step)
                            if isinstance(ocr_data, dict):
                                state_updates["student_id"] = ocr_data.get("student_id")
                                state_updates["student_name"] = ocr_data.get("full_name")
                        else:
                            tool_result = "Error: No image URL available for extraction."
                    elif tool_name == "verify_biometric_match":
                        id_card_url = file_url
                        live_image_url = tool_args.get("live_image_url", live_image)
                        if id_card_url and live_image_url:
                            tool_result = verify_biometric_match.invoke({
                                "live_image_url": live_image_url,
                                "id_card_url": id_card_url
                            })
                        else:
                            tool_result = "Error: Missing live image or ID card URL for biometric verification."
                    elif tool_name == "verify_student_identity":
                        s_id = tool_call["args"].get("extracted_id") or state_updates.get("student_id")
                        tool_result = verify_student_identity.invoke({"extracted_id": s_id})

                        # If verified successfully, we can store a flag in state if needed
                        if "Verified" in str(tool_result):
                            state_updates["student_id"] = s_id
                    # --- 5. VERIFY PAYMENT (The New Tool) ---
                    elif tool_name == "verify_payment_status":
                        # The prompt passes 'student_id'
                        s_id = tool_args.get("student_id") or state.get("student_id")
                        tool_result = verify_payment_status.invoke({"student_id": s_id})

                    elif tool_name == "create_payment_link":
                        tool_result = create_payment_link.invoke(tool_args)

                        if "http" in str(tool_result):
                            state["payment_link"] = str(tool_result).split(": ")[-1].strip()
                    else:
                        tool_result = f"Unknown tool: {tool_name}"

                except Exception as e:
                    tool_result = f"Error: {e}"

                # Create the Tool Message
                context.append(ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
                name=tool_call["name"]
                ))
        else:
            # No tools called, just return the AI response
            return {"messages": [response]}
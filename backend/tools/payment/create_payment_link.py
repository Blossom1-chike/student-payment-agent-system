import stripe
import os
from typing_extensions import TypedDict
from langchain.tools import tool
from graph.state import UniversityState

""" 
The payment process involves:
User - wants to pay
Agent - requests for ID card upload
User - uploads card

Agent - 
-> extracts name from ID card 
-> verifies the student in the DB 
-> generates a payment strip link 
-> sends the link to the user

"""
class PaymentDTO(TypedDict):
    student_name: str | None
    email:  str | None
    amount:  float | None
    currency:  str | None = "gbp"
    card_name:  str | None

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # set your secret key

@tool("create_payment_link", return_direct=False, description="Generates a stripe payment link for student to make payment with")
def create_payment_link(state: UniversityState):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {"name": f"Course Fee for student {state["student_id"]}"},
                        "unit_amount": state["amount"],
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            customer_email=email or None,
            success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://yourdomain.com/cancel",
        )
        return {"success": True, "url": session.url, "session_id": session.id}
    except Exception as e:
        print("Error generating payment link:", e)
        return {"success": False, "error": str(e)}

def verify_payment(session_id):
    """
    Verify payment from a Stripe Checkout session ID.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_status = session.payment_status
        metadata = session.metadata
        amount = session.amount_total
        currency = session.currency

        return {
            "success": payment_status == "paid",
            "student_name": metadata.get("student_name"),
            "amount": amount,
            "currency": currency,
        }

    except Exception as e:
        print("Error verifying payment:", e)
        return {"success": False, "error": str(e)}
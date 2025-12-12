from database.db import SessionLocal
from models.payment import Payment

#Insert a new payment record into the database
def create_payment(student_id: str, amount: float, transaction_id: str, status: str):
    db = SessionLocal()
    try:
        payment = Payment(
            student_id=student_id,
            amount=amount,
            transaction_id=transaction_id,
            status=status
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    finally:
        db.close()

#Fetch a payments record by transaction ID
def get_payments_by_student(student_id: str):
    db = SessionLocal()
    try:
        return db.query(Payment).filter(Payment.student_id == student_id).all()
    finally:
        db.close()

# Update payment status
def update_payment_status(transaction_id: str, status: str):
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
        if payment:
            payment.status = status
            db.commit()
            db.refresh(payment)
        return payment
    finally:
        db.close()

def delete_payment(transaction_id: str):
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
        if payment:
            db.delete(payment)
            db.commit()
        return payment
    finally:
        db.close()
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from ..database.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    amount = Column(Float)
    status = Column(String)
    transaction_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

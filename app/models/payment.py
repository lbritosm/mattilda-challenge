from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Payment(Base):
    """Modelo de Pago"""
    
    __tablename__ = "payments"
    __table_args__ = (
        Index('idx_payment_student_date', 'student_id', 'payment_date'),
        Index('idx_payment_school_date', 'school_id', 'payment_date'),
        CheckConstraint('amount > 0', name='ck_payment_amount_positive'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)  # Aumentado a 12,2
    payment_method = Column(String(50), nullable=True)  # cash, card, transfer, etc.
    payment_reference = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)
    payment_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    invoice = relationship("Invoice", back_populates="payments")
    school = relationship("School", backref="payments")
    student = relationship("Student", backref="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, invoice_id={self.invoice_id}, amount={self.amount})>"


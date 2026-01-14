from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Numeric, Enum as SQLEnum, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.core.database import Base


class InvoiceStatus(str, enum.Enum):
    """Estados de una factura"""
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class Invoice(Base):
    """Modelo de Factura"""
    
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint('school_id', 'invoice_number', name='uq_invoice_school_number'),
        Index('idx_invoice_school_due', 'school_id', 'due_date'),
        Index('idx_invoice_student_due', 'student_id', 'due_date'),
        CheckConstraint('total_amount >= 0', name='ck_invoice_total_amount_positive'),
        CheckConstraint('due_date >= issue_date', name='ck_invoice_due_after_issue'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_number = Column(String(50), nullable=False)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    total_amount = Column(Numeric(12, 2), nullable=False)  # Renombrado de amount
    description = Column(String(500), nullable=True)
    issue_date = Column(Date, nullable=False, server_default=func.current_date())
    due_date = Column(Date, nullable=False)  # Cambiado de DateTime a Date
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    school = relationship("School", backref="invoices")
    student = relationship("Student", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', total_amount={self.total_amount}, status='{self.status}')>"


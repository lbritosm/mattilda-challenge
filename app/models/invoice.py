from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
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
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    student = relationship("Student", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', amount={self.amount}, status='{self.status}')>"


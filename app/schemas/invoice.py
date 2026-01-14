from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from app.models.invoice import InvoiceStatus
from app.schemas.payment import Payment


class InvoiceBase(BaseModel):
    """Schema base para Invoice"""
    invoice_number: str = Field(..., min_length=1, max_length=50, description="Número de factura (único por colegio)")
    school_id: UUID = Field(..., description="ID del colegio")
    student_id: UUID = Field(..., description="ID del estudiante")
    total_amount: Decimal = Field(..., gt=0, description="Monto total de la factura (debe ser mayor a 0)")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la factura")
    issue_date: date = Field(default_factory=date.today, description="Fecha de emisión")
    due_date: date = Field(..., description="Fecha de vencimiento")
    status: InvoiceStatus = Field(InvoiceStatus.PENDING, description="Estado de la factura")


class InvoiceCreate(InvoiceBase):
    """Schema para crear un Invoice"""
    pass


class InvoiceUpdate(BaseModel):
    """Schema para actualizar un Invoice"""
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=50)
    school_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    total_amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[InvoiceStatus] = None


class Invoice(InvoiceBase):
    """Schema para retornar un Invoice"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    payments: Optional[List[Payment]] = Field(default=[], description="Lista de pagos asociados a la factura")
    
    class Config:
        from_attributes = True


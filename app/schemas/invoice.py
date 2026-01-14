from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.models.invoice import InvoiceStatus


class InvoiceBase(BaseModel):
    """Schema base para Invoice"""
    invoice_number: str = Field(..., min_length=1, max_length=50, description="Número único de factura")
    student_id: UUID = Field(..., description="ID del estudiante")
    amount: Decimal = Field(..., gt=0, description="Monto de la factura (debe ser mayor a 0)")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la factura")
    due_date: datetime = Field(..., description="Fecha de vencimiento")
    status: InvoiceStatus = Field(InvoiceStatus.PENDING, description="Estado de la factura")


class InvoiceCreate(InvoiceBase):
    """Schema para crear un Invoice"""
    pass


class InvoiceUpdate(BaseModel):
    """Schema para actualizar un Invoice"""
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=50)
    student_id: Optional[UUID] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None
    status: Optional[InvoiceStatus] = None


class Invoice(InvoiceBase):
    """Schema para retornar un Invoice"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


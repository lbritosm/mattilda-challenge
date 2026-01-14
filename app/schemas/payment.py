from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class PaymentBase(BaseModel):
    """Schema base para Payment"""
    invoice_id: UUID = Field(..., description="ID de la factura")
    school_id: UUID = Field(..., description="ID del colegio")
    student_id: UUID = Field(..., description="ID del estudiante")
    amount: Decimal = Field(..., gt=0, description="Monto del pago (debe ser mayor a 0)")
    payment_method: Optional[str] = Field(None, max_length=50, description="Método de pago")
    payment_reference: Optional[str] = Field(None, max_length=100, description="Referencia del pago")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    payment_date: datetime = Field(default_factory=datetime.now, description="Fecha del pago")


class PaymentCreate(BaseModel):
    """Schema para crear un Payment - invoice_id, student_id y school_id se obtienen automáticamente"""
    amount: Decimal = Field(..., gt=0, description="Monto del pago (debe ser mayor a 0)")
    payment_method: Optional[str] = Field(None, max_length=50, description="Método de pago")
    payment_reference: Optional[str] = Field(None, max_length=100, description="Referencia del pago")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    payment_date: datetime = Field(default_factory=datetime.now, description="Fecha del pago")
    
    class Config:
        extra = "forbid"  # Rechazar campos no permitidos (como invoice_id, student_id y school_id)


class Payment(PaymentBase):
    """Schema para retornar un Payment"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


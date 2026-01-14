from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from uuid import UUID
from app.schemas.invoice import Invoice


class AccountStatus(BaseModel):
    """Schema base para estado de cuenta"""
    total_invoiced: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    total_pending: Decimal = Decimal("0.00")


class SchoolAccountStatus(AccountStatus):
    """Schema para estado de cuenta de un colegio"""
    school_id: UUID
    school_name: str
    total_students: int
    invoices: List[Invoice] = []
    total_invoices: int = Field(0, description="Total de facturas")
    skip: int = Field(0, description="Número de facturas saltadas")
    limit: int = Field(10, description="Límite de facturas retornadas")


class StudentAccountStatus(AccountStatus):
    """Schema para estado de cuenta de un estudiante"""
    student_id: UUID
    student_name: str
    school_id: UUID
    school_name: str
    invoices: List[Invoice] = []
    total_invoices: int = Field(0, description="Total de facturas")
    skip: int = Field(0, description="Número de facturas saltadas")
    limit: int = Field(10, description="Límite de facturas retornadas")


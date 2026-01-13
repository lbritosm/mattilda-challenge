from pydantic import BaseModel
from typing import List
from decimal import Decimal
from app.schemas.invoice import Invoice


class AccountStatus(BaseModel):
    """Schema base para estado de cuenta"""
    total_invoiced: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    total_pending: Decimal = Decimal("0.00")


class SchoolAccountStatus(AccountStatus):
    """Schema para estado de cuenta de un colegio"""
    school_id: int
    school_name: str
    total_students: int
    invoices: List[Invoice] = []


class StudentAccountStatus(AccountStatus):
    """Schema para estado de cuenta de un estudiante"""
    student_id: int
    student_name: str
    school_id: int
    school_name: str
    invoices: List[Invoice] = []


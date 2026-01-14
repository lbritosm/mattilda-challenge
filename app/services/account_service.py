from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from decimal import Decimal
from uuid import UUID
from app.models.school import School
from app.models.student import Student
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.schemas.account import SchoolAccountStatus, StudentAccountStatus
from app.schemas.invoice import Invoice as InvoiceSchema


class AccountService:
    """Servicio para calcular estados de cuenta"""
    
    @staticmethod
    def get_school_account_status(db: Session, school_id: UUID) -> SchoolAccountStatus:
        """
        Calcula el estado de cuenta de un colegio.
        Incluye: total facturado, total pagado, total pendiente y listado de facturas.
        """
        # Validar que el colegio existe
        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            raise ValueError(f"School with id {school_id} does not exist")
        
        # Obtener todas las facturas del colegio
        invoices = db.query(Invoice).join(Student).filter(
            Student.school_id == school_id
        ).all()
        
        # Calcular totales
        total_invoiced = Decimal("0.00")
        total_paid = Decimal("0.00")
        
        invoice_schemas = []
        for invoice in invoices:
            total_invoiced += invoice.amount
            
            # Calcular pagos de esta factura
            payments = db.query(Payment).filter(Payment.invoice_id == invoice.id).all()
            invoice_paid = sum(payment.amount for payment in payments)
            total_paid += invoice_paid
            
            # Convertir a schema
            invoice_schemas.append(InvoiceSchema.model_validate(invoice))
        
        total_pending = total_invoiced - total_paid
        
        # Contar estudiantes activos
        total_students = db.query(Student).filter(
            Student.school_id == school_id,
            Student.is_active == True
        ).count()
        
        return SchoolAccountStatus(
            school_id=school.id,
            school_name=school.name,
            total_students=total_students,
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            total_pending=total_pending,
            invoices=invoice_schemas
        )
    
    @staticmethod
    def get_student_account_status(db: Session, student_id: UUID) -> StudentAccountStatus:
        """
        Calcula el estado de cuenta de un estudiante.
        Incluye: total facturado, total pagado, total pendiente y listado de facturas.
        """
        # Validar que el estudiante existe
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student with id {student_id} does not exist")
        
        # Obtener todas las facturas del estudiante
        invoices = db.query(Invoice).filter(Invoice.student_id == student_id).all()
        
        # Calcular totales
        total_invoiced = Decimal("0.00")
        total_paid = Decimal("0.00")
        
        invoice_schemas = []
        for invoice in invoices:
            total_invoiced += invoice.amount
            
            # Calcular pagos de esta factura
            payments = db.query(Payment).filter(Payment.invoice_id == invoice.id).all()
            invoice_paid = sum(payment.amount for payment in payments)
            total_paid += invoice_paid
            
            # Convertir a schema
            invoice_schemas.append(InvoiceSchema.model_validate(invoice))
        
        total_pending = total_invoiced - total_paid
        
        return StudentAccountStatus(
            student_id=student.id,
            student_name=student.full_name,
            school_id=student.school_id,
            school_name=student.school.name,
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            total_pending=total_pending,
            invoices=invoice_schemas
        )


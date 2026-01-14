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
    def get_school_account_status(
        db: Session, 
        school_id: UUID,
        skip: int = 0,
        limit: int = 10
    ) -> SchoolAccountStatus:
        """
        Calcula el estado de cuenta de un colegio.
        Incluye: total facturado, total pagado, total pendiente y listado de facturas paginado.
        """
        # Validar que el colegio existe
        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            raise ValueError(f"School with id {school_id} does not exist")
        
        # Query base para facturas del colegio
        invoices_query = db.query(Invoice).join(Student).filter(
            Student.school_id == school_id
        )
        
        # Contar total de facturas
        total_invoices = invoices_query.count()
        
        # Obtener facturas paginadas
        invoices = invoices_query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
        
        # Calcular totales (necesitamos todas las facturas para los totales)
        all_invoices = db.query(Invoice).join(Student).filter(
            Student.school_id == school_id
        ).all()
        
        total_invoiced = Decimal("0.00")
        total_paid = Decimal("0.00")
        
        for invoice in all_invoices:
            total_invoiced += invoice.amount
            
            # Calcular pagos de esta factura
            payments = db.query(Payment).filter(Payment.invoice_id == invoice.id).all()
            invoice_paid = sum(payment.amount for payment in payments)
            total_paid += invoice_paid
        
        total_pending = total_invoiced - total_paid
        
        # Convertir facturas paginadas a schemas
        invoice_schemas = [InvoiceSchema.model_validate(invoice) for invoice in invoices]
        
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
            invoices=invoice_schemas,
            total_invoices=total_invoices,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    def get_student_account_status(
        db: Session, 
        student_id: UUID,
        skip: int = 0,
        limit: int = 10
    ) -> StudentAccountStatus:
        """
        Calcula el estado de cuenta de un estudiante.
        Incluye: total facturado, total pagado, total pendiente y listado de facturas paginado.
        """
        # Validar que el estudiante existe
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student with id {student_id} does not exist")
        
        # Query base para facturas del estudiante
        invoices_query = db.query(Invoice).filter(Invoice.student_id == student_id)
        
        # Contar total de facturas
        total_invoices = invoices_query.count()
        
        # Obtener facturas paginadas
        invoices = invoices_query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
        
        # Calcular totales (necesitamos todas las facturas para los totales)
        all_invoices = db.query(Invoice).filter(Invoice.student_id == student_id).all()
        
        total_invoiced = Decimal("0.00")
        total_paid = Decimal("0.00")
        
        for invoice in all_invoices:
            total_invoiced += invoice.amount
            
            # Calcular pagos de esta factura
            payments = db.query(Payment).filter(Payment.invoice_id == invoice.id).all()
            invoice_paid = sum(payment.amount for payment in payments)
            total_paid += invoice_paid
        
        total_pending = total_invoiced - total_paid
        
        # Convertir facturas paginadas a schemas
        invoice_schemas = [InvoiceSchema.model_validate(invoice) for invoice in invoices]
        
        return StudentAccountStatus(
            student_id=student.id,
            student_name=student.full_name,
            school_id=student.school_id,
            school_name=student.school.name,
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            total_pending=total_pending,
            invoices=invoice_schemas,
            total_invoices=total_invoices,
            skip=skip,
            limit=limit
        )


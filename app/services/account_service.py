from sqlalchemy.orm import Session, joinedload
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
        Optimizado: usa school_id directamente en invoices y payments (sin joins).
        """
        # Validar que el colegio existe
        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            raise ValueError(f"School with id {school_id} does not exist")
        
        # Query base para facturas del colegio (ahora con school_id directo, sin join)
        invoices_query = db.query(Invoice).filter(Invoice.school_id == school_id)
        
        # Contar total de facturas
        total_invoices = invoices_query.count()
        
        # Obtener facturas paginadas con sus pagos
        invoices = invoices_query.options(
            joinedload(Invoice.payments)
        ).order_by(Invoice.due_date.desc(), Invoice.created_at.desc()).offset(skip).limit(limit).all()
        
        # Calcular totales usando agregaciones directas (evita doble conteo)
        # Total facturado: suma directa de invoices por school_id
        total_invoiced_result = db.query(func.sum(Invoice.total_amount)).filter(
            Invoice.school_id == school_id
        ).scalar()
        total_invoiced = Decimal(total_invoiced_result) if total_invoiced_result else Decimal("0.00")
        
        # Total pagado: suma directa de payments por school_id (evita joins y doble conteo)
        total_paid_result = db.query(func.sum(Payment.amount)).filter(
            Payment.school_id == school_id
        ).scalar()
        total_paid = Decimal(total_paid_result) if total_paid_result else Decimal("0.00")
        
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
        Optimizado: usa student_id directamente en invoices y payments (sin joins).
        """
        # Validar que el estudiante existe
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student with id {student_id} does not exist")
        
        # Query base para facturas del estudiante
        invoices_query = db.query(Invoice).filter(Invoice.student_id == student_id)
        
        # Contar total de facturas
        total_invoices = invoices_query.count()
        
        # Obtener facturas paginadas con sus pagos
        invoices = invoices_query.options(
            joinedload(Invoice.payments)
        ).order_by(Invoice.due_date.desc(), Invoice.created_at.desc()).offset(skip).limit(limit).all()
        
        # Calcular totales usando agregaciones directas (evita doble conteo)
        # Total facturado: suma directa de invoices por student_id
        total_invoiced_result = db.query(func.sum(Invoice.total_amount)).filter(
            Invoice.student_id == student_id
        ).scalar()
        total_invoiced = Decimal(total_invoiced_result) if total_invoiced_result else Decimal("0.00")
        
        # Total pagado: suma directa de payments por student_id (evita joins y doble conteo)
        total_paid_result = db.query(func.sum(Payment.amount)).filter(
            Payment.student_id == student_id
        ).scalar()
        total_paid = Decimal(total_paid_result) if total_paid_result else Decimal("0.00")
        
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


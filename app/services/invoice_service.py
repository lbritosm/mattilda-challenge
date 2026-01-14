from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from decimal import Decimal
from uuid import UUID
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from app.models.student import Student
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.schemas.payment import PaymentCreate


class InvoiceService:
    """Servicio para operaciones relacionadas con Invoices"""
    
    @staticmethod
    def get_invoice(db: Session, invoice_id: UUID) -> Optional[Invoice]:
        """Obtiene una factura por ID con sus pagos cargados"""
        return db.query(Invoice).options(
            joinedload(Invoice.payments)
        ).filter(Invoice.id == invoice_id).first()
    
    @staticmethod
    def get_invoices(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        student_id: Optional[UUID] = None,
        school_id: Optional[UUID] = None,
        status: Optional[InvoiceStatus] = None
    ) -> List[Invoice]:
        """Obtiene una lista de facturas con paginación y filtros, ordenadas por fecha de creación descendente.
        Incluye los pagos asociados a cada factura."""
        query = db.query(Invoice).options(
            joinedload(Invoice.payments)
        )
        
        if student_id is not None:
            query = query.filter(Invoice.student_id == student_id)
        
        if school_id is not None:
            query = query.join(Student).filter(Student.school_id == school_id)
        
        if status is not None:
            query = query.filter(Invoice.status == status)
        
        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_invoices(
        db: Session,
        student_id: Optional[UUID] = None,
        school_id: Optional[UUID] = None,
        status: Optional[InvoiceStatus] = None
    ) -> int:
        """Cuenta el total de facturas"""
        query = db.query(Invoice)
        
        if student_id is not None:
            query = query.filter(Invoice.student_id == student_id)
        
        if school_id is not None:
            query = query.join(Student).filter(Student.school_id == school_id)
        
        if status is not None:
            query = query.filter(Invoice.status == status)
        
        return query.count()
    
    @staticmethod
    def create_invoice(db: Session, invoice: InvoiceCreate) -> Invoice:
        """Crea una nueva factura"""
        # Validar que el estudiante existe
        student = db.query(Student).filter(Student.id == invoice.student_id).first()
        if not student:
            raise ValueError(f"Student with id {invoice.student_id} does not exist")
        
        # Validar que school_id coincida con student.school_id
        if invoice.school_id != student.school_id:
            raise ValueError(f"School ID {invoice.school_id} does not match student's school ID {student.school_id}")
        
        # Validar que el número de factura sea único por colegio
        existing = db.query(Invoice).filter(
            Invoice.school_id == invoice.school_id,
            Invoice.invoice_number == invoice.invoice_number
        ).first()
        if existing:
            raise ValueError(f"Invoice number {invoice.invoice_number} already exists for this school")
        
        db_invoice = Invoice(**invoice.model_dump())
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)
        
        return db_invoice
    
    @staticmethod
    def update_invoice(
        db: Session,
        invoice_id: UUID,
        invoice_update: InvoiceUpdate
    ) -> Optional[Invoice]:
        """Actualiza una factura existente"""
        db_invoice = InvoiceService.get_invoice(db, invoice_id)
        if not db_invoice:
            return None
        
        # Validar número de factura único por colegio si se está actualizando
        if invoice_update.invoice_number is not None:
            school_id = invoice_update.school_id if invoice_update.school_id else db_invoice.school_id
            existing = db.query(Invoice).filter(
                Invoice.school_id == school_id,
                Invoice.invoice_number == invoice_update.invoice_number,
                Invoice.id != invoice_id
            ).first()
            if existing:
                raise ValueError(f"Invoice number {invoice_update.invoice_number} already exists for this school")
        
        # Validar estudiante y school_id si se está actualizando
        if invoice_update.student_id is not None:
            student = db.query(Student).filter(Student.id == invoice_update.student_id).first()
            if not student:
                raise ValueError(f"Student with id {invoice_update.student_id} does not exist")
            
            # Si se actualiza school_id, validar que coincida con student.school_id
            school_id = invoice_update.school_id if invoice_update.school_id else db_invoice.school_id
            if school_id != student.school_id:
                raise ValueError(f"School ID {school_id} does not match student's school ID {student.school_id}")
        
        update_data = invoice_update.model_dump(exclude_unset=True)
        
        # Verificar si se actualiza total_amount (esto puede cambiar el estado)
        total_amount_changed = 'total_amount' in update_data
        
        for field, value in update_data.items():
            setattr(db_invoice, field, value)
        
        db.commit()
        db.refresh(db_invoice)
        
        # Solo actualizar el estado si cambió total_amount
        # (los pagos no cambian al actualizar otros campos de la factura)
        if total_amount_changed:
            InvoiceService._update_invoice_status(db, db_invoice)
        
        return db_invoice
    
    @staticmethod
    def delete_invoice(db: Session, invoice_id: UUID) -> bool:
        """Elimina una factura"""
        db_invoice = InvoiceService.get_invoice(db, invoice_id)
        if not db_invoice:
            return False
        
        db.delete(db_invoice)
        db.commit()
        return True
    
    @staticmethod
    def create_payment(db: Session, invoice_id: UUID, payment: PaymentCreate, invoice: Invoice) -> Payment:
        """
        Crea un nuevo pago para una factura.
        
        Los campos invoice_id, school_id y student_id se obtienen automáticamente de la factura.
        """
        # Validar que el monto del pago no exceda el monto pendiente
        total_paid = InvoiceService._get_total_paid(db, invoice_id)
        pending = invoice.total_amount - total_paid
        
        if payment.amount > pending:
            raise ValueError(
                f"Payment amount ({payment.amount}) exceeds pending amount ({pending})"
            )
        
        # Crear el pago con invoice_id, school_id y student_id de la factura
        payment_data = payment.model_dump()
        payment_data['invoice_id'] = invoice_id
        payment_data['school_id'] = invoice.school_id
        payment_data['student_id'] = invoice.student_id
        
        db_payment = Payment(**payment_data)
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        # Actualizar estado de la factura
        InvoiceService._update_invoice_status(db, invoice)
        
        return db_payment
    
    @staticmethod
    def get_payments(
        db: Session,
        invoice_id: UUID,
        skip: int = 0,
        limit: int = 10
    ) -> List[Payment]:
        """Obtiene una lista de pagos de una factura con paginación, ordenados por fecha de pago descendente"""
        # Validar que la factura existe
        invoice = InvoiceService.get_invoice(db, invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with id {invoice_id} does not exist")
        
        return db.query(Payment).filter(
            Payment.invoice_id == invoice_id
        ).order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_payments(db: Session, invoice_id: UUID) -> int:
        """Cuenta el total de pagos de una factura"""
        return db.query(Payment).filter(Payment.invoice_id == invoice_id).count()
    
    @staticmethod
    def _get_total_paid(db: Session, invoice_id: UUID) -> Decimal:
        """Calcula el total pagado de una factura (solo pagos asociados a la factura)"""
        result = db.query(func.sum(Payment.amount)).filter(
            Payment.invoice_id == invoice_id
        ).scalar()
        return Decimal(result) if result else Decimal("0.00")
    
    @staticmethod
    def _update_invoice_status(db: Session, invoice: Invoice):
        """Actualiza el estado de una factura basado en los pagos"""
        total_paid = InvoiceService._get_total_paid(db, invoice.id)
        
        if total_paid >= invoice.total_amount:
            invoice.status = InvoiceStatus.PAID
        elif total_paid > 0:
            invoice.status = InvoiceStatus.PARTIAL
        else:
            invoice.status = InvoiceStatus.PENDING
        
        db.commit()
        db.refresh(invoice)


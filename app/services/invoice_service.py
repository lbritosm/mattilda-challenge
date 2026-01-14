from sqlalchemy.orm import Session
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
        """Obtiene una factura por ID"""
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    @staticmethod
    def get_invoices(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        student_id: Optional[UUID] = None,
        school_id: Optional[UUID] = None,
        status: Optional[InvoiceStatus] = None
    ) -> List[Invoice]:
        """Obtiene una lista de facturas con paginación y filtros, ordenadas por fecha de creación descendente"""
        query = db.query(Invoice)
        
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
        
        # Validar que el número de factura sea único
        existing = db.query(Invoice).filter(
            Invoice.invoice_number == invoice.invoice_number
        ).first()
        if existing:
            raise ValueError(f"Invoice number {invoice.invoice_number} already exists")
        
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
        
        # Validar número de factura único si se está actualizando
        if invoice_update.invoice_number is not None:
            existing = db.query(Invoice).filter(
                Invoice.invoice_number == invoice_update.invoice_number,
                Invoice.id != invoice_id
            ).first()
            if existing:
                raise ValueError(f"Invoice number {invoice_update.invoice_number} already exists")
        
        # Validar estudiante si se está actualizando
        if invoice_update.student_id is not None:
            student = db.query(Student).filter(Student.id == invoice_update.student_id).first()
            if not student:
                raise ValueError(f"Student with id {invoice_update.student_id} does not exist")
        
        update_data = invoice_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_invoice, field, value)
        
        db.commit()
        db.refresh(db_invoice)
        
        # Actualizar estado de la factura basado en pagos
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
    def create_payment(db: Session, payment: PaymentCreate) -> Payment:
        """Crea un nuevo pago para una factura"""
        # Validar que la factura existe
        invoice = InvoiceService.get_invoice(db, payment.invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with id {payment.invoice_id} does not exist")
        
        # Validar que el monto del pago no exceda el monto pendiente
        total_paid = InvoiceService._get_total_paid(db, payment.invoice_id)
        pending = invoice.amount - total_paid
        
        if payment.amount > pending:
            raise ValueError(
                f"Payment amount ({payment.amount}) exceeds pending amount ({pending})"
            )
        
        db_payment = Payment(**payment.model_dump())
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        # Actualizar estado de la factura
        InvoiceService._update_invoice_status(db, invoice)
        
        return db_payment
    
    @staticmethod
    def _get_total_paid(db: Session, invoice_id: UUID) -> Decimal:
        """Calcula el total pagado de una factura"""
        result = db.query(func.sum(Payment.amount)).filter(
            Payment.invoice_id == invoice_id
        ).scalar()
        return Decimal(result) if result else Decimal("0.00")
    
    @staticmethod
    def _update_invoice_status(db: Session, invoice: Invoice):
        """Actualiza el estado de una factura basado en los pagos"""
        total_paid = InvoiceService._get_total_paid(db, invoice.id)
        
        if total_paid >= invoice.amount:
            invoice.status = InvoiceStatus.PAID
        elif total_paid > 0:
            invoice.status = InvoiceStatus.PARTIAL
        else:
            invoice.status = InvoiceStatus.PENDING
        
        db.commit()
        db.refresh(invoice)


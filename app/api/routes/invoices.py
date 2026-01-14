from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.schemas.invoice import Invoice, InvoiceCreate, InvoiceUpdate
from app.schemas.payment import Payment, PaymentCreate
from app.services.invoice_service import InvoiceService
from app.models.invoice import InvoiceStatus
from app.core.cache import invalidate_statements_for_invoice, invalidate_statements_for_payment
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=Invoice, status_code=201)
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva factura.
    """
    try:
        result = InvoiceService.create_invoice(db, invoice)
        # Invalidar cache de statements relacionados
        invalidate_statements_for_invoice(result.id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Invoice])
def get_invoices(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Número de registros a retornar"),
    student_id: Optional[UUID] = Query(None, description="Filtrar por ID de estudiante"),
    school_id: Optional[UUID] = Query(None, description="Filtrar por ID de colegio"),
    status: Optional[InvoiceStatus] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de facturas con paginación y filtros.
    """
    return InvoiceService.get_invoices(
        db,
        skip=skip,
        limit=limit,
        student_id=student_id,
        school_id=school_id,
        status=status
    )


@router.get("/count", response_model=dict)
def count_invoices(
    student_id: Optional[UUID] = Query(None, description="Filtrar por ID de estudiante"),
    school_id: Optional[UUID] = Query(None, description="Filtrar por ID de colegio"),
    status: Optional[InvoiceStatus] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Cuenta el total de facturas.
    """
    count = InvoiceService.count_invoices(
        db,
        student_id=student_id,
        school_id=school_id,
        status=status
    )
    return {"total": count}


@router.get("/{invoice_id}", response_model=Invoice)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene una factura por ID.
    """
    invoice = InvoiceService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.put("/{invoice_id}", response_model=Invoice)
def update_invoice(
    invoice_id: UUID,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una factura existente.
    """
    try:
        invoice = InvoiceService.update_invoice(db, invoice_id, invoice_update)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        # Invalidar cache de statements relacionados
        invalidate_statements_for_invoice(invoice_id, db)
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina una factura.
    """
    # Invalidar cache antes de eliminar (necesitamos los datos de la factura)
    invalidate_statements_for_invoice(invoice_id, db)
    
    success = InvoiceService.delete_invoice(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return None


@router.post("/{invoice_id}/payments", response_model=Payment, status_code=201)
def create_payment(
    invoice_id: UUID,
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo pago para una factura.
    """
    # Asegurar que el invoice_id del path coincida con el del body
    if payment.invoice_id != invoice_id:
        raise HTTPException(
            status_code=400,
            detail="Invoice ID in path does not match invoice_id in body"
        )
    
    try:
        result = InvoiceService.create_payment(db, payment)
        # Invalidar cache de statements relacionados
        invalidate_statements_for_payment(result.id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


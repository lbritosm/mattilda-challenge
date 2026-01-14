from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.schemas.invoice import Invoice, InvoiceCreate, InvoiceUpdate
from app.schemas.payment import Payment, PaymentCreate
from app.schemas.pagination import PaginatedResponse
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


@router.get("/", response_model=PaginatedResponse[Invoice])
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
    
    Retorna información de paginación incluyendo:
    - items: Lista de facturas de la página actual
    - total: Total de facturas disponibles
    - skip: Número de registros saltados
    - limit: Límite de registros por página
    - has_next: Indica si hay más páginas
    - has_previous: Indica si hay páginas anteriores
    """
    items = InvoiceService.get_invoices(
        db,
        skip=skip,
        limit=limit,
        student_id=student_id,
        school_id=school_id,
        status=status
    )
    total = InvoiceService.count_invoices(
        db,
        student_id=student_id,
        school_id=school_id,
        status=status
    )
    return PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)


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


@router.get("/{invoice_id}/payments", response_model=PaginatedResponse[Payment])
def get_invoice_payments(
    invoice_id: UUID,
    skip: int = Query(0, ge=0, description="Número de pagos a saltar"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Número de pagos a retornar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de pagos asociados a una factura con paginación.
    
    Retorna información de paginación incluyendo:
    - items: Lista de pagos de la página actual
    - total: Total de pagos disponibles
    - skip: Número de pagos saltados
    - limit: Límite de pagos por página
    - has_next: Indica si hay más páginas
    - has_previous: Indica si hay páginas anteriores
    
    Los pagos están ordenados por fecha de pago descendente (más recientes primero).
    """
    try:
        items = InvoiceService.get_payments(db, invoice_id, skip=skip, limit=limit)
        total = InvoiceService.count_payments(db, invoice_id)
        return PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{invoice_id}/payments", response_model=Payment, status_code=201)
def create_payment(
    invoice_id: UUID,
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo pago para una factura.
    
    El invoice_id del path se usa automáticamente. Los campos school_id y student_id
    se obtienen de la factura si no se proporcionan en el body.
    """
    # Si hay invoice_id en el body, debe coincidir con el path
    if payment.invoice_id is not None and payment.invoice_id != invoice_id:
        raise HTTPException(
            status_code=400,
            detail="Invoice ID in path does not match invoice_id in body"
        )
    
    # Obtener la factura para extraer school_id y student_id
    invoice = InvoiceService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Crear un nuevo objeto PaymentCreate con los valores correctos
    payment_data = payment.model_dump()
    payment_data['invoice_id'] = invoice_id
    payment_data['school_id'] = payment_data.get('school_id') or invoice.school_id
    payment_data['student_id'] = payment_data.get('student_id') or invoice.student_id
    
    from app.schemas.payment import PaymentCreate
    payment_with_ids = PaymentCreate(**payment_data)
    
    try:
        result = InvoiceService.create_payment(db, payment_with_ids)
        # Invalidar cache de statements relacionados
        invalidate_statements_for_payment(result.id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.schemas.school import School, SchoolCreate, SchoolUpdate
from app.schemas.account import SchoolAccountStatus
from app.schemas.pagination import PaginatedResponse
from app.services.school_service import SchoolService
from app.services.account_service import AccountService
from app.core.cache import get_cached_statement, set_cached_statement
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=School, status_code=201)
def create_school(
    school: SchoolCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo colegio.
    """
    try:
        return SchoolService.create_school(db, school)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedResponse[School])
def get_schools(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Número de registros a retornar"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de colegios con paginación.
    
    Retorna información de paginación incluyendo:
    - items: Lista de colegios de la página actual
    - total: Total de colegios disponibles
    - skip: Número de registros saltados
    - limit: Límite de registros por página
    - has_next: Indica si hay más páginas
    - has_previous: Indica si hay páginas anteriores
    """
    items = SchoolService.get_schools(db, skip=skip, limit=limit, is_active=is_active)
    total = SchoolService.count_schools(db, is_active=is_active)
    return PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)


@router.get("/count", response_model=dict)
def count_schools(
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """
    Cuenta el total de colegios.
    """
    count = SchoolService.count_schools(db, is_active=is_active)
    return {"total": count}


@router.get("/{school_id}", response_model=School)
def get_school(
    school_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene un colegio por ID.
    """
    school = SchoolService.get_school(db, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.put("/{school_id}", response_model=School)
def update_school(
    school_id: UUID,
    school_update: SchoolUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un colegio existente.
    """
    school = SchoolService.update_school(db, school_id, school_update)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.delete("/{school_id}", status_code=204)
def delete_school(
    school_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina un colegio.
    """
    success = SchoolService.delete_school(db, school_id)
    if not success:
        raise HTTPException(status_code=404, detail="School not found")
    return None


@router.get("/{school_id}/students/count", response_model=dict)
def count_school_students(
    school_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Cuenta el número de estudiantes activos de un colegio.
    """
    school = SchoolService.get_school(db, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    count = SchoolService.count_students(db, school_id)
    return {"school_id": str(school_id), "total_students": count}


@router.get("/{school_id}/statement", response_model=SchoolAccountStatus)
def get_school_statement(
    school_id: UUID,
    skip: int = Query(0, ge=0, description="Número de facturas a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Número de facturas a retornar (máximo 100)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de cuenta de un colegio.
    
    Incluye:
    - Total facturado
    - Total pagado
    - Total pendiente
    - Número de estudiantes
    - Listado de facturas paginado (ordenado por fecha de creación descendente)
    
    Los resultados se cachean por 60 segundos para mejorar el rendimiento.
    La paginación permite manejar grandes volúmenes de facturas eficientemente.
    """
    cache_key = f"school:{str(school_id)}:statement:skip:{skip}:limit:{limit}"
    
    # Intentar obtener de cache
    cached = get_cached_statement(cache_key)
    if cached:
        return SchoolAccountStatus(**cached)
    
    # Si no está en cache, obtener de la base de datos
    try:
        result = AccountService.get_school_account_status(db, school_id, skip=skip, limit=limit)
        # Guardar en cache (TTL: 60 segundos)
        set_cached_statement(cache_key, result, ttl=60)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


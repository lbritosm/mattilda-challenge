from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.schemas.student import Student, StudentCreate, StudentUpdate
from app.schemas.account import StudentAccountStatus
from app.schemas.pagination import PaginatedResponse
from app.services.student_service import StudentService
from app.services.account_service import AccountService
from app.core.cache import get_cached_statement, set_cached_statement
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=Student, status_code=201)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo estudiante.
    """
    try:
        return StudentService.create_student(db, student)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=PaginatedResponse[Student])
def get_students(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Número de registros a retornar"),
    school_id: Optional[UUID] = Query(None, description="Filtrar por ID de colegio"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de estudiantes con paginación y filtros.
    
    Retorna información de paginación incluyendo:
    - items: Lista de estudiantes de la página actual
    - total: Total de estudiantes disponibles
    - skip: Número de registros saltados
    - limit: Límite de registros por página
    - has_next: Indica si hay más páginas
    - has_previous: Indica si hay páginas anteriores
    """
    items = StudentService.get_students(
        db, 
        skip=skip, 
        limit=limit, 
        school_id=school_id, 
        is_active=is_active
    )
    total = StudentService.count_students(db, school_id=school_id, is_active=is_active)
    return PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)


@router.get("/count", response_model=dict)
def count_students(
    school_id: Optional[UUID] = Query(None, description="Filtrar por ID de colegio"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """
    Cuenta el total de estudiantes.
    """
    count = StudentService.count_students(db, school_id=school_id, is_active=is_active)
    return {"total": count}


@router.get("/{student_id}", response_model=Student)
def get_student(
    student_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene un estudiante por ID.
    """
    student = StudentService.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=Student)
def update_student(
    student_id: UUID,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un estudiante existente.
    """
    try:
        student = StudentService.update_student(db, student_id, student_update)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina un estudiante.
    """
    success = StudentService.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return None


@router.get("/{student_id}/statement", response_model=StudentAccountStatus)
def get_student_statement(
    student_id: UUID,
    skip: int = Query(0, ge=0, description="Número de facturas a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Número de facturas a retornar (máximo 100)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de cuenta de un estudiante.
    
    Incluye:
    - Total facturado
    - Total pagado
    - Total pendiente
    - Listado de facturas paginado (ordenado por fecha de creación descendente)
    
    Los resultados se cachean por 60 segundos para mejorar el rendimiento.
    La paginación permite manejar grandes volúmenes de facturas eficientemente.
    """
    cache_key = f"student:{str(student_id)}:statement:skip:{skip}:limit:{limit}"
    
    # Intentar obtener de cache
    cached = get_cached_statement(cache_key)
    if cached:
        return StudentAccountStatus(**cached)
    
    # Si no está en cache, obtener de la base de datos
    try:
        result = AccountService.get_student_account_status(db, student_id, skip=skip, limit=limit)
        # Guardar en cache (TTL: 60 segundos)
        set_cached_statement(cache_key, result, ttl=60)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


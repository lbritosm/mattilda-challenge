from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from app.core.database import get_db
from app.schemas.account import SchoolAccountStatus, StudentAccountStatus
from app.services.account_service import AccountService

router = APIRouter()


@router.get("/schools/{school_id}", response_model=SchoolAccountStatus)
def get_school_account_status(
    school_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de cuenta de un colegio.
    
    Incluye:
    - Total facturado
    - Total pagado
    - Total pendiente
    - Número de estudiantes
    - Listado de facturas relevantes
    """
    try:
        return AccountService.get_school_account_status(db, school_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}", response_model=StudentAccountStatus)
def get_student_account_status(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de cuenta de un estudiante.
    
    Incluye:
    - Total facturado
    - Total pagado
    - Total pendiente
    - Listado de facturas del estudiante
    """
    try:
        return AccountService.get_student_account_status(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}/debt/{school_id}", response_model=dict)
def get_student_debt(
    student_id: int,
    school_id: int,
    db: Session = Depends(get_db)
):
    """
    Calcula cuánto le debe un estudiante a un colegio.
    """
    try:
        debt = AccountService.get_student_debt(db, student_id, school_id)
        return {
            "student_id": student_id,
            "school_id": school_id,
            "debt": float(debt)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schools/{school_id}/total-debt", response_model=dict)
def get_school_total_debt(
    school_id: int,
    db: Session = Depends(get_db)
):
    """
    Calcula cuánto le deben todos los estudiantes a un colegio.
    """
    try:
        total_debt = AccountService.get_school_total_debt(db, school_id)
        return {
            "school_id": school_id,
            "total_debt": float(total_debt)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


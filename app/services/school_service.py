from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from app.models.school import School
from app.models.student import Student
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from app.schemas.school import SchoolCreate, SchoolUpdate


class SchoolService:
    """Servicio para operaciones relacionadas con Schools"""
    
    @staticmethod
    def get_school(db: Session, school_id: UUID) -> Optional[School]:
        """Obtiene un colegio por ID"""
        return db.query(School).filter(School.id == school_id).first()
    
    @staticmethod
    def get_schools(
        db: Session, 
        skip: int = 0, 
        limit: int = 10,
        is_active: Optional[bool] = None
    ) -> List[School]:
        """Obtiene una lista de colegios con paginación, ordenados por fecha de creación descendente"""
        query = db.query(School)
        
        if is_active is not None:
            query = query.filter(School.is_active == is_active)
        
        return query.order_by(School.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_schools(db: Session, is_active: Optional[bool] = None) -> int:
        """Cuenta el total de colegios"""
        query = db.query(School)
        
        if is_active is not None:
            query = query.filter(School.is_active == is_active)
        
        return query.count()
    
    @staticmethod
    def create_school(db: Session, school: SchoolCreate) -> School:
        """Crea un nuevo colegio"""
        db_school = School(**school.model_dump())
        db.add(db_school)
        db.commit()
        db.refresh(db_school)
        return db_school
    
    @staticmethod
    def update_school(
        db: Session, 
        school_id: UUID, 
        school_update: SchoolUpdate
    ) -> Optional[School]:
        """Actualiza un colegio existente"""
        db_school = SchoolService.get_school(db, school_id)
        if not db_school:
            return None
        
        update_data = school_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_school, field, value)
        
        db.commit()
        db.refresh(db_school)
        return db_school
    
    @staticmethod
    def delete_school(db: Session, school_id: UUID) -> bool:
        """Elimina un colegio"""
        db_school = SchoolService.get_school(db, school_id)
        if not db_school:
            return False
        
        db.delete(db_school)
        db.commit()
        return True
    
    @staticmethod
    def count_students(db: Session, school_id: UUID) -> int:
        """Cuenta el número de estudiantes activos de un colegio"""
        return db.query(Student).filter(
            Student.school_id == school_id,
            Student.is_active == True
        ).count()


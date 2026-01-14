from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from decimal import Decimal
from uuid import UUID
from app.models.student import Student
from app.models.school import School
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.schemas.student import StudentCreate, StudentUpdate
from app.core.cache import invalidate_student_statement, invalidate_school_statement


class StudentService:
    """Servicio para operaciones relacionadas con Students"""
    
    @staticmethod
    def get_student(db: Session, student_id: UUID) -> Optional[Student]:
        """Obtiene un estudiante por ID"""
        return db.query(Student).filter(Student.id == student_id).first()
    
    @staticmethod
    def get_students(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        school_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> List[Student]:
        """Obtiene una lista de estudiantes con paginación y filtros, ordenados por fecha de creación descendente"""
        query = db.query(Student)
        
        if school_id is not None:
            query = query.filter(Student.school_id == school_id)
        
        if is_active is not None:
            query = query.filter(Student.is_active == is_active)
        
        return query.order_by(Student.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_students(
        db: Session,
        school_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Cuenta el total de estudiantes"""
        query = db.query(Student)
        
        if school_id is not None:
            query = query.filter(Student.school_id == school_id)
        
        if is_active is not None:
            query = query.filter(Student.is_active == is_active)
        
        return query.count()
    
    @staticmethod
    def create_student(db: Session, student: StudentCreate) -> Student:
        """Crea un nuevo estudiante"""
        # Validar que el colegio existe
        school = db.query(School).filter(School.id == student.school_id).first()
        if not school:
            raise ValueError(f"School with id {student.school_id} does not exist")
        
        db_student = Student(**student.model_dump())
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    
    @staticmethod
    def update_student(
        db: Session,
        student_id: UUID,
        student_update: StudentUpdate
    ) -> Optional[Student]:
        """
        Actualiza un estudiante existente.
        
        Si se intenta cambiar el school_id, se valida que el estudiante no tenga deuda
        con el colegio actual. Si tiene deuda, se lanza un error.
        """
        db_student = StudentService.get_student(db, student_id)
        if not db_student:
            return None
        
        # Validar que el colegio existe si se está actualizando
        old_school_id = db_student.school_id
        new_school_id = None
        
        if student_update.school_id is not None:
            school = db.query(School).filter(School.id == student_update.school_id).first()
            if not school:
                raise ValueError(f"School with id {student_update.school_id} does not exist")
            new_school_id = student_update.school_id
        
        # Detectar si se intenta cambiar el school_id
        school_id_changed = new_school_id is not None and new_school_id != old_school_id
        
        # Si se intenta cambiar el school_id, validar que no tenga deuda
        if school_id_changed:
            # Calcular total facturado
            total_invoiced_result = db.query(func.sum(Invoice.total_amount)).filter(
                Invoice.student_id == student_id
            ).scalar()
            total_invoiced = Decimal(total_invoiced_result) if total_invoiced_result else Decimal("0.00")
            
            # Calcular total pagado
            total_paid_result = db.query(func.sum(Payment.amount)).filter(
                Payment.student_id == student_id
            ).scalar()
            total_paid = Decimal(total_paid_result) if total_paid_result else Decimal("0.00")
            
            # Calcular deuda
            debt = total_invoiced - total_paid
            
            # Si hay deuda, no permitir el cambio
            if debt > 0:
                raise ValueError(
                    f"No se puede cambiar el colegio del estudiante. "
                    f"Tiene una deuda pendiente de ${debt:.2f} con el colegio actual."
                )
            
            # Invalidar cache de ambos colegios (anterior y nuevo) y del estudiante
            invalidate_school_statement(old_school_id)
            invalidate_school_statement(new_school_id)
            invalidate_student_statement(student_id)
        
        update_data = student_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_student, field, value)
        
        db.commit()
        db.refresh(db_student)
        return db_student
    
    @staticmethod
    def delete_student(db: Session, student_id: UUID) -> bool:
        """Elimina un estudiante"""
        db_student = StudentService.get_student(db, student_id)
        if not db_student:
            return False
        
        db.delete(db_student)
        db.commit()
        return True


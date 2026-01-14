from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.student import Student
from app.models.school import School
from app.schemas.student import StudentCreate, StudentUpdate


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
        """Obtiene una lista de estudiantes con paginación y filtros"""
        query = db.query(Student)
        
        if school_id is not None:
            query = query.filter(Student.school_id == school_id)
        
        if is_active is not None:
            query = query.filter(Student.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
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
        """Actualiza un estudiante existente"""
        db_student = StudentService.get_student(db, student_id)
        if not db_student:
            return None
        
        # Validar que el colegio existe si se está actualizando
        if student_update.school_id is not None:
            school = db.query(School).filter(School.id == student_update.school_id).first()
            if not school:
                raise ValueError(f"School with id {student_update.school_id} does not exist")
        
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


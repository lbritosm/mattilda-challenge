from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Student(Base):
    """Modelo de Estudiante"""
    
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True, unique=True, index=True)
    date_of_birth = Column(Date, nullable=True)
    student_code = Column(String(50), nullable=True, unique=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    school = relationship("School", back_populates="students")
    invoices = relationship("Invoice", back_populates="student", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        """Retorna el nombre completo del estudiante"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.full_name}', school_id={self.school_id})>"


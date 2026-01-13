from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class School(Base):
    """Modelo de Colegio"""
    
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    students = relationship("Student", back_populates="school", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<School(id={self.id}, name='{self.name}')>"


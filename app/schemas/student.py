from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date


class StudentBase(BaseModel):
    """Schema base para Student"""
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre del estudiante")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellido del estudiante")
    email: Optional[EmailStr] = Field(None, description="Email del estudiante")
    date_of_birth: Optional[date] = Field(None, description="Fecha de nacimiento")
    student_code: Optional[str] = Field(None, max_length=50, description="Código único del estudiante")
    school_id: int = Field(..., description="ID del colegio al que pertenece")
    is_active: bool = Field(True, description="Indica si el estudiante está activo")


class StudentCreate(StudentBase):
    """Schema para crear un Student"""
    pass


class StudentUpdate(BaseModel):
    """Schema para actualizar un Student"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    student_code: Optional[str] = Field(None, max_length=50)
    school_id: Optional[int] = None
    is_active: Optional[bool] = None


class Student(StudentBase):
    """Schema para retornar un Student"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


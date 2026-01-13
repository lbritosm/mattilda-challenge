from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class SchoolBase(BaseModel):
    """Schema base para School"""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre del colegio")
    address: Optional[str] = Field(None, max_length=500, description="Dirección del colegio")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono del colegio")
    email: Optional[EmailStr] = Field(None, description="Email del colegio")
    is_active: bool = Field(True, description="Indica si el colegio está activo")


class SchoolCreate(SchoolBase):
    """Schema para crear un School"""
    pass


class SchoolUpdate(BaseModel):
    """Schema para actualizar un School"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class School(SchoolBase):
    """Schema para retornar un School"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


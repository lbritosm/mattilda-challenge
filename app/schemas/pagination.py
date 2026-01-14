from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico para respuestas paginadas"""
    items: List[T] = Field(..., description="Lista de items de la página actual")
    total: int = Field(..., description="Total de items disponibles")
    skip: int = Field(0, description="Número de items saltados")
    limit: int = Field(10, description="Límite de items por página")
    has_next: bool = Field(..., description="Indica si hay más páginas disponibles")
    has_previous: bool = Field(..., description="Indica si hay páginas anteriores")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int = 0,
        limit: int = 10
    ) -> "PaginatedResponse[T]":
        """Método helper para crear una respuesta paginada"""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
            has_previous=skip > 0
        )


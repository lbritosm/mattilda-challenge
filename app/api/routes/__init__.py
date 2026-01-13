from fastapi import APIRouter
from app.api.routes import schools, students, invoices

api_router = APIRouter()

api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])


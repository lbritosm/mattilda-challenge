from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import get_db, init_db
from app.api.routes import api_router
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Mattilda API",
    description="""
    API para gestión de colegios, estudiantes y facturación.
    
    ## Características
    
    * **CRUD de Colegios**: Gestión completa de colegios
    * **CRUD de Estudiantes**: Gestión de estudiantes asociados a colegios
    * **CRUD de Facturas**: Gestión de facturas y pagos
    * **Estados de Cuenta**: Consulta de estados de cuenta de colegios y estudiantes
    
    ## Preguntas que responde
    
    * ¿Cuánto le debe un estudiante a un colegio?
    * ¿Cuánto le deben todos los estudiantes a un colegio?
    * ¿Cuántos alumnos tiene un colegio?
    * ¿Cuál es el estado de cuenta de un colegio o de un estudiante?
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al arrancar la aplicación"""
    logger.info("Inicializando aplicación...")
    try:
        init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")


@app.get("/", tags=["root"])
def root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a la API de Mattilda",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    Verifica el estado de la aplicación y la conexión a la base de datos.
    """
    try:
        # Verificar conexión a la base de datos
        db = next(get_db())
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "database": "connected",
                "service": "mattilda-api"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "service": "mattilda-api",
                "error": str(e)
            }
        )


@app.get("/metrics", tags=["metrics"])
def metrics():
    """
    Endpoint básico de métricas.
    En producción, se podría integrar con Prometheus u otro sistema de métricas.
    """
    try:
        db = next(get_db())
        # Métricas básicas
        from app.models.school import School
        from app.models.student import Student
        from app.models.invoice import Invoice
        
        total_schools = db.query(School).count()
        total_students = db.query(Student).count()
        total_invoices = db.query(Invoice).count()
        
        db.close()
        
        return {
            "total_schools": total_schools,
            "total_students": total_students,
            "total_invoices": total_invoices
        }
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


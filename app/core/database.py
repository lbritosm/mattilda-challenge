from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener la sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa las tablas de la base de datos.
    Ejecuta las migraciones de Alembic automáticamente.
    """
    # Ejecutar migraciones de Alembic
    try:
        import os
        from alembic.config import Config
        from alembic import command
        
        # Obtener la ruta del directorio raíz del proyecto
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        alembic_ini_path = os.path.join(base_dir, "alembic.ini")
        
        if os.path.exists(alembic_ini_path):
            alembic_cfg = Config(alembic_ini_path)
            # Usar la URL de la base de datos de la configuración en lugar de la del alembic.ini
            alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
            command.upgrade(alembic_cfg, "head")
            logger = logging.getLogger(__name__)
            logger.info("Migraciones de Alembic ejecutadas correctamente")
        else:
            raise FileNotFoundError(f"alembic.ini no encontrado en {alembic_ini_path}")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"No se pudieron ejecutar migraciones de Alembic: {e}")
        # Fallback: crear tablas si no existen (solo para desarrollo)
        logger.info("Usando create_all como fallback...")
        Base.metadata.create_all(bind=engine)


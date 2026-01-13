from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    DATABASE_URL: str = "postgresql://mattilda:mattilda123@localhost:5432/mattilda_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Configuración de paginación
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # Configuración de cache
    CACHE_TTL: int = 300  # 5 minutos
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


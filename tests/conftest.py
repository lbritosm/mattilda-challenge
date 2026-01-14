import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app

# Base de datos de prueba
# Desde el contenedor Docker, usar "db" como hostname
TEST_DB_NAME = "mattilda_test_db"
SQLALCHEMY_DATABASE_URL = f"postgresql://mattilda:mattilda123@db:5432/{TEST_DB_NAME}"
# URL para conectar a postgres (base de datos por defecto) para crear la BD de tests
ADMIN_DATABASE_URL = "postgresql://mattilda:mattilda123@db:5432/postgres"

# Crear la base de datos de tests si no existe
admin_engine = create_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
try:
    with admin_engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{TEST_DB_NAME}'"))
        if not result.fetchone():
            conn.execute(text(f'CREATE DATABASE {TEST_DB_NAME}'))
except Exception as e:
    # Si falla, asumir que la BD ya existe o que no tenemos permisos
    pass
finally:
    admin_engine.dispose()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Crea una nueva base de datos de prueba para cada test"""
    # Limpiar todas las tablas antes de crear
    Base.metadata.drop_all(bind=engine)
    # Crear todas las tablas con el esquema actualizado
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpiar después del test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Crea un cliente de prueba"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


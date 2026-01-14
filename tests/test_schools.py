import pytest
import uuid
from app.models.school import School
from app.schemas.school import SchoolCreate


def test_create_school(client, db):
    """Test para crear un colegio"""
    school_data = {
        "name": "Colegio Test",
        "address": "Calle Test 123",
        "phone": "123456789",
        "email": "test@colegio.com",
        "is_active": True
    }
    
    response = client.post("/api/v1/schools/", json=school_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == school_data["name"]
    assert data["id"] is not None
    # Verificar que el ID es un UUID válido
    import uuid
    try:
        uuid.UUID(data["id"])
    except ValueError:
        pytest.fail(f"ID no es un UUID válido: {data['id']}")


def test_get_school(client, db):
    """Test para obtener un colegio"""
    # Crear un colegio primero
    school_data = {
        "name": "Colegio Test",
        "is_active": True
    }
    create_response = client.post("/api/v1/schools/", json=school_data)
    school_id = create_response.json()["id"]
    
    # Obtener el colegio
    response = client.get(f"/api/v1/schools/{school_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == school_data["name"]


def test_get_schools(client, db):
    """Test para listar colegios con paginación"""
    # Crear algunos colegios
    for i in range(5):
        school_data = {
            "name": f"Colegio {i}",
            "is_active": True
        }
        client.post("/api/v1/schools/", json=school_data)
    
    # Obtener lista
    response = client.get("/api/v1/schools/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    # Verificar estructura de respuesta paginada
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "has_next" in data
    assert "has_previous" in data
    assert len(data["items"]) == 5
    assert data["total"] == 5
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert data["has_next"] == False
    assert data["has_previous"] == False


def test_update_school(client, db):
    """Test para actualizar un colegio"""
    # Crear un colegio
    school_data = {
        "name": "Colegio Original",
        "is_active": True
    }
    create_response = client.post("/api/v1/schools/", json=school_data)
    school_id = create_response.json()["id"]
    
    # Actualizar
    update_data = {"name": "Colegio Actualizado"}
    response = client.put(f"/api/v1/schools/{school_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Colegio Actualizado"


def test_delete_school(client, db):
    """Test para eliminar un colegio"""
    # Crear un colegio
    school_data = {
        "name": "Colegio a Eliminar",
        "is_active": True
    }
    create_response = client.post("/api/v1/schools/", json=school_data)
    school_id = create_response.json()["id"]
    
    # Eliminar
    response = client.delete(f"/api/v1/schools/{school_id}")
    assert response.status_code == 204
    
    # Verificar que no existe
    get_response = client.get(f"/api/v1/schools/{school_id}")
    assert get_response.status_code == 404


def test_invalid_uuid_format(client, db):
    """Test para verificar que se rechazan UUIDs inválidos"""
    # Intentar obtener con un ID inválido
    response = client.get("/api/v1/schools/invalid-uuid")
    assert response.status_code == 422  # Unprocessable Entity - error de validación


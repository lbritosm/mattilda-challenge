import pytest
from app.models.student import Student


def test_create_student(client, db):
    """Test para crear un estudiante"""
    # Primero crear un colegio
    school_data = {"name": "Colegio Test", "is_active": True}
    school_response = client.post("/api/v1/schools/", json=school_data)
    school_id = school_response.json()["id"]
    
    # Crear estudiante
    student_data = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan@test.com",
        "school_id": school_id,
        "is_active": True
    }
    
    response = client.post("/api/v1/students/", json=student_data)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == student_data["first_name"]
    assert data["school_id"] == school_id


def test_get_student(client, db):
    """Test para obtener un estudiante"""
    # Crear colegio y estudiante
    school_data = {"name": "Colegio Test", "is_active": True}
    school_response = client.post("/api/v1/schools/", json=school_data)
    school_id = school_response.json()["id"]
    
    student_data = {
        "first_name": "María",
        "last_name": "García",
        "school_id": school_id,
        "is_active": True
    }
    create_response = client.post("/api/v1/students/", json=student_data)
    student_id = create_response.json()["id"]
    
    # Obtener estudiante
    response = client.get(f"/api/v1/students/{student_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == student_data["first_name"]


def test_get_students_by_school(client, db):
    """Test para filtrar estudiantes por colegio"""
    # Crear colegio
    school_data = {"name": "Colegio Test", "is_active": True}
    school_response = client.post("/api/v1/schools/", json=school_data)
    school_id = school_response.json()["id"]
    
    # Crear estudiantes
    for i in range(3):
        student_data = {
            "first_name": f"Estudiante {i}",
            "last_name": "Test",
            "school_id": school_id,
            "is_active": True
        }
        client.post("/api/v1/students/", json=student_data)
    
    # Obtener estudiantes del colegio
    response = client.get(f"/api/v1/students/?school_id={school_id}")
    assert response.status_code == 200
    data = response.json()
    # Verificar estructura de respuesta paginada
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 3
    assert data["total"] == 3


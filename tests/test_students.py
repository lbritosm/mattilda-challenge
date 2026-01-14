import pytest
from datetime import date, timedelta
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
    assert "skip" in data
    assert "limit" in data
    assert "has_next" in data
    assert "has_previous" in data
    assert len(data["items"]) == 3
    assert data["total"] == 3


def test_update_student_school_id_with_debt(client, db):
    """Test que no se puede cambiar school_id si el estudiante tiene deuda"""
    # Crear dos colegios
    school1_data = {"name": "Colegio 1", "is_active": True}
    school1_response = client.post("/api/v1/schools/", json=school1_data)
    school1_id = school1_response.json()["id"]
    
    school2_data = {"name": "Colegio 2", "is_active": True}
    school2_response = client.post("/api/v1/schools/", json=school2_data)
    school2_id = school2_response.json()["id"]
    
    # Crear estudiante en colegio 1
    student_data = {
        "first_name": "Estudiante",
        "last_name": "Con Deuda",
        "school_id": school1_id,
        "is_active": True
    }
    student_response = client.post("/api/v1/students/", json=student_data)
    student_id = student_response.json()["id"]
    
    # Crear factura (genera deuda)
    due_date = (date.today() + timedelta(days=30)).isoformat()
    issue_date = date.today().isoformat()
    invoice_data = {
        "invoice_number": "INV-DEBT-TEST",
        "school_id": school1_id,
        "student_id": student_id,
        "total_amount": "1000.00",
        "issue_date": issue_date,
        "due_date": due_date,
        "status": "pending"
    }
    client.post("/api/v1/invoices/", json=invoice_data)
    
    # Intentar cambiar de colegio (debe fallar)
    update_data = {"school_id": school2_id}
    response = client.put(f"/api/v1/students/{student_id}", json=update_data)
    assert response.status_code == 400
    assert "deuda" in response.json()["detail"].lower() or "debt" in response.json()["detail"].lower()


def test_update_student_school_id_without_debt(client, db):
    """Test que se puede cambiar school_id si el estudiante no tiene deuda"""
    # Crear dos colegios
    school1_data = {"name": "Colegio 1", "is_active": True}
    school1_response = client.post("/api/v1/schools/", json=school1_data)
    school1_id = school1_response.json()["id"]
    
    school2_data = {"name": "Colegio 2", "is_active": True}
    school2_response = client.post("/api/v1/schools/", json=school2_data)
    school2_id = school2_response.json()["id"]
    
    # Crear estudiante en colegio 1
    student_data = {
        "first_name": "Estudiante",
        "last_name": "Sin Deuda",
        "school_id": school1_id,
        "is_active": True
    }
    student_response = client.post("/api/v1/students/", json=student_data)
    student_id = student_response.json()["id"]
    
    # Crear factura y pagarla completamente (sin deuda)
    due_date = (date.today() + timedelta(days=30)).isoformat()
    issue_date = date.today().isoformat()
    invoice_data = {
        "invoice_number": "INV-PAID-TEST",
        "school_id": school1_id,
        "student_id": student_id,
        "total_amount": "1000.00",
        "issue_date": issue_date,
        "due_date": due_date,
        "status": "pending"
    }
    invoice_response = client.post("/api/v1/invoices/", json=invoice_data)
    invoice_id = invoice_response.json()["id"]
    
    # Pagar la factura completamente
    payment_data = {"amount": "1000.00"}
    client.post(f"/api/v1/invoices/{invoice_id}/payments", json=payment_data)
    
    # Cambiar de colegio (debe funcionar)
    update_data = {"school_id": school2_id}
    response = client.put(f"/api/v1/students/{student_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["school_id"] == school2_id


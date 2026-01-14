import pytest
from datetime import datetime, timedelta


def test_school_account_status(client, db):
    """Test para obtener estado de cuenta de un colegio"""
    # Crear colegio
    school_data = {"name": "Colegio Test", "is_active": True}
    school_response = client.post("/api/v1/schools/", json=school_data)
    school_id = school_response.json()["id"]
    
    # Crear estudiantes
    student_ids = []
    for i in range(2):
        student_data = {
            "first_name": f"Estudiante {i}",
            "last_name": "Test",
            "school_id": school_id,
            "is_active": True
        }
        student_response = client.post("/api/v1/students/", json=student_data)
        student_ids.append(student_response.json()["id"])
    
    # Crear facturas para cada estudiante
    due_date = (datetime.now() + timedelta(days=30)).isoformat()
    for i, student_id in enumerate(student_ids):
        invoice_data = {
            "invoice_number": f"INV-SCHOOL-{i}",
            "student_id": student_id,
            "amount": "500.00",
            "due_date": due_date,
            "status": "pending"
        }
        client.post("/api/v1/invoices/", json=invoice_data)
    
    # Obtener estado de cuenta del colegio
    response = client.get(f"/api/v1/schools/{school_id}/statement")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_invoiced"]) == 1000.00
    assert data["total_students"] == 2
    # Verificar campos de paginación
    assert "total_invoices" in data
    assert "skip" in data
    assert "limit" in data
    assert "invoices" in data
    assert data["total_invoices"] == 2
    assert len(data["invoices"]) <= data["limit"]


def test_student_account_status(client, db):
    """Test para obtener estado de cuenta de un estudiante"""
    # Crear colegio y estudiante
    school_data = {"name": "Colegio Test", "is_active": True}
    school_response = client.post("/api/v1/schools/", json=school_data)
    school_id = school_response.json()["id"]
    
    student_data = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "school_id": school_id,
        "is_active": True
    }
    student_response = client.post("/api/v1/students/", json=student_data)
    student_id = student_response.json()["id"]
    
    # Crear factura
    due_date = (datetime.now() + timedelta(days=30)).isoformat()
    invoice_data = {
        "invoice_number": "INV-DEBT-001",
        "student_id": student_id,
        "amount": "1000.00",
        "due_date": due_date,
        "status": "pending"
    }
    client.post("/api/v1/invoices/", json=invoice_data)
    
    # Obtener estado de cuenta del estudiante
    response = client.get(f"/api/v1/students/{student_id}/statement")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_invoiced"]) == 1000.00
    assert float(data["total_pending"]) == 1000.00
    # Verificar campos de paginación
    assert "total_invoices" in data
    assert "skip" in data
    assert "limit" in data
    assert "invoices" in data
    assert data["total_invoices"] == 1
    assert len(data["invoices"]) <= data["limit"]


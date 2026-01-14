import pytest
from datetime import datetime, timedelta
from decimal import Decimal


def test_create_invoice(client, db):
    """Test para crear una factura"""
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
        "invoice_number": "INV-001",
        "student_id": student_id,
        "amount": "1000.00",
        "description": "Mensualidad",
        "due_date": due_date,
        "status": "pending"
    }
    
    response = client.post("/api/v1/invoices/", json=invoice_data)
    assert response.status_code == 201
    data = response.json()
    assert data["invoice_number"] == invoice_data["invoice_number"]
    assert float(data["amount"]) == 1000.00


def test_create_payment(client, db):
    """Test para crear un pago"""
    # Crear colegio, estudiante y factura
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
    
    due_date = (datetime.now() + timedelta(days=30)).isoformat()
    invoice_data = {
        "invoice_number": "INV-002",
        "student_id": student_id,
        "amount": "500.00",
        "due_date": due_date,
        "status": "pending"
    }
    invoice_response = client.post("/api/v1/invoices/", json=invoice_data)
    invoice_id = invoice_response.json()["id"]
    
    # Crear pago
    payment_data = {
        "invoice_id": invoice_id,
        "amount": "300.00",
        "payment_method": "cash",
        "payment_reference": "REF-001"
    }
    
    response = client.post(f"/api/v1/invoices/{invoice_id}/payments", json=payment_data)
    assert response.status_code == 201
    data = response.json()
    assert float(data["amount"]) == 300.00


def test_account_status(client, db):
    """Test para obtener estado de cuenta de estudiante"""
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
    
    # Crear facturas
    due_date = (datetime.now() + timedelta(days=30)).isoformat()
    for i in range(2):
        invoice_data = {
            "invoice_number": f"INV-{i+10}",
            "student_id": student_id,
            "amount": "1000.00",
            "due_date": due_date,
            "status": "pending"
        }
        client.post("/api/v1/invoices/", json=invoice_data)
    
    # Obtener estado de cuenta
    response = client.get(f"/api/v1/students/{student_id}/statement")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_invoiced"]) == 2000.00
    assert float(data["total_pending"]) == 2000.00
    # Verificar campos de paginación
    assert "total_invoices" in data
    assert data["total_invoices"] == 2
    assert len(data["invoices"]) <= data["limit"]


def test_get_invoices_pagination(client, db):
    """Test para listar facturas con paginación"""
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
    
    # Crear múltiples facturas
    due_date = (datetime.now() + timedelta(days=30)).isoformat()
    for i in range(5):
        invoice_data = {
            "invoice_number": f"INV-PAG-{i}",
            "student_id": student_id,
            "amount": "100.00",
            "due_date": due_date,
            "status": "pending"
        }
        client.post("/api/v1/invoices/", json=invoice_data)
    
    # Obtener lista paginada
    response = client.get(f"/api/v1/invoices/?student_id={student_id}&skip=0&limit=3")
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
    assert data["total"] == 5
    assert data["has_next"] == True
    assert data["has_previous"] == False


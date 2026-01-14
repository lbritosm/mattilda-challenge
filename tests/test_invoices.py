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
    # Verificar que la factura incluye la lista de pagos (inicialmente vacía)
    assert "payments" in data
    assert isinstance(data["payments"], list)
    assert len(data["payments"]) == 0


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
    
    # Verificar que al obtener la factura, incluye el pago
    invoice_response = client.get(f"/api/v1/invoices/{invoice_id}")
    assert invoice_response.status_code == 200
    invoice_data = invoice_response.json()
    assert "payments" in invoice_data
    assert len(invoice_data["payments"]) == 1
    assert float(invoice_data["payments"][0]["amount"]) == 300.00
    
    # Verificar el endpoint GET para listar pagos de una factura
    payments_response = client.get(f"/api/v1/invoices/{invoice_id}/payments")
    assert payments_response.status_code == 200
    payments_data = payments_response.json()
    # Verificar estructura de respuesta paginada
    assert "items" in payments_data
    assert "total" in payments_data
    assert "skip" in payments_data
    assert "limit" in payments_data
    assert "has_next" in payments_data
    assert "has_previous" in payments_data
    assert len(payments_data["items"]) == 1
    assert payments_data["total"] == 1
    assert float(payments_data["items"][0]["amount"]) == 300.00


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


def test_get_invoice_payments(client, db):
    """Test para listar pagos de una factura con paginación"""
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
        "invoice_number": "INV-PAYMENTS-001",
        "student_id": student_id,
        "amount": "1000.00",
        "due_date": due_date,
        "status": "pending"
    }
    invoice_response = client.post("/api/v1/invoices/", json=invoice_data)
    invoice_id = invoice_response.json()["id"]
    
    # Crear múltiples pagos
    for i in range(3):
        payment_data = {
            "invoice_id": invoice_id,
            "amount": "100.00",
            "payment_method": "cash",
            "payment_reference": f"REF-{i}"
        }
        client.post(f"/api/v1/invoices/{invoice_id}/payments", json=payment_data)
    
    # Obtener lista de pagos
    response = client.get(f"/api/v1/invoices/{invoice_id}/payments?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    # Verificar estructura de respuesta paginada
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["has_next"] == False
    assert data["has_previous"] == False
    
    # Verificar que los pagos están ordenados por fecha descendente
    payment_dates = [item["payment_date"] for item in data["items"]]
    assert payment_dates == sorted(payment_dates, reverse=True)
    
    # Test con paginación
    response_page = client.get(f"/api/v1/invoices/{invoice_id}/payments?skip=0&limit=2")
    assert response_page.status_code == 200
    data_page = response_page.json()
    assert len(data_page["items"]) == 2
    assert data_page["total"] == 3
    assert data_page["has_next"] == True
    assert data_page["has_previous"] == False


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


"""
Script para cargar datos de ejemplo en la base de datos.
Ejecutar con: python scripts/load_sample_data.py
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.school import School
from app.models.student import Student
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from decimal import Decimal


def load_sample_data():
    """Carga datos de ejemplo en la base de datos"""
    # Inicializar base de datos
    init_db()
    
    db: Session = SessionLocal()
    
    try:
        print("Cargando datos de ejemplo...")
        
        # Crear colegios
        school1 = School(
            name="Escuela Primaria de Springfield",
            address="Evergreen Terrace 742",
            phone="555-0199",
            email="info@springfield-elementary.edu",
            is_active=True
        )
        school2 = School(
            name="Instituto Springfield",
            address="Main Street 123",
            phone="555-0200",
            email="contacto@springfield-institute.edu",
            is_active=True
        )
        db.add(school1)
        db.add(school2)
        db.commit()
        db.refresh(school1)
        db.refresh(school2)
        print(f"✓ Creados 2 colegios: {school1.name}, {school2.name}")
        
        # Crear estudiantes
        students_data = [
            {"first_name": "Bart", "last_name": "Simpson", "email": "bart.simpson@springfield.edu", "school": school1},
            {"first_name": "Lisa", "last_name": "Simpson", "email": "lisa.simpson@springfield.edu", "school": school1},
            {"first_name": "Milhouse", "last_name": "Van Houten", "email": "milhouse.vanhouten@springfield.edu", "school": school1},
            {"first_name": "Nelson", "last_name": "Muntz", "email": "nelson.muntz@springfield.edu", "school": school2},
            {"first_name": "Martin", "last_name": "Prince", "email": "martin.prince@springfield.edu", "school": school2},
        ]
        
        students = []
        for i, data in enumerate(students_data, 1):
            student = Student(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                student_code=f"STU-{data['school'].id:03d}-{i:03d}",
                school_id=data["school"].id,
                is_active=True
            )
            db.add(student)
            students.append(student)
        
        db.commit()
        for student in students:
            db.refresh(student)
        print(f"✓ Creados {len(students)} estudiantes")
        
        # Crear facturas
        due_date = datetime.now() + timedelta(days=30)
        invoices_data = [
            {"number": "INV-2024-001", "student": students[0], "amount": Decimal("1000.00"), "description": "Mensualidad Enero - Bart Simpson"},
            {"number": "INV-2024-002", "student": students[0], "amount": Decimal("1000.00"), "description": "Mensualidad Febrero - Bart Simpson"},
            {"number": "INV-2024-003", "student": students[1], "amount": Decimal("1200.00"), "description": "Mensualidad Enero - Lisa Simpson (Saxofón)"},
            {"number": "INV-2024-004", "student": students[2], "amount": Decimal("800.00"), "description": "Mensualidad Enero - Milhouse Van Houten"},
            {"number": "INV-2024-005", "student": students[3], "amount": Decimal("1500.00"), "description": "Mensualidad Enero - Nelson Muntz"},
            {"number": "INV-2024-006", "student": students[4], "amount": Decimal("900.00"), "description": "Mensualidad Enero - Martin Prince"},
        ]
        
        invoices = []
        for data in invoices_data:
            invoice = Invoice(
                invoice_number=data["number"],
                student_id=data["student"].id,
                amount=data["amount"],
                description=data["description"],
                due_date=due_date,
                status=InvoiceStatus.PENDING
            )
            db.add(invoice)
            invoices.append(invoice)
        
        db.commit()
        for invoice in invoices:
            db.refresh(invoice)
        print(f"✓ Creadas {len(invoices)} facturas")
        
        # Crear algunos pagos
        payments_data = [
            {"invoice": invoices[0], "amount": Decimal("500.00"), "method": "transfer", "reference": "TRF-001", "notes": "Pago de Homero Simpson"},
            {"invoice": invoices[0], "amount": Decimal("300.00"), "method": "cash", "reference": "CASH-001", "notes": "Pago parcial de Marge"},
            {"invoice": invoices[2], "amount": Decimal("1200.00"), "method": "card", "reference": "CARD-001", "notes": "Pago completo de Lisa"},
        ]
        
        for data in payments_data:
            payment = Payment(
                invoice_id=data["invoice"].id,
                amount=data["amount"],
                payment_method=data["method"],
                payment_reference=data["reference"],
                payment_date=datetime.now(),
                notes=data.get("notes", "")
            )
            db.add(payment)
        
        db.commit()
        print(f"✓ Creados {len(payments_data)} pagos")
        
        # Actualizar estados de facturas
        for invoice in invoices:
            total_paid = sum(
                p.amount for p in db.query(Payment).filter(Payment.invoice_id == invoice.id).all()
            )
            if total_paid >= invoice.amount:
                invoice.status = InvoiceStatus.PAID
            elif total_paid > 0:
                invoice.status = InvoiceStatus.PARTIAL
        
        db.commit()
        print("✓ Estados de facturas actualizados")
        
        print("\n✅ Datos de ejemplo cargados exitosamente!")
        print(f"\nResumen:")
        print(f"  - Colegios: 2")
        print(f"  - Estudiantes: {len(students)}")
        print(f"  - Facturas: {len(invoices)}")
        print(f"  - Pagos: {len(payments_data)}")
        print(f"\nPuedes consultar la API en: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_sample_data()


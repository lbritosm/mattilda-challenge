"""change_ids_to_uuid

Revision ID: 001
Revises: 
Create Date: 2026-01-13 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Convierte todas las columnas ID de Integer a UUID.
    Para bases de datos con datos existentes, genera nuevos UUIDs y mantiene las relaciones.
    """
    connection = op.get_bind()
    
    # 1. Schools: Crear columna temporal UUID
    op.add_column('schools', sa.Column('id_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Generar UUIDs para schools existentes
    schools = connection.execute(sa.text("SELECT id FROM schools")).fetchall()
    school_id_map = {}  # Mapeo: old_id -> new_uuid
    for (old_id,) in schools:
        new_uuid = uuid.uuid4()
        connection.execute(
            sa.text("UPDATE schools SET id_uuid = :uuid WHERE id = :old_id"),
            {"uuid": new_uuid, "old_id": old_id}
        )
        school_id_map[old_id] = new_uuid
    
    # 2. Students: Crear columnas temporales UUID
    op.add_column('students', sa.Column('id_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('students', sa.Column('school_id_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Generar UUIDs para students y mapear school_id
    students = connection.execute(sa.text("SELECT id, school_id FROM students")).fetchall()
    student_id_map = {}  # Mapeo: old_id -> new_uuid
    for old_id, old_school_id in students:
        new_uuid = uuid.uuid4()
        new_school_uuid = school_id_map.get(old_school_id)
        connection.execute(
            sa.text("UPDATE students SET id_uuid = :uuid, school_id_uuid = :school_uuid WHERE id = :old_id"),
            {"uuid": new_uuid, "school_uuid": new_school_uuid, "old_id": old_id}
        )
        student_id_map[old_id] = new_uuid
    
    # 3. Invoices: Crear columnas temporales UUID
    op.add_column('invoices', sa.Column('id_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('invoices', sa.Column('student_id_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Generar UUIDs para invoices y mapear student_id
    invoices = connection.execute(sa.text("SELECT id, student_id FROM invoices")).fetchall()
    invoice_id_map = {}  # Mapeo: old_id -> new_uuid
    for old_id, old_student_id in invoices:
        new_uuid = uuid.uuid4()
        new_student_uuid = student_id_map.get(old_student_id)
        connection.execute(
            sa.text("UPDATE invoices SET id_uuid = :uuid, student_id_uuid = :student_uuid WHERE id = :old_id"),
            {"uuid": new_uuid, "student_uuid": new_student_uuid, "old_id": old_id}
        )
        invoice_id_map[old_id] = new_uuid
    
    # 4. Payments: Crear columnas temporales UUID
    op.add_column('payments', sa.Column('id_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('payments', sa.Column('invoice_id_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Generar UUIDs para payments y mapear invoice_id
    payments = connection.execute(sa.text("SELECT id, invoice_id FROM payments")).fetchall()
    for old_id, old_invoice_id in payments:
        new_uuid = uuid.uuid4()
        new_invoice_uuid = invoice_id_map.get(old_invoice_id)
        connection.execute(
            sa.text("UPDATE payments SET id_uuid = :uuid, invoice_id_uuid = :invoice_uuid WHERE id = :old_id"),
            {"uuid": new_uuid, "invoice_uuid": new_invoice_uuid, "old_id": old_id}
        )
    
    # 5. Eliminar TODAS las foreign keys primero (en orden inverso de dependencias)
    op.drop_constraint('payments_invoice_id_fkey', 'payments', type_='foreignkey')
    op.drop_constraint('invoices_student_id_fkey', 'invoices', type_='foreignkey')
    op.drop_constraint('students_school_id_fkey', 'students', type_='foreignkey')
    
    # 6. Eliminar primary keys y columnas antiguas, renombrar nuevas
    # Payments
    op.drop_constraint('payments_pkey', 'payments', type_='primary')
    op.drop_column('payments', 'id')
    op.drop_column('payments', 'invoice_id')
    op.alter_column('payments', 'id_uuid', new_column_name='id', nullable=False)
    op.alter_column('payments', 'invoice_id_uuid', new_column_name='invoice_id', nullable=False)
    op.create_primary_key('payments_pkey', 'payments', ['id'])
    
    # Invoices
    op.drop_constraint('invoices_pkey', 'invoices', type_='primary')
    op.drop_column('invoices', 'id')
    op.drop_column('invoices', 'student_id')
    op.alter_column('invoices', 'id_uuid', new_column_name='id', nullable=False)
    op.alter_column('invoices', 'student_id_uuid', new_column_name='student_id', nullable=False)
    op.create_primary_key('invoices_pkey', 'invoices', ['id'])
    
    # Students
    op.drop_constraint('students_pkey', 'students', type_='primary')
    op.drop_column('students', 'id')
    op.drop_column('students', 'school_id')
    op.alter_column('students', 'id_uuid', new_column_name='id', nullable=False)
    op.alter_column('students', 'school_id_uuid', new_column_name='school_id', nullable=False)
    op.create_primary_key('students_pkey', 'students', ['id'])
    
    # Schools
    op.drop_constraint('schools_pkey', 'schools', type_='primary')
    op.drop_column('schools', 'id')
    op.alter_column('schools', 'id_uuid', new_column_name='id', nullable=False)
    op.create_primary_key('schools_pkey', 'schools', ['id'])
    
    # 7. Recrear foreign keys (en orden de dependencias)
    op.create_foreign_key('students_school_id_fkey', 'students', 'schools', ['school_id'], ['id'])
    op.create_foreign_key('invoices_student_id_fkey', 'invoices', 'students', ['student_id'], ['id'])
    op.create_foreign_key('payments_invoice_id_fkey', 'payments', 'invoices', ['invoice_id'], ['id'])
    
    # Eliminar secuencias que ya no se necesitan
    op.execute("DROP SEQUENCE IF EXISTS schools_id_seq CASCADE")
    op.execute("DROP SEQUENCE IF EXISTS students_id_seq CASCADE")
    op.execute("DROP SEQUENCE IF EXISTS invoices_id_seq CASCADE")
    op.execute("DROP SEQUENCE IF EXISTS payments_id_seq CASCADE")


def downgrade() -> None:
    # Revertir a Integer (complejo, mejor no implementar por ahora)
    # Si necesitas revertir, sería mejor restaurar desde un backup
    pass

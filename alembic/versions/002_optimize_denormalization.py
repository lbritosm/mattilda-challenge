"""optimize_denormalization

Revision ID: 002
Revises: 001
Create Date: 2026-01-14 14:09:04.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Optimizaciones de denormalización y índices:
    1. Agregar school_id a invoices (denormalización)
    2. Renombrar amount a amount_total en invoices
    3. Agregar issue_date a invoices
    4. Cambiar due_date de timestamp a date
    5. Cambiar constraint de invoice_number a unique(school_id, invoice_number)
    6. Agregar school_id y student_id a payments
    7. Hacer invoice_id nullable en payments
    8. Cambiar amount a numeric(12,2) en payments
    9. Agregar índices optimizados
    10. Cambiar constraint de student_code a unique(school_id, student_code)
    """
    
    # ===== INVOICES =====
    
    # 1. Agregar school_id a invoices
    op.add_column('invoices', sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Poblar school_id desde students
    op.execute("""
        UPDATE invoices 
        SET school_id = students.school_id 
        FROM students 
        WHERE invoices.student_id = students.id
    """)
    
    # Hacer school_id NOT NULL después de poblar
    op.alter_column('invoices', 'school_id', nullable=False)
    
    # 2. Agregar issue_date
    op.add_column('invoices', sa.Column('issue_date', sa.Date(), nullable=True, server_default=sa.func.current_date()))
    op.alter_column('invoices', 'issue_date', nullable=False)
    
    # 3. Renombrar amount a amount_total y cambiar a numeric(12,2)
    op.alter_column('invoices', 'amount', new_column_name='amount_total', type_=sa.Numeric(12, 2))
    
    # 4. Cambiar due_date de timestamp a date
    op.execute("""
        ALTER TABLE invoices 
        ALTER COLUMN due_date TYPE DATE USING due_date::date
    """)
    
    # 5. Eliminar índice único de invoice_number si existe y crear unique(school_id, invoice_number)
    # El constraint puede ser un índice único, verificar y eliminar
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Obtener todos los índices únicos
    indexes = inspector.get_indexes('invoices')
    unique_indexes = [idx['name'] for idx in indexes if idx.get('unique', False)]
    
    # Intentar eliminar el índice único si existe
    for idx_name in ['ix_invoices_invoice_number', 'invoices_invoice_number_key', 'invoices_invoice_number_unique']:
        if idx_name in unique_indexes:
            op.drop_index(idx_name, table_name='invoices')
            break
    
    # También intentar eliminar como constraint único
    try:
        constraints = [c['name'] for c in inspector.get_unique_constraints('invoices')]
        for constraint_name in ['invoices_invoice_number_key', 'uq_invoice_invoice_number']:
            if constraint_name in constraints:
                op.drop_constraint(constraint_name, 'invoices', type_='unique')
                break
    except:
        pass  # Si no hay constraints únicos, continuar
    
    op.create_unique_constraint('uq_invoice_school_number', 'invoices', ['school_id', 'invoice_number'])
    
    # 6. Agregar foreign key de school_id
    op.create_foreign_key('invoices_school_id_fkey', 'invoices', 'schools', ['school_id'], ['id'])
    
    # 7. Agregar índices optimizados para invoices
    op.create_index('idx_invoice_school_due', 'invoices', ['school_id', 'due_date'])
    op.create_index('idx_invoice_student_due', 'invoices', ['student_id', 'due_date'])
    
    # ===== PAYMENTS =====
    
    # 8. Agregar school_id y student_id a payments
    op.add_column('payments', sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('payments', sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Poblar school_id y student_id desde invoices
    op.execute("""
        UPDATE payments 
        SET school_id = invoices.school_id,
            student_id = invoices.student_id
        FROM invoices 
        WHERE payments.invoice_id = invoices.id
    """)
    
    # Hacer NOT NULL después de poblar
    op.alter_column('payments', 'school_id', nullable=False)
    op.alter_column('payments', 'student_id', nullable=False)
    
    # 9. Hacer invoice_id nullable (para pagos "a cuenta")
    op.alter_column('payments', 'invoice_id', nullable=True)
    
    # 10. Cambiar amount a numeric(12,2)
    op.alter_column('payments', 'amount', type_=sa.Numeric(12, 2))
    
    # 11. Agregar foreign keys
    op.create_foreign_key('payments_school_id_fkey', 'payments', 'schools', ['school_id'], ['id'])
    op.create_foreign_key('payments_student_id_fkey', 'payments', 'students', ['student_id'], ['id'])
    
    # 12. Agregar índices optimizados para payments
    op.create_index('idx_payment_student_date', 'payments', ['student_id', 'payment_date'])
    op.create_index('idx_payment_school_date', 'payments', ['school_id', 'payment_date'])
    
    # ===== STUDENTS =====
    
    # 13. Eliminar índice único de student_code si existe y crear unique(school_id, student_code)
    # Verificar si el índice único existe antes de eliminarlo
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Obtener todos los índices únicos
    student_indexes = inspector.get_indexes('students')
    student_unique_indexes = [idx['name'] for idx in student_indexes if idx.get('unique', False)]
    
    # Intentar eliminar el índice único si existe
    for idx_name in ['ix_students_student_code', 'students_student_code_key', 'students_student_code_unique']:
        if idx_name in student_unique_indexes:
            op.drop_index(idx_name, table_name='students')
            break
    
    # También intentar eliminar como constraint único
    try:
        student_constraints = [c['name'] for c in inspector.get_unique_constraints('students')]
        for constraint_name in ['students_student_code_key', 'uq_student_student_code']:
            if constraint_name in student_constraints:
                op.drop_constraint(constraint_name, 'students', type_='unique')
                break
    except:
        pass  # Si no hay constraints únicos, continuar
    
    op.create_unique_constraint('uq_student_school_code', 'students', ['school_id', 'student_code'])
    
    # 14. Agregar índice compuesto para is_active + school_id
    op.create_index('idx_student_active_school', 'students', ['is_active', 'school_id'])


def downgrade() -> None:
    # Revertir cambios (complejo, mejor no implementar por ahora)
    # Si necesitas revertir, sería mejor restaurar desde un backup
    pass


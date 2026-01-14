"""add_constraints_and_indexes

Revision ID: 004
Revises: 003
Create Date: 2026-01-14 14:38:47.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Agrega constraints CHECK, índices adicionales optimizados y updated_at en payments.
    
    1. Constraints CHECK:
       - invoices: total_amount >= 0, due_date >= issue_date
       - payments: amount > 0
    
    2. Índices adicionales:
       - students: (school_id, is_active) si no existe
       - invoices: (school_id, due_date DESC), (student_id, due_date DESC), (school_id, status)
       - payments: (school_id, payment_date DESC), (student_id, payment_date DESC), 
                   (invoice_id) WHERE invoice_id IS NOT NULL (partial index)
    
    3. Agregar updated_at en payments
    """
    
    # ===== CONSTRAINTS CHECK =====
    
    # INVOICES: total_amount >= 0
    op.create_check_constraint(
        'ck_invoice_total_amount_positive',
        'invoices',
        'total_amount >= 0'
    )
    
    # INVOICES: due_date >= issue_date
    op.create_check_constraint(
        'ck_invoice_due_after_issue',
        'invoices',
        'due_date >= issue_date'
    )
    
    # PAYMENTS: amount > 0
    op.create_check_constraint(
        'ck_payment_amount_positive',
        'payments',
        'amount > 0'
    )
    
    # ===== ÍNDICES ADICIONALES =====
    
    # STUDENTS: Verificar si el índice compuesto ya existe, si no, crearlo
    # (Ya debería existir de la migración 002, pero por si acaso)
    try:
        op.create_index(
            'idx_student_active_school',
            'students',
            ['school_id', 'is_active'],
            if_not_exists=True
        )
    except:
        pass  # Si ya existe, continuar
    
    # INVOICES: Índices con DESC para ordenamiento descendente
    # Eliminar índices antiguos si existen y recrearlos con DESC
    try:
        op.drop_index('idx_invoice_school_due', table_name='invoices')
    except:
        pass
    
    try:
        op.drop_index('idx_invoice_student_due', table_name='invoices')
    except:
        pass
    
    # Crear índices con DESC usando SQL directo
    op.execute("""
        CREATE INDEX idx_invoice_school_due 
        ON invoices(school_id, due_date DESC)
    """)
    
    op.execute("""
        CREATE INDEX idx_invoice_student_due 
        ON invoices(student_id, due_date DESC)
    """)
    
    # INVOICES: Índice compuesto (school_id, status) para filtros comunes
    op.create_index(
        'idx_invoice_school_status',
        'invoices',
        ['school_id', 'status'],
        if_not_exists=True
    )
    
    # PAYMENTS: Índices con DESC
    # Eliminar índices antiguos si existen y recrearlos con DESC
    try:
        op.drop_index('idx_payment_school_date', table_name='payments')
    except:
        pass
    
    try:
        op.drop_index('idx_payment_student_date', table_name='payments')
    except:
        pass
    
    # Crear índices con DESC usando SQL directo
    op.execute("""
        CREATE INDEX idx_payment_school_date 
        ON payments(school_id, payment_date DESC)
    """)
    
    op.execute("""
        CREATE INDEX idx_payment_student_date 
        ON payments(student_id, payment_date DESC)
    """)
    
    # PAYMENTS: Partial index para invoice_id (solo cuando no es NULL)
    op.execute("""
        CREATE INDEX idx_payments_invoice_id 
        ON payments(invoice_id) 
        WHERE invoice_id IS NOT NULL
    """)
    
    # ===== AGREGAR updated_at EN PAYMENTS =====
    
    op.add_column('payments', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # No hay necesidad de poblar datos históricos, updated_at será NULL para registros antiguos


def downgrade() -> None:
    """
    Revierte los cambios: elimina constraints, índices y columna.
    """
    # Eliminar columna updated_at
    op.drop_column('payments', 'updated_at')
    
    # Eliminar índices
    try:
        op.drop_index('idx_payments_invoice_id', table_name='payments')
    except:
        pass
    
    try:
        op.drop_index('idx_payment_student_date', table_name='payments')
    except:
        pass
    
    try:
        op.drop_index('idx_payment_school_date', table_name='payments')
    except:
        pass
    
    try:
        op.drop_index('idx_invoice_school_status', table_name='invoices')
    except:
        pass
    
    try:
        op.drop_index('idx_invoice_student_due', table_name='invoices')
    except:
        pass
    
    try:
        op.drop_index('idx_invoice_school_due', table_name='invoices')
    except:
        pass
    
    # Eliminar constraints
    try:
        op.drop_constraint('ck_payment_amount_positive', 'payments', type_='check')
    except:
        pass
    
    try:
        op.drop_constraint('ck_invoice_due_after_issue', 'invoices', type_='check')
    except:
        pass
    
    try:
        op.drop_constraint('ck_invoice_total_amount_positive', 'invoices', type_='check')
    except:
        pass


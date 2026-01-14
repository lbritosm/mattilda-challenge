"""make_payment_invoice_id_required

Revision ID: 005
Revises: 004
Create Date: 2026-01-14 15:02:08.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Hace invoice_id obligatorio en payments (elimina pagos "a cuenta").
    
    1. Eliminar cualquier pago sin invoice_id (si existen)
    2. Eliminar el partial index de invoice_id (ya no es necesario)
    3. Hacer invoice_id NOT NULL
    """
    
    # 1. Eliminar pagos sin invoice_id (si existen)
    op.execute("""
        DELETE FROM payments 
        WHERE invoice_id IS NULL
    """)
    
    # 2. Eliminar el partial index de invoice_id
    try:
        op.drop_index('idx_payments_invoice_id', table_name='payments')
    except:
        pass  # Si no existe, continuar
    
    # 3. Hacer invoice_id NOT NULL
    op.alter_column('payments', 'invoice_id', nullable=False)


def downgrade() -> None:
    """
    Revierte el cambio: hace invoice_id nullable nuevamente.
    """
    # Hacer invoice_id nullable
    op.alter_column('payments', 'invoice_id', nullable=True)
    
    # Recrear el partial index
    op.execute("""
        CREATE INDEX idx_payments_invoice_id 
        ON payments(invoice_id) 
        WHERE invoice_id IS NOT NULL
    """)


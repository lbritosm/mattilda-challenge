"""rename_amount_total_to_total_amount

Revision ID: 003
Revises: 002
Create Date: 2026-01-14 14:36:33.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Renombra la columna amount_total a total_amount en la tabla invoices.
    """
    op.alter_column('invoices', 'amount_total', new_column_name='total_amount')


def downgrade() -> None:
    """
    Revierte el cambio: renombra total_amount a amount_total.
    """
    op.alter_column('invoices', 'total_amount', new_column_name='amount_total')


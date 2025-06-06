"""add is_admin to users

Revision ID: add_is_admin_to_users
Revises: 
Create Date: 2024-03-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_admin_to_users'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    op.drop_column('users', 'is_admin') 
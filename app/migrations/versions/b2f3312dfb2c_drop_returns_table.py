"""drop returns table

Revision ID: b2f3312dfb2c
Revises: 05f4816ddad1
Create Date: 2023-11-14 16:25:24.770608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2f3312dfb2c'
down_revision = '05f4816ddad1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DROP TABLE returns CASCADE')


def downgrade():
    pass

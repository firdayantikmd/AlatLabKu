"""drop returns table

Revision ID: 85bd5f61eb6a
Revises: a68bd522ef3f
Create Date: 2023-11-09 17:16:46.572295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85bd5f61eb6a'
down_revision = 'a68bd522ef3f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DROP TABLE returns CASCADE')


def downgrade():
    pass

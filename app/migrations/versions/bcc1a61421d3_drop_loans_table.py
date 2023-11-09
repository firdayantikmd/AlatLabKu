"""drop loans table

Revision ID: bcc1a61421d3
Revises: 3f1c1ff76573
Create Date: 2023-11-09 16:43:27.548656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcc1a61421d3'
down_revision = '3f1c1ff76573'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DROP TABLE loans CASCADE')


def downgrade():
    pass

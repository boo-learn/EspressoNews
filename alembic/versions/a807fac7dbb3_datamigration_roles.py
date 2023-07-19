"""Datamigration roles

Revision ID: a807fac7dbb3
Revises: 278c443fec0d
Create Date: 2023-07-19 15:56:21.664743

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String

# revision identifiers, used by Alembic.
revision = 'a807fac7dbb3'
down_revision = '278c443fec0d'
branch_labels = None
depends_on = None

role = table('roles',
             column('id', Integer),
             column('role', String),
             column('button_name', String)
             )


def upgrade():
    op.bulk_insert(role,
                   [
                       {'id': 1, 'role': 'Helpfull assistant.', 'button_name': 'Стандартная'},
                       {'id': 2, 'role': 'Announcer', 'button_name': 'Диктор'}
                   ]
                   )


def downgrade():
    op.execute(role.delete())

"""Datamigration for roles

Revision ID: 445ce91e529d
Revises: 11d40df04227
Create Date: 2023-07-19 16:26:08.109706

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table, Integer, String

# revision identifiers, used by Alembic.
revision = '445ce91e529d'
down_revision = '11d40df04227'
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

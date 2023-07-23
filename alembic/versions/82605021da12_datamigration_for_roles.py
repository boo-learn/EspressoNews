"""Datamigration for roles

Revision ID: 82605021da12
Revises: ad5a014ddbb3
Create Date: 2023-07-23 02:17:55.781307

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String

# revision identifiers, used by Alembic.
revision = '82605021da12'
down_revision = 'ad5a014ddbb3'
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
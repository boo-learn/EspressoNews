"""Datamigration for roles

Revision ID: 18f9173501f5
Revises: 47f1fbcd214c
Create Date: 2023-07-19 13:32:46.811105

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String

# revision identifiers, used by Alembic.
revision = '18f9173501f5'
down_revision = '47f1fbcd214c'
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

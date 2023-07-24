"""Datamigration_for_roles

Revision ID: b9b6d00e928d
Revises: 783df719bc14
Create Date: 2023-07-25 02:32:20.899104

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String

# revision identifiers, used by Alembic.
revision = 'b9b6d00e928d'
down_revision = '783df719bc14'
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
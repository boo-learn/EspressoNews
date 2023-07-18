"""Datamigration for roles

Revision ID: 0a6038165f0b
Revises: ed37c912789d
Create Date: 2023-07-18 19:01:31.389193

"""
from alembic import op
from sqlalchemy import String, Integer
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '0a6038165f0b'
down_revision = 'ed37c912789d'
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
                       {'id': 1, 'role': 'You are helpfull assistant.', 'button_name': 'Стандартная'},
                       {'id': 2, 'role': 'Announcer', 'button_name': 'Диктор'}
                   ]
                   )


def downgrade():
    op.execute(role.delete())

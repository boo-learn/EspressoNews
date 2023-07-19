"""Datamigration intonations

Revision ID: e1f40c01425b
Revises: a807fac7dbb3
Create Date: 2023-07-19 15:57:01.966421

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String

# revision identifiers, used by Alembic.
revision = 'e1f40c01425b'
down_revision = 'a807fac7dbb3'
branch_labels = None
depends_on = None

role = table('intonations',
             column('id', Integer),
             column('intonation', String),
             column('button_name', String)
             )


def upgrade():
    op.bulk_insert(role,
                   [
                       {'id': 1, 'intonation': 'Comedy_sarcastic', 'button_name': 'Саркастично-шутливая'},
                       {'id': 2, 'intonation': 'Official', 'button_name': 'Официальная'}
                   ]
                   )


def downgrade():
    op.execute(role.delete())

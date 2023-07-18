"""Datamigration for intonation

Revision ID: d770eba2cbb2
Revises: 0a6038165f0b
Create Date: 2023-07-18 19:28:21.892576

"""
from alembic import op
from sqlalchemy import String, Integer
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'd770eba2cbb2'
down_revision = '0a6038165f0b'
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
"""Datamigration for intonations

Revision ID: 9ace8f1888cb
Revises: 445ce91e529d
Create Date: 2023-07-19 16:26:55.895485

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String

# revision identifiers, used by Alembic.
revision = '9ace8f1888cb'
down_revision = '445ce91e529d'
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

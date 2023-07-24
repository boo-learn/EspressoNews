"""Datamigration_for_intonations

Revision ID: 059e9f243f3d
Revises: b9b6d00e928d
Create Date: 2023-07-25 02:32:55.953824

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String

# revision identifiers, used by Alembic.
revision = '059e9f243f3d'
down_revision = 'b9b6d00e928d'
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
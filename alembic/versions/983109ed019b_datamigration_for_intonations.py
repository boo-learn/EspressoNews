"""Datamigration for intonations

Revision ID: 983109ed019b
Revises: 18f9173501f5
Create Date: 2023-07-19 13:33:45.183236

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String

# revision identifiers, used by Alembic.
revision = '983109ed019b'
down_revision = '18f9173501f5'
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

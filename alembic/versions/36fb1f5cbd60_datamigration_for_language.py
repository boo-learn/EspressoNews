"""datamigration_for_language

Revision ID: 36fb1f5cbd60
Revises: 721071d7260c
Create Date: 2023-09-05 18:46:29.975756

"""
from alembic import op
from sqlalchemy import table, column, Integer, String

revision = '36fb1f5cbd60'
down_revision = '721071d7260c'
branch_labels = None
depends_on = None


languages = table('languages',
                  column('id', Integer),
                  column('name', String),
                  column('code', String)
                  )


def upgrade():
    op.bulk_insert(languages,
                   [
                       {'id': 1, 'name': '中文', 'code': 'zh'},
                       {'id': 2, 'name': 'Español', 'code': 'es'},
                       {'id': 3, 'name': 'English', 'code': 'en'},
                       {'id': 4, 'name': 'हिन्दी', 'code': 'hi'},
                       {'id': 5, 'name': 'العربية', 'code': 'ar'},
                       {'id': 6, 'name': 'বাংলা', 'code': 'bn'},
                       {'id': 7, 'name': 'পর্তুগিজ', 'code': 'pt'},
                       {'id': 8, 'name': 'Русский', 'code': 'ru'},
                       {'id': 9, 'name': '日本語', 'code': 'ja'}
                   ]
                   )


def downgrade():
    op.execute(languages.delete())

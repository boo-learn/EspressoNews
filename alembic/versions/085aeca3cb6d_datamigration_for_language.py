"""datamigration_for_language

Revision ID: 085aeca3cb6d
Revises: 5ad5924aafbb
Create Date: 2023-09-03 13:59:07.505317

"""
from alembic import op
from sqlalchemy import table, column, Integer, String


revision = '085aeca3cb6d'
down_revision = '5ad5924aafbb'
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

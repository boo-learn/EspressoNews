"""add table Language and relations

Revision ID: 5ad5924aafbb
Revises: a8d1597c4783
Create Date: 2023-09-03 13:40:20.864377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ad5924aafbb'
down_revision = 'a8d1597c4783'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('languages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('digests', sa.Column('language_id', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'digests', ['user_id'])
    op.add_column('summaries', sa.Column('language_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'summaries', 'languages', ['language_id'], ['id'])
    op.add_column('user_settings', sa.Column('language_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user_settings', 'languages', ['language_id'], ['id'])
    op.drop_column('user_settings', 'language')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_settings', sa.Column('language', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user_settings', type_='foreignkey')
    op.drop_column('user_settings', 'language_id')
    op.drop_constraint(None, 'summaries', type_='foreignkey')
    op.drop_column('summaries', 'language_id')
    op.drop_constraint(None, 'digests', type_='unique')
    op.drop_column('digests', 'language_id')
    op.drop_table('languages')
    # ### end Alembic commands ###

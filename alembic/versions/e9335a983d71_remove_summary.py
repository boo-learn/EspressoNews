"""remove summary

Revision ID: e9335a983d71
Revises: ce55dc2bef78
Create Date: 2023-07-18 16:13:42.757304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9335a983d71'
down_revision = 'ce55dc2bef78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'summary')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('summary', sa.TEXT(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###

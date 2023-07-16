"""add schedule to db

Revision ID: 0d6c35b70afd
Revises: 827df158d60a
Create Date: 2023-07-16 19:34:42.009726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d6c35b70afd'
down_revision = '827df158d60a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('beat_schedule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task', sa.String(), nullable=False),
    sa.Column('schedule', sa.Integer(), nullable=False),
    sa.Column('args', sa.JSON(), nullable=True),
    sa.Column('kwargs', sa.JSON(), nullable=True),
    sa.Column('last_run_at', sa.DateTime(), nullable=True),
    sa.Column('total_run_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('beat_schedule')
    # ### end Alembic commands ###

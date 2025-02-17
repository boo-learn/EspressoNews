"""AdminUser unique email

Revision ID: a8d1597c4783
Revises: 4e1d6081727c
Create Date: 2023-08-31 22:34:28.770525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8d1597c4783'
down_revision = '4e1d6081727c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'admin_users', ['email'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'admin_users', type_='unique')
    # ### end Alembic commands ###

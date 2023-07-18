"""add connection telegram acc to channels

Revision ID: eac6de98fd69
Revises: 5dcee4ce2b91
Create Date: 2023-07-18 00:33:46.366567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eac6de98fd69'
down_revision = '493a154e6c48'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('telegram_channels',
    sa.Column('account_id', sa.BigInteger(), nullable=False),
    sa.Column('channel_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['telegram_accounts.account_id'], ),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.channel_id'], ),
    sa.PrimaryKeyConstraint('account_id', 'channel_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('telegram_channels')
    # ### end Alembic commands ###

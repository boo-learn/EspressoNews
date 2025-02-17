"""Init

Revision ID: faddec4e5ccf
Revises: 
Create Date: 2023-07-25 02:31:49.365816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'faddec4e5ccf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('beat_schedule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_name', sa.String(), nullable=False),
    sa.Column('task', sa.String(), nullable=False),
    sa.Column('schedule', sa.String(), nullable=False),
    sa.Column('args', sa.JSON(), nullable=True),
    sa.Column('kwargs', sa.JSON(), nullable=True),
    sa.Column('last_run_at', sa.DateTime(), nullable=True),
    sa.Column('total_run_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gpt_accounts',
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('api_key', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('account_id')
    )
    op.create_table('intonations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('intonation', sa.String(length=50), nullable=False),
    sa.Column('button_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('posts_rubrics',
    sa.Column('rubric_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('rubric_id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('button_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('telegram_accounts',
    sa.Column('account_id', sa.BigInteger(), nullable=False),
    sa.Column('api_id', sa.Integer(), nullable=True),
    sa.Column('api_hash', sa.String(length=100), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=False),
    sa.Column('session_string', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('account_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('language_code', sa.Enum('ru', 'en', name='language_code'), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_staff', sa.Boolean(), nullable=True),
    sa.Column('join_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('channels',
    sa.Column('channel_id', sa.BigInteger(), nullable=False),
    sa.Column('channel_name', sa.String(), nullable=False),
    sa.Column('channel_username', sa.String(length=50), nullable=False),
    sa.Column('channel_description', sa.Text(), nullable=True),
    sa.Column('member_count', sa.Integer(), nullable=True),
    sa.Column('channel_invite_link', sa.String(length=65), nullable=True),
    sa.Column('account_id', sa.BigInteger(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['telegram_accounts.account_id'], ),
    sa.PrimaryKeyConstraint('channel_id')
    )
    op.create_table('digests',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('generation_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('periodicity', sa.String(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('intonation_id', sa.Integer(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['intonation_id'], ['intonations.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('posts',
    sa.Column('post_id', sa.BigInteger(), nullable=False),
    sa.Column('channel_id', sa.BigInteger(), nullable=True),
    sa.Column('rubric_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('post_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.channel_id'], ),
    sa.ForeignKeyConstraint(['rubric_id'], ['posts_rubrics.rubric_id'], ),
    sa.PrimaryKeyConstraint('post_id'),
    sa.UniqueConstraint('post_id')
    )
    op.create_table('subscriptions',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('channel_id', sa.BigInteger(), nullable=False),
    sa.Column('subscription_date', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.channel_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'channel_id')
    )
    op.create_table('digests_posts',
    sa.Column('digest_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['digest_id'], ['digests.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.post_id'], ),
    sa.PrimaryKeyConstraint('digest_id', 'post_id')
    )
    op.create_table('files_library',
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('image', sa.LargeBinary(), nullable=False),
    sa.Column('video', sa.LargeBinary(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['posts.post_id'], ),
    sa.PrimaryKeyConstraint('file_id')
    )
    op.create_table('summaries',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('intonation_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['intonation_id'], ['intonations.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.post_id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('summaries')
    op.drop_table('files_library')
    op.drop_table('digests_posts')
    op.drop_table('subscriptions')
    op.drop_table('posts')
    op.drop_table('user_settings')
    op.drop_table('digests')
    op.drop_table('channels')
    op.drop_table('users')
    op.drop_table('telegram_accounts')
    op.drop_table('roles')
    op.drop_table('posts_rubrics')
    op.drop_table('intonations')
    op.drop_table('gpt_accounts')
    op.drop_table('beat_schedule')
    # ### end Alembic commands ###

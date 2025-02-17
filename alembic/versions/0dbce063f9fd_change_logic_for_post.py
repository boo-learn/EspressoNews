"""change logic for Post

Revision ID: 0dbce063f9fd
Revises: 854b1791c62c
Create Date: 2023-08-08 23:55:17.751727

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0dbce063f9fd'
down_revision = '854b1791c62c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Удаляем все записи в таблицах 'digests', 'files_library', и 'summaries'
    op.execute('DELETE FROM digests_posts')
    op.execute('DELETE FROM summaries')
    op.execute('DELETE FROM posts')
    op.execute('DELETE FROM digests')
    op.execute('DELETE FROM files_library')

    # Удаляем внешние ключи, которые ссылаются на столбец 'post_id' в таблице 'posts'
    op.drop_constraint('digests_posts_post_id_fkey', 'digests_posts', type_='foreignkey')
    op.drop_constraint('files_library_post_id_fkey', 'files_library', type_='foreignkey')
    op.drop_constraint('summaries_post_id_fkey', 'summaries', type_='foreignkey')
    op.execute("CREATE SEQUENCE posts_id_seq")

    # Добавляем новый столбец 'id' в таблицу 'posts'
    op.add_column('posts', sa.Column('id', sa.Integer, server_default=sa.text('nextval(\'posts_id_seq\'::regclass)'), primary_key=False, nullable=False))

    # Удаляем текущий первичный ключ для 'post_id'
    op.drop_constraint('posts_pkey', 'posts', type_='primary')

    # Делаем столбец 'post_id' неуникальным и nullable
    op.alter_column('posts', 'post_id', existing_type=sa.BIGINT(), nullable=True)

    # Добавляем новый первичный ключ для 'id'
    op.create_primary_key(None, 'posts', ['id'])

    # Добавляем обратно внешние ключи, но теперь ссылающиеся на новый столбец 'id' в таблице 'posts'
    op.create_foreign_key(None, 'digests_posts', 'posts', ['post_id'], ['id'])
    op.create_foreign_key(None, 'files_library', 'posts', ['post_id'], ['id'])
    op.create_foreign_key(None, 'summaries', 'posts', ['post_id'], ['id'])


def downgrade() -> None:
    # Удаляем внешние ключи, которые ссылаются на столбец 'id' в таблице 'posts'
    op.drop_constraint(None, 'digests_posts', type_='foreignkey')
    op.drop_constraint(None, 'files_library', type_='foreignkey')
    op.drop_constraint(None, 'summaries', type_='foreignkey')

    # Удаляем текущий первичный ключ для 'id'
    op.drop_constraint(None, 'posts', type_='primary')

    # Удаляем столбец 'id'
    op.drop_column('posts', 'id')

    # Делаем столбец 'post_id' не nullable и уникальным
    op.alter_column('posts', 'post_id', existing_type=sa.BIGINT(), nullable=False)

    # Добавляем обратно первичный ключ для 'post_id'
    op.create_primary_key(None, 'posts', ['post_id'])

    # Добавляем обратно внешние ключи, ссылающиеся на столбец 'post_id' в таблице 'posts'
    op.create_foreign_key('digests_posts_post_id_fkey', 'digests_posts', 'posts', ['post_id'], ['post_id'])
    op.create_foreign_key('files_library_post_id_fkey', 'files_library', 'posts', ['post_id'], ['post_id'])
    op.create_foreign_key('summaries_post_id_fkey', 'summaries', 'posts', ['post_id'], ['post_id'])

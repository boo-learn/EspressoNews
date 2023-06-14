import os
from shared.database import DATABASE_URI
from logging.config import fileConfig
from shared.database import Base
from shared import models

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    # TODO: может будет правильнее в databases.py положить DATABASE_URI в переменную окружения SQLALCHEMY_URL,
    #  а тут SQLALCHEMY_URL использовать?
    # os.environ["SQLALCHEMY_URL"] = DATABASE_URI
    # url = os.environ.get(
    #     "SQLALCHEMY_URL",
    #     default=config.get_main_option("sqlalchemy.url"),
    # )

    url = DATABASE_URI
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    url = DATABASE_URI
    # print(f"URL = {url}")
    connectable = engine_from_config(
        configuration={"sqlalchemy.url": url},
        # Замените 'sqlalchemy.url' на значение настройки строки подключения к БД
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # url = DATABASE_URI
        # url = url,
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

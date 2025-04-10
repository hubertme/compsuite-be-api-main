from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
# from dotenv import load_dotenv
from app.config.app_config import settings

# Setup env variables using the .env file.
# def setup_dotenv(use_cli_args=True):
#     work_dir = os.getcwd()
#     file_path = f"{work_dir}/envs/.{os.getenv('APP_ENV', 'dev')}.env"
#     print(f"Loading env file: {file_path}")
#     if not load_dotenv(file_path):
#         raise SystemExit("PANIC!!!! Failed to load dotenv!!!!!")
        
# setup_dotenv(use_cli_args=False)

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your model's Base.
# (Make sure Base is defined in your models and is imported so that
# Alembic can detect your tables for autogeneration.)
from app.models import Base  # adjust path if needed
from app.models import Log, User

target_metadata = Base.metadata

def get_sync_db_url() -> str:
    """
    Convert the async URL (with asyncpg) from settings into a sync URL for Alembic.
    For example, change:
      postgresql+asyncpg://user:pass@host/db
    to:
      postgresql://user:pass@host/db
    """
    url = settings.SQLALCHEMY_DATABASE_URI
    return url.replace("+asyncpg", "")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_sync_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = get_sync_db_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db.base import Base
from app.models import models  # noqa: F401 - registers model metadata


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required for Alembic migrations")
    return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)


config.set_main_option("sqlalchemy.url", database_url().replace("%", "%%"))
target_metadata = Base.metadata

# These indexes are deliberately managed by the baseline migration because
# several use PostgreSQL/PostGIS operator classes not represented in the ORM.
MIGRATION_MANAGED_INDEXES = {
    "ux_utilisateurs_firebase_uid",
    "idx_articles_localisation",
    "idx_articles_categorie_statut",
    "idx_articles_prix",
    "idx_articles_titre_trgm",
    "idx_reservations_dates",
    "idx_reservations_statut",
    "idx_reservations_locataire",
    "idx_reservations_loueur",
    "idx_messages_conversation",
    "idx_notifications_user_lu",
}


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in (None, "public")
    if type_ == "table":
        return name in target_metadata.tables or name == "alembic_version"
    return True


def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "index" and reflected and compare_to is None:
        if name in MIGRATION_MANAGED_INDEXES:
            return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=include_name,
        include_object=include_object,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=include_name,
            include_object=include_object,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

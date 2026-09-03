# Lokiini database migrations

The PostgreSQL schema is owned exclusively by Alembic. FastAPI must not call
`create_all()` or execute ad-hoc schema changes during application startup.

## Upgrade

```sh
alembic current
alembic upgrade head
```

Docker Compose runs the one-shot `migrate` service before starting FastAPI.
For a deployment outside Compose, run `alembic upgrade head` as a release step
before starting application replicas.

## Create a migration

```sh
alembic revision --autogenerate -m "describe the schema change"
alembic upgrade head
```

Review generated migrations before applying them. Back up production data
before migrations that alter or remove columns.

## Development seed

The seed is explicit, idempotent, and refuses to run outside development:

```sh
python -m app.db.seed
```

With Docker Compose:

```sh
docker compose -f docker-compose.yml -f docker-compose.development.yml \
  run --rm backend python -m app.db.seed
```

Schema migrations never create fake users or equipment.

## Rollback

Inspect the target revision before downgrading:

```sh
alembic history
alembic downgrade -1
```

The initial baseline downgrade removes Lokiini tables and is destructive. It
is intended for disposable test databases only, not an existing environment.

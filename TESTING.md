# Lokiini automated tests

The test suite is split into fast local checks and an isolated PostgreSQL/PostGIS journey.

## Backend unit and contract tests

From `src/backend`, install `requirements-test.txt`, provide development-safe configuration, and run:

```text
pytest -q
```

The PostgreSQL journey skips unless both `DATABASE_URL` and `LOKIINI_TEST_DATABASE_URL` point to the same database whose name ends in `_test`.

## Isolated PostgreSQL journey

With Docker Desktop running, from the repository root run:

```text
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from backend-test
```

The test Compose file uses an ephemeral PostGIS database, applies every Alembic migration, then runs the complete backend suite. The critical journey covers registration/authentication, signed KYC verification, equipment publishing and search, reservation and overlap rejection, authorization, payment/deposit server states, check-in, active rental, check-out, and completion.

## Web tests

From `src/frontend/web` run:

```text
npm test
npm run build
```

`npm test` runs the existing source/contract checks and the browser-like React tests for authentication restoration, protected account access, booking conflicts, duplicate submission protection, booking status presentation, API failures, and shared accessible components.

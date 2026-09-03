# Lokiini pull request quality gates

The GitHub Actions workflow in `.github/workflows/ci.yml` runs for pull requests and manual
dispatch only. It contains no deployment job, registry push, environment mutation, or production
credential requirement.

## Required checks

- Backend correctness lint, changed-file formatting, and non-integration tests
- Web lint, TypeScript API-contract validation, tests, and production build
- Mobile lint, Expo configuration validation, and Android export
- Alembic upgrade, model drift check, rollback, clean re-upgrade, and the critical PostgreSQL journey
- Pull-request secret scan with redacted output
- Python, web, and mobile dependency vulnerability audits
- Production backend and web Docker image builds without publishing
- One final `Required quality gate` job that fails unless every preceding gate passes

Configure branch protection to require `Required quality gate`. The workflow cancels superseded
runs on the same pull request to keep feedback fast.

## Local commands

Backend:

```text
cd src/backend
python -m pip install -r requirements-test.txt
ruff check app tests scripts alembic
ruff format --check app tests scripts alembic
pytest -q -m "not integration"
```

Web:

```text
cd src/frontend/web
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

Mobile:

```text
cd src/frontend/mobile
npm ci
npm run validate
```

PostgreSQL migration and E2E validation:

```text
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from backend-test
```

The security gates intentionally fail when high or critical dependency vulnerabilities are
present. They must not be bypassed with `continue-on-error`; dependencies should be upgraded or a
reviewed, time-bounded exception should be documented in a separate change.

# Shared FastAPI contract

`openapi.json` is exported from the running FastAPI application. It is the authoritative contract for both frontend clients.

From `src/backend`, export the schema:

```powershell
$env:PYTHONPATH='.'
uv run --python 3.12 --with-requirements requirements.txt python scripts/export_openapi.py
```

From `src/frontend/web`, generate or verify the runtime-free TypeScript declarations:

```powershell
pnpm run api:types
pnpm run api:types:check
```

Do not edit `openapi.json` or `openapi.d.ts` manually. The web runtime remains in `web/src/services/httpClient.js`; mobile can consume the same declarations while supplying Firebase bearer authentication instead of web cookies.

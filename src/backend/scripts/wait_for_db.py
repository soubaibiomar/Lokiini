"""Wait for PostgreSQL database readiness with retries."""
import os
import sys
import time
from urllib.parse import urlparse

import psycopg2


def wait_for_db(timeout_seconds: int = 60) -> None:
    database_url = os.getenv("DATABASE_URL") or os.getenv("LOKIINI_TEST_DATABASE_URL")
    if not database_url:
        print("No DATABASE_URL provided; proceeding without wait.")
        return

    # Normalize asyncpg dialect for psycopg2 if needed
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    parsed = urlparse(sync_url)
    dbname = parsed.path.lstrip("/") or "postgres"
    user = parsed.username or "postgres"
    password = parsed.password or ""
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432

    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
                connect_timeout=2,
            )
            conn.close()
            print(f"Database at {host}:{port}/{dbname} is ready.")
            return
        except Exception as exc:
            last_error = exc
            time.sleep(1)

    print(f"Database wait timed out after {timeout_seconds}s: {last_error}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    wait_for_db()

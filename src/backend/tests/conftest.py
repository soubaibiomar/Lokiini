import os
from urllib.parse import urlparse

import pytest


def pytest_collection_modifyitems(config, items):
    """Keep PostgreSQL tests explicit and harmless on a developer machine."""
    if os.getenv("LOKIINI_TEST_DATABASE_URL"):
        return
    skip = pytest.mark.skip(reason="set LOKIINI_TEST_DATABASE_URL or use docker-compose.test.yml")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def isolated_database_url():
    url = os.getenv("LOKIINI_TEST_DATABASE_URL")
    if not url:
        pytest.skip("isolated PostgreSQL test database is not configured")
    database_name = urlparse(url.replace("postgresql+asyncpg", "postgresql")).path.lstrip("/")
    if not database_name.endswith("_test"):
        pytest.fail("LOKIINI_TEST_DATABASE_URL must target a database ending in '_test'")
    runtime_url = os.getenv("DATABASE_URL")
    runtime_database = urlparse((runtime_url or "").replace("postgresql+asyncpg", "postgresql")).path.lstrip("/")
    if runtime_url != url or not runtime_database.endswith("_test"):
        pytest.fail("DATABASE_URL and LOKIINI_TEST_DATABASE_URL must identify the same isolated *_test database")
    return url

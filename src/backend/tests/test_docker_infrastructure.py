import pytest
import yaml
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = (
    BACKEND_DIR.parent.parent
    if (BACKEND_DIR.parent.parent / "docker-compose.yml").exists()
    else None
)


def test_docker_compose_services():
    """Test that all infrastructure containers are declared in docker-compose.yml."""
    if not REPO_DIR:
        pytest.skip("docker-compose.yml not in container filesystem")
    compose_path = REPO_DIR / "docker-compose.yml"
    assert compose_path.exists()
    
    with open(compose_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    services = data.get("services", {})
    assert len(services) == 8
    for name in ["gateway", "frontend", "backend", "migrate", "postgres", "redis", "meilisearch", "n8n"]:
        assert name in services


def test_nginx_gateway_routes():
    """Test that Nginx routes the public web/API surface without admin services."""
    if not REPO_DIR:
        pytest.skip("docker config not in container filesystem")
    nginx_path = REPO_DIR / "docker" / "nginx" / "nginx.conf"
    assert nginx_path.exists()
    
    with open(nginx_path, "r", encoding="utf-8") as f:
        conf = f.read()

    assert "location /api/v1/" in conf
    assert "location /docs" in conf
    assert "location /n8n/" not in conf
    assert "location /search/" not in conf
    assert "location /" in conf


def test_backend_environment_variables():
    """Test required environment variables for FastAPI container."""
    if not REPO_DIR:
        pytest.skip("docker-compose.yml not in container filesystem")
    compose_path = REPO_DIR / "docker-compose.yml"
    with open(compose_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    backend_env = data["services"]["backend"]["environment"]
    env_str = " ".join(backend_env)
    
    assert "DATABASE_URL" in env_str
    assert "REDIS_URL" in env_str
    assert "MEILISEARCH_URL" in env_str
    assert "DIDIT_API_KEY" in env_str


def test_services_have_healthchecks_and_healthy_startup_dependencies():
    if not REPO_DIR:
        pytest.skip("docker-compose.yml not in container filesystem")
    with open(REPO_DIR / "docker-compose.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    services = data["services"]
    for name in ["gateway", "frontend", "backend", "postgres", "redis", "meilisearch", "n8n"]:
        assert "healthcheck" in services[name]

    assert services["gateway"]["depends_on"]["backend"]["condition"] == "service_healthy"
    assert services["gateway"]["depends_on"]["frontend"]["condition"] == "service_healthy"
    assert services["backend"]["depends_on"]["migrate"]["condition"] == "service_completed_successfully"
    for dependency in ["postgres", "redis", "meilisearch"]:
        assert services["backend"]["depends_on"][dependency]["condition"] == "service_healthy"


def test_gateway_uses_dynamic_docker_dns_and_production_hides_admin_routes():
    if not REPO_DIR:
        pytest.skip("docker configs not in container filesystem")
    development = (REPO_DIR / "docker/nginx/nginx.conf").read_text(encoding="utf-8")
    production = (REPO_DIR / "docker/nginx/nginx.production.conf").read_text(encoding="utf-8")

    for config in [development, production]:
        assert "resolver 127.0.0.11" in config
        assert "server backend:8000 resolve" in config
        assert "server frontend:3000 resolve" in config
        assert "location /api/v1/" in config

    assert "location /n8n/" not in production
    assert "location /search/" not in production


def test_production_uses_release_targets_and_internal_only_services():
    if not REPO_DIR:
        pytest.skip("docker-compose.production.yml not in container filesystem")
    production_compose = (REPO_DIR / "docker-compose.production.yml").read_text(encoding="utf-8")
    backend_dockerfile = (BACKEND_DIR / "Dockerfile").read_text(encoding="utf-8")
    production_backend = backend_dockerfile.split("FROM base AS production", 1)[1]

    assert production_compose.count("ports: !reset []") >= 6
    assert production_compose.count("target: production") == 3
    assert "--reload" not in production_backend

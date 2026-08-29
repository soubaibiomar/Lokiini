import pytest
import sys
import yaml
from pathlib import Path

def test_docker_compose_services():
    """Test that all 7 containers are declared in docker-compose.yml."""
    compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
    assert compose_path.exists()
    
    with open(compose_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    services = data.get("services", {})
    assert len(services) == 7
    for name in ["gateway", "frontend", "backend", "postgres", "redis", "meilisearch", "n8n"]:
        assert name in services

def test_nginx_gateway_routes():
    """Test that Nginx configuration routes all subsystems under port 80."""
    nginx_path = Path(__file__).parent.parent.parent.parent / "docker" / "nginx" / "nginx.conf"
    assert nginx_path.exists()
    
    with open(nginx_path, "r", encoding="utf-8") as f:
        conf = f.read()

    assert "location /api/v1/" in conf
    assert "location /docs" in conf
    assert "location /n8n/" in conf
    assert "location /search/" in conf
    assert "location /" in conf

def test_backend_environment_variables():
    """Test required environment variables for FastAPI container."""
    compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
    with open(compose_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    backend_env = data["services"]["backend"]["environment"]
    env_str = " ".join(backend_env)
    
    assert "DATABASE_URL" in env_str
    assert "REDIS_URL" in env_str
    assert "MEILISEARCH_URL" in env_str
    assert "DIDIT_API_KEY" in env_str

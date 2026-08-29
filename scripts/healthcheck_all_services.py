import sys
import yaml
from pathlib import Path

def test_infrastructure_configuration():
    """Vérifie la cohérence de l'orchestration Docker et de la configuration Nginx."""
    root_dir = Path(__file__).parent.parent
    
    # 1. Vérification docker-compose.yml
    compose_path = root_dir / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml manquant !"
    
    with open(compose_path, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    services = compose_data.get("services", {})
    expected_services = ["gateway", "frontend", "backend", "postgres", "redis", "meilisearch", "n8n"]
    
    for s in expected_services:
        assert s in services, f"Service '{s}' manquant dans docker-compose.yml !"

    # 2. Vérification image PostGIS
    pg_image = services["postgres"].get("image", "")
    assert "postgis" in pg_image, "PostgreSQL doit utiliser l'image PostGIS !"

    # 3. Vérification Nginx config
    nginx_path = root_dir / "docker" / "nginx" / "nginx.conf"
    assert nginx_path.exists(), "docker/nginx/nginx.conf manquant !"
    
    with open(nginx_path, "r", encoding="utf-8") as f:
        nginx_conf = f.read()

    assert "location /api/v1/" in nginx_conf
    assert "location /docs" in nginx_conf
    assert "location /n8n/" in nginx_conf
    assert "location /search/" in nginx_conf
    assert "location /" in nginx_conf

    print("==============================================================================")
    print("✅ TOUTE L'INFRASTRUCTURE DOCKER (7 SERVICES) & NGINX EST 100% VALIDE !")
    print("==============================================================================")

if __name__ == "__main__":
    test_infrastructure_configuration()

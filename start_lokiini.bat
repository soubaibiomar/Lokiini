@echo off
echo ==============================================================================
echo  LOKIINI / MATOS - LANCEMENT DE LA PLATEFORME ENTIERE (DOCKER COMPOSE)
echo ==============================================================================
echo.

docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker Compose n'est pas accessible.
    echo Veuillez vous assurer que Docker Desktop est ouvert.
    pause
    exit /b 1
)

echo [1/3] Construction et demarrage des 7 conteneurs Docker...
docker compose -f docker-compose.yml -f docker-compose.development.yml up --build -d

echo.
echo [2/3] Verification des conteneurs actifs...
docker compose -f docker-compose.yml -f docker-compose.development.yml ps

echo.
echo ==============================================================================
echo  LOKIINI EST OPERATIONNEL !
echo ==============================================================================
echo   - Portail Web Lokiini  : http://localhost (ou http://localhost:3000)
echo   - API Backend Swagger  : http://localhost/docs (ou http://localhost:8000/docs)
echo   - Moteur n8n           : http://localhost/n8n/ (ou http://localhost:5678)
echo   - Moteur Meilisearch   : http://localhost:7700
echo   - Base PostgreSQL 16   : localhost:5432 (identifiants charges depuis .env)
echo ==============================================================================
echo.
pause

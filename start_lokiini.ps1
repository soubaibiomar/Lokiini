Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " LOKIINI / MATOS - LANCEMENT DE LA PLATEFORME ENTIERE (DOCKER COMPOSE)" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan

try {
    docker compose version | Out-Null
} catch {
    Write-Host "[ERREUR] Docker Compose n'est pas accessible. Veuillez demarrer Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/3] Construction et demarrage des conteneurs Docker..." -ForegroundColor Yellow
docker compose up --build -d

Write-Host "`n[2/3] Verification des conteneurs actifs..." -ForegroundColor Yellow
docker compose ps

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host " LOKIINI EST OPERATIONNEL !" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  - Portail Web Lokiini  : http://localhost (ou http://localhost:3000)" -ForegroundColor White
Write-Host "  - API Backend Swagger  : http://localhost/docs (ou http://localhost:8000/docs)" -ForegroundColor White
Write-Host "  - Moteur n8n           : http://localhost/n8n/ (ou http://localhost:5678)" -ForegroundColor White
Write-Host "  - Moteur Meilisearch   : http://localhost:7700" -ForegroundColor White
Write-Host "  - Base PostgreSQL 16   : localhost:5432 (lokiini_user / lokiini_secure_pass_2026)" -ForegroundColor White
Write-Host "==============================================================================`n" -ForegroundColor Cyan

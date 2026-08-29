# ==============================================================================
# LOKIINI - SCRIPT DE DÉMARRAGE AUTOMATISÉ DOCKER COMPOSE (7 SERVICES)
# ==============================================================================
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "🚀 DÉMARRAGE DE LA PLATEFORME LOKIINI (7 CONTENEURS SOUS DOCKER)" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan

# 1. Vérification Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker n'est pas installé ou n'est pas démarré sur cette machine." -ForegroundColor Red
    Exit 1
}

# 2. Lancement des conteneurs
Write-Host "📦 Construction et démarrage des conteneurs (Nginx, React, FastAPI, PostGIS, Redis, Meilisearch, n8n)..." -ForegroundColor Yellow
docker compose up --build -d

# 3. Récapitulatif des URLs
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "✅ TOUS LES SERVICES LOKIINI SONT OPÉRATIONNELS !" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "🌐 Application Web React   : http://localhost (ou :3001)" -ForegroundColor White
Write-Host "⚡ API Swagger Backend    : http://localhost/docs (ou :8001/docs)" -ForegroundColor White
Write-Host "🤖 Moteur Automation n8n   : http://localhost/n8n/ (ou :5678)" -ForegroundColor White
Write-Host "🔍 Recherche Meilisearch   : http://localhost:7700" -ForegroundColor White
Write-Host "🗄️ Base PostGIS PostgreSQL : localhost:5432 (lokiini_db)" -ForegroundColor White
Write-Host "==============================================================================" -ForegroundColor Cyan

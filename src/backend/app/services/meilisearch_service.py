import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger("meilisearch-service")

class MeilisearchService:
    def __init__(self):
        self.url = settings.MEILISEARCH_URL
        self.key = settings.MEILISEARCH_MASTER_KEY
        self.index_name = "articles"

    async def index_article(self, article_data: Dict[str, Any]):
        """Indexe ou met à jour un article dans Meilisearch."""
        try:
            import httpx
            headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
            doc = {
                "id": str(article_data["id"]),
                "titre": article_data["titre"],
                "description": article_data.get("description", ""),
                "categorie": article_data["categorie"],
                "prix_par_jour": float(article_data["prix_par_jour"]),
                "city": article_data.get("city", "Casablanca"),
                "niveau_risque": article_data.get("niveau_risque", "faible")
            }
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(f"{self.url}/indexes/{self.index_name}/documents", json=[doc], headers=headers)
        except Exception as e:
            logger.debug(f"Meilisearch offline (fallback SQL actif) : {e}")

    async def search_articles(self, query: str, limit: int = 100) -> Optional[List[str]]:
        """Return matching IDs, or None when Meilisearch is unavailable."""
        try:
            import httpx
            headers = {"Authorization": f"Bearer {self.key}"}
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.post(
                    f"{self.url}/indexes/{self.index_name}/search",
                    json={"q": query, "limit": limit},
                    headers=headers
                )
                if res.status_code == 200:
                    hits = res.json().get("hits", [])
                    return [h["id"] for h in hits]
                logger.debug("Meilisearch search failed with status %s", res.status_code)
        except Exception as exc:
            logger.debug("Meilisearch unavailable; SQL search will be used: %s", exc)
        return None

    async def remove_article(self, article_id: str):
        """Retire un article de l'index Meilisearch."""
        try:
            import httpx
            headers = {"Authorization": f"Bearer {self.key}"}
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.delete(f"{self.url}/indexes/{self.index_name}/documents/{article_id}", headers=headers)
        except Exception:
            pass

meilisearch_service = MeilisearchService()

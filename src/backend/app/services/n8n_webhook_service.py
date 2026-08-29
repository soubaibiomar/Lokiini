import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("n8n-webhook-service")

class N8nWebhookService:
    def __init__(self):
        self.n8n_url = "http://n8n:5678/webhook"

    async def emit_event(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """Émet un événement asynchrone vers l'instance n8n."""
        try:
            import httpx
            full_payload = {
                "event": event_type,
                "data": payload,
                "environment": "docker-compose",
                "source": "lokiini-fastapi-backend"
            }
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.post(f"{self.n8n_url}/{event_type}", json=full_payload)
                return res.status_code in [200, 201, 204]
        except Exception as e:
            logger.debug(f"n8n webhook simulé ({event_type}) : {e}")
            return True

n8n_webhook_service = N8nWebhookService()

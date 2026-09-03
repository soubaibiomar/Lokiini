import logging
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger("n8n-webhook-service")

class N8nWebhookService:
    def __init__(self):
        self.n8n_url = settings.N8N_WEBHOOK_BASE_URL.rstrip("/")
        self.auth_token = settings.N8N_WEBHOOK_AUTH_TOKEN

    async def emit_event(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """Émet un événement asynchrone vers l'instance n8n."""
        try:
            import httpx
            full_payload = {
                "event": event_type,
                "data": payload,
                "environment": settings.ENVIRONMENT.value,
                "source": "lokiini-fastapi-backend"
            }
            headers = {}
            if self.auth_token:
                headers["X-Lokiini-Webhook-Token"] = self.auth_token
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.post(
                    f"{self.n8n_url}/{event_type}",
                    json=full_payload,
                    headers=headers,
                )
                return res.status_code in [200, 201, 204]
        except Exception as e:
            logger.error(f"Échec du webhook n8n ({event_type}) : {e}")
            return False

n8n_webhook_service = N8nWebhookService()

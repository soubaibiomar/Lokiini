import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional
from app.core.config import settings

class DiditService:
    def __init__(self):
        self.api_key = settings.DIDIT_API_KEY
        self.api_url = settings.DIDIT_API_URL
        self.webhook_secret = settings.DIDIT_WEBHOOK_SECRET

    async def initiate_verification_session(
        self, 
        user_id: str, 
        email: Optional[str] = None, 
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a hosted Didit V3 session without sending identity documents to Lokiini."""
        if not self.api_key or not settings.DIDIT_WORKFLOW_ID or self.api_key.startswith("didit_demo"):
            raise RuntimeError("Le fournisseur KYC Didit n'est pas configuré.")

        import httpx
        payload = {
            "vendor_data": str(user_id),
            "workflow_id": settings.DIDIT_WORKFLOW_ID,
        }
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(f"{self.api_url.rstrip('/')}/session/", json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()

        session_id = data.get("session_id")
        session_token = data.get("session_token")
        verification_url = data.get("url")
        if not all((session_id, session_token, verification_url)):
            raise RuntimeError("Réponse de session Didit incomplète.")
        return {
            "session_id": str(session_id),
            "session_token": str(session_token),
            "verification_url": str(verification_url),
            "provider_status": str(data.get("status") or "Not Started"),
        }

    def verify_webhook_signature(
        self,
        raw_payload: bytes,
        signature_header: Optional[str],
        *,
        timestamp_header: Optional[str] = None,
        parsed_payload: Optional[Dict[str, Any]] = None,
        now: Optional[int] = None,
    ) -> bool:
        """Verify Didit V3 canonical JSON, with raw-body support for legacy deliveries."""
        if (
            not signature_header
            or not self.webhook_secret
            or self.webhook_secret.startswith("didit_webhook_secret")
        ):
            return False

        if timestamp_header is not None:
            try:
                timestamp = int(timestamp_header)
            except (TypeError, ValueError):
                return False
            if abs((now if now is not None else int(time.time())) - timestamp) > 300:
                return False

        signed_payload = raw_payload
        if parsed_payload is not None:
            signed_payload = json.dumps(
                parsed_payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        expected_sig = hmac.new(self.webhook_secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature_header)

didit_service = DiditService()

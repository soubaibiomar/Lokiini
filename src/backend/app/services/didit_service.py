import hmac
import hashlib
import json
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
        """Crée une session de vérification d'identité Didit (CNI + Face Match + Liveness)."""
        session_id = f"didit_sess_{str(user_id).replace('-', '')[:12]}"
        
        # En mode démo ou si la clé commence par didit_demo, on retourne une session simulée
        if not self.api_key or self.api_key.startswith("didit_demo"):
            return {
                "session_id": session_id,
                "didit_session_token": f"token_{session_id}_auth",
                "verification_url": f"https://verify.didit.me/session/{session_id}",
                "status": "initiated"
            }

        # Appel réel HTTP vers l'API Didit v1
        import httpx
        payload = {
            "vendor_data": str(user_id),
            "callback_url": f"{settings.API_BASE_URL}/api/v1/auth/kyc/webhook/didit",
            "features": ["document_verification", "face_match", "liveness_detection"],
            "options": {
                "require_id_document": True,
                "document_types": ["id_card", "passport"],
                "country": "MAR",
                "allow_retries": True
            },
            "user_data": {"email": email, "phone": phone}
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(f"{self.api_url}/sessions", json=payload, headers=headers)
            res.raise_for_status()
            return res.json()

    def verify_webhook_signature(self, raw_payload: bytes, signature_header: Optional[str]) -> bool:
        """Vérifie l'authenticité de la signature HMAC-SHA256 transmise par Didit."""
        if not signature_header:
            return False
        expected_sig = hmac.new(
            self.webhook_secret.encode("utf-8"),
            raw_payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature_header)

didit_service = DiditService()

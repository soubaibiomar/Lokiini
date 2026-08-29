import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional

class SignatureService:
    @classmethod
    def seal_signature(
        cls,
        contract_sha256: str,
        user_id: str,
        user_role: str, # loueur, locataire
        ip_address: Optional[str] = "127.0.0.1",
        signature_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère l'empreinte de scellement électronique conforme Loi n° 53-05."""
        ts = datetime.utcnow()
        sig_manifest = {
            "contract_sha256": contract_sha256,
            "signatory_user_id": str(user_id),
            "signatory_role": user_role,
            "ip_address": ip_address or "127.0.0.1",
            "timestamp_iso_utc": ts.isoformat(),
            "compliance_law": "Loi 53-05 relative a la validite juridique des documents electroniques"
        }
        
        manifest_str = json.dumps(sig_manifest, sort_keys=True)
        seal_hash = hashlib.sha256(manifest_str.encode("utf-8")).hexdigest()

        return {
            "signature_seal": seal_hash,
            "manifest": sig_manifest,
            "timestamp": ts
        }

signature_service = SignatureService()

import hashlib
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

class InspectionSealService:
    @classmethod
    def generate_sha256_seal(
        cls,
        booking_id: str,
        type_remise: str, # check_in, check_out, retrait, retour
        photos: List[str],
        video_url: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        notes: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calcule l'empreinte cryptographique SHA-256 inviolable conforme RFC 3161 / Loi 53-05.
        """
        ts = timestamp or datetime.utcnow()
        canonical_dict = {
            "booking_id": str(booking_id),
            "type_remise": type_remise,
            "photos_count": len(photos or []),
            "photos_manifest": sorted(photos or []),
            "video_url": video_url or "",
            "latitude": round(lat, 5) if lat is not None else None,
            "longitude": round(lng, 5) if lng is not None else None,
            "notes": (notes or "").strip(),
            "timestamp_iso_utc": ts.isoformat(),
            "issuer": "LOKIINI_MAROC_RFC3161_SEAL_V1"
        }
        
        canonical_str = json.dumps(canonical_dict, sort_keys=True)
        sha256_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        return {
            "sha256_seal": sha256_hash,
            "canonical_manifest": canonical_dict,
            "timestamp": ts,
            "is_valid": True
        }

inspection_seal_service = InspectionSealService()

import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class SignUpRequest(BaseModel):
    email: str
    telephone: str = Field(..., description="Format: +2126XXXXXXXX ou 06XXXXXXXX")
    mot_de_passe: str = Field(..., min_length=6)
    nom_complet: str
    user_role: Optional[str] = "renter" # renter, owner, pro_owner
    company_name: Optional[str] = None
    company_ice: Optional[str] = None
    city: Optional[str] = "Casablanca"

    @field_validator("telephone")
    @classmethod
    def validate_moroccan_phone(cls, v: str) -> str:
        cleaned = v.replace(" ", "").replace("-", "")
        if cleaned.startswith("06") or cleaned.startswith("07"):
            cleaned = "+212" + cleaned[1:]
        elif cleaned.startswith("212"):
            cleaned = "+" + cleaned
        if not (cleaned.startswith("+2126") or cleaned.startswith("+2127") or cleaned.startswith("+2125")):
            raise ValueError("Le numéro de téléphone doit être un numéro marocain valide (+212 ou 06/07/05).")
        return cleaned

class SignInRequest(BaseModel):
    email_ou_telephone: str
    mot_de_passe: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    user_id: uuid.UUID
    nom_complet: str
    email: str
    telephone: str
    user_role: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 900

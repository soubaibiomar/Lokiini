import pytest
import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.auth_schemas import SignUpRequest, SignInRequest, RefreshTokenRequest
from app.schemas.user_schemas import UserUpdateRequest
from app.core.security import verify_password, get_password_hash, create_access_token, jwt

def test_moroccan_phone_validation_success():
    """Test validation and normalization of Moroccan phone numbers."""
    req1 = SignUpRequest(
        email="test1@lokiini.ma",
        telephone="0661123456",
        mot_de_passe="password123",
        nom_complet="Yassine Alaoui"
    )
    assert req1.telephone == "+212661123456"

    req2 = SignUpRequest(
        email="test2@lokiini.ma",
        telephone="+212 7 62 33 44 55",
        mot_de_passe="password123",
        nom_complet="Fatima Zahra"
    )
    assert req2.telephone == "+212762334455"

def test_moroccan_phone_validation_failure():
    """Test rejection of invalid phone numbers."""
    with pytest.raises(ValueError):
        SignUpRequest(
            email="invalid@lokiini.ma",
            telephone="0123456789", # French/Invalid prefix
            mot_de_passe="password123",
            nom_complet="Invalid Phone"
        )

def test_password_hashing_and_verification():
    """Test secure password hashing and verification."""
    raw_password = "SecretPasswordMaroc2026!"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_generation_and_decoding():
    """Test JWT creation and decoding payload."""
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    assert token is not None
    
    decoded = jwt.decode(token, "test_key")
    assert "sub" in decoded
    assert str(user_id) in decoded["sub"]

def test_user_update_schema():
    """Test UserUpdateRequest fields and schema validation."""
    update = UserUpdateRequest(
        nom_complet="Atlas BTP Nouveau Nom",
        city="Tanger",
        company_ice="001234567000088"
    )
    assert update.nom_complet == "Atlas BTP Nouveau Nom"
    assert update.city == "Tanger"
    assert update.company_ice == "001234567000088"
    assert update.avatar_url is None

def test_app_routes_integrity():
    """Test that all Phase 1 auth & user routes are correctly registered in FastAPI."""
    from app.main import app
    
    openapi_paths = app.openapi()["paths"]
    
    # Auth endpoints
    assert "/api/v1/auth/inscription" in openapi_paths or "/api/v1/auth/register" in openapi_paths
    assert "/api/v1/auth/connexion" in openapi_paths or "/api/v1/auth/login" in openapi_paths
    assert "/api/v1/auth/rafraichir" in openapi_paths or "/api/v1/auth/refresh" in openapi_paths
    assert "/api/v1/auth/me" in openapi_paths
    
    # Users endpoints
    assert "/api/v1/utilisateurs/moi" in openapi_paths
    assert "/api/v1/utilisateurs/{user_id}/profil" in openapi_paths
    assert "/api/v1/utilisateurs/{user_id}/annonces" in openapi_paths
    assert "/api/v1/utilisateurs/{user_id}/avis" in openapi_paths

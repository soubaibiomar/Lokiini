"""Critical cross-domain journey against an isolated PostgreSQL/PostGIS database.

Firebase and Didit are external systems. Their adapters are replaced only inside
this test; all Lokiini authorization, persistence, state transitions and evidence
handling execute through the real FastAPI application and real database schema.
The payment-provider boundary is advanced through the server-only state machine
because no payment provider is configured in development and runtime fake success
is deliberately forbidden.
"""

import hashlib
import hmac
import json
import time
import uuid
from datetime import date, timedelta
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import select, text

from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.db.base import Base
from app.main import app
from app.models.models import DepositRecord, RentalPayment, Reservation, User
from app.services import firebase_identity
from app.services.booking_state_machine import BookingAction, BookingActor, booking_state_machine
from app.services.didit_service import didit_service
from app.services.meilisearch_service import meilisearch_service


pytestmark = pytest.mark.integration


async def _clean_database():
    table_names = [table.name for table in reversed(Base.metadata.sorted_tables)]
    quoted = ", ".join(f'"{name}"' for name in table_names)
    async with AsyncSessionLocal() as session:
        await session.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))
        await session.commit()


def _token(label: str) -> str:
    return f"{label}." + ("x" * 120) + ".signature"


async def _authenticate(client: httpx.AsyncClient, token: str):
    response = await client.post("/api/v1/auth/session", json={"id_token": token})
    assert response.status_code == 200, response.text
    assert "httponly" in response.headers["set-cookie"].lower()
    return response.json()


async def _upload_photos(client: httpx.AsyncClient, booking_id: str, inspection_type: str):
    evidence_ids = []
    for index in range(3):
        content = b"\x89PNG\r\n\x1a\n" + f"lokiini-{inspection_type}-{index}".encode()
        response = await client.post(
            "/api/v1/inspections/evidence",
            data={"booking_id": booking_id, "inspection_type": inspection_type},
            files={"evidence_file": (f"evidence-{index}.png", content, "image/png")},
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["sha256_hash"] == hashlib.sha256(content).hexdigest()
        evidence_ids.append(body["id"])
    return evidence_ids


async def _submit_inspection(client, booking_id, inspection_type, evidence_ids, key):
    response = await client.post(
        "/api/v1/inspections",
        headers={"Idempotency-Key": key},
        json={
            "booking_id": booking_id,
            "inspection_type": inspection_type,
            "evidence_ids": evidence_ids,
            "condition": "good",
            "existing_damage": "Aucun dommage supplémentaire observé.",
            "accessories": ["Câble", "Mallette"],
            "serial_number": "LK-TEST-001",
            "meter_type": "none",
            "meter_reading": None,
            "notes": "Inspection automatisée du parcours critique.",
            "confirmed": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_register_authenticate_verify_publish_reserve_and_complete(
    isolated_database_url, monkeypatch,
):
    await _clean_database()
    owner_token, renter_token, outsider_token = _token("owner"), _token("renter"), _token("outsider")
    claims_by_token = {
        owner_token: {"uid": "firebase-owner", "email": "owner@test.lokiini.ma", "email_verified": True, "name": "Owner Test"},
        renter_token: {"uid": "firebase-renter", "email": "renter@test.lokiini.ma", "email_verified": True, "name": "Renter Test"},
        outsider_token: {"uid": "firebase-outsider", "email": "outsider@test.lokiini.ma", "email_verified": True, "name": "Outsider Test"},
    }

    async def verify_id_token(token):
        if token not in claims_by_token:
            raise firebase_identity.InvalidFirebaseToken("test token rejected")
        return claims_by_token[token]

    async def create_session_cookie(token, _expires_in):
        return f"test-session::{claims_by_token[token]['uid']}"

    async def verify_session_cookie(cookie):
        uid = cookie.removeprefix("test-session::")
        for claims in claims_by_token.values():
            if claims["uid"] == uid:
                return claims
        raise firebase_identity.InvalidFirebaseToken("test session rejected")

    async def initiate_kyc(user_id, email=None, phone=None):
        return {
            "session_id": f"didit-test-{user_id}",
            "session_token": "provider-session-token",
            "verification_url": "https://provider.test/verification",
            "provider_status": "Not Started",
        }

    async def no_search_index(*_args, **_kwargs):
        return None

    monkeypatch.setattr(firebase_identity, "verify_id_token", verify_id_token)
    monkeypatch.setattr(firebase_identity, "create_session_cookie", create_session_cookie)
    monkeypatch.setattr(firebase_identity, "verify_session_cookie", verify_session_cookie)
    monkeypatch.setattr(didit_service, "initiate_verification_session", initiate_kyc)
    monkeypatch.setattr(meilisearch_service, "index_article", no_search_index)
    monkeypatch.setattr(meilisearch_service, "search_articles", no_search_index)

    transport = httpx.ASGITransport(app=app)
    client_options = {
        "transport": transport,
        "base_url": "http://testserver",
        "headers": {"Origin": settings.cors_origins[0]},
    }
    async with (
        httpx.AsyncClient(**client_options) as owner,
        httpx.AsyncClient(**client_options) as renter,
        httpx.AsyncClient(**client_options) as outsider,
    ):
        owner_profile = await _authenticate(owner, owner_token)
        renter_profile = await _authenticate(renter, renter_token)
        await _authenticate(outsider, outsider_token)

        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as anonymous:
            missing_credentials = await anonymous.get("/api/v1/auth/me")
        assert missing_credentials.status_code == 401
        assert missing_credentials.json()["erreur"]["code"] == "AUTH_REQUIRED"

        initiation = await renter.post("/api/v1/auth/kyc/initier", json={})
        assert initiation.status_code == 200, initiation.text
        kyc_session = initiation.json()["session_id"]
        webhook_payload = {
            "event_id": str(uuid.uuid4()),
            "webhook_type": "status.updated",
            "timestamp": int(time.time()),
            "session_id": kyc_session,
            "vendor_data": renter_profile["id"],
            "status": "Approved",
            "session_kind": "KYC",
        }
        canonical = json.dumps(webhook_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        timestamp = str(webhook_payload["timestamp"])
        signature = hmac.new(didit_service.webhook_secret.encode(), canonical, hashlib.sha256).hexdigest()
        verified = await renter.post(
            "/api/v1/auth/kyc/webhook/didit",
            content=json.dumps(webhook_payload).encode(),
            headers={"Content-Type": "application/json", "X-Timestamp": timestamp, "X-Signature-V2": signature},
        )
        assert verified.status_code == 200, verified.text
        assert verified.json()["status"] == "verified"

        published = await owner.post("/api/v1/equipment", json={
            "titre": "Perceuse professionnelle test",
            "description": "Annonce isolée créée uniquement dans la base de test.",
            "categorie": "tools",
            "prix_par_jour": 100,
            "montant_caution": 300,
            "photos": [],
            "specs": {"power": "18V"},
            "city": "Casablanca",
            "adresse_approximative": "Maarif",
            "is_available": True,
            "calendrier_disponibilite": {},
        })
        assert published.status_code == 201, published.text
        equipment_id = published.json()["article_id"]

        search = await renter.get("/api/v1/equipment", params={"q": "Perceuse", "city": "Casablanca"})
        assert search.status_code == 200, search.text
        assert equipment_id in {row["id"] for row in search.json()["donnees"]}

        start = date.today() + timedelta(days=30)
        end = start + timedelta(days=2)
        reservation = await renter.post("/api/v1/bookings/create", json={
            "article_id": equipment_id,
            "date_debut": start.isoformat(),
            "date_fin": end.isoformat(),
            "mode_paiement": "cash_on_delivery",
            "mode_caution": "cash",
        })
        assert reservation.status_code == 201, reservation.text
        booking_id = reservation.json()["reservation_id"]
        assert reservation.json()["statut_reservation"] == "en_attente_approbation"

        outsider_read = await outsider.get(f"/api/v1/bookings/{booking_id}")
        assert outsider_read.status_code == 403
        assert outsider_read.json()["erreur"]["code"] == "FORBIDDEN"

        accepted = await owner.patch(f"/api/v1/bookings/{booking_id}/status", json={"action": "owner_accept"})
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["nouveau_statut"] == "acceptee"

        conflict = await renter.post("/api/v1/bookings/create", json={
            "article_id": equipment_id,
            "date_debut": start.isoformat(),
            "date_fin": end.isoformat(),
        })
        assert conflict.status_code == 400
        assert conflict.json()["erreur"]["code"] == "BOOKING_DATE_UNAVAILABLE"

        # This is a test-only provider driver: production exposes no fake payment success.
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Reservation).where(Reservation.id == uuid.UUID(booking_id)).with_for_update())
            booking = result.scalars().one()
            booking_state_machine.transition(booking, BookingAction.START_PAYMENT, BookingActor.SYSTEM)
            session.add(RentalPayment(
                booking_id=booking.id, provider="test-provider",
                provider_transaction_id=f"payment-{booking.id}", idempotency_key=f"payment-{booking.id}",
                currency="MAD", amount_mad=Decimal(booking.prix_total), status="succeeded",
            ))
            session.add(DepositRecord(
                booking_id=booking.id, provider="test-provider",
                provider_transaction_id=f"deposit-{booking.id}", idempotency_key=f"deposit-{booking.id}",
                currency="MAD", authorized_amount_mad=Decimal(booking.montant_caution),
                captured_amount_mad=Decimal("0"), released_amount_mad=Decimal("0"), status="authorized",
            ))
            booking_state_machine.transition(booking, BookingAction.CONFIRM_PAYMENT, BookingActor.SYSTEM)
            await session.commit()

        ready = await owner.patch(f"/api/v1/bookings/{booking_id}/status", json={"action": "mark_ready"})
        assert ready.status_code == 200, ready.text
        assert ready.json()["nouveau_statut"] == "prete_remise"

        check_in_evidence = await _upload_photos(renter, booking_id, "check_in")
        check_in = await _submit_inspection(renter, booking_id, "check_in", check_in_evidence, "check-in-journey-key-0001")
        check_in_confirmed = await owner.post(f"/api/v1/inspections/{check_in['id']}/confirm")
        assert check_in_confirmed.status_code == 200, check_in_confirmed.text
        active = await renter.get(f"/api/v1/bookings/{booking_id}")
        assert active.json()["statut_reservation"] == "en_cours"

        check_out_evidence = await _upload_photos(owner, booking_id, "check_out")
        check_out = await _submit_inspection(owner, booking_id, "check_out", check_out_evidence, "check-out-journey-key-001")
        check_out_confirmed = await renter.post(f"/api/v1/inspections/{check_out['id']}/confirm")
        assert check_out_confirmed.status_code == 200, check_out_confirmed.text
        completed = await renter.get(f"/api/v1/bookings/{booking_id}")
        assert completed.status_code == 200
        assert completed.json()["statut_reservation"] == "termine"
        assert owner_profile["id"] != renter_profile["id"]
        await engine.dispose()


@pytest.mark.asyncio
async def test_damage_dispute_evidence_decision_and_deposit_resolution(
    isolated_database_url, monkeypatch,
):
    await _clean_database()
    owner_token, renter_token, admin_token = _token("owner"), _token("renter"), _token("admin")
    claims_by_token = {
        owner_token: {"uid": "firebase-owner-2", "email": "owner2@test.lokiini.ma", "email_verified": True, "name": "Owner 2"},
        renter_token: {"uid": "firebase-renter-2", "email": "renter2@test.lokiini.ma", "email_verified": True, "name": "Renter 2"},
        admin_token: {"uid": "firebase-admin", "email": "admin@test.lokiini.ma", "email_verified": True, "name": "Admin Test"},
    }

    async def verify_id_token(token):
        if token not in claims_by_token:
            raise firebase_identity.InvalidFirebaseToken("test token rejected")
        return claims_by_token[token]

    async def create_session_cookie(token, _expires_in):
        return f"test-session::{claims_by_token[token]['uid']}"

    async def verify_session_cookie(cookie):
        uid = cookie.removeprefix("test-session::")
        for claims in claims_by_token.values():
            if claims["uid"] == uid:
                return claims
        raise firebase_identity.InvalidFirebaseToken("test session rejected")

    async def no_search_index(*_args, **_kwargs):
        return None

    monkeypatch.setattr(firebase_identity, "verify_id_token", verify_id_token)
    monkeypatch.setattr(firebase_identity, "create_session_cookie", create_session_cookie)
    monkeypatch.setattr(firebase_identity, "verify_session_cookie", verify_session_cookie)
    monkeypatch.setattr(meilisearch_service, "index_article", no_search_index)
    monkeypatch.setattr(meilisearch_service, "search_articles", no_search_index)

    transport = httpx.ASGITransport(app=app)
    client_options = {
        "transport": transport,
        "base_url": "http://testserver",
        "headers": {"Origin": settings.cors_origins[0]},
    }
    async with (
        httpx.AsyncClient(**client_options) as owner,
        httpx.AsyncClient(**client_options) as renter,
        httpx.AsyncClient(**client_options) as admin,
    ):
        owner_profile = await _authenticate(owner, owner_token)
        renter_profile = await _authenticate(renter, renter_token)
        admin_profile = await _authenticate(admin, admin_token)

        # Set admin and verified renter directly in DB
        async with AsyncSessionLocal() as session:
            adm_res = await session.execute(select(User).where(User.id == uuid.UUID(admin_profile["id"])))
            adm_user = adm_res.scalars().one()
            adm_user.user_role = "admin"

            rnt_res = await session.execute(select(User).where(User.id == uuid.UUID(renter_profile["id"])))
            rnt_user = rnt_res.scalars().one()
            rnt_user.statut_verification = "verified"
            await session.commit()

        # Create equipment & booking
        published = await owner.post("/api/v1/equipment", json={
            "titre": "Scie circulaire test",
            "description": "Annonce de test pour litige.",
            "categorie": "tools",
            "prix_par_jour": 80,
            "montant_caution": 500,
            "photos": [],
            "specs": {},
            "city": "Rabat",
            "is_available": True,
        })
        assert published.status_code == 201, published.text
        equipment_id = published.json()["article_id"]

        start = date.today() + timedelta(days=10)
        end = start + timedelta(days=2)
        reservation = await renter.post("/api/v1/bookings/create", json={
            "article_id": equipment_id,
            "date_debut": start.isoformat(),
            "date_fin": end.isoformat(),
            "mode_paiement": "cash_on_delivery",
            "mode_caution": "cash",
        })
        assert reservation.status_code == 201, reservation.text
        booking_id = reservation.json()["reservation_id"]

        # Accept and establish deposit
        await owner.patch(f"/api/v1/bookings/{booking_id}/status", json={"action": "owner_accept"})

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Reservation).where(Reservation.id == uuid.UUID(booking_id)).with_for_update())
            booking = result.scalars().one()
            booking_state_machine.transition(booking, BookingAction.START_PAYMENT, BookingActor.SYSTEM)
            session.add(DepositRecord(
                booking_id=booking.id, provider="test-provider",
                provider_transaction_id=f"deposit-dispute-{booking.id}", idempotency_key=f"deposit-dispute-{booking.id}",
                currency="MAD", authorized_amount_mad=Decimal("500.00"),
                captured_amount_mad=Decimal("0"), released_amount_mad=Decimal("0"), status="authorized",
            ))
            booking_state_machine.transition(booking, BookingAction.CONFIRM_PAYMENT, BookingActor.SYSTEM)
            await session.commit()

        # 1. Open Dispute for damage
        dispute_res = await owner.post(
            "/api/v1/disputes",
            headers={"Idempotency-Key": f"dispute-open-{booking_id}"},
            json={
                "booking_id": booking_id,
                "reason_code": "equipment_condition",
                "description": "Carter endommagé lors de la remise de l'équipement au retour.",
            },
        )
        assert dispute_res.status_code == 201, dispute_res.text
        dispute_id = dispute_res.json()["id"]
        assert dispute_res.json()["status"] == "open"

        # 2. Upload dispute evidence photo
        photo_bytes = b"\x89PNG\r\n\x1a\n" + b"dispute-damage-photo"
        evidence_res = await owner.post(
            f"/api/v1/disputes/{dispute_id}/evidence",
            files={"evidence_file": ("damage.png", photo_bytes, "image/png")},
        )
        assert evidence_res.status_code == 201, evidence_res.text
        assert evidence_res.json()["sha256_hash"] == hashlib.sha256(photo_bytes).hexdigest()

        # 3. Owner and Renter submit their evidence
        submit_owner = await owner.post(f"/api/v1/disputes/{dispute_id}/submit")
        assert submit_owner.status_code == 200, submit_owner.text
        assert submit_owner.json()["status"] == "evidence_collection"
        assert submit_owner.json()["evidence_submitted_by_owner"] is True

        submit_renter = await renter.post(f"/api/v1/disputes/{dispute_id}/submit")
        assert submit_renter.status_code == 200, submit_renter.text
        assert submit_renter.json()["status"] == "under_review"
        assert submit_renter.json()["evidence_submitted_by_renter"] is True

        # 4. Admin records decision
        decision_res = await admin.post(
            f"/api/v1/disputes/{dispute_id}/decision",
            json={
                "decision_code": "partial_deposit_capture",
                "deposit_capture_amount_mad": 150.00,
                "decision_summary": "Dommages confirmés sur le carter de protection; retenue partielle de 150 MAD.",
            },
        )
        assert decision_res.status_code == 200, decision_res.text
        assert decision_res.json()["status"] == "decision"
        assert decision_res.json()["decision_code"] == "partial_deposit_capture"
        assert decision_res.json()["deposit_capture_amount_mad"] == 150.00
        await engine.dispose()


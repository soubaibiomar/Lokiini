import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.authorization import require_resource_access
from app.core.database import get_db
from app.models.models import Article, Reservation, User
from app.routers.auth import get_current_user
from app.schemas.contract_schemas import (
    ContractEquipmentResponse,
    ContractPartyResponse,
    ContractResponse,
    ContractSignRequest,
)
from app.services.contract_generator_service import contract_generator_service


router = APIRouter(tags=["Contrats de location"])

CONTRACT_READY_STATUSES = {
    "confirmee",
    "prete_remise",
    "en_cours",
    "en_attente_validation",
    "termine",
    "en_litige",
    "resolu",
}


@router.get("/contrats/{booking_id}", response_model=ContractResponse)
@router.get("/contracts/{booking_id}", response_model=ContractResponse)
async def get_booking_contract(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a reviewable contract from an authorized confirmed reservation."""
    result = await db.execute(select(Reservation).where(Reservation.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réservation introuvable.")

    require_resource_access(current_user, booking.locataire_id, booking.loueur_id)
    if booking.statut not in CONTRACT_READY_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CONTRACT_NOT_READY",
                "message": "Le contrat sera généré lorsque la réservation sera confirmée.",
            },
        )

    article = (await db.execute(select(Article).where(Article.id == booking.article_id))).scalars().first()
    renter = (await db.execute(select(User).where(User.id == booking.locataire_id))).scalars().first()
    owner = (await db.execute(select(User).where(User.id == booking.loueur_id))).scalars().first()
    if not article or not renter or not owner:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CONTRACT_DATA_INCOMPLETE",
                "message": "Les informations nécessaires au contrat sont incomplètes.",
            },
        )

    booking_data = {
        "id": str(booking.id),
        "nombre_jours": booking.total_days,
        "date_debut": booking.date_debut.isoformat(),
        "date_fin": booking.date_fin.isoformat(),
        "prix_total": float(booking.prix_total),
        "montant_caution": float(booking.montant_caution),
        "payment_method": booking.payment_method,
        "deposit_method": "cash",
    }
    article_data = {
        "titre": article.titre,
        "categorie": article.categorie,
        "description": article.description,
    }
    renter_data = {
        "nom_complet": renter.nom_complet,
        "cin_number": renter.cin_number,
        "company_ice": renter.company_ice,
        "telephone": renter.telephone,
        "city": renter.city,
    }
    owner_data = {
        "nom_complet": owner.nom_complet,
        "cin_number": owner.cin_number,
        "company_ice": owner.company_ice,
        "telephone": owner.telephone,
        "city": owner.city,
    }
    contract_data = contract_generator_service.generate_lease_contract(
        booking_data=booking_data,
        article_data=article_data,
        renter_data=renter_data,
        owner_data=owner_data,
    )

    # The current database has only one legacy aggregate signature field. It
    # cannot prove which party signed, so per-party completion remains false.
    return ContractResponse(
        booking_id=booking.id,
        booking_status=booking.statut,
        contract_number=contract_data["contract_number"],
        contract_text=contract_data["contract_text"],
        contract_sha256=contract_data["contract_sha256"],
        applicable_law=contract_data["applicable_law"],
        language=contract_data["language"],
        available_languages=contract_data["available_languages"],
        owner=ContractPartyResponse(
            user_id=owner.id,
            name=owner.nom_complet,
            city=owner.city,
            company_name=owner.company_name,
            company_ice=owner.company_ice,
        ),
        renter=ContractPartyResponse(
            user_id=renter.id,
            name=renter.nom_complet,
            city=renter.city,
            company_name=renter.company_name,
            company_ice=renter.company_ice,
        ),
        equipment=ContractEquipmentResponse(
            article_id=article.id,
            title=article.titre,
            category=article.categorie,
            description=article.description,
        ),
        start_date=booking.date_debut,
        end_date=booking.date_fin,
        number_of_days=booking.total_days,
        rental_price_mad=float(booking.prix_total),
        deposit_amount_mad=float(booking.montant_caution),
        payment_method=contract_data["payment_method_label"],
        deposit_method=contract_data["deposit_method_label"],
        responsibilities=contract_data["responsibilities"],
        important_conditions=contract_data["important_conditions"],
        signature_available=False,
        owner_signature_status="unavailable",
        renter_signature_status="unavailable",
        completed=False,
        document_url=booking.contrat_pdf_url,
        est_signe_locataire=False,
        est_signe_loueur=False,
        signe_le=None,
        genere_le=contract_data["generated_at"],
    )


@router.post("/contrats/{booking_id}/signer", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
@router.post("/contracts/{booking_id}/sign", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
async def sign_booking_contract(
    booking_id: uuid.UUID,
    payload: ContractSignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject signing until a professionally validated provider is configured."""
    if not payload.consentement_explicite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CONTRACT_CONSENT_REQUIRED", "message": "Vous devez confirmer avoir lu le contrat."},
        )
    booking = (
        await db.execute(select(Reservation).where(Reservation.id == booking_id))
    ).scalars().first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réservation introuvable.")
    require_resource_access(current_user, booking.locataire_id, booking.loueur_id)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "SIGNATURE_UNAVAILABLE",
            "status": "pending",
            "message": "Aucun prestataire de signature professionnellement validé n’est configuré.",
        },
    )


@router.get("/contrats/{booking_id}/certificat", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
@router.get("/contracts/{booking_id}/certificate", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
async def get_signature_certificate(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return no certificate while qualified signing is unavailable."""
    booking = (
        await db.execute(select(Reservation).where(Reservation.id == booking_id))
    ).scalars().first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réservation introuvable.")
    require_resource_access(current_user, booking.locataire_id, booking.loueur_id)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "CERTIFICATE_UNAVAILABLE",
            "status": "pending",
            "message": "Aucun certificat de signature qualifiée n’est disponible.",
        },
    )

import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Boolean, Numeric, Integer, Text, ForeignKey,
    DateTime, Date, JSON, CheckConstraint, Index, UniqueConstraint, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.base import Base

# 1. Table Utilisateur / User
class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Uniqueness is enforced by the migration-managed partial index so NULL is
    # allowed for legacy/password-only development accounts.
    firebase_uid = Column(String(128), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    telephone = Column(String(30), unique=True, nullable=True)
    nom_complet = Column(String(150), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    cin_number = Column(String(100), nullable=True) # Encrypted
    avatar_url = Column(Text, nullable=True)
    statut_verification = Column(String(30), default="not_started")
    didit_session_id = Column(String(100), nullable=True)
    kyc_provider_status = Column(String(30), nullable=True)
    kyc_last_event_id = Column(String(36), nullable=True)
    verifie_le = Column(DateTime(timezone=True), nullable=True)
    note = Column(Numeric(3, 2), default=5.00)
    temps_reponse_minutes = Column(Integer, default=30)
    user_role = Column(String(30), default="renter") # renter, owner, pro_owner, admin
    company_name = Column(String(150), nullable=True)
    company_ice = Column(String(30), nullable=True) # ICE Maroc
    city = Column(String(60), default="Casablanca")
    plan_abonnement = Column(String(30), default="Gratuit") # Gratuit, Premium, Pro, Entreprise
    abonnement_valable_jusqu = Column(DateTime(timezone=True), nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    modifie_le = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Aliases properties for backward compatibility
    @property
    def full_name(self): return self.nom_complet
    @property
    def phone_number(self): return self.telephone
    @property
    def is_kyc_verified(self): return self.statut_verification == "verified"
    @property
    def created_at(self): return self.cree_le

    articles = relationship("Article", back_populates="loueur", cascade="all, delete-orphan")
    reservations_locataire = relationship("Reservation", foreign_keys="Reservation.locataire_id", back_populates="locataire")
    reservations_loueur = relationship("Reservation", foreign_keys="Reservation.loueur_id", back_populates="loueur")

# Alias
User = Utilisateur

# 2. Table Article / Equipment
class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loueur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    categorie = Column(String(60), nullable=False) # btp, audiovisual, tools, event, outdoor, transport, cleaning, energy
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    photos = Column(JSONB, default=list)
    prix_par_jour = Column(Numeric(10, 2), nullable=False)
    montant_caution = Column(Numeric(10, 2), default=0.00)
    niveau_risque = Column(String(20), default="faible") # faible, moyen, eleve
    localisation = Column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)
    city = Column(String(60), nullable=False, default="Casablanca")
    adresse = Column(Text, nullable=False)
    calendrier_disponibilite = Column(JSONB, default=dict)
    statut = Column(String(30), default="actif") # actif, en_pause, archive, en_revision
    is_available = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    discount_pct = Column(Integer, default=0)
    specs_json = Column(JSONB, default=dict)
    nb_vues = Column(Integer, default=0)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    modifie_le = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Aliases properties
    @property
    def owner_id(self): return self.loueur_id
    @property
    def title(self): return self.titre
    @property
    def category(self): return self.categorie
    @property
    def address(self): return self.adresse
    @property
    def daily_price_mad(self): return self.prix_par_jour
    @property
    def deposit_amount_mad(self): return self.montant_caution
    @property
    def images_urls(self): return self.photos
    @property
    def created_at(self): return self.cree_le
    @property
    def prix_par_semaine(self): return float(self.prix_par_jour) * 5 if self.prix_par_jour else None
    @property
    def prix_par_mois(self): return float(self.prix_par_jour) * 20 if self.prix_par_jour else None
    @property
    def mode_caution(self): return "cash"
    @property
    def kyc_requis(self): return self.niveau_risque != "faible"
    @property
    def specs(self): return self.specs_json or {}
    @property
    def adresse_approximative(self): return self.adresse

    loueur = relationship("Utilisateur", back_populates="articles")
    reservations = relationship("Reservation", back_populates="article")

# Alias
Equipment = Article

# 3. Table Reservation / Booking
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False)
    locataire_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    loueur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    prix_total = Column(Numeric(10, 2), nullable=False)
    montant_caution = Column(Numeric(10, 2), nullable=False)
    option_livraison = Column(String(40), default="retrait_sur_place") # retrait_sur_place, livraison_premium
    adresse_retrait = Column(Text, nullable=True)
    payment_method = Column(String(30), default="cash_cod") # cash_cod, cmi_card, cashplus
    # Values and transitions are authoritative in booking_state_machine.py.
    statut = Column(String(40), default="en_attente_approbation")
    cmi_status = Column(String(30), default="pending_cod")
    contrat_pdf_url = Column(Text, nullable=True)
    contrat_sha256 = Column(String(64), nullable=True)
    contrat_signe = Column(Boolean, default=False)
    contrat_signe_le = Column(DateTime(timezone=True), nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    modifie_le = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Aliases
    @property
    def equipment_id(self): return self.article_id
    @property
    def renter_id(self): return self.locataire_id
    @property
    def start_date(self): return self.date_debut
    @property
    def end_date(self): return self.date_fin
    @property
    def rental_total_mad(self): return self.prix_total
    @property
    def platform_commission_mad(self): return float(self.prix_total) * 0.15
    @property
    def deposit_hold_mad(self): return self.montant_caution
    @property
    def booking_status(self): return self.statut
    @property
    def created_at(self): return self.cree_le

    article = relationship("Article", back_populates="reservations")
    locataire = relationship("Utilisateur", foreign_keys=[locataire_id], back_populates="reservations_locataire")
    loueur = relationship("Utilisateur", foreign_keys=[loueur_id], back_populates="reservations_loueur")
    remises = relationship("Remise", back_populates="reservation", cascade="all, delete-orphan")
    confirmations_cash = relationship("ConfirmationCash", back_populates="reservation", cascade="all, delete-orphan")

# Alias
Booking = Reservation

class CMITransaction(Base):
    """Legacy CMI-shaped record retained for migration compatibility only."""
    __tablename__ = "cmi_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    cmi_auth_token = Column(String(255), nullable=True)
    cmi_trans_id = Column(String(100), nullable=True)
    card_brand = Column(String(20), nullable=True)
    preauth_amount_mad = Column(Numeric(10, 2), default=0.00)
    captured_amount_mad = Column(Numeric(10, 2), default=0.00)
    deposit_status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class RentalPayment(Base):
    __tablename__ = "rental_payments"
    __table_args__ = (
        UniqueConstraint("provider", "provider_transaction_id", name="uq_rental_payment_provider_transaction"),
        CheckConstraint("amount_mad >= 0", name="ck_rental_payment_amount_nonnegative"),
        CheckConstraint("status IN ('pending','requires_action','succeeded','failed','cancelled','partially_refunded','refunded')", name="ck_rental_payment_status"),
        Index("ix_rental_payments_booking_created", "booking_id", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="RESTRICT"), nullable=False)
    provider = Column(String(30), nullable=False)
    provider_transaction_id = Column(String(150), nullable=True)
    idempotency_key = Column(String(128), unique=True, nullable=False)
    currency = Column(String(3), nullable=False, default="MAD")
    amount_mad = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), nullable=False, default="pending")
    provider_status = Column(String(80), nullable=True)
    failure_code = Column(String(80), nullable=True)
    failure_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reconciled_at = Column(DateTime(timezone=True), nullable=True)


class PlatformFeeRecord(Base):
    __tablename__ = "platform_fee_records"
    __table_args__ = (
        CheckConstraint("amount_mad >= 0", name="ck_platform_fee_amount_nonnegative"),
        CheckConstraint("status IN ('pending','earned','reversed')", name="ck_platform_fee_status"),
        Index("ix_platform_fees_booking_created", "booking_id", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="RESTRICT"), nullable=False)
    rental_payment_id = Column(UUID(as_uuid=True), ForeignKey("rental_payments.id", ondelete="RESTRICT"), nullable=True)
    currency = Column(String(3), nullable=False, default="MAD")
    amount_mad = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class DepositRecord(Base):
    __tablename__ = "deposit_records"
    __table_args__ = (
        UniqueConstraint("provider", "provider_transaction_id", name="uq_deposit_provider_transaction"),
        CheckConstraint("authorized_amount_mad >= 0", name="ck_deposit_authorized_nonnegative"),
        CheckConstraint("captured_amount_mad >= 0", name="ck_deposit_captured_nonnegative"),
        CheckConstraint("released_amount_mad >= 0", name="ck_deposit_released_nonnegative"),
        CheckConstraint("captured_amount_mad <= authorized_amount_mad", name="ck_deposit_capture_within_authorization"),
        CheckConstraint("released_amount_mad <= authorized_amount_mad", name="ck_deposit_release_within_authorization"),
        CheckConstraint("status IN ('authorization_pending','authorized','authorization_failed','released','partially_captured','captured')", name="ck_deposit_status"),
        Index("ix_deposits_booking_created", "booking_id", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="RESTRICT"), nullable=False)
    provider = Column(String(30), nullable=False)
    provider_transaction_id = Column(String(150), nullable=True)
    idempotency_key = Column(String(128), unique=True, nullable=False)
    currency = Column(String(3), nullable=False, default="MAD")
    authorized_amount_mad = Column(Numeric(12, 2), nullable=False)
    captured_amount_mad = Column(Numeric(12, 2), nullable=False, default=0)
    released_amount_mad = Column(Numeric(12, 2), nullable=False, default=0)
    status = Column(String(30), nullable=False, default="authorization_pending")
    provider_status = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reconciled_at = Column(DateTime(timezone=True), nullable=True)


class RefundRecord(Base):
    __tablename__ = "refund_records"
    __table_args__ = (
        UniqueConstraint("provider", "provider_transaction_id", name="uq_refund_provider_transaction"),
        CheckConstraint("amount_mad > 0", name="ck_refund_amount_positive"),
        CheckConstraint("status IN ('pending','succeeded','failed')", name="ck_refund_status"),
        Index("ix_refunds_booking_created", "booking_id", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="RESTRICT"), nullable=False)
    rental_payment_id = Column(UUID(as_uuid=True), ForeignKey("rental_payments.id", ondelete="RESTRICT"), nullable=False)
    provider = Column(String(30), nullable=False)
    provider_transaction_id = Column(String(150), nullable=True)
    idempotency_key = Column(String(128), unique=True, nullable=False)
    currency = Column(String(3), nullable=False, default="MAD")
    amount_mad = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), nullable=False, default="pending")
    failure_code = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reconciled_at = Column(DateTime(timezone=True), nullable=True)


class OwnerPayout(Base):
    __tablename__ = "owner_payouts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_transaction_id", name="uq_payout_provider_transaction"),
        CheckConstraint("rental_amount_mad >= 0", name="ck_payout_rental_nonnegative"),
        CheckConstraint("platform_fee_amount_mad >= 0", name="ck_payout_fee_nonnegative"),
        CheckConstraint("payout_amount_mad >= 0", name="ck_payout_amount_nonnegative"),
        CheckConstraint("payout_amount_mad = rental_amount_mad - platform_fee_amount_mad", name="ck_payout_amount_balances"),
        CheckConstraint("status IN ('not_ready','pending','paid','failed','reversed')", name="ck_payout_status"),
        Index("ix_owner_payouts_owner_created", "owner_id", "created_at"),
        Index("ix_owner_payouts_booking_created", "booking_id", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="RESTRICT"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    provider = Column(String(30), nullable=False)
    provider_transaction_id = Column(String(150), nullable=True)
    idempotency_key = Column(String(128), unique=True, nullable=False)
    currency = Column(String(3), nullable=False, default="MAD")
    rental_amount_mad = Column(Numeric(12, 2), nullable=False)
    platform_fee_amount_mad = Column(Numeric(12, 2), nullable=False)
    payout_amount_mad = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), nullable=False, default="not_ready")
    failure_code = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reconciled_at = Column(DateTime(timezone=True), nullable=True)


class PaymentWebhookEvent(Base):
    __tablename__ = "payment_webhook_events"
    __table_args__ = (
        UniqueConstraint("provider", "provider_event_id", name="uq_payment_webhook_provider_event"),
        Index("ix_payment_webhooks_transaction", "provider", "provider_transaction_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(30), nullable=False)
    provider_event_id = Column(String(150), nullable=False)
    event_type = Column(String(80), nullable=False)
    provider_transaction_id = Column(String(150), nullable=True)
    payload_sha256 = Column(String(64), nullable=False)
    processing_status = Column(String(30), nullable=False, default="received")
    received_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

# 4. Table Remise / Handoff
class Remise(Base):
    __tablename__ = "remises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False) # retrait, retour
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="RESTRICT"), nullable=True)
    renter_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=True)
    submitted_by_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=True)
    photos = Column(JSONB, default=list)
    videos = Column(JSONB, default=list)
    video_url = Column(Text, nullable=True)
    # Legacy compatibility only. New evidence hashes live on InspectionEvidence.
    video_sha256_hash = Column(String(64), nullable=True)
    geolocalisation = Column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)
    horodatage = Column(DateTime(timezone=True), default=datetime.utcnow)
    signatures = Column(JSONB, default=dict)
    signed_by_owner = Column(Boolean, default=False)
    signed_by_renter = Column(Boolean, default=False)
    condition = Column(String(30), nullable=True)
    existing_damage = Column(Text, nullable=True)
    accessories = Column(JSONB, default=list)
    serial_number = Column(String(150), nullable=True)
    meter_type = Column(String(20), nullable=True)
    meter_reading = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text, nullable=True)
    statut = Column(String(30), default="en_attente") # en_attente, confirme
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    reservation = relationship("Reservation", back_populates="remises")
    evidence = relationship("InspectionEvidence", back_populates="inspection", cascade="all, delete-orphan")


class InspectionEvidence(Base):
    __tablename__ = "inspection_evidence"
    __table_args__ = (
        UniqueConstraint("storage_key", name="uq_inspection_evidence_storage_key"),
        CheckConstraint("media_kind IN ('photo','video')", name="ck_inspection_evidence_media_kind"),
        CheckConstraint("inspection_type IN ('check_in','check_out')", name="ck_inspection_evidence_type"),
        CheckConstraint("size_bytes > 0", name="ck_inspection_evidence_size_positive"),
        CheckConstraint("sha256_hash ~ '^[0-9a-f]{64}$'", name="ck_inspection_evidence_sha256"),
        Index("ix_inspection_evidence_booking_type", "reservation_id", "inspection_type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("remises.id", ondelete="CASCADE"), nullable=True)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False)
    renter_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    inspection_type = Column(String(20), nullable=False)
    media_kind = Column(String(10), nullable=False)
    original_filename = Column(String(255), nullable=False)
    storage_key = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    stored_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    inspection = relationship("Remise", back_populates="evidence")

# Alias
InspectionReport = Remise

# 5. Table ConfirmationCash
class ConfirmationCash(Base):
    __tablename__ = "confirmations_cash"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    montant_recu = Column(Numeric(10, 2), nullable=False)
    confirme_par = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False)
    confirme_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    reservation = relationship("Reservation", back_populates="confirmations_cash")

# 6. Table Conversation
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="SET NULL"), nullable=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="SET NULL"), nullable=True)
    participant1_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    participant2_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    dernier_message_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("participant1_id <> participant2_id", name="ck_conversations_distinct_participants"),
        Index(
            "uq_conversations_reservation_participants",
            func.least(participant1_id, participant2_id),
            func.greatest(participant1_id, participant2_id),
            reservation_id,
            unique=True,
            postgresql_where=reservation_id.is_not(None),
        ),
        Index(
            "uq_conversations_article_participants",
            func.least(participant1_id, participant2_id),
            func.greatest(participant1_id, participant2_id),
            article_id,
            unique=True,
            postgresql_where=(reservation_id.is_(None) & article_id.is_not(None)),
        ),
        Index("ix_conversations_participant1_updated", "participant1_id", "dernier_message_le"),
        Index("ix_conversations_participant2_updated", "participant2_id", "dernier_message_le"),
    )

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

# 7. Table Message
class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    expediteur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    contenu = Column(Text, nullable=False)
    lu = Column(Boolean, default=False)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

# 8. Table Avis / Review
class Avis(Base):
    __tablename__ = "avis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    avisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    avise_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    note = Column(Integer, nullable=False)
    commentaire = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

# Alias
Review = Avis

# 9. Table Abonnement
class Abonnement(Base):
    __tablename__ = "abonnements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    plan = Column(String(30), nullable=False) # Gratuit, Premium, Pro, Entreprise
    taux_commission = Column(Numeric(5, 2), nullable=False)
    prix_mad = Column(Numeric(10, 2), nullable=False)
    debute_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    expire_le = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(20), default="actif") # actif, expire, annule
    fonctionnalites = Column(JSONB, default=list)

# 10. Table Litige
class Litige(Base):
    __tablename__ = "litiges"
    __table_args__ = (
        CheckConstraint(
            "statut IN ('open','evidence_collection','under_review','decision','resolved')",
            name="ck_disputes_status",
        ),
        CheckConstraint(
            "reason_code IN ('equipment_condition','missing_accessory','late_return','handover_problem','payment_issue','cancellation','other')",
            name="ck_disputes_reason",
        ),
        CheckConstraint("deposit_capture_amount_mad IS NULL OR deposit_capture_amount_mad >= 0", name="ck_disputes_capture_nonnegative"),
        Index("ix_disputes_booking_created", "reservation_id", "cree_le"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False)
    renter_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    soumis_par = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False)
    reason_code = Column(String(40), nullable=False)
    motif = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    idempotency_key = Column(String(128), unique=True, nullable=False)
    photos = Column(JSONB, default=list)
    statut = Column(String(30), default="open", nullable=False)
    decision_code = Column(String(40), nullable=True)
    deposit_capture_amount_mad = Column(Numeric(12, 2), nullable=True)
    deposit_action_status = Column(String(30), nullable=True)
    decided_by_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=True)
    evidence_submitted_by_renter = Column(Boolean, nullable=False, default=False)
    evidence_submitted_by_owner = Column(Boolean, nullable=False, default=False)
    renter_submitted_at = Column(DateTime(timezone=True), nullable=True)
    owner_submitted_at = Column(DateTime(timezone=True), nullable=True)
    notes_resolution = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    modifie_le = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    resolu_le = Column(DateTime(timezone=True), nullable=True)

    evidence = relationship("DisputeEvidence", back_populates="dispute", cascade="all, delete-orphan")


class DisputeEvidence(Base):
    __tablename__ = "dispute_evidence"
    __table_args__ = (
        UniqueConstraint("storage_key", name="uq_dispute_evidence_storage_key"),
        CheckConstraint("media_kind IN ('photo','video','document')", name="ck_dispute_evidence_media_kind"),
        CheckConstraint("size_bytes > 0", name="ck_dispute_evidence_size_positive"),
        CheckConstraint("sha256_hash ~ '^[0-9a-f]{64}$'", name="ck_dispute_evidence_sha256"),
        Index("ix_dispute_evidence_dispute_stored", "dispute_id", "stored_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("litiges.id", ondelete="CASCADE"), nullable=False)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False)
    renter_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    media_kind = Column(String(10), nullable=False)
    original_filename = Column(String(255), nullable=False)
    storage_key = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    stored_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    dispute = relationship("Litige", back_populates="evidence")

# 11. Table Notification
class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_read_created", "utilisateur_id", "lu", "cree_le"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(30), nullable=False) # reservation, message, systeme, paiement
    titre = Column(String(255), nullable=False)
    corps = Column(Text, nullable=False)
    data = Column(JSONB, default=dict)
    lu = Column(Boolean, default=False)
    lu_le = Column(DateTime(timezone=True), nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

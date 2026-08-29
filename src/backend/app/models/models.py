import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Boolean, Numeric, Integer, Text, ForeignKey,
    DateTime, Date, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

# 1. Table Utilisateur / User
class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    telephone = Column(String(30), unique=True, nullable=False)
    nom_complet = Column(String(150), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    cin_number = Column(String(100), nullable=True) # Encrypted
    avatar_url = Column(Text, nullable=True)
    statut_verification = Column(String(30), default="en_attente") # en_attente, approuve, rejete, revision_manuelle
    didit_session_id = Column(String(100), nullable=True)
    verifie_le = Column(DateTime(timezone=True), nullable=True)
    kyc_liveness_score = Column(Numeric(5, 2), default=0.00)
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
    def is_kyc_verified(self): return self.statut_verification == "approuve"
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
    city = Column(String(60), nullable=False, default="Casablanca")
    adresse = Column(Text, nullable=False)
    calendrier_disponibilite = Column(JSONB, default=dict)
    statut = Column(String(30), default="actif") # actif, en_pause, archive, en_revision
    is_available = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
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
    statut = Column(String(40), default="en_attente_approbation") # en_attente_verification, en_attente_approbation, confirme_cod, en_cours, en_attente_validation, termine, annule, en_litige
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
    __tablename__ = "cmi_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    cmi_auth_token = Column(String(255), default="mock_cmi_token")
    cmi_trans_id = Column(String(100), default="cmi_tx_001")
    card_brand = Column(String(20), default="CMI/VISA")
    preauth_amount_mad = Column(Numeric(10, 2), default=0.00)
    captured_amount_mad = Column(Numeric(10, 2), default=0.00)
    deposit_status = Column(String(20), default="held")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

# 4. Table Remise / Handoff
class Remise(Base):
    __tablename__ = "remises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False) # retrait, retour
    photos = Column(JSONB, default=list)
    videos = Column(JSONB, default=list)
    video_url = Column(Text, nullable=True)
    video_sha256_hash = Column(String(64), nullable=True)
    horodatage = Column(DateTime(timezone=True), default=datetime.utcnow)
    signatures = Column(JSONB, default=dict)
    signed_by_owner = Column(Boolean, default=False)
    signed_by_renter = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    statut = Column(String(30), default="en_attente") # en_attente, confirme
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    reservation = relationship("Reservation", back_populates="remises")

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
    participant1_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    participant2_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    dernier_message_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    soumis_par = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False)
    motif = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    photos = Column(JSONB, default=list)
    statut = Column(String(30), default="en_attente") # en_attente, resolu, clos
    notes_resolution = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolu_le = Column(DateTime(timezone=True), nullable=True)

# 11. Table Notification
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(30), nullable=False) # reservation, message, systeme, paiement
    titre = Column(String(255), nullable=False)
    corps = Column(Text, nullable=False)
    data = Column(JSONB, default=dict)
    lu = Column(Boolean, default=False)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

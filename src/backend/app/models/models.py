import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Boolean, Numeric, Integer, Text, ForeignKey,
    DateTime, Date, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.database import Base

# ------------------------------------------------------------------------------
# 1. MODEL: Utilisateur
# ------------------------------------------------------------------------------
class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    telephone = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nom_complet = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    role = Column(String, default="particulier") # 'particulier', 'pro', 'admin'
    statut_verification = Column(String, default="en_attente") # 'en_attente', 'approuve', 'rejete', 'revision_manuelle'
    didit_session_id = Column(String, nullable=True)
    verifie_le = Column(DateTime(timezone=True), nullable=True)
    note = Column(Numeric(3, 2), default=5.00)
    date_inscription = Column(DateTime(timezone=True), default=datetime.utcnow)
    temps_reponse_minutes = Column(Integer, default=15)
    plan_abonnement = Column(String, default="Gratuit") # 'Gratuit', 'Premium', 'Pro', 'Entreprise'
    abonnement_valable_jusqu = Column(DateTime(timezone=True), nullable=True)
    ville = Column(String, default="Casablanca")
    adresse = Column(Text, nullable=True)
    company_name = Column(String, nullable=True)
    company_ice = Column(String, nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    modifie_le = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Compatibility properties
    @hybrid_property
    def full_name(self):
        return self.nom_complet

    @hybrid_property
    def phone_number(self):
        return self.telephone

    @hybrid_property
    def user_role(self):
        return self.role

    @hybrid_property
    def is_kyc_verified(self):
        return self.statut_verification == "approuve"

    @hybrid_property
    def badge_verifie(self):
        return self.statut_verification == "approuve"

    @hybrid_property
    def nom(self):
        return self.nom_complet

    @hybrid_property
    def temps_reponse(self):
        return f"< {self.temps_reponse_minutes} min"

    @hybrid_property
    def kyc_liveness_score(self):
        return 98.50

    # Relations
    articles = relationship("Article", back_populates="loueur", cascade="all, delete-orphan")
    reservations_locataire = relationship("Reservation", foreign_keys="Reservation.locataire_id", back_populates="locataire")
    reservations_loueur = relationship("Reservation", foreign_keys="Reservation.loueur_id", back_populates="loueur")
    abonnements = relationship("Abonnement", back_populates="utilisateur", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="utilisateur", cascade="all, delete-orphan")


# ------------------------------------------------------------------------------
# 2. MODEL: Article
# ------------------------------------------------------------------------------
class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loueur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    categorie = Column(String, nullable=False, index=True) # outils, electronique, musique, evenementiel, outdoor, velos, btp
    titre = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    photos = Column(JSON, default=list)
    prix_par_jour = Column(Numeric(10, 2), nullable=False)
    montant_caution = Column(Numeric(10, 2), nullable=False, default=0.00)
    niveau_risque = Column(String, default="faible") # 'faible', 'moyen', 'eleve'
    ville = Column(String, nullable=False, default="Casablanca", index=True)
    adresse = Column(Text, nullable=True)
    localisation = Column(JSON, default=lambda: {"lat": 33.5731, "lng": -7.5898})
    calendrier_disponibilite = Column(JSON, default=lambda: {"dates_bloquees": []})
    statut = Column(String, default="actif", index=True) # 'actif', 'en_pause', 'archive', 'en_revision'
    nb_vues = Column(Integer, default=0)
    specs = Column(JSON, default=dict)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    modifie_le = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Compatibility properties for legacy routers
    @hybrid_property
    def is_available(self):
        return self.statut == "actif"

    @hybrid_property
    def daily_price_mad(self):
        return self.prix_par_jour

    @hybrid_property
    def deposit_amount_mad(self):
        return self.montant_caution

    @hybrid_property
    def is_verified(self):
        return True

    @hybrid_property
    def specs_json(self):
        return self.specs

    @hybrid_property
    def images_urls(self):
        return self.photos

    @hybrid_property
    def city(self):
        return self.ville

    @hybrid_property
    def created_at(self):
        return self.cree_le

    # Relations
    loueur = relationship("Utilisateur", back_populates="articles", lazy="selectin")
    reservations = relationship("Reservation", back_populates="article", lazy="selectin")


# ------------------------------------------------------------------------------
# 3. MODEL: Reservation
# ------------------------------------------------------------------------------
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False)
    locataire_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    loueur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    prix_total = Column(Numeric(10, 2), nullable=False)
    montant_caution = Column(Numeric(10, 2), nullable=False)
    option_livraison = Column(String, default="retrait_sur_place") # 'retrait_sur_place', 'livraison_premium'
    adresse_retrait = Column(Text, nullable=True)
    statut = Column(String, default="en_attente_approbation", index=True) 
    # 'en_attente_verification', 'en_attente_approbation', 'confirme_cod', 'en_cours', 'en_attente_validation', 'termine', 'annule', 'en_litige'
    contrat_pdf_url = Column(Text, nullable=True)
    contrat_signe = Column(Boolean, default=False)
    contrat_signe_le = Column(DateTime(timezone=True), nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    modifie_le = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Compatibility properties
    @hybrid_property
    def equipment_id(self):
        return self.article_id

    @hybrid_property
    def booking_status(self):
        return self.statut

    @hybrid_property
    def rental_total_mad(self):
        return self.prix_total

    @hybrid_property
    def deposit_hold_mad(self):
        return self.montant_caution

    @hybrid_property
    def total_days(self):
        return max(1, (self.date_fin - self.date_debut).days)

    @hybrid_property
    def cmi_status(self):
        return "cod_cash"

    @hybrid_property
    def equipment(self):
        return self.article

    @hybrid_property
    def created_at(self):
        return self.cree_le

    @hybrid_property
    def renter(self):
        return self.locataire

    # Relations
    article = relationship("Article", back_populates="reservations")
    locataire = relationship("Utilisateur", foreign_keys=[locataire_id], back_populates="reservations_locataire")
    loueur = relationship("Utilisateur", foreign_keys=[loueur_id], back_populates="reservations_loueur")
    remises = relationship("Remise", back_populates="reservation", cascade="all, delete-orphan")
    confirmations_cash = relationship("ConfirmationCash", back_populates="reservation", cascade="all, delete-orphan")
    avis = relationship("Avis", back_populates="reservation", cascade="all, delete-orphan")
    litiges = relationship("Litige", back_populates="reservation", cascade="all, delete-orphan")


# ------------------------------------------------------------------------------
# 4. MODEL: Remise (État des Lieux)
# ------------------------------------------------------------------------------
class Remise(Base):
    __tablename__ = "remises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False) # 'retrait', 'retour'
    photos = Column(JSON, default=list)
    videos = Column(JSON, default=list)
    geolocalisation = Column(JSON, default=dict)
    horodatage = Column(DateTime(timezone=True), default=datetime.utcnow)
    signatures = Column(JSON, default=lambda: {"locataire": None, "loueur": None})
    statut = Column(String, default="en_attente") # 'en_attente', 'confirme'
    notes = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    reservation = relationship("Reservation", back_populates="remises")


# ------------------------------------------------------------------------------
# 5. MODEL: ConfirmationCash
# ------------------------------------------------------------------------------
class ConfirmationCash(Base):
    __tablename__ = "confirmations_cash"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    montant_recu = Column(Numeric(10, 2), nullable=False)
    confirme_par = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    confirme_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    reservation = relationship("Reservation", back_populates="confirmations_cash")


# ------------------------------------------------------------------------------
# 6. MODEL: Conversation & Message
# ------------------------------------------------------------------------------
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="SET NULL"), nullable=True)
    participant1_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    participant2_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    dernier_message_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="SET NULL"), nullable=True)
    expediteur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    contenu = Column(Text, nullable=False)
    lu = Column(Boolean, default=False)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


# ------------------------------------------------------------------------------
# 7. MODEL: Avis
# ------------------------------------------------------------------------------
class Avis(Base):
    __tablename__ = "avis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    avisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    avise_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    note = Column(Integer, nullable=False)
    commentaire = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    reservation = relationship("Reservation", back_populates="avis")


# ------------------------------------------------------------------------------
# 8. MODEL: Abonnement
# ------------------------------------------------------------------------------
class Abonnement(Base):
    __tablename__ = "abonnements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    plan = Column(String, nullable=False) # 'Gratuit', 'Premium', 'Pro', 'Entreprise'
    taux_commission = Column(Numeric(5, 2), default=15.00)
    prix_mad = Column(Numeric(10, 2), default=0.00)
    debute_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    expire_le = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String, default="actif") # 'actif', 'expire', 'annule'
    fonctionnalites = Column(JSON, default=list)

    utilisateur = relationship("Utilisateur", back_populates="abonnements")


# ------------------------------------------------------------------------------
# 9. MODEL: Litige
# ------------------------------------------------------------------------------
class Litige(Base):
    __tablename__ = "litiges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False)
    soumis_par = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False)
    motif = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    photos = Column(JSON, default=list)
    statut = Column(String, default="en_attente") # 'en_attente', 'resolu', 'clos'
    notes_resolution = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolu_le = Column(DateTime(timezone=True), nullable=True)

    reservation = relationship("Reservation", back_populates="litiges")


# ------------------------------------------------------------------------------
# 10. MODEL: Notification
# ------------------------------------------------------------------------------
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False) # 'reservation', 'message', 'systeme', 'paiement'
    titre = Column(String, nullable=False)
    corps = Column(Text, nullable=False)
    data = Column(JSON, default=dict)
    lu = Column(Boolean, default=False)
    cree_le = Column(DateTime(timezone=True), default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", back_populates="notifications")

# Aliases for compatibility
User = Utilisateur
Equipment = Article
Booking = Reservation
InspectionReport = Remise
Review = Avis
CMITransaction = ConfirmationCash

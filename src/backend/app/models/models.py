import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Numeric, Integer, Text, ForeignKey,
    DateTime, Date, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    cin_number = Column(String(100), nullable=True) # Encrypted
    is_kyc_verified = Column(Boolean, default=False)
    kyc_liveness_score = Column(Numeric(5, 2), default=0.00)
    kyc_verified_at = Column(DateTime(timezone=True), nullable=True)
    user_role = Column(String(20), default="renter") # renter, owner, pro_owner, admin
    company_name = Column(String(150), nullable=True)
    company_ice = Column(String(20), nullable=True)
    city = Column(String(50), default="Casablanca")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="owner", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="renter")

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    address = Column(Text, nullable=True)
    daily_price_mad = Column(Numeric(10, 2), nullable=False)
    deposit_amount_mad = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    discount_pct = Column(Integer, default=0)
    specs_json = Column(JSON, default={})
    images_urls = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    owner = relationship("User", back_populates="equipment")
    bookings = relationship("Booking", back_populates="equipment")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="RESTRICT"), nullable=False)
    renter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    daily_rate_applied_mad = Column(Numeric(10, 2), nullable=False)
    rental_total_mad = Column(Numeric(10, 2), nullable=False)
    platform_commission_mad = Column(Numeric(10, 2), nullable=False)
    deposit_hold_mad = Column(Numeric(10, 2), nullable=False)
    booking_status = Column(String(30), default="pending") # pending, confirmed, in_progress, completed, cancelled, disputed
    cmi_status = Column(String(30), default="pending_preauth") # pending_preauth, held, captured, released
    contract_pdf_url = Column(Text, nullable=True)
    contract_sha256 = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="bookings")
    renter = relationship("User", back_populates="bookings")
    cmi_transaction = relationship("CMITransaction", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    inspections = relationship("InspectionReport", back_populates="booking", cascade="all, delete-orphan")

class CMITransaction(Base):
    __tablename__ = "cmi_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    cmi_auth_token = Column(String(255), nullable=False)
    cmi_trans_id = Column(String(100), nullable=True)
    card_brand = Column(String(20), default="CMI/VISA")
    preauth_amount_mad = Column(Numeric(10, 2), nullable=False)
    captured_amount_mad = Column(Numeric(10, 2), default=0.00)
    deposit_status = Column(String(20), default="held") # held, released, captured
    released_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    booking = relationship("Booking", back_populates="cmi_transaction")

class InspectionReport(Base):
    __tablename__ = "inspection_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(10), nullable=False) # check_in, check_out
    video_url = Column(Text, nullable=False)
    video_sha256_hash = Column(String(64), nullable=False)
    rfc3161_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    signed_by_owner = Column(Boolean, default=False)
    signed_by_renter = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    booking = relationship("Booking", back_populates="inspections")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    rating_score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

"""Add structured inspections and private cryptographic evidence records.

Revision ID: 20260901_05
Revises: 20260901_04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260901_05"
down_revision: Union[str, None] = "20260901_04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE remises DROP CONSTRAINT IF EXISTS remises_statut_check")
    op.execute("ALTER TABLE remises DROP CONSTRAINT IF EXISTS remises_type_check")
    op.execute("""
        ALTER TABLE remises ADD CONSTRAINT remises_statut_check
        CHECK (statut IN ('pending_counterparty', 'confirmed', 'disputed', 'en_attente', 'confirme'))
    """)
    op.execute("""
        ALTER TABLE remises ADD CONSTRAINT remises_type_check
        CHECK (type IN ('check_in', 'check_out', 'retrait', 'retour'))
    """)
    op.add_column("remises", sa.Column("equipment_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("remises", sa.Column("renter_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("remises", sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("remises", sa.Column("submitted_by_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("remises", sa.Column("condition", sa.String(30), nullable=True))
    op.add_column("remises", sa.Column("existing_damage", sa.Text(), nullable=True))
    op.add_column("remises", sa.Column("accessories", postgresql.JSONB(), nullable=False, server_default="[]"))
    op.add_column("remises", sa.Column("serial_number", sa.String(150), nullable=True))
    op.add_column("remises", sa.Column("meter_type", sa.String(20), nullable=True))
    op.add_column("remises", sa.Column("meter_reading", sa.Numeric(12, 2), nullable=True))
    op.add_column("remises", sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("fk_remises_equipment", "remises", "articles", ["equipment_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_remises_renter", "remises", "utilisateurs", ["renter_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_remises_owner", "remises", "utilisateurs", ["owner_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_remises_submitted_by", "remises", "utilisateurs", ["submitted_by_id"], ["id"], ondelete="RESTRICT")
    op.execute("""
        UPDATE remises AS inspection
        SET equipment_id = booking.article_id,
            renter_id = booking.locataire_id,
            owner_id = booking.loueur_id
        FROM reservations AS booking
        WHERE inspection.reservation_id = booking.id
    """)
    op.create_index(
        "uq_remises_booking_current_type", "remises", ["reservation_id", "type"],
        unique=True, postgresql_where=sa.text("type IN ('check_in', 'check_out')"),
    )

    op.create_table(
        "inspection_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("remises.id", ondelete="CASCADE"), nullable=True),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("equipment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("renter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("inspection_type", sa.String(20), nullable=False),
        sa.Column("media_kind", sa.String(10), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("stored_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("storage_key", name="uq_inspection_evidence_storage_key"),
        sa.CheckConstraint("media_kind IN ('photo','video')", name="ck_inspection_evidence_media_kind"),
        sa.CheckConstraint("inspection_type IN ('check_in','check_out')", name="ck_inspection_evidence_type"),
        sa.CheckConstraint("size_bytes > 0", name="ck_inspection_evidence_size_positive"),
        sa.CheckConstraint("sha256_hash ~ '^[0-9a-f]{64}$'", name="ck_inspection_evidence_sha256"),
    )
    op.create_index("ix_inspection_evidence_booking_type", "inspection_evidence", ["reservation_id", "inspection_type"])


def downgrade() -> None:
    op.drop_table("inspection_evidence")
    op.drop_index("uq_remises_booking_current_type", table_name="remises")
    op.drop_constraint("fk_remises_submitted_by", "remises", type_="foreignkey")
    op.drop_constraint("fk_remises_owner", "remises", type_="foreignkey")
    op.drop_constraint("fk_remises_renter", "remises", type_="foreignkey")
    op.drop_constraint("fk_remises_equipment", "remises", type_="foreignkey")
    for column in (
        "confirmed_at", "meter_reading", "meter_type", "serial_number", "accessories", "existing_damage",
        "condition", "submitted_by_id", "owner_id", "renter_id", "equipment_id",
    ):
        op.drop_column("remises", column)
    op.execute("ALTER TABLE remises DROP CONSTRAINT IF EXISTS remises_statut_check")
    op.execute("ALTER TABLE remises DROP CONSTRAINT IF EXISTS remises_type_check")
    op.execute("""
        ALTER TABLE remises ADD CONSTRAINT remises_statut_check
        CHECK (statut IN ('en_attente', 'confirme'))
    """)
    op.execute("""
        ALTER TABLE remises ADD CONSTRAINT remises_type_check
        CHECK (type IN ('retrait', 'retour'))
    """)

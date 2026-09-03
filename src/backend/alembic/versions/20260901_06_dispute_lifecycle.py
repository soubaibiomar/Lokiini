"""Promote disputes to a versioned lifecycle with private evidence and deposit decisions.

Revision ID: 20260901_06
Revises: 20260901_05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260901_06"
down_revision: Union[str, None] = "20260901_05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("litiges", sa.Column("equipment_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("litiges", sa.Column("renter_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("litiges", sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("litiges", sa.Column("reason_code", sa.String(40), nullable=True))
    op.add_column("litiges", sa.Column("idempotency_key", sa.String(128), nullable=True))
    op.add_column("litiges", sa.Column("decision_code", sa.String(40), nullable=True))
    op.add_column("litiges", sa.Column("deposit_capture_amount_mad", sa.Numeric(12, 2), nullable=True))
    op.add_column("litiges", sa.Column("deposit_action_status", sa.String(30), nullable=True))
    op.add_column("litiges", sa.Column("decided_by_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("litiges", sa.Column("modifie_le", sa.DateTime(timezone=True), nullable=True))
    op.add_column("litiges", sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("""
        UPDATE litiges AS dispute
        SET equipment_id = booking.article_id,
            renter_id = booking.locataire_id,
            owner_id = booking.loueur_id,
            reason_code = 'other',
            idempotency_key = 'legacy-' || dispute.id::text,
            statut = CASE WHEN dispute.statut IN ('resolu', 'clos') THEN 'resolved' ELSE 'open' END,
            modifie_le = COALESCE(dispute.resolu_le, dispute.cree_le, NOW())
        FROM reservations AS booking
        WHERE dispute.reservation_id = booking.id
    """)
    for column in ("equipment_id", "renter_id", "owner_id", "reason_code", "idempotency_key", "modifie_le"):
        op.alter_column("litiges", column, nullable=False)
    op.create_unique_constraint("uq_disputes_idempotency_key", "litiges", ["idempotency_key"])
    op.create_foreign_key("fk_disputes_equipment", "litiges", "articles", ["equipment_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_disputes_renter", "litiges", "utilisateurs", ["renter_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_disputes_owner", "litiges", "utilisateurs", ["owner_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_disputes_decided_by", "litiges", "utilisateurs", ["decided_by_id"], ["id"], ondelete="RESTRICT")
    op.execute("ALTER TABLE litiges DROP CONSTRAINT IF EXISTS litiges_statut_check")
    op.create_check_constraint("ck_disputes_status", "litiges", "statut IN ('open','evidence_collection','under_review','decision','resolved')")
    op.create_check_constraint("ck_disputes_reason", "litiges", "reason_code IN ('equipment_condition','missing_accessory','late_return','handover_problem','payment_issue','cancellation','other')")
    op.create_check_constraint("ck_disputes_capture_nonnegative", "litiges", "deposit_capture_amount_mad IS NULL OR deposit_capture_amount_mad >= 0")
    op.create_index("ix_disputes_booking_created", "litiges", ["reservation_id", "cree_le"])

    op.create_table(
        "dispute_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dispute_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("litiges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("equipment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("renter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("media_kind", sa.String(10), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("stored_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("storage_key", name="uq_dispute_evidence_storage_key"),
        sa.CheckConstraint("media_kind IN ('photo','video','document')", name="ck_dispute_evidence_media_kind"),
        sa.CheckConstraint("size_bytes > 0", name="ck_dispute_evidence_size_positive"),
        sa.CheckConstraint("sha256_hash ~ '^[0-9a-f]{64}$'", name="ck_dispute_evidence_sha256"),
    )
    op.create_index("ix_dispute_evidence_dispute_stored", "dispute_evidence", ["dispute_id", "stored_at"])


def downgrade() -> None:
    op.drop_table("dispute_evidence")
    op.drop_index("ix_disputes_booking_created", table_name="litiges")
    op.drop_constraint("ck_disputes_capture_nonnegative", "litiges", type_="check")
    op.drop_constraint("ck_disputes_reason", "litiges", type_="check")
    op.drop_constraint("ck_disputes_status", "litiges", type_="check")
    op.drop_constraint("fk_disputes_decided_by", "litiges", type_="foreignkey")
    op.drop_constraint("fk_disputes_owner", "litiges", type_="foreignkey")
    op.drop_constraint("fk_disputes_renter", "litiges", type_="foreignkey")
    op.drop_constraint("fk_disputes_equipment", "litiges", type_="foreignkey")
    op.drop_constraint("uq_disputes_idempotency_key", "litiges", type_="unique")
    op.execute("UPDATE litiges SET statut = CASE WHEN statut = 'resolved' THEN 'resolu' ELSE 'en_attente' END")
    for column in (
        "decided_at", "modifie_le", "decided_by_id", "deposit_action_status",
        "deposit_capture_amount_mad", "decision_code", "idempotency_key",
        "reason_code", "owner_id", "renter_id", "equipment_id",
    ):
        op.drop_column("litiges", column)

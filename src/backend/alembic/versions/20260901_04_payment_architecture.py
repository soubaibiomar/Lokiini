"""Add separate, reconciliation-friendly payment and deposit records.

Revision ID: 20260901_04
Revises: 20260830_03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260901_04"
down_revision: Union[str, None] = "20260830_03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _common_columns():
    return (
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reservations.id", ondelete="RESTRICT"), nullable=False),
    )


def upgrade() -> None:
    op.create_table(
        "rental_payments", *_common_columns(),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_transaction_id", sa.String(150)),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="MAD"),
        sa.Column("amount_mad", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("provider_status", sa.String(80)),
        sa.Column("failure_code", sa.String(80)),
        sa.Column("failure_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reconciled_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("provider", "provider_transaction_id", name="uq_rental_payment_provider_transaction"),
        sa.CheckConstraint("amount_mad >= 0", name="ck_rental_payment_amount_nonnegative"),
        sa.CheckConstraint("status IN ('pending','requires_action','succeeded','failed','cancelled','partially_refunded','refunded')", name="ck_rental_payment_status"),
    )
    op.create_index("ix_rental_payments_booking_created", "rental_payments", ["booking_id", "created_at"])

    op.create_table(
        "platform_fee_records", *_common_columns(),
        sa.Column("rental_payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rental_payments.id", ondelete="RESTRICT")),
        sa.Column("currency", sa.String(3), nullable=False, server_default="MAD"),
        sa.Column("amount_mad", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("amount_mad >= 0", name="ck_platform_fee_amount_nonnegative"),
        sa.CheckConstraint("status IN ('pending','earned','reversed')", name="ck_platform_fee_status"),
    )
    op.create_index("ix_platform_fees_booking_created", "platform_fee_records", ["booking_id", "created_at"])

    op.create_table(
        "deposit_records", *_common_columns(),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_transaction_id", sa.String(150)),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="MAD"),
        sa.Column("authorized_amount_mad", sa.Numeric(12, 2), nullable=False),
        sa.Column("captured_amount_mad", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("released_amount_mad", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(30), nullable=False, server_default="authorization_pending"),
        sa.Column("provider_status", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reconciled_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("provider", "provider_transaction_id", name="uq_deposit_provider_transaction"),
        sa.CheckConstraint("authorized_amount_mad >= 0", name="ck_deposit_authorized_nonnegative"),
        sa.CheckConstraint("captured_amount_mad >= 0", name="ck_deposit_captured_nonnegative"),
        sa.CheckConstraint("released_amount_mad >= 0", name="ck_deposit_released_nonnegative"),
        sa.CheckConstraint("captured_amount_mad <= authorized_amount_mad", name="ck_deposit_capture_within_authorization"),
        sa.CheckConstraint("released_amount_mad <= authorized_amount_mad", name="ck_deposit_release_within_authorization"),
        sa.CheckConstraint("status IN ('authorization_pending','authorized','authorization_failed','released','partially_captured','captured')", name="ck_deposit_status"),
    )
    op.create_index("ix_deposits_booking_created", "deposit_records", ["booking_id", "created_at"])

    op.create_table(
        "refund_records", *_common_columns(),
        sa.Column("rental_payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rental_payments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_transaction_id", sa.String(150)),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="MAD"),
        sa.Column("amount_mad", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("failure_code", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reconciled_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("provider", "provider_transaction_id", name="uq_refund_provider_transaction"),
        sa.CheckConstraint("amount_mad > 0", name="ck_refund_amount_positive"),
        sa.CheckConstraint("status IN ('pending','succeeded','failed')", name="ck_refund_status"),
    )
    op.create_index("ix_refunds_booking_created", "refund_records", ["booking_id", "created_at"])

    op.create_table(
        "owner_payouts", *_common_columns(),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_transaction_id", sa.String(150)),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="MAD"),
        sa.Column("rental_amount_mad", sa.Numeric(12, 2), nullable=False),
        sa.Column("platform_fee_amount_mad", sa.Numeric(12, 2), nullable=False),
        sa.Column("payout_amount_mad", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="not_ready"),
        sa.Column("failure_code", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reconciled_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("provider", "provider_transaction_id", name="uq_payout_provider_transaction"),
        sa.CheckConstraint("rental_amount_mad >= 0", name="ck_payout_rental_nonnegative"),
        sa.CheckConstraint("platform_fee_amount_mad >= 0", name="ck_payout_fee_nonnegative"),
        sa.CheckConstraint("payout_amount_mad >= 0", name="ck_payout_amount_nonnegative"),
        sa.CheckConstraint("payout_amount_mad = rental_amount_mad - platform_fee_amount_mad", name="ck_payout_amount_balances"),
        sa.CheckConstraint("status IN ('not_ready','pending','paid','failed','reversed')", name="ck_payout_status"),
    )
    op.create_index("ix_owner_payouts_owner_created", "owner_payouts", ["owner_id", "created_at"])
    op.create_index("ix_owner_payouts_booking_created", "owner_payouts", ["booking_id", "created_at"])

    op.create_table(
        "payment_webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_event_id", sa.String(150), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("provider_transaction_id", sa.String(150)),
        sa.Column("payload_sha256", sa.String(64), nullable=False),
        sa.Column("processing_status", sa.String(30), nullable=False, server_default="received"),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("provider", "provider_event_id", name="uq_payment_webhook_provider_event"),
    )
    op.create_index("ix_payment_webhooks_transaction", "payment_webhook_events", ["provider", "provider_transaction_id"])


def downgrade() -> None:
    op.drop_table("payment_webhook_events")
    op.drop_table("owner_payouts")
    op.drop_table("refund_records")
    op.drop_table("deposit_records")
    op.drop_table("platform_fee_records")
    op.drop_table("rental_payments")

"""Unify notification event types and read state tracking.

Revision ID: 20260901_09
Revises: 20260901_08
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260901_09"
down_revision: Union[str, None] = "20260901_08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_type_check")
    op.add_column("notifications", sa.Column("lu_le", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE notifications SET lu_le = cree_le WHERE lu = TRUE AND lu_le IS NULL")
    op.execute(
        """
        UPDATE notifications
        SET type = CASE type
            WHEN 'reservation' THEN 'reservation_requested'
            WHEN 'booking_approved' THEN 'reservation_accepted'
            WHEN 'message' THEN 'message_received'
            WHEN 'paiement' THEN 'payment_updated'
            WHEN 'payment' THEN 'payment_updated'
            WHEN 'dispute' THEN 'dispute_updated'
            ELSE type
        END
        """
    )
    op.create_index(
        "ix_notifications_user_read_created",
        "notifications",
        ["utilisateur_id", "lu", "cree_le"],
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_user_read_created", table_name="notifications")
    op.drop_column("notifications", "lu_le")
    op.create_check_constraint(
        "notifications_type_check",
        "notifications",
        "type IN ('reservation', 'message', 'systeme', 'paiement')",
    )

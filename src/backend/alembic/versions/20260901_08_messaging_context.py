"""Persist messaging context and prevent duplicate conversations.

Revision ID: 20260901_08
Revises: 20260901_07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260901_08"
down_revision: Union[str, None] = "20260901_07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column(
            "article_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("articles.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.execute(
        """
        UPDATE conversations AS conversation
        SET article_id = reservation.article_id
        FROM reservations AS reservation
        WHERE conversation.reservation_id = reservation.id
          AND conversation.article_id IS NULL
        """
    )

    # Preserve every message if an older database contains duplicate booking
    # conversations, then keep the oldest conversation as the canonical thread.
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                FIRST_VALUE(id) OVER (
                    PARTITION BY LEAST(participant1_id, participant2_id),
                                 GREATEST(participant1_id, participant2_id),
                                 reservation_id
                    ORDER BY cree_le, id
                ) AS canonical_id,
                ROW_NUMBER() OVER (
                    PARTITION BY LEAST(participant1_id, participant2_id),
                                 GREATEST(participant1_id, participant2_id),
                                 reservation_id
                    ORDER BY cree_le, id
                ) AS duplicate_number
            FROM conversations
            WHERE reservation_id IS NOT NULL
        )
        UPDATE messages AS message
        SET conversation_id = ranked.canonical_id
        FROM ranked
        WHERE ranked.duplicate_number > 1
          AND message.conversation_id = ranked.id
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY LEAST(participant1_id, participant2_id),
                                 GREATEST(participant1_id, participant2_id),
                                 reservation_id
                    ORDER BY cree_le, id
                ) AS duplicate_number
            FROM conversations
            WHERE reservation_id IS NOT NULL
        )
        DELETE FROM conversations AS conversation
        USING ranked
        WHERE ranked.duplicate_number > 1
          AND conversation.id = ranked.id
        """
    )

    op.create_check_constraint(
        "ck_conversations_distinct_participants",
        "conversations",
        "participant1_id <> participant2_id",
    )
    op.create_index(
        "uq_conversations_reservation_participants",
        "conversations",
        [
            sa.text("LEAST(participant1_id, participant2_id)"),
            sa.text("GREATEST(participant1_id, participant2_id)"),
            "reservation_id",
        ],
        unique=True,
        postgresql_where=sa.text("reservation_id IS NOT NULL"),
    )
    op.create_index(
        "uq_conversations_article_participants",
        "conversations",
        [
            sa.text("LEAST(participant1_id, participant2_id)"),
            sa.text("GREATEST(participant1_id, participant2_id)"),
            "article_id",
        ],
        unique=True,
        postgresql_where=sa.text("reservation_id IS NULL AND article_id IS NOT NULL"),
    )
    op.create_index(
        "ix_conversations_participant1_updated",
        "conversations",
        ["participant1_id", "dernier_message_le"],
    )
    op.create_index(
        "ix_conversations_participant2_updated",
        "conversations",
        ["participant2_id", "dernier_message_le"],
    )


def downgrade() -> None:
    op.drop_index("ix_conversations_participant2_updated", table_name="conversations")
    op.drop_index("ix_conversations_participant1_updated", table_name="conversations")
    op.drop_index("uq_conversations_article_participants", table_name="conversations")
    op.drop_index("uq_conversations_reservation_participants", table_name="conversations")
    op.drop_constraint("ck_conversations_distinct_participants", "conversations", type_="check")
    op.drop_column("conversations", "article_id")

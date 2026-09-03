"""Track each participant's evidence submission independently.

Revision ID: 20260901_07
Revises: 20260901_06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260901_07"
down_revision: Union[str, None] = "20260901_06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("litiges", sa.Column("evidence_submitted_by_renter", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("litiges", sa.Column("evidence_submitted_by_owner", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("litiges", sa.Column("renter_submitted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("litiges", sa.Column("owner_submitted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("litiges", "owner_submitted_at")
    op.drop_column("litiges", "renter_submitted_at")
    op.drop_column("litiges", "evidence_submitted_by_owner")
    op.drop_column("litiges", "evidence_submitted_by_renter")

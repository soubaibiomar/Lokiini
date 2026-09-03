"""Add the explicit reservation lifecycle states.

Revision ID: 20260830_02
Revises: 20260830_01
"""
from typing import Sequence, Union

from alembic import op


revision: str = "20260830_02"
down_revision: Union[str, None] = "20260830_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LIFECYCLE_VALUES = (
    "brouillon",
    "en_attente_approbation",
    "acceptee",
    "paiement_en_attente",
    "confirmee",
    "prete_remise",
    "en_cours",
    "en_attente_validation",
    "termine",
    "rejete",
    "annule",
    "en_litige",
    "resolu",
)


def _check_constraint(values: tuple[str, ...]) -> str:
    allowed = ", ".join(f"'{value}'" for value in values)
    return f"CHECK (statut IN ({allowed}))"


def upgrade() -> None:
    op.execute("ALTER TABLE public.reservations DROP CONSTRAINT IF EXISTS reservations_statut_check")
    op.execute("ALTER TABLE public.reservations DROP CONSTRAINT IF EXISTS ck_reservations_statut_lifecycle")
    op.execute("UPDATE public.reservations SET statut = 'brouillon' WHERE statut = 'en_attente_verification'")
    op.execute("UPDATE public.reservations SET statut = 'confirmee' WHERE statut = 'confirme_cod'")
    op.execute(
        "ALTER TABLE public.reservations "
        "ADD CONSTRAINT ck_reservations_statut_lifecycle "
        + _check_constraint(LIFECYCLE_VALUES)
    )


def downgrade() -> None:
    op.execute("ALTER TABLE public.reservations DROP CONSTRAINT IF EXISTS ck_reservations_statut_lifecycle")
    op.execute("UPDATE public.reservations SET statut = 'en_attente_verification' WHERE statut = 'brouillon'")
    op.execute(
        "UPDATE public.reservations SET statut = 'confirme_cod' "
        "WHERE statut IN ('acceptee', 'paiement_en_attente', 'confirmee', 'prete_remise')"
    )
    op.execute("UPDATE public.reservations SET statut = 'annule' WHERE statut = 'rejete'")
    op.execute("UPDATE public.reservations SET statut = 'termine' WHERE statut = 'resolu'")
    legacy_values = (
        "en_attente_verification",
        "en_attente_approbation",
        "confirme_cod",
        "en_cours",
        "en_attente_validation",
        "termine",
        "annule",
        "en_litige",
    )
    op.execute(
        "ALTER TABLE public.reservations "
        "ADD CONSTRAINT reservations_statut_check "
        + _check_constraint(legacy_values)
    )

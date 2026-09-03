from pathlib import Path
import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = (
    BACKEND_DIR.parent.parent
    if (BACKEND_DIR.parent.parent / "docker-compose.yml").exists()
    else None
)


def test_fastapi_startup_does_not_manage_relational_schema():
    main_source = (BACKEND_DIR / "app/main.py").read_text(encoding="utf-8")
    assert "create_all" not in main_source
    assert "ALTER TABLE" not in main_source


def test_initial_migration_is_versioned_and_contains_no_seed_data():
    migration = BACKEND_DIR / "alembic/versions/20260830_01_initial_schema.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260830_01"' in source
    assert "CREATE TABLE public.utilisateurs" in source
    assert "INSERT INTO" not in source


def test_booking_lifecycle_constraint_is_a_follow_up_migration():
    migration = BACKEND_DIR / "alembic/versions/20260830_02_booking_lifecycle.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260830_02"' in source
    assert 'down_revision: Union[str, None] = "20260830_01"' in source
    assert "ck_reservations_statut_lifecycle" in source
    assert "paiement_en_attente" in source
    assert "prete_remise" in source


def test_kyc_lifecycle_removes_fake_scores_and_versions_statuses():
    migration = BACKEND_DIR / "alembic/versions/20260830_03_kyc_lifecycle.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260830_03"' in source
    assert 'down_revision: Union[str, None] = "20260830_02"' in source
    assert "ck_utilisateurs_kyc_status" in source
    assert '"verified"' in source
    assert "DROP COLUMN IF EXISTS kyc_liveness_score" in source


def test_payment_architecture_has_a_versioned_additive_migration():
    migration = BACKEND_DIR / "alembic/versions/20260901_04_payment_architecture.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260901_04"' in source
    assert 'down_revision: Union[str, None] = "20260830_03"' in source
    assert "payment_webhook_events" in source
    assert "owner_payouts" in source
    assert "INSERT INTO" not in source


def test_inspection_evidence_has_a_versioned_additive_migration():
    migration = BACKEND_DIR / "alembic/versions/20260901_05_inspection_evidence.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260901_05"' in source
    assert 'down_revision: Union[str, None] = "20260901_04"' in source
    assert '"inspection_evidence"' in source
    assert "sha256_hash" in source
    assert "stored_at" in source
    assert "renter_id" in source
    assert "owner_id" in source
    assert "INSERT INTO" not in source


def test_disputes_have_a_versioned_lifecycle_and_private_evidence_migration():
    migration = BACKEND_DIR / "alembic/versions/20260901_06_dispute_lifecycle.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260901_06"' in source
    assert 'down_revision: Union[str, None] = "20260901_05"' in source
    assert '"dispute_evidence"' in source
    assert "evidence_collection" in source
    assert "under_review" in source
    assert "deposit_capture_amount_mad" in source
    assert "sha256_hash" in source
    assert "INSERT INTO" not in source


def test_dispute_evidence_submission_is_tracked_for_each_party():
    migration = BACKEND_DIR / "alembic/versions/20260901_07_dispute_participant_submissions.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260901_07"' in source
    assert 'down_revision: Union[str, None] = "20260901_06"' in source
    assert "evidence_submitted_by_renter" in source
    assert "evidence_submitted_by_owner" in source
    assert "renter_submitted_at" in source
    assert "owner_submitted_at" in source
    assert "INSERT INTO" not in source


def test_messaging_context_is_versioned_without_fake_conversations():
    migration = BACKEND_DIR / "alembic/versions/20260901_08_messaging_context.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260901_08"' in source
    assert 'down_revision: Union[str, None] = "20260901_07"' in source
    assert '"article_id"' in source
    assert "uq_conversations_reservation_participants" in source
    assert "uq_conversations_article_participants" in source
    assert "INSERT INTO" not in source


def test_unified_notifications_add_read_tracking_without_seeded_events():
    migration = BACKEND_DIR / "alembic/versions/20260901_09_unified_notifications.py"
    source = migration.read_text(encoding="utf-8")
    assert 'revision: str = "20260901_09"' in source
    assert 'down_revision: Union[str, None] = "20260901_08"' in source
    assert '"lu_le"' in source
    assert "ix_notifications_user_read_created" in source
    assert "INSERT INTO" not in source


def test_compose_runs_migrations_before_backend():
    if not REPO_DIR or not (REPO_DIR / "docker-compose.yml").exists():
        pytest.skip("docker-compose.yml is not in the isolated container filesystem")
    compose = (REPO_DIR / "docker-compose.yml").read_text(encoding="utf-8")
    assert 'command: ["alembic", "upgrade", "head"]' in compose
    assert "condition: service_completed_successfully" in compose


def test_development_seed_is_explicit_and_environment_guarded():
    seed = (BACKEND_DIR / "app/db/seed.py").read_text(encoding="utf-8")
    assert "RuntimeEnvironment.DEVELOPMENT" in seed
    assert 'if __name__ == "__main__"' in seed
    assert "'not_started'" in seed
    assert "TRUE, FALSE" in seed

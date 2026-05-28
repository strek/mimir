"""Ensure deploy-idle.sh runs backup before update-environment."""

from pathlib import Path

DEPLOY_IDLE = Path(__file__).resolve().parents[2] / "scripts" / "deploy-idle.sh"


def test_deploy_idle_runs_backup_before_update_environment():
    text = DEPLOY_IDLE.read_text()
    backup_pos = text.find("run-eb-backup.sh")
    update_pos = text.find("aws elasticbeanstalk update-environment")
    assert backup_pos != -1, "run-eb-backup.sh not referenced in deploy-idle.sh"
    assert update_pos != -1, "update-environment not found in deploy-idle.sh"
    assert backup_pos < update_pos, "backup must run before update-environment"


def test_deploy_idle_requires_s3_backup_bucket():
    text = DEPLOY_IDLE.read_text()
    assert "S3_BACKUP_BUCKET" in text
    assert "pre-migrate" in text

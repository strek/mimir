#!/usr/bin/env bash
# pre-deploy-backup.sh — local / Makefile entrypoint for pre_deploy_backup management command.
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL not set}"
: "${S3_BACKUP_BUCKET:?S3_BACKUP_BUCKET not set}"

export MIMIR_GIT_REVISION="${MIMIR_GIT_REVISION:-manual-$(date +%Y%m%d)}"

echo "Running pre_deploy_backup → s3://${S3_BACKUP_BUCKET}/pre-migrate/${MIMIR_GIT_REVISION}/..."
exec python manage.py pre_deploy_backup

"""Run Galdr assessments from the shell (ops / tests)."""

import logging

from django.core.management.base import BaseCommand

from methodology.services.galdr_engine import GaldrEngine

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Assess a single PIP synchronously."""

    help = "Run Galdr assessment for pip id (blocking)."

    def add_arguments(self, parser):
        parser.add_argument("pip_id", type=int, help="ProcessImprovementProposal primary key")

    def handle(self, *args, **options):
        pk = int(options["pip_id"])
        logger.info("run_galdr: promote + assess pip_id=%s", pk)

        from django.db import transaction

        from methodology.models import ProcessImprovementProposal

        with transaction.atomic():
            locked = ProcessImprovementProposal.objects.select_for_update().get(pk=pk)
            if locked.status == ProcessImprovementProposal.STATUS_SUBMITTED:
                locked.status = ProcessImprovementProposal.STATUS_PROCESSING_GALDR
                locked.save(update_fields=["status", "updated_at"])
                logger.info("run_galdr: lifted pip_id=%s submitted→processing", pk)

        GaldrEngine.assess_sync(pk)
        logger.info("run_galdr: finished pip_id=%s", pk)
        self.stdout.write(self.style.SUCCESS(f"Galdr assessed pip id={pk}"))

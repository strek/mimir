"""Galdr playbook assessment runner (daemon thread MVP + Anthropic staging)."""

from __future__ import annotations

import logging
import threading

from django.db import close_old_connections, transaction
from django.utils import timezone

from methodology.models import PipChange, ProcessImprovementProposal

logger = logging.getLogger(__name__)


class GaldrEngine:
    """Background worker transitioning ``processing_galdr → reviewed``."""

    REC_CODE = {
        "ACCEPT": PipChange.GALDR_ACCEPT,
        "REJECT": PipChange.GALDR_REJECT,
        "NEEDS_CLARIFICATION": PipChange.GALDR_NEEDS_CLARIFICATION,
    }

    @classmethod
    def schedule(cls, pip_id: int) -> None:
        """Fire-and-forget thread; survives the HTTP response lifecycle."""
        from django.conf import settings

        if getattr(settings, "GALDR_EAGER", False):
            close_old_connections()
            try:
                cls.assess_sync(pip_id)
            except ProcessImprovementProposal.DoesNotExist:
                logger.error("Galdr eager: missing pip id=%s", pip_id)
            except Exception:
                logger.exception("Galdr eager failure pip id=%s", pip_id)
            return

        def _runner() -> None:
            close_old_connections()
            try:
                cls.assess_sync(pip_id)
            except ProcessImprovementProposal.DoesNotExist:
                logger.error("Galdr: missing pip id=%s", pip_id)
            except Exception:
                logger.exception("Galdr: unhandled failure pip id=%s", pip_id)

        threading.Thread(
            target=_runner,
            name=f"galdr-pip-{pip_id}",
            daemon=True,
        ).start()
        logger.info("GaldrEngine.schedule dispatched pip id=%s", pip_id)

    @classmethod
    def _mark_submitted_retry(cls, pip_id: int) -> None:
        """Return PIP to Submitted state when synchronous assessment fails."""

        try:
            with transaction.atomic():
                locked = ProcessImprovementProposal.objects.select_for_update().get(
                    pk=pip_id
                )
                if locked.status == ProcessImprovementProposal.STATUS_PROCESSING_GALDR:
                    locked.status = ProcessImprovementProposal.STATUS_SUBMITTED
                    locked.save(update_fields=["status", "updated_at"])
                    logger.warning(
                        "Galdr pip id=%s rolled back → submitted for retry",
                        pip_id,
                    )
        except ProcessImprovementProposal.DoesNotExist:
            logger.warning("Galdr failure handler: pip id=%s missing", pip_id)

    @classmethod
    def assess_sync(cls, pip_id: int) -> None:
        """
        Blocking assessment used by daemon thread and ``manage.py run_galdr``.

        Performs LLM turns **outside** DB locks to avoid holding rows open.
        """
        from methodology.services.galdr_client import GaldrLLMError, get_galdr_client
        from methodology.services.galdr_prompts import (
            build_change_prompt,
            build_playbook_context_summary,
        )

        bootstrap = ProcessImprovementProposal.objects.select_related("playbook").get(
            pk=pip_id
        )
        if bootstrap.status != ProcessImprovementProposal.STATUS_PROCESSING_GALDR:
            logger.info(
                "Galdr skipped pip id=%s unexpected status=%s",
                pip_id,
                bootstrap.status,
            )
            return

        playbook = bootstrap.playbook
        summary_text = build_playbook_context_summary(playbook)
        client = get_galdr_client()

        payloads: list[tuple[int, str, str]] = []
        try:
            qs = PipChange.objects.filter(pip_id=pip_id).order_by("order", "pk")
            if not qs.exists():
                raise GaldrLLMError("PIP has zero changes.")

            for change in qs.iterator():
                user_prompt = build_change_prompt(change, summary_text)
                rec_text, reasoning = client.evaluate_change(user_prompt)
                rec_upper = rec_text.upper()
                if rec_upper not in cls.REC_CODE:
                    raise GaldrLLMError(f"Unsupported recommendation '{rec_text}'.")
                payloads.append((change.pk, rec_upper, reasoning))
        except GaldrLLMError as exc:
            logger.warning("Galdr assess LLM phase failed pip id=%s: %s", pip_id, exc)
            cls._mark_submitted_retry(pip_id)
            return
        except Exception:
            logger.exception("Galdr assess unexpected pip id=%s", pip_id)
            cls._mark_submitted_retry(pip_id)
            return

        try:
            with transaction.atomic():
                pip = ProcessImprovementProposal.objects.select_for_update().get(
                    pk=pip_id
                )
                if pip.status != ProcessImprovementProposal.STATUS_PROCESSING_GALDR:
                    logger.info(
                        "Galdr aborted save pip id=%s status changed to=%s",
                        pip_id,
                        pip.status,
                    )
                    return
                for cid, code, reasoning in payloads:
                    rec_value = cls.REC_CODE[code]
                    PipChange.objects.filter(pk=cid).update(
                        galdr_recommendation=rec_value,
                        galdr_reasoning=reasoning,
                        updated_at=timezone.now(),
                    )
                pip.status = ProcessImprovementProposal.STATUS_REVIEWED
                pip.reviewed_at = timezone.now()
                pip.save(update_fields=["status", "reviewed_at", "updated_at"])
                logger.info("Galdr persisted pip id=%s → reviewed", pip_id)
        except Exception:
            logger.exception("Galdr DB persist pip id=%s", pip_id)
            cls._mark_submitted_retry(pip_id)

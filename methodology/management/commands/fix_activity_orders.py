"""Management command: reassign sequential orders to activities that share the same
order value within a workflow (caused by a race condition in concurrent MCP creates).

Tie-breaking: activities with the same order are re-sequenced by their primary key
(creation order), which preserves the intended insertion sequence.

Usage:
    python manage.py fix_activity_orders          # dry-run (show what would change)
    python manage.py fix_activity_orders --apply  # write changes to DB
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from methodology.models import Activity, Workflow

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Repair duplicate activity order values within each workflow."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Write changes to the database (default: dry-run only).",
        )

    def handle(self, *args, **options):
        apply = options["apply"]
        mode = "APPLY" if apply else "DRY-RUN"
        self.stdout.write(f"[fix_activity_orders] mode={mode}")

        workflows_fixed = 0
        activities_changed = 0

        for wf in Workflow.objects.all().order_by("id"):
            activities = list(wf.activities.order_by("order", "id"))
            if not activities:
                continue

            # Build desired order: sort by (current order, id) → assign 1,2,3,...
            new_assignments = {act.id: idx + 1 for idx, act in enumerate(activities)}

            # Find those that differ
            to_fix = [
                (act, new_assignments[act.id])
                for act in activities
                if act.order != new_assignments[act.id]
            ]

            if not to_fix:
                continue

            workflows_fixed += 1
            self.stdout.write(
                f"  Workflow pk={wf.id} '{wf.name}' ({wf.playbook.name}) — "
                f"{len(to_fix)} activities need reorder:"
            )
            for act, new_order in to_fix:
                self.stdout.write(
                    f"    pk={act.id} '{act.name}': order {act.order} → {new_order}"
                )
                activities_changed += 1

            if apply:
                with transaction.atomic():
                    # First pass: push all to negative to avoid unique constraint collisions
                    for act, new_order in to_fix:
                        Activity.objects.filter(pk=act.id).update(order=-new_order)
                    # Second pass: set correct positive values
                    for act, new_order in to_fix:
                        Activity.objects.filter(pk=act.id).update(order=new_order)
                self.stdout.write(self.style.SUCCESS(f"    ✓ fixed"))

        if workflows_fixed == 0:
            self.stdout.write(self.style.SUCCESS("No duplicate orders found — nothing to do."))
        else:
            summary = f"{activities_changed} activities across {workflows_fixed} workflows"
            if apply:
                self.stdout.write(self.style.SUCCESS(f"Done. Fixed {summary}."))
                logger.info(f"fix_activity_orders: fixed {summary}")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Dry-run complete. Would fix {summary}. "
                        "Re-run with --apply to commit."
                    )
                )

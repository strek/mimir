# Generated manually for Act 9 PIP model expansion

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def _migrate_pip_rows(apps, schema_editor):
    PIP = apps.get_model("methodology", "ProcessImprovementProposal")
    mapping = {
        "pending": "draft",
        "approved": "accepted",
        "implemented": "accepted",
    }
    now = timezone.now()
    for row in PIP.objects.all().iterator():
        new_status = mapping.get(row.status, row.status)
        fields_to_write = []
        if new_status != row.status:
            row.status = new_status
            fields_to_write.append("status")
        if getattr(row, "status_changed_at", None) is None:
            row.status_changed_at = row.created_at if row.created_at else now
            fields_to_write.append("status_changed_at")
        if fields_to_write:
            row.save(update_fields=fields_to_write)


def _noop_reverse(apps, schema_editor):
    """Irreversible data migration."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("methodology", "0014_add_shared_groups"),
    ]

    operations = [
        migrations.AddField(
            model_name="processimprovementproposal",
            name="summary",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="processimprovementproposal",
            name="submitted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="processimprovementproposal",
            name="reviewed_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When Galdr finished (PIP moved to Reviewed).",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="processimprovementproposal",
            name="decided_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="processimprovementproposal",
            name="status_changed_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                help_text="Updated whenever status changes — drives unread nav count.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="processimprovementproposal",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.RunPython(_migrate_pip_rows, _noop_reverse),
        migrations.AlterField(
            model_name="processimprovementproposal",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("submitted", "Submitted"),
                    ("processing_galdr", "Processing (Galdr)"),
                    ("reviewed", "Reviewed"),
                    ("accepted", "Accepted"),
                    ("accepted_partial", "Partially Accepted"),
                    ("rejected", "Rejected"),
                ],
                default="draft",
                max_length=40,
            ),
        ),
        migrations.CreateModel(
            name="UserPIPListVisit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_visited_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Last time user loaded the authenticated PIPs list page.",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pip_list_visit",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User PIP list visit",
            },
        ),
        migrations.CreateModel(
            name="PipChange",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "change_type",
                    models.CharField(
                        choices=[("ADD", "ADD"), ("ALTER", "ALTER"), ("DROP", "DROP")],
                        max_length=16,
                    ),
                ),
                (
                    "entity_type",
                    models.CharField(
                        choices=[
                            ("Workflow", "Workflow"),
                            ("Activity", "Activity"),
                            ("Skill", "Skill"),
                            ("Agent", "Agent"),
                            ("Artifact", "Artifact"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "order",
                    models.PositiveSmallIntegerField(
                        default=1,
                        help_text="Stable sequence within the pip (1-based).",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=255)),
                ("target_id", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "target_name_snapshot",
                    models.CharField(blank=True, max_length=255),
                ),
                (
                    "append_to_playbook_end",
                    models.BooleanField(
                        default=False,
                        help_text="ADD Workflow / Activity: append to end of container.",
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        blank=True,
                        help_text="Guidance payload or rationale text.",
                    ),
                ),
                (
                    "galdr_recommendation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("ACCEPT", "Accept"),
                            ("REJECT", "Reject"),
                            ("NEEDS_CLARIFICATION", "Needs clarification"),
                        ],
                        max_length=40,
                    ),
                ),
                ("galdr_reasoning", models.TextField(blank=True)),
                (
                    "admin_decision",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "Unset"),
                            ("ACCEPT", "Accept"),
                            ("REJECT", "Reject"),
                        ],
                        default="",
                        max_length=16,
                    ),
                ),
                ("admin_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "insert_after_activity",
                    models.ForeignKey(
                        blank=True,
                        help_text="ADD Activity: sibling to insert immediately after.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pip_inserts_pending",
                        to="methodology.activity",
                    ),
                ),
                (
                    "parent_workflow",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pip_changes_pending",
                        to="methodology.workflow",
                    ),
                ),
                (
                    "pip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="changes",
                        to="methodology.processimprovementproposal",
                    ),
                ),
            ],
            options={
                "ordering": ["pip", "order", "pk"],
                "verbose_name": "PIP change",
            },
        ),
        migrations.AddIndex(
            model_name="pipchange",
            index=models.Index(fields=["pip", "order"], name="m_pipchg_pip_ord"),
        ),
    ]

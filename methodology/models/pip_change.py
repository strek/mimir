"""Structured change attached to a :class:`~methodology.models.ProcessImprovementProposal`."""

from django.db import models


class PipChange(models.Model):
    """
    Single ADD / ALTER / DROP change belonging to one PIP.

    Populated progressively as authors build drafts; enforced by ``PIPService``.
    """

    CHANGE_ADD = "ADD"
    CHANGE_ALTER = "ALTER"
    CHANGE_DROP = "DROP"
    CHANGE_TYPE_CHOICES = [
        (CHANGE_ADD, "ADD"),
        (CHANGE_ALTER, "ALTER"),
        (CHANGE_DROP, "DROP"),
    ]

    ENTITY_WORKFLOW = "Workflow"
    ENTITY_ACTIVITY = "Activity"
    ENTITY_SKILL = "Skill"
    ENTITY_AGENT = "Agent"
    ENTITY_ARTIFACT = "Artifact"
    ENTITY_TYPE_CHOICES = [
        (ENTITY_WORKFLOW, "Workflow"),
        (ENTITY_ACTIVITY, "Activity"),
        (ENTITY_SKILL, "Skill"),
        (ENTITY_AGENT, "Agent"),
        (ENTITY_ARTIFACT, "Artifact"),
    ]

    GALDR_ACCEPT = "ACCEPT"
    GALDR_REJECT = "REJECT"
    GALDR_NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    GALDR_CHOICES = [
        (GALDR_ACCEPT, "Accept"),
        (GALDR_REJECT, "Reject"),
        (GALDR_NEEDS_CLARIFICATION, "Needs clarification"),
    ]

    ADMIN_UNSET = ""
    ADMIN_ACCEPT = "ACCEPT"
    ADMIN_REJECT = "REJECT"
    ADMIN_DECISION_CHOICES = [
        (ADMIN_UNSET, "Unset"),
        (ADMIN_ACCEPT, "Accept"),
        (ADMIN_REJECT, "Reject"),
    ]

    pip = models.ForeignKey(
        "methodology.ProcessImprovementProposal",
        on_delete=models.CASCADE,
        related_name="changes",
    )
    change_type = models.CharField(max_length=16, choices=CHANGE_TYPE_CHOICES)
    entity_type = models.CharField(max_length=32, choices=ENTITY_TYPE_CHOICES)
    order = models.PositiveSmallIntegerField(
        default=1,
        help_text="Stable sequence within the pip (1-based).",
    )
    name = models.CharField(max_length=255, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target_name_snapshot = models.CharField(max_length=255, blank=True)
    parent_workflow = models.ForeignKey(
        "methodology.Workflow",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pip_changes_pending",
    )
    insert_after_activity = models.ForeignKey(
        "methodology.Activity",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pip_inserts_pending",
        help_text="ADD Activity: sibling to insert immediately after.",
    )
    append_to_playbook_end = models.BooleanField(
        default=False,
        help_text="ADD Workflow / Activity: append to end of container.",
    )
    content = models.TextField(blank=True, help_text="Guidance payload or rationale text.")
    galdr_recommendation = models.CharField(
        max_length=40,
        choices=GALDR_CHOICES,
        blank=True,
    )
    galdr_reasoning = models.TextField(blank=True)
    admin_decision = models.CharField(
        max_length=16,
        choices=ADMIN_DECISION_CHOICES,
        blank=True,
        default="",
    )
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pip", "order", "pk"]
        verbose_name = "PIP change"
        indexes = [
            models.Index(fields=["pip", "order"]),
        ]

    def __str__(self) -> str:
        return f"PipChange({self.pk} {self.change_type} {self.entity_type})"

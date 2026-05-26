"""
Team model representing a group of users sharing playbooks.

A Team is the top-level entity for the ACT-11 Teams feature.
It tracks visibility, join policy, category, and an admin user.
"""

import logging

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class Team(models.Model):
    """
    A named group of users that can share playbooks.

    :param name: Unique team name.
    :param description: Optional free-text description.
    :param visibility: Public (discoverable) or Hidden.
    :param join_policy: Controls how new members may join.
    :param category: Broad classification of the team's purpose.
    :param admin: User who administers the team.
    :param created_at: Timestamp of creation (auto-set).
    :param updated_at: Timestamp of last update (auto-set).
    """

    VISIBILITY_PUBLIC = "Public"
    VISIBILITY_HIDDEN = "Hidden"
    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, "Public"),
        (VISIBILITY_HIDDEN, "Hidden"),
    ]

    JOIN_POLICY_AUTO = "Auto-approve"
    JOIN_POLICY_APPROVAL = "Requires Approval"
    JOIN_POLICY_INVITE = "Invite Only"
    JOIN_POLICY_CHOICES = [
        (JOIN_POLICY_AUTO, "Auto-approve"),
        (JOIN_POLICY_APPROVAL, "Requires Approval"),
        (JOIN_POLICY_INVITE, "Invite Only"),
    ]

    CATEGORY_CHOICES = [
        ("Engineering", "Engineering"),
        ("Design", "Design"),
        ("Research", "Research"),
        ("Product", "Product"),
        ("Private", "Private"),
        ("Other", "Other"),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
    )
    join_policy = models.CharField(
        max_length=30,
        choices=JOIN_POLICY_CHOICES,
        default=JOIN_POLICY_AUTO,
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="Other",
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="administered_teams",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self) -> str:
        """Return team name as string representation."""
        return self.name

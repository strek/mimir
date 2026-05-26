"""
TeamMembership model linking Users to Teams with a role.

A membership record is created when a user joins or is invited to a team.
The unique_together constraint prevents duplicate memberships.
"""

import logging

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class TeamMembership(models.Model):
    """
    Associates a User with a Team and assigns a role.

    :param team: The team the user belongs to.
    :param user: The member user.
    :param role: Either 'admin' or 'member'.
    :param joined_at: Timestamp of when the membership was created.
    """

    ROLE_ADMIN = "admin"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
    ]

    team = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "user")
        ordering = ["joined_at"]
        verbose_name = "Team Membership"
        verbose_name_plural = "Team Memberships"

    def __str__(self) -> str:
        """Return a readable representation of this membership."""
        return f"{self.user} in {self.team} ({self.role})"

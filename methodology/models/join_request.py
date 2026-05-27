"""
JoinRequest model representing a user's request to join a team.

Tracks whether the request was self-initiated or resulted from an invitation,
and the current approval status.
"""

import logging

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class JoinRequest(models.Model):
    """
    A request by a User to join a Team.

    :param team: Target team.
    :param user: Requesting or invited user.
    :param source: Origin of the request — self, invited, or invited_new.
    :param requested_at: Timestamp of request creation.
    :param status: Current approval state (pending/approved/rejected).
    """

    SOURCE_SELF = "self"
    SOURCE_INVITED = "invited"
    SOURCE_INVITED_NEW = "invited_new"
    SOURCE_CHOICES = [
        (SOURCE_SELF, "Self"),
        (SOURCE_INVITED, "Invited"),
        (SOURCE_INVITED_NEW, "Invited (new user)"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    team = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
        related_name="join_requests",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="join_requests",
    )
    source = models.CharField(
        max_length=15,
        choices=SOURCE_CHOICES,
        default=SOURCE_SELF,
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    class Meta:
        ordering = ["requested_at"]
        verbose_name = "Join Request"
        verbose_name_plural = "Join Requests"

    def __str__(self) -> str:
        """Return a readable representation of this join request."""
        return f"{self.user} → {self.team} [{self.status}]"

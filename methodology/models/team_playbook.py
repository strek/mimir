"""
TeamPlaybook model associating Teams with Playbooks.

Records which playbooks a team has access to, who added them, and when.
The unique_together constraint prevents a playbook being added to the same
team twice.
"""

import logging

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class TeamPlaybook(models.Model):
    """
    A many-to-many join between Team and Playbook with audit fields.

    :param team: The team that has access to the playbook.
    :param playbook: The playbook shared with the team.
    :param added_at: Timestamp of when the association was created.
    :param added_by: User who added the playbook to the team (nullable).
    """

    team = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
        related_name="team_playbooks",
    )
    playbook = models.ForeignKey(
        "Playbook",
        on_delete=models.CASCADE,
        related_name="team_playbooks",
    )
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="added_team_playbooks",
    )

    class Meta:
        unique_together = ("team", "playbook")
        ordering = ["added_at"]
        verbose_name = "Team Playbook"
        verbose_name_plural = "Team Playbooks"

    def __str__(self) -> str:
        """Return a readable representation of this team-playbook association."""
        return f"{self.team} — {self.playbook}"

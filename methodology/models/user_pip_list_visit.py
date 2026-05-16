"""Per-user bookmark for last time the submitter viewed the global PIPs list."""

from django.conf import settings
from django.db import models


class UserPIPListVisit(models.Model):
    """
    Tracks when ``user`` last opened ``/pips/`` for unread count / blue-dot logic.

    :param user: One-to-one Django auth user.
    :param last_visited_at: Timestamp of latest successful list-page load.

    Compared against :attr:`ProcessImprovementProposal.status_changed_at` rows
    owned by ``user``.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pip_list_visit",
    )
    last_visited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time user loaded the authenticated PIPs list page.",
    )

    class Meta:
        verbose_name = "User PIP list visit"

    def __str__(self) -> str:
        return f"PIPVisit({self.user} @ {self.last_visited_at})"

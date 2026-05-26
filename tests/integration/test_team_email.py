"""Integration tests for team event email notifications (WP-6).

Tests verify that each team lifecycle event triggers the correct email
via team_notification_service — using Django's in-memory email backend
(configured in mimir/settings/test.py).
"""

from __future__ import annotations

import pytest
from django.core import mail
from django.contrib.auth.models import User

from methodology.models import Team, TeamMembership, JoinRequest
from methodology.services.team_service import TeamService
from methodology.services import team_notification_service


@pytest.mark.django_db
class TestTeamEmailNotifications:
    def setup_method(self):
        self.service = TeamService()
        self.admin = User.objects.create_user(
            "email_admin", email="admin@example.com", password="pass"
        )
        self.user = User.objects.create_user(
            "email_user", email="user@example.com", password="pass"
        )
        self.team = self.service.create_team(
            self.admin, "Email Test Team", "desc", "Public", "Auto-approve", "Engineering"
        )

    def test_send_auto_join_confirmation(self):
        membership = self.service.add_member(self.team, self.user)
        mail.outbox.clear()

        team_notification_service.send_auto_join_confirmation(membership)

        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert self.user.email in msg.to
        assert "Email Test Team" in msg.body
        assert ("joined" in msg.subject.lower() or "Email Test Team" in msg.subject)

    def test_send_join_request_to_admin(self):
        jr = self.service.create_join_request(self.team, self.user)
        mail.outbox.clear()

        team_notification_service.send_join_request_to_admin(jr)

        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert self.admin.email in msg.to
        assert "Email Test Team" in msg.body
        assert ("manage" in msg.body.lower() or "join" in msg.body.lower())

    def test_send_request_approved(self):
        jr = self.service.create_join_request(self.team, self.user)
        mail.outbox.clear()

        team_notification_service.send_request_approved(jr)

        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert self.user.email in msg.to
        assert ("approved" in msg.subject.lower() or "Email Test Team" in msg.body)

    def test_send_request_rejected(self):
        jr = self.service.create_join_request(self.team, self.user)
        mail.outbox.clear()

        team_notification_service.send_request_rejected(jr)

        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert self.user.email in msg.to

    def test_send_member_removed(self):
        membership = self.service.add_member(self.team, self.user)
        mail.outbox.clear()

        team_notification_service.send_member_removed(membership)

        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert self.user.email in msg.to
        assert ("removed" in msg.subject.lower() or "Email Test Team" in msg.body)

    def test_send_admin_transferred(self):
        new_admin = User.objects.create_user(
            "new_admin", email="newadmin@example.com", password="pass"
        )
        self.service.add_member(self.team, new_admin)
        mail.outbox.clear()

        team_notification_service.send_admin_transferred(self.team, new_admin, self.admin)

        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert new_admin.email in msg.to
        assert ("admin" in msg.subject.lower() or "Email Test Team" in msg.body)

    def test_no_email_when_recipient_has_no_email(self):
        """Gracefully skip email when user has no email address set."""
        no_email_user = User.objects.create_user("noemail_user", email="", password="pass")
        membership = self.service.add_member(self.team, no_email_user)
        mail.outbox.clear()

        team_notification_service.send_auto_join_confirmation(membership)

        assert len(mail.outbox) == 0

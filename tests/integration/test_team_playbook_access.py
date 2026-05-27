"""
Integration test for team playbook access bug.

Tests that team members can view playbooks shared with their team.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from methodology.models import Playbook, Team, TeamMembership, TeamPlaybook

User = get_user_model()


@pytest.mark.django_db
class TestTeamPlaybookAccess:
    """Test that team members can access team playbooks."""

    def test_team_member_can_view_team_playbook(self):
        """
        Bug reproduction test:
        Team member should be able to view a playbook shared with their team,
        but currently gets 404.
        """
        # Setup: Create owner and team member users
        owner = User.objects.create_user(username="owner", password="pass")
        member = User.objects.create_user(username="member", password="pass")

        # Create a team with owner as admin
        team = Team.objects.create(
            name="Test Team",
            admin=owner,
            visibility="Public",
            join_policy="Auto-approve",
        )

        # Add member to team
        TeamMembership.objects.create(team=team, user=member, role="member")

        # Create a released playbook owned by admin
        playbook = Playbook.objects.create(
            name="Team Playbook",
            description="Shared with team",
            author=owner,
            version="1.0",
            status="released",
            visibility="public",
            source="owned",
        )

        # Share playbook with team
        TeamPlaybook.objects.create(team=team, playbook=playbook)

        # Test: Member should be able to view the playbook via can_view()
        assert playbook.can_view(member), (
            f"Team member '{member.username}' should be able to view "
            f"playbook '{playbook.name}' shared with team '{team.name}'"
        )

    def test_team_member_can_access_team_playbook_via_http(self):
        """
        HTTP-level test: Team member should get 200 when accessing team playbook,
        not 404.
        """
        # Setup: Create owner and team member users
        owner = User.objects.create_user(username="owner", password="pass")
        member = User.objects.create_user(username="member", password="pass")

        # Create a team with owner as admin
        team = Team.objects.create(
            name="Test Team",
            admin=owner,
            visibility="Public",
            join_policy="Auto-approve",
        )

        # Add member to team
        TeamMembership.objects.create(team=team, user=member, role="member")

        # Create a released playbook owned by admin
        playbook = Playbook.objects.create(
            name="Team Playbook",
            description="Shared with team",
            author=owner,
            version="1.0",
            status="released",
            visibility="public",
            source="owned",
        )

        # Share playbook with team
        TeamPlaybook.objects.create(team=team, playbook=playbook)

        # Test: Member should be able to access playbook detail page
        client = Client()
        client.login(username="member", password="pass")
        response = client.get(f"/playbooks/{playbook.pk}/")

        assert response.status_code == 200, (
            f"Team member should get 200 when accessing team playbook, "
            f"but got {response.status_code}"
        )

    def test_non_team_member_cannot_view_private_team_playbook(self):
        """
        Non-team members should NOT be able to view private team playbooks.
        """
        # Setup: Create owner, team member, and outsider users
        owner = User.objects.create_user(username="owner", password="pass")
        member = User.objects.create_user(username="member", password="pass")
        outsider = User.objects.create_user(username="outsider", password="pass")

        # Create a team with owner as admin
        team = Team.objects.create(
            name="Test Team",
            admin=owner,
            visibility="Public",
            join_policy="Auto-approve",
        )

        # Add member to team
        TeamMembership.objects.create(team=team, user=member, role="member")

        # Create a PRIVATE playbook owned by admin
        playbook = Playbook.objects.create(
            name="Private Team Playbook",
            description="Private playbook shared with team",
            author=owner,
            version="1.0",
            status="released",
            visibility="private",  # PRIVATE
            source="owned",
        )

        # Share playbook with team
        TeamPlaybook.objects.create(team=team, playbook=playbook)

        # Test: Team member CAN view it
        assert playbook.can_view(member), (
            f"Team member should be able to view private team playbook"
        )

        # Test: Outsider CANNOT view it
        assert not playbook.can_view(outsider), (
            f"Non-team member should NOT be able to view private team playbook"
        )

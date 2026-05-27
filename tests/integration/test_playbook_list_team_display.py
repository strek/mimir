"""
Integration test for team playbooks display in playbook list view.

Tests that team playbooks are properly displayed in the /playbooks/ list.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from methodology.models import Playbook, Team, TeamMembership, TeamPlaybook

User = get_user_model()


@pytest.mark.django_db
class TestPlaybookListTeamDisplay:
    """Test that team playbooks appear in the playbook list view."""

    def test_team_playbooks_appear_in_list_view(self):
        """
        Team playbooks should appear in the /playbooks/ list for team members.
        Bug: The template was missing the loop for team_playbooks.
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
            name="Shared Team Playbook",
            description="Playbook shared with team",
            author=owner,
            version="1.0",
            status="released",
            visibility="public",
            source="owned",
            category="development",
        )

        # Share playbook with team
        TeamPlaybook.objects.create(team=team, playbook=playbook)

        # Test: Member should see the playbook in their list
        client = Client()
        client.login(username="member", password="pass")
        response = client.get("/playbooks/")

        assert response.status_code == 200
        
        # Check that playbook appears in the response
        assert "Shared Team Playbook" in response.content.decode()
        
        # Check that team_playbooks context is set correctly
        assert "team_playbooks" in response.context
        team_playbooks = response.context["team_playbooks"]
        assert len(team_playbooks) == 1
        assert team_playbooks[0].name == "Shared Team Playbook"

    def test_team_playbooks_not_shown_to_non_members(self):
        """
        Non-team members should NOT see private team playbooks in their list.
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

        # Add member to team (but NOT outsider)
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
            category="development",
        )

        # Share playbook with team
        TeamPlaybook.objects.create(team=team, playbook=playbook)

        # Test: Member SHOULD see it
        client = Client()
        client.login(username="member", password="pass")
        response = client.get("/playbooks/")
        assert response.status_code == 200
        assert "Private Team Playbook" in response.content.decode()

        # Test: Outsider should NOT see it
        client.logout()
        client.login(username="outsider", password="pass")
        response = client.get("/playbooks/")
        assert response.status_code == 200
        assert "Private Team Playbook" not in response.content.decode()

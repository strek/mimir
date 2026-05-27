"""Integration tests for team playbooks appearing in /playbooks/ list (WP-B).

Tests that playbooks shared via team membership appear in the playbook list
for team members, both in the web view and MCP tool.
"""
import pytest
from django.contrib.auth.models import User

from methodology.models import Playbook, Team
from methodology.services.playbook_service import PlaybookService
from methodology.services.team_service import TeamService


@pytest.mark.django_db
class TestTeamPlaybookList:
    def setup_method(self):
        self.playbook_service = PlaybookService()
        self.team_service = TeamService()

    def test_team_playbook_appears_in_list_view(self, client, django_user_model):
        """Test that team-shared playbook appears in /playbooks/ for member."""
        # Create admin and a released playbook
        admin = django_user_model.objects.create_user("tpl_admin", password="pass")
        playbook = self.playbook_service.create_playbook(
            name="Team Shared Playbook",
            description="Test playbook",
            category="development",
            author=admin,
            status="released",
            visibility="public",
        )
        
        # Create team and add playbook
        team = self.team_service.create_team(
            admin, "Test Team", "desc", "Public", "Auto-approve", "Engineering"
        )
        self.team_service.add_playbook_to_team(team, playbook, admin)
        
        # Create another user who joins the team
        member = django_user_model.objects.create_user("tpl_member", password="pass")
        self.team_service.add_member(team, member)
        
        # Log in as member and check playbook list
        client.force_login(member)
        response = client.get("/playbooks/")
        
        assert response.status_code == 200
        assert b"Team Shared Playbook" in response.content
        assert "team_playbooks" in response.context
        assert len(response.context["team_playbooks"]) == 1
        assert response.context["team_playbooks"][0].id == playbook.id

    def test_team_playbook_not_in_list_for_non_member(self, client, django_user_model):
        """Test that team playbook does NOT appear for non-members."""
        admin = django_user_model.objects.create_user("tpl_admin2", password="pass")
        playbook = self.playbook_service.create_playbook(
            name="Team Only Playbook",
            description="Test",
            category="development",
            author=admin,
            status="released",
            visibility="public",
        )
        
        team = self.team_service.create_team(
            admin, "Private Team", "desc", "Public", "Auto-approve", "Engineering"
        )
        self.team_service.add_playbook_to_team(team, playbook, admin)
        
        # Create non-member user
        other_user = django_user_model.objects.create_user("tpl_other", password="pass")
        
        # Non-member should NOT see team playbook (only public_playbooks)
        client.force_login(other_user)
        response = client.get("/playbooks/")
        
        assert response.status_code == 200
        assert "team_playbooks" in response.context
        # Should be empty for non-member
        assert len(response.context["team_playbooks"]) == 0
        # But playbook IS in public_playbooks (visibility=public, released)
        assert playbook.name.encode() in response.content

    def test_team_playbook_excludes_own_authored(self, client, django_user_model):
        """Test that own-authored playbooks don't appear in team_playbooks."""
        author = django_user_model.objects.create_user("tpl_author", password="pass")
        playbook = self.playbook_service.create_playbook(
            name="My Own Playbook",
            description="Test",
            category="development",
            author=author,
            status="released",
            visibility="public",
        )
        
        # Create team where author is admin
        team = self.team_service.create_team(
            author, "My Team", "desc", "Public", "Auto-approve", "Engineering"
        )
        self.team_service.add_playbook_to_team(team, playbook, author)
        
        # Author logs in and checks list
        client.force_login(author)
        response = client.get("/playbooks/")
        
        assert response.status_code == 200
        # Playbook should be in 'playbooks' (owned), not team_playbooks
        assert len(response.context["playbooks"]) == 1
        assert response.context["playbooks"][0].id == playbook.id
        assert len(response.context["team_playbooks"]) == 0

    def test_list_team_playbooks_service_method(self, django_user_model):
        """Test PlaybookService.list_team_playbooks_for_user directly."""
        admin = django_user_model.objects.create_user("tpl_svc_admin", password="pass")
        member = django_user_model.objects.create_user("tpl_svc_member", password="pass")
        
        playbook = self.playbook_service.create_playbook(
            name="Service Test Playbook",
            description="Test",
            category="development",
            author=admin,
            status="released",
            visibility="public",
        )
        
        team = self.team_service.create_team(
            admin, "Service Team", "desc", "Public", "Auto-approve", "Engineering"
        )
        self.team_service.add_playbook_to_team(team, playbook, admin)
        self.team_service.add_member(team, member)
        
        # Member should see 1 team playbook
        team_playbooks = self.playbook_service.list_team_playbooks_for_user(member)
        assert len(team_playbooks) == 1
        assert team_playbooks[0].id == playbook.id
        
        # Admin should see 0 (excludes own-authored)
        team_playbooks_admin = self.playbook_service.list_team_playbooks_for_user(admin)
        assert len(team_playbooks_admin) == 0

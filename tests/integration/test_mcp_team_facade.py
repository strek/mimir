"""Integration tests for MCP team facade tools (WP-F)."""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.authtoken.models import Token

from methodology.models import Team, TeamMembership

User = get_user_model()


@pytest.mark.django_db
class TestMCPTeamFacade:
    """Test Team REST API endpoints (no httpx mocking - real Django test client)."""

    def test_list_teams_endpoint(self):
        """GET /api/teams/ should return visible teams."""
        admin = User.objects.create_user(username="admin_facade", password="pass", email="admin@test.com")
        token, _ = Token.objects.get_or_create(user=admin)

        team = Team.objects.create(
            name="Public Facade Team",
            admin=admin,
            visibility=Team.VISIBILITY_PUBLIC,
        )
        TeamMembership.objects.create(team=team, user=admin)

        client = Client()
        response = client.get(
            "/api/teams/",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        team_names = [t["name"] for t in data]
        assert "Public Facade Team" in team_names

    def test_create_team_endpoint(self):
        """POST /api/teams/ should create a team."""
        user = User.objects.create_user(username="creator_facade", password="pass", email="creator@test.com")
        token, _ = Token.objects.get_or_create(user=user)

        client = Client()
        response = client.post(
            "/api/teams/",
            data={
                "name": "New Facade Team",
                "description": "Test team",
                "visibility": "Public",
                "join_policy": "Auto-approve",
                "category": "Engineering",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Facade Team"
        assert data["admin_id"] == user.id
        assert data["member_count"] == 1

    def test_get_team_endpoint(self):
        """GET /api/teams/<pk>/ should return team detail."""
        admin = User.objects.create_user(username="admin_facade2", password="pass", email="admin2@test.com")
        token, _ = Token.objects.get_or_create(user=admin)

        team = Team.objects.create(
            name="Detail Team",
            description="Test description",
            admin=admin,
            visibility=Team.VISIBILITY_PUBLIC,
        )
        TeamMembership.objects.create(team=team, user=admin)

        client = Client()
        response = client.get(
            f"/api/teams/{team.pk}/",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Detail Team"
        assert data["description"] == "Test description"
        assert data["admin_id"] == admin.id

    def test_move_playbook_to_team_endpoint(self):
        """POST /api/teams/<pk>/move_playbook_to_team/ should add playbook."""
        from methodology.models import Playbook

        admin = User.objects.create_user(username="admin_facade3", password="pass", email="admin3@test.com")
        token, _ = Token.objects.get_or_create(user=admin)

        team = Team.objects.create(name="Test Team", admin=admin)
        TeamMembership.objects.create(team=team, user=admin)

        playbook = Playbook.objects.create(
            name="Test Playbook",
            author=admin,
            status="draft",
        )

        client = Client()
        response = client.post(
            f"/api/teams/{team.pk}/move_playbook_to_team/",
            data={"playbook_id": playbook.pk},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["playbook_id"] == playbook.pk

    def test_invite_endpoint(self):
        """POST /api/teams/<pk>/invite/ should send invites."""
        admin = User.objects.create_user(username="admin_facade4", password="pass", email="admin4@test.com")
        token, _ = Token.objects.get_or_create(user=admin)

        team = Team.objects.create(name="Test Team", admin=admin)
        TeamMembership.objects.create(team=team, user=admin)

        client = Client()
        response = client.post(
            f"/api/teams/{team.pk}/invite/",
            data={
                "emails": ["new@test.com"],
                "welcome_text": "Welcome!",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "invited_count" in data

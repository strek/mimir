"""Integration tests for Teams Create view (FOB-TEAMS-CREATE-*).

Tests cover: login-required redirect, form rendering, successful POST,
blank name validation, and duplicate name validation.
"""

import pytest
from django.test import Client

from methodology.models import Team
from methodology.services.team_service import TeamService


@pytest.mark.django_db
class TestTeamsCreateView:
    def test_create_requires_login(self, client: Client) -> None:
        response = client.get("/teams/create/")
        assert response.status_code == 302

    def test_create_form_renders(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("creator1", password="pass")
        client.force_login(user)
        response = client.get("/teams/create/")
        assert response.status_code == 200
        assert b'data-testid="team-create-form"' in response.content

    def test_create_form_has_submit_button(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("creator1b", password="pass")
        client.force_login(user)
        response = client.get("/teams/create/")
        assert response.status_code == 200
        assert b'data-testid="team-create-submit"' in response.content

    def test_create_post_valid_creates_team(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("creator2", password="pass")
        client.force_login(user)
        response = client.post("/teams/create/", {
            "name": "New Test Team",
            "description": "A test team",
            "visibility": "Public",
            "join_policy": "Auto-approve",
            "category": "Engineering",
        })
        assert response.status_code == 302
        assert Team.objects.filter(name="New Test Team").exists()

    def test_create_post_makes_user_admin_member(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("creator2b", password="pass")
        client.force_login(user)
        client.post("/teams/create/", {
            "name": "Team With Admin",
            "description": "desc",
            "visibility": "Public",
            "join_policy": "Auto-approve",
            "category": "Engineering",
        })
        team = Team.objects.get(name="Team With Admin")
        assert team.admin == user

    def test_create_post_blank_name_shows_error(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("creator3", password="pass")
        client.force_login(user)
        response = client.post("/teams/create/", {
            "name": "",
            "description": "desc",
            "visibility": "Public",
            "join_policy": "Auto-approve",
            "category": "Engineering",
        })
        assert response.status_code == 200
        content_lower = response.content.lower()
        assert b"required" in content_lower or b"team name" in content_lower

    def test_create_post_duplicate_name_shows_error(self, client: Client, django_user_model) -> None:
        admin = django_user_model.objects.create_user("creator_admin5", password="pass")
        service = TeamService()
        service.create_team(admin, "Existing Team", "desc", "Public", "Auto-approve", "Engineering")
        user = django_user_model.objects.create_user("creator4", password="pass")
        client.force_login(user)
        response = client.post("/teams/create/", {
            "name": "Existing Team",
            "description": "desc",
            "visibility": "Public",
            "join_policy": "Auto-approve",
            "category": "Engineering",
        })
        assert response.status_code == 200
        assert b"already exists" in response.content.lower()

    def test_create_post_name_too_long_shows_error(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("creator5", password="pass")
        client.force_login(user)
        response = client.post("/teams/create/", {
            "name": "x" * 101,
            "description": "desc",
            "visibility": "Public",
            "join_policy": "Auto-approve",
            "category": "Engineering",
        })
        assert response.status_code == 200
        assert b"100" in response.content or b"exceed" in response.content.lower()

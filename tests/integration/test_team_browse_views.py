"""Integration tests for Teams Browse view (FOB-TEAMS-BROWSE-*).

Tests cover: login-required redirect, public team visibility, hidden team
visibility rules for members and non-members, search/filter behaviour,
and required data-testid attributes.
"""

import pytest
from django.test import Client

from methodology.models import Team, TeamMembership
from methodology.services.team_service import TeamService


@pytest.mark.django_db
class TestTeamsBrowseView:
    def test_browse_requires_login(self, client: Client) -> None:
        response = client.get("/teams/")
        assert response.status_code == 302
        assert "/login" in response.url

    def test_browse_shows_public_teams(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("browse_user1", password="pass")
        admin = django_user_model.objects.create_user("browse_admin1", password="pass")
        service = TeamService()
        service.create_team(admin, "Public Team", "desc", "Public", "Auto-approve", "Engineering")
        client.force_login(user)
        response = client.get("/teams/")
        assert response.status_code == 200
        assert b"Public Team" in response.content

    def test_browse_excludes_hidden_non_member_teams(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("browse_user2", password="pass")
        admin = django_user_model.objects.create_user("browse_admin2", password="pass")
        service = TeamService()
        service.create_team(admin, "Secret Team", "desc", "Hidden", "Invite Only", "Private")
        client.force_login(user)
        response = client.get("/teams/")
        assert response.status_code == 200
        assert b"Secret Team" not in response.content

    def test_browse_shows_hidden_team_for_member(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("browse_member1", password="pass")
        admin = django_user_model.objects.create_user("browse_admin3", password="pass")
        service = TeamService()
        team = service.create_team(admin, "Hidden Team", "desc", "Hidden", "Invite Only", "Private")
        service.add_member(team, user)
        client.force_login(user)
        response = client.get("/teams/")
        assert response.status_code == 200
        assert b"Hidden Team" in response.content

    def test_browse_page_has_required_testids(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("browse_user3", password="pass")
        client.force_login(user)
        response = client.get("/teams/")
        assert response.status_code == 200
        assert b'data-testid="teams-browse-page"' in response.content
        assert b'data-testid="teams-search-input"' in response.content
        assert b'data-testid="teams-category-filter"' in response.content
        assert b'data-testid="create-team-btn"' in response.content

    def test_browse_search_filters_by_name(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("browse_search1", password="pass")
        admin = django_user_model.objects.create_user("browse_search_admin", password="pass")
        service = TeamService()
        service.create_team(admin, "Alpha Squad", "alpha desc", "Public", "Auto-approve", "Engineering")
        service.create_team(admin, "Beta Gang", "beta desc", "Public", "Auto-approve", "Design")
        client.force_login(user)
        response = client.get("/teams/?q=Alpha")
        assert response.status_code == 200
        assert b"Alpha Squad" in response.content
        assert b"Beta Gang" not in response.content

    def test_browse_category_filter(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("browse_cat1", password="pass")
        admin = django_user_model.objects.create_user("browse_cat_admin", password="pass")
        service = TeamService()
        service.create_team(admin, "Eng Team X", "desc", "Public", "Auto-approve", "Engineering")
        service.create_team(admin, "Design Team X", "desc", "Public", "Auto-approve", "Design")
        client.force_login(user)
        response = client.get("/teams/?category=Engineering")
        assert response.status_code == 200
        assert b"Eng Team X" in response.content
        assert b"Design Team X" not in response.content

    def test_browse_empty_state_when_no_teams(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("browse_empty1", password="pass")
        client.force_login(user)
        Team.objects.all().delete()
        response = client.get("/teams/")
        assert response.status_code == 200
        assert b'data-testid="teams-empty-state"' in response.content

    def test_browse_team_card_has_testid(self, client: Client, django_user_model) -> None:
        user = django_user_model.objects.create_user("browse_card1", password="pass")
        admin = django_user_model.objects.create_user("browse_card_admin", password="pass")
        service = TeamService()
        service.create_team(admin, "Card Team", "desc", "Public", "Auto-approve", "Engineering")
        client.force_login(user)
        response = client.get("/teams/")
        assert response.status_code == 200
        assert b'data-testid="team-card-card-team"' in response.content

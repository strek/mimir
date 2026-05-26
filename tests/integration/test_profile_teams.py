"""Integration tests for the My Teams section on the user profile page."""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from methodology.models import Team, TeamMembership


def _make_user(username, email=None):
    """Create and return a test user."""
    return User.objects.create_user(
        username=username,
        email=email or f"{username}@example.com",
        password="TestPass123",
    )


def _make_team(admin, name="Test Team", visibility=Team.VISIBILITY_PUBLIC):
    """Create and return a team with an admin membership (mirrors TeamService.create_team)."""
    team = Team.objects.create(
        name=name,
        description="A test team",
        visibility=visibility,
        join_policy=Team.JOIN_POLICY_AUTO,
        category="Engineering",
        admin=admin,
    )
    TeamMembership.objects.create(team=team, user=admin, role=TeamMembership.ROLE_ADMIN)
    return team


@pytest.mark.django_db
class TestProfileTeamsSection:
    """Tests for the My Teams section on the user profile page."""

    def test_profile_page_shows_teams_section(self):
        """Profile page renders the data-testid=profile-teams-section element."""
        client = Client()
        user = _make_user("teams_user1")
        client.force_login(user)

        response = client.get(reverse("profile"))

        assert response.status_code == 200
        html = response.content.decode()
        assert 'data-testid="profile-teams-section"' in html

    def test_profile_teams_shows_user_memberships(self):
        """User who is a member of teams sees those teams listed in the table."""
        client = Client()
        admin = _make_user("teams_admin")
        member = _make_user("teams_member")

        team = _make_team(admin, name="Alpha Team")
        TeamMembership.objects.create(team=team, user=member, role=TeamMembership.ROLE_MEMBER)

        client.force_login(member)
        response = client.get(reverse("profile"))

        assert response.status_code == 200
        html = response.content.decode()
        assert 'data-testid="profile-teams-table"' in html
        assert "Alpha Team" in html

    def test_profile_teams_empty_state(self):
        """User with no team memberships sees the empty-state message."""
        client = Client()
        user = _make_user("no_teams_user")
        client.force_login(user)

        response = client.get(reverse("profile"))

        assert response.status_code == 200
        html = response.content.decode()
        assert 'data-testid="profile-teams-empty"' in html
        assert 'data-testid="profile-teams-table"' not in html

    def test_profile_team_row_has_view_link(self):
        """Each team row contains a link to /teams/<pk>/."""
        client = Client()
        admin = _make_user("link_admin")
        team = _make_team(admin, name="Link Team")

        client.force_login(admin)
        response = client.get(reverse("profile"))

        assert response.status_code == 200
        html = response.content.decode()
        assert f"/teams/{team.pk}/" in html

    def test_profile_team_admin_shows_admin_badge(self):
        """A membership with role=admin shows the 'Admin' badge."""
        client = Client()
        admin = _make_user("badge_admin")
        team = _make_team(admin, name="Badge Team")

        client.force_login(admin)
        response = client.get(reverse("profile"))

        assert response.status_code == 200
        html = response.content.decode()
        assert "Admin" in html
        assert f'data-testid="profile-team-row-{team.pk}"' in html

    def test_profile_hidden_team_shows_for_member(self):
        """A hidden team is still shown in My Teams for its member."""
        client = Client()
        admin = _make_user("hidden_admin")
        member = _make_user("hidden_member")
        team = _make_team(admin, name="Secret Team", visibility=Team.VISIBILITY_HIDDEN)
        TeamMembership.objects.create(team=team, user=member, role=TeamMembership.ROLE_MEMBER)

        client.force_login(member)
        response = client.get(reverse("profile"))

        assert response.status_code == 200
        html = response.content.decode()
        assert "Secret Team" in html
        assert 'data-testid="profile-teams-table"' in html

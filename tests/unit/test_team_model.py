"""
Unit tests for Team, TeamMembership, JoinRequest, and TeamPlaybook models.

Covers: creation, defaults, __str__, uniqueness constraints.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from methodology.models import JoinRequest, Playbook, Team, TeamMembership, TeamPlaybook

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db):
    """Create a primary test user."""
    return User.objects.create_user(username="team_test_user", password="testpass123")


@pytest.fixture
def second_user(db):
    """Create a secondary test user."""
    return User.objects.create_user(username="team_test_user_2", password="testpass123")


@pytest.fixture
def team(user):
    """Create a minimal team owned by *user*."""
    return Team.objects.create(name="Alpha Squad", admin=user)


@pytest.fixture
def playbook(user):
    """Create a test playbook owned by *user*."""
    return Playbook.objects.create(
        name="Team Test Playbook",
        description="Playbook for team tests",
        category="development",
        status="draft",
        source="owned",
        author=user,
    )


# ---------------------------------------------------------------------------
# Team tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTeamModel:
    """Tests for the Team model."""

    def test_team_str_returns_name(self, team):
        """__str__ should return the team name."""
        assert str(team) == "Alpha Squad"

    def test_team_default_visibility_is_public(self, user):
        """Default visibility must be 'Public'."""
        t = Team.objects.create(name="Visibility Team", admin=user)
        assert t.visibility == Team.VISIBILITY_PUBLIC

    def test_team_default_join_policy_is_auto_approve(self, user):
        """Default join_policy must be 'Auto-approve'."""
        t = Team.objects.create(name="JoinPolicy Team", admin=user)
        assert t.join_policy == Team.JOIN_POLICY_AUTO

    def test_team_name_unique_constraint(self, team, user):
        """Creating two teams with the same name should raise IntegrityError."""
        with pytest.raises(IntegrityError):
            Team.objects.create(name="Alpha Squad", admin=user)

    def test_team_has_timestamps(self, team):
        """created_at and updated_at are set automatically."""
        assert team.created_at is not None
        assert team.updated_at is not None

    def test_team_description_defaults_to_empty(self, user):
        """description defaults to empty string when not provided."""
        t = Team.objects.create(name="No Description Team", admin=user)
        assert t.description == ""


# ---------------------------------------------------------------------------
# TeamMembership tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTeamMembershipModel:
    """Tests for the TeamMembership model."""

    def test_team_membership_unique_together(self, team, user):
        """Same (team, user) pair cannot be inserted twice."""
        TeamMembership.objects.create(team=team, user=user)
        with pytest.raises(IntegrityError):
            TeamMembership.objects.create(team=team, user=user)

    def test_team_membership_default_role_is_member(self, team, user):
        """Default role for a new membership is 'member'."""
        m = TeamMembership.objects.create(team=team, user=user)
        assert m.role == TeamMembership.ROLE_MEMBER

    def test_team_membership_str(self, team, user):
        """__str__ includes user, team, and role."""
        m = TeamMembership.objects.create(team=team, user=user)
        assert "Alpha Squad" in str(m)

    def test_two_different_users_can_join_same_team(self, team, user, second_user):
        """Different users can each have a membership in the same team."""
        m1 = TeamMembership.objects.create(team=team, user=user)
        m2 = TeamMembership.objects.create(team=team, user=second_user)
        assert m1.pk != m2.pk


# ---------------------------------------------------------------------------
# JoinRequest tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestJoinRequestModel:
    """Tests for the JoinRequest model."""

    def test_join_request_default_status_is_pending(self, team, user):
        """Default status for a new join request is 'pending'."""
        jr = JoinRequest.objects.create(team=team, user=user)
        assert jr.status == JoinRequest.STATUS_PENDING

    def test_join_request_default_source_is_self(self, team, user):
        """Default source for a new join request is 'self'."""
        jr = JoinRequest.objects.create(team=team, user=user)
        assert jr.source == JoinRequest.SOURCE_SELF

    def test_join_request_str(self, team, user):
        """__str__ includes user, team, and status."""
        jr = JoinRequest.objects.create(team=team, user=user)
        assert "Alpha Squad" in str(jr)
        assert "pending" in str(jr)

    def test_join_request_has_requested_at(self, team, user):
        """requested_at is set automatically on creation."""
        jr = JoinRequest.objects.create(team=team, user=user)
        assert jr.requested_at is not None


# ---------------------------------------------------------------------------
# TeamPlaybook tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTeamPlaybookModel:
    """Tests for the TeamPlaybook model."""

    def test_team_playbook_unique_together(self, team, playbook, user):
        """Same (team, playbook) pair cannot be inserted twice."""
        TeamPlaybook.objects.create(team=team, playbook=playbook, added_by=user)
        with pytest.raises(IntegrityError):
            TeamPlaybook.objects.create(team=team, playbook=playbook, added_by=user)

    def test_team_playbook_str(self, team, playbook, user):
        """__str__ includes both team name and playbook name."""
        tp = TeamPlaybook.objects.create(team=team, playbook=playbook, added_by=user)
        assert "Alpha Squad" in str(tp)
        assert "Team Test Playbook" in str(tp)

    def test_team_playbook_added_by_nullable(self, team, playbook):
        """added_by may be null (e.g. system-created entry)."""
        tp = TeamPlaybook.objects.create(team=team, playbook=playbook, added_by=None)
        assert tp.pk is not None
        assert tp.added_by is None

    def test_team_playbook_has_added_at(self, team, playbook, user):
        """added_at is populated automatically."""
        tp = TeamPlaybook.objects.create(team=team, playbook=playbook, added_by=user)
        assert tp.added_at is not None

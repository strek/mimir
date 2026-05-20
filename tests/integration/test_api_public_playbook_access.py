"""
Regression test for bug #115:
  list_playbooks returns public playbooks owned by other users,
  but list_workflows / list_skills / list_agents / list_rules / list_phases
  return empty for those same playbooks.

All resource endpoints must honour Playbook.can_view() — same as /api/playbooks/.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from methodology.models import Playbook, Workflow, Phase, Skill, Agent, Rule

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def owner(db):
    return User.objects.create_user(username="owner", email="owner@test.com", password="pw")


@pytest.fixture
def visitor(db):
    return User.objects.create_user(username="visitor", email="visitor@test.com", password="pw")


@pytest.fixture
def owner_client(owner):
    c = APIClient()
    c.force_authenticate(user=owner)
    return c


@pytest.fixture
def visitor_client(visitor):
    c = APIClient()
    c.force_authenticate(user=visitor)
    return c


@pytest.fixture
def public_playbook(owner):
    """A released, public playbook owned by `owner`."""
    return Playbook.objects.create(
        name="Public Playbook",
        description="shared",
        category="development",
        author=owner,
        status="released",
        visibility="public",
        version="1.0",
    )


@pytest.fixture
def playbook_with_resources(public_playbook, owner):
    """Public playbook populated with one of each resource type."""
    wf = Workflow.objects.create(playbook=public_playbook, name="WF1", order=1)
    phase = Phase.objects.create(playbook=public_playbook, name="Phase1", order=1)
    skill = Skill.objects.create(playbook=public_playbook, title="Skill1")
    agent = Agent.objects.create(playbook=public_playbook, name="Agent1")
    rule = Rule.objects.create(playbook=public_playbook, title="Rule1", slug="rule-1")
    return {
        "playbook": public_playbook,
        "workflow": wf,
        "phase": phase,
        "skill": skill,
        "agent": agent,
        "rule": rule,
    }


# ---------------------------------------------------------------------------
# Bug-proof: owner can always read their own resources
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOwnerCanReadOwnResources:
    def test_owner_sees_workflows(self, owner_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = owner_client.get("/api/workflows/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1

    def test_owner_sees_skills(self, owner_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = owner_client.get("/api/skills/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1

    def test_owner_sees_agents(self, owner_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = owner_client.get("/api/agents/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1

    def test_owner_sees_rules(self, owner_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = owner_client.get("/api/rules/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1

    def test_owner_sees_phases(self, owner_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = owner_client.get("/api/phases/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1


# ---------------------------------------------------------------------------
# Bug reproduction: visitor sees the playbook in list but gets empty content
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestVisitorCanReadPublicPlaybookResources:
    """Bug #115: public playbook resources must be readable by any authenticated user."""

    def test_visitor_sees_public_playbook_in_list(self, visitor_client, playbook_with_resources):
        """Precondition: public playbook is visible in /api/playbooks/."""
        pb = playbook_with_resources["playbook"]
        r = visitor_client.get("/api/playbooks/")
        assert r.status_code == 200
        ids = [p["id"] for p in r.data["results"]]
        assert pb.pk in ids, "Public playbook must appear in list_playbooks for visitor"

    def test_visitor_can_read_workflows(self, visitor_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = visitor_client.get("/api/workflows/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1, (
            f"Bug #115: expected 1 workflow for public playbook, got {r.data['count']}"
        )

    def test_visitor_can_read_skills(self, visitor_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = visitor_client.get("/api/skills/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1, (
            f"Bug #115: expected 1 skill for public playbook, got {r.data['count']}"
        )

    def test_visitor_can_read_agents(self, visitor_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = visitor_client.get("/api/agents/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1, (
            f"Bug #115: expected 1 agent for public playbook, got {r.data['count']}"
        )

    def test_visitor_can_read_rules(self, visitor_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = visitor_client.get("/api/rules/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1, (
            f"Bug #115: expected 1 rule for public playbook, got {r.data['count']}"
        )

    def test_visitor_can_read_phases(self, visitor_client, playbook_with_resources):
        pb = playbook_with_resources["playbook"]
        r = visitor_client.get("/api/phases/", {"playbook_id": pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 1, (
            f"Bug #115: expected 1 phase for public playbook, got {r.data['count']}"
        )

    def test_visitor_can_retrieve_workflow_detail(self, visitor_client, playbook_with_resources):
        wf = playbook_with_resources["workflow"]
        r = visitor_client.get(f"/api/workflows/{wf.pk}/")
        assert r.status_code == 200, (
            f"Bug #115: GET /api/workflows/{wf.pk}/ returned {r.status_code} for visitor"
        )

    def test_visitor_cannot_mutate_public_playbook_workflow(self, visitor_client, playbook_with_resources):
        """Visitor must NOT be able to write to a public playbook they don't own."""
        wf = playbook_with_resources["workflow"]
        r = visitor_client.patch(f"/api/workflows/{wf.pk}/", {"name": "Hacked"}, format="json")
        assert r.status_code in (403, 404), (
            f"Visitor should be denied write access, got {r.status_code}"
        )


# ---------------------------------------------------------------------------
# Private playbooks must remain invisible to non-owners
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPrivatePlaybookRemainsHidden:
    def test_visitor_cannot_read_private_playbook_workflows(self, visitor_client, owner):
        private_pb = Playbook.objects.create(
            name="Private", description="", category="dev",
            author=owner, status="released", visibility="private", version="1.0",
        )
        Workflow.objects.create(playbook=private_pb, name="Secret WF", order=1)
        r = visitor_client.get("/api/workflows/", {"playbook_id": private_pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 0, "Private playbook workflows must not be visible to visitor"

    def test_visitor_cannot_read_draft_public_playbook_workflows(self, visitor_client, owner):
        draft_pb = Playbook.objects.create(
            name="Draft Public", description="", category="dev",
            author=owner, status="draft", visibility="public", version="0.1",
        )
        Workflow.objects.create(playbook=draft_pb, name="Draft WF", order=1)
        r = visitor_client.get("/api/workflows/", {"playbook_id": draft_pb.pk})
        assert r.status_code == 200
        assert r.data["count"] == 0, "Draft public playbook resources must not be visible to visitor"

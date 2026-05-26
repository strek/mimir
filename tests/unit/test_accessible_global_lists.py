"""
Unit tests for global list service methods (owned + public + team visibility).
"""

import pytest
from django.contrib.auth import get_user_model

from methodology.models import (
    Activity,
    Artifact,
    Phase,
    Playbook,
    Team,
    TeamMembership,
    TeamPlaybook,
    Workflow,
)
from methodology.services.activity_service import ActivityService
from methodology.services.agent_service import AgentService
from methodology.services.artifact_service import ArtifactService
from methodology.services.phase_service import PhaseService
from methodology.services.playbook_service import PlaybookService
from methodology.services.rule_service import RuleService
from methodology.services.skill_service import SkillService
from methodology.services.workflow_service import WorkflowService

User = get_user_model()


@pytest.fixture
def team_playbook_setup(db):
    """Admin owns private playbook shared via team; member and outsider users."""
    admin = User.objects.create_user(username="admin_gl", password="pass", email="a@test.com")
    member = User.objects.create_user(username="member_gl", password="pass", email="m@test.com")
    outsider = User.objects.create_user(username="outsider_gl", password="pass", email="o@test.com")

    playbook = Playbook.objects.create(
        name="Team Shared PB",
        author=admin,
        status="released",
        visibility="private",
    )
    workflow = Workflow.objects.create(playbook=playbook, name="WF", order=1)
    activity = Activity.objects.create(workflow=workflow, name="Act", guidance="", order=1)
    phase = Phase.objects.create(playbook=playbook, name="Phase", order=1)
    artifact = Artifact.objects.create(
        playbook=playbook,
        name="Art",
        produced_by=activity,
    )

    team = Team.objects.create(name="Team GL", visibility=Team.VISIBILITY_HIDDEN, admin=admin)
    TeamMembership.objects.create(team=team, user=admin, role="admin")
    TeamMembership.objects.create(team=team, user=member, role="member")
    TeamPlaybook.objects.create(team=team, playbook=playbook)

    return {
        "admin": admin,
        "member": member,
        "outsider": outsider,
        "playbook": playbook,
        "workflow": workflow,
        "activity": activity,
        "phase": phase,
        "artifact": artifact,
    }


@pytest.mark.django_db
class TestAccessibleGlobalListServices:
    """Service-level visibility for global browse helpers."""

    def test_member_sees_team_workflows_activities_phases_artifacts(self, team_playbook_setup):
        data = team_playbook_setup
        member = data["member"]

        wf_ids = list(WorkflowService.list_global_workflows(member).values_list("id", flat=True))
        assert data["workflow"].id in wf_ids

        act_ids = list(ActivityService.list_activities_global(member).values_list("id", flat=True))
        assert data["activity"].id in act_ids

        phases, _ = PhaseService.list_phases_global(member)
        assert data["phase"].id in list(phases.values_list("id", flat=True))

        art_ids = list(
            ArtifactService.list_artifacts_global(member).values_list("id", flat=True)
        )
        assert data["artifact"].id in art_ids

    def test_outsider_cannot_see_private_team_items(self, team_playbook_setup):
        data = team_playbook_setup
        outsider = data["outsider"]

        wf_ids = list(WorkflowService.list_global_workflows(outsider).values_list("id", flat=True))
        assert data["workflow"].id not in wf_ids

        assert ActivityService.count_accessible_activities(outsider) == 0

    def test_public_playbook_visible_to_outsider(self, team_playbook_setup):
        data = team_playbook_setup
        outsider = data["outsider"]
        admin = data["admin"]

        public_pb = Playbook.objects.create(
            name="Public PB",
            author=admin,
            status="released",
            visibility="public",
        )
        public_wf = Workflow.objects.create(playbook=public_pb, name="Public WF", order=1)

        wf_ids = list(WorkflowService.list_global_workflows(outsider).values_list("id", flat=True))
        assert public_wf.id in wf_ids

    def test_get_accessible_playbook_ids_deduplicates(self, team_playbook_setup):
        data = team_playbook_setup
        member = data["member"]
        admin = data["admin"]

        public_pb = Playbook.objects.create(
            name="Public Also Team",
            author=admin,
            status="released",
            visibility="public",
        )
        team = Team.objects.get(name="Team GL")
        TeamPlaybook.objects.create(team=team, playbook=public_pb)

        ids = PlaybookService.get_accessible_playbook_ids(member)
        assert public_pb.id in ids
        assert len(ids) == len(set(ids))

    def test_search_agents_skills_rules_use_accessible_playbooks(self, team_playbook_setup):
        from methodology.models import Agent, Skill, Rule

        data = team_playbook_setup
        member = data["member"]
        playbook = data["playbook"]

        agent = Agent.objects.create(playbook=playbook, name="Team Agent")
        skill = Skill.objects.create(playbook=playbook, title="Team Skill", content="x")
        rule = Rule.objects.create(playbook=playbook, title="Team Rule", slug="team-rule", content="x")

        assert agent.id in AgentService.search_agents("", user=member).values_list("id", flat=True)
        assert skill.id in SkillService.search_skills("", user=member).values_list("id", flat=True)
        assert rule.id in RuleService.search_rules("", user=member).values_list("id", flat=True)

"""Tests for primary navbar section (single active tab)."""

from django.test import RequestFactory

from methodology.context_processors import primary_nav_section


def _section(path: str):
    rf = RequestFactory()
    req = rf.get(path)
    return primary_nav_section(req)["nav_section"]


def test_nested_activity_detail_only_activities_not_playbooks():
    assert (
        _section("/playbooks/12/workflows/25/activities/129/") == "activities"
    )


def test_playbook_detail_playbooks():
    assert _section("/playbooks/12/") == "playbooks"


def test_playbook_workflow_detail_workflows_not_playbooks():
    assert _section("/playbooks/12/workflows/25/") == "workflows"


def test_global_activity_list():
    assert _section("/activities/") == "activities"


def test_playbook_activity_list_for_playbook():
    assert _section("/playbooks/12/activities/") == "activities"


def test_dashboard_home():
    assert _section("/dashboard/") == "home"


def test_index_no_primary_nav_section():
    assert _section("/") is None


def test_global_workflows():
    assert _section("/workflows/") == "workflows"


def test_pips_section():
    assert _section("/pips/") == "pips"


def test_legacy_pip_path_prefix():
    assert _section("/pip/list/") == "pips"

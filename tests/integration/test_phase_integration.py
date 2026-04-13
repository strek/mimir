"""
Integration tests for Phase ↔ Activity integration, Workflow tab, MCP tools,
and data migration (S3).

Tests exercise: Activity.phase_fk FK, Workflow.get_phase_count(),
ActivityService with Phase FK, MCP tool backward-compat for phase-as-string,
Workflow detail Phases tab, and migrate_string_phases().
"""

import pytest
from django.test import TestCase

from methodology.models import Activity, Phase, Workflow
from methodology.services.phase_service import PhaseService
from methodology.services.activity_service import ActivityService


class TestActivityPhaseForeignKey(TestCase):
    """Activity.phase_fk FK field behaviour after S3 migration."""

    def test_activity_can_be_assigned_to_phase(self):
        """Setting activity.phase_fk persists and is readable."""
        raise NotImplementedError()

    def test_activity_phase_fk_null_by_default(self):
        """New activities have phase_fk=None (unassigned)."""
        raise NotImplementedError()

    def test_deleting_phase_nullifies_activity_phase_fk(self):
        """Phase deletion sets activity.phase_fk=None (SET_NULL)."""
        raise NotImplementedError()


class TestWorkflowPhaseCount(TestCase):
    """Workflow.get_phase_count() after Phase model exists."""

    def test_get_phase_count_zero_when_no_phases(self):
        """Returns 0 when workflow has no phases."""
        raise NotImplementedError()

    def test_get_phase_count_reflects_phase_records(self):
        """Returns correct count matching Phase records."""
        raise NotImplementedError()


class TestActivityServiceWithPhase(TestCase):
    """ActivityService creates/updates activities using Phase FK."""

    def test_create_activity_with_phase_id(self):
        """create_activity accepts phase_id kwarg and sets FK."""
        raise NotImplementedError()

    def test_create_activity_with_phase_name_string_backward_compat(self):
        """create_activity still accepts phase as string for backward compat."""
        raise NotImplementedError()

    def test_update_activity_phase_fk(self):
        """update_activity can change the phase FK."""
        raise NotImplementedError()

    def test_get_activities_grouped_by_phase_uses_fk(self):
        """Grouping uses Phase FK name, not the legacy string field."""
        raise NotImplementedError()


class TestWorkflowDetailPhasesTab(TestCase):
    """Workflow detail page Phases tab rendering."""

    def test_phases_tab_visible_when_phases_exist(self):
        """Phases tab and count badge appear when workflow has phases."""
        raise NotImplementedError()

    def test_phases_tab_shows_phase_list_link(self):
        """Phases tab links to phase_list URL."""
        raise NotImplementedError()

    def test_phases_tab_shows_create_button_for_owner(self):
        """Create Phase button present for workflow owner."""
        raise NotImplementedError()


class TestMCPPhaseBackwardCompat(TestCase):
    """MCP tool backward-compatibility: phase still accepted as string."""

    def test_mcp_create_activity_phase_string_resolves_to_fk(self):
        """MCP create_activity with phase='Planning' finds or creates Phase."""
        raise NotImplementedError()

    def test_mcp_update_activity_phase_string_resolves_to_fk(self):
        """MCP update_activity with phase='Execution' updates FK correctly."""
        raise NotImplementedError()

    def test_mcp_activity_response_includes_phase_name(self):
        """MCP tool response includes phase name string for readability."""
        raise NotImplementedError()


class TestStringPhaseMigration(TestCase):
    """End-to-end: migrate_string_phases converts legacy string data."""

    def test_full_migration_creates_phases_and_links_activities(self):
        """Activities with phase='Planning' get phase_fk pointing to Phase(name='Planning')."""
        raise NotImplementedError()

    def test_migration_preserves_unassigned_activities(self):
        """Activities with blank phase string remain with phase_fk=None."""
        raise NotImplementedError()

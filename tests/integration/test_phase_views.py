"""
Integration tests for Phase views (S2).

Tests exercise the full Django request/response cycle using the test client.
No mocks — real DB, real views, real templates.
"""

import pytest
from django.test import TestCase
from django.urls import reverse

from methodology.models import Phase, Workflow, Playbook
from methodology.services.phase_service import PhaseService


class TestPhaseListView(TestCase):
    """GET /playbooks/<pb>/workflows/<wf>/phases/"""

    def test_list_requires_login(self):
        """Unauthenticated request redirects to login."""
        raise NotImplementedError()

    def test_list_shows_phases_in_order(self):
        """All phases displayed, ordered by phase.order."""
        raise NotImplementedError()

    def test_list_shows_empty_state(self):
        """'No phases yet' + create button shown when workflow has no phases."""
        raise NotImplementedError()

    def test_list_scoped_to_workflow(self):
        """Phases from other workflows not shown."""
        raise NotImplementedError()


class TestPhaseCreateView(TestCase):
    """GET+POST /playbooks/<pb>/workflows/<wf>/phases/create/"""

    def test_create_get_renders_form(self):
        """GET renders form with parent workflow shown read-only."""
        raise NotImplementedError()

    def test_create_post_success_redirects_to_list(self):
        """Valid POST creates phase and redirects to phase_list."""
        raise NotImplementedError()

    def test_create_post_empty_name_shows_error(self):
        """POST with blank name re-renders form with validation error."""
        raise NotImplementedError()

    def test_create_post_duplicate_name_shows_error(self):
        """POST with duplicate phase name re-renders form with error."""
        raise NotImplementedError()


class TestPhaseDetailView(TestCase):
    """GET /playbooks/<pb>/workflows/<wf>/phases/<pk>/"""

    def test_detail_shows_name_and_order_badge(self):
        """Phase name, order badge, and parent workflow badge visible."""
        raise NotImplementedError()

    def test_detail_shows_assigned_activities(self):
        """Activities assigned to phase are listed."""
        raise NotImplementedError()

    def test_detail_shows_edit_delete_buttons_for_owner(self):
        """Edit and Delete buttons present for playbook owner."""
        raise NotImplementedError()

    def test_detail_hides_edit_delete_for_non_owner(self):
        """Edit and Delete buttons absent for non-owner."""
        raise NotImplementedError()


class TestPhaseEditView(TestCase):
    """GET+POST /playbooks/<pb>/workflows/<wf>/phases/<pk>/edit/"""

    def test_edit_get_prepopulates_form(self):
        """GET pre-fills all form fields with current values."""
        raise NotImplementedError()

    def test_edit_post_name_success(self):
        """Valid name change is persisted and redirects to detail."""
        raise NotImplementedError()

    def test_edit_post_order_change(self):
        """Order change is persisted correctly."""
        raise NotImplementedError()

    def test_edit_post_duplicate_name_shows_error(self):
        """Duplicate name shows validation error."""
        raise NotImplementedError()


class TestPhaseDeleteView(TestCase):
    """POST /playbooks/<pb>/workflows/<wf>/phases/<pk>/delete/"""

    def test_delete_removes_phase(self):
        """POST deletes phase from DB."""
        raise NotImplementedError()

    def test_delete_unassigns_activities(self):
        """Activities that had this phase get phase_fk=None."""
        raise NotImplementedError()

    def test_delete_shows_success_notification(self):
        """Success message present after deletion."""
        raise NotImplementedError()

    def test_delete_renumbers_remaining_phases(self):
        """Remaining phases are renumbered after deletion."""
        raise NotImplementedError()

"""
Regression test for issue #117:
update_activity MCP tool silently ignores the `order` field.

Root cause: `order` was in `read_only_fields` on ActivitySerializer, so
PATCH /api/activities/{id}/ always stripped it before reaching the service.
"""

import json
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from methodology.models import Playbook, Workflow, Activity

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="test_order_user", email="order@test.com", password="pass"
    )


@pytest.fixture
def auth_client(user):
    c = Client()
    c.login(username="test_order_user", password="pass")
    return c


@pytest.fixture
def draft_playbook(user):
    return Playbook.objects.create(
        name="Order Bug Playbook",
        description="",
        category="test",
        status="draft",
        source="owned",
        author=user,
    )


@pytest.fixture
def workflow(draft_playbook):
    return Workflow.objects.create(
        name="Order Bug Workflow",
        description="",
        playbook=draft_playbook,
        order=1,
    )


@pytest.fixture
def activity(workflow):
    return Activity.objects.create(
        name="Step One",
        guidance="Do the thing",
        workflow=workflow,
        order=1,
    )


@pytest.mark.django_db
class TestActivityOrderPatch:
    """Regression tests for issue #117 — order field writable via PATCH API."""

    def test_patch_order_persists_in_response(self, auth_client, activity):
        """PATCH with order=2 must return order=2 in the response (was silently returning 1)."""
        url = f"/api/activities/{activity.pk}/"
        resp = auth_client.patch(
            url, data=json.dumps({"order": 2}), content_type="application/json"
        )
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert data["order"] == 2, (
            f"Expected order=2 in response, got {data['order']}. "
            "Likely cause: 'order' is still in read_only_fields on ActivitySerializer."
        )

    def test_patch_order_persists_in_database(self, auth_client, activity):
        """PATCH with order=3 must commit the value to the database."""
        url = f"/api/activities/{activity.pk}/"
        resp = auth_client.patch(
            url, data=json.dumps({"order": 3}), content_type="application/json"
        )
        assert resp.status_code == 200, resp.content
        activity.refresh_from_db()
        assert activity.order == 3, (
            f"DB order is still {activity.order} after PATCH with order=3."
        )

    def test_patch_order_does_not_affect_other_fields(self, auth_client, activity):
        """Changing only order must leave name and guidance untouched."""
        url = f"/api/activities/{activity.pk}/"
        original_name = activity.name
        resp = auth_client.patch(
            url, data=json.dumps({"order": 5}), content_type="application/json"
        )
        assert resp.status_code == 200, resp.content
        activity.refresh_from_db()
        assert activity.name == original_name
        assert activity.order == 5

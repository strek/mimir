"""Workflow detail header: Back + Submit PIP on released owned playbooks."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from methodology.models import Playbook, Workflow

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(username="wf_detail_owner", password="pwWF")


@pytest.fixture
def released_playbook(db, owner):
    return Playbook.objects.create(
        name="Released WF Detail PB",
        description="x" * 30,
        category="development",
        author=owner,
        status="released",
        version=Decimal("3.0"),
    )


@pytest.fixture
def draft_playbook(db, owner):
    return Playbook.objects.create(
        name="Draft WF Detail PB",
        description="x" * 30,
        category="development",
        author=owner,
        status="draft",
        version=Decimal("0.1"),
    )


@pytest.fixture
def released_workflow(db, released_playbook):
    return Workflow.objects.create(
        name="Test Workflow",
        description="E2E workflow",
        playbook=released_playbook,
        order=1,
    )


@pytest.fixture
def draft_workflow(db, draft_playbook):
    return Workflow.objects.create(
        name="Draft WF",
        playbook=draft_playbook,
        order=1,
    )


@pytest.mark.django_db
def test_workflow_detail_released_owner_shows_back_and_submit_pip(
    owner, released_playbook, released_workflow
):
    client = Client()
    client.force_login(owner)
    url = reverse(
        "workflow_detail",
        kwargs={"playbook_pk": released_playbook.pk, "pk": released_workflow.pk},
    )
    rsp = client.get(url)
    assert rsp.status_code == 200
    body = rsp.content.decode()
    assert 'data-testid="workflow-back-btn"' in body
    assert 'data-testid="workflow-submit-pip"' in body
    assert (
        f"pips/create/?playbook={released_playbook.pk}&amp;workflow={released_workflow.pk}"
        in body
        or f"pips/create/?playbook={released_playbook.pk}&workflow={released_workflow.pk}"
        in body
    )


@pytest.mark.django_db
def test_workflow_detail_draft_owner_shows_edit_delete_back(
    owner, draft_playbook, draft_workflow
):
    client = Client()
    client.force_login(owner)
    url = reverse(
        "workflow_detail",
        kwargs={"playbook_pk": draft_playbook.pk, "pk": draft_workflow.pk},
    )
    rsp = client.get(url)
    assert rsp.status_code == 200
    body = rsp.content.decode()
    assert 'data-testid="workflow-back-btn"' in body
    assert 'data-testid="workflow-edit-btn"' in body
    assert 'data-testid="workflow-delete-btn"' in body
    assert 'data-testid="workflow-submit-pip"' not in body

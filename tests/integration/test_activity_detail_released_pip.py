"""Activity detail: Submit PIP on released owned playbook; edit when draft."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from methodology.models import Activity, Playbook, Workflow

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(username="act_rel_owner", password="pwACT")


@pytest.fixture
def released_playbook(db, owner):
    return Playbook.objects.create(
        name="Released Act PB",
        description="x" * 30,
        category="development",
        author=owner,
        status="released",
        version=Decimal("2.0"),
    )


@pytest.fixture
def draft_playbook(db, owner):
    return Playbook.objects.create(
        name="Draft Act PB",
        description="x" * 30,
        category="development",
        author=owner,
        status="draft",
        version=Decimal("0.1"),
    )


@pytest.fixture
def wf_released(db, released_playbook):
    return Workflow.objects.create(
        name="WF",
        playbook=released_playbook,
        order=1,
    )


@pytest.fixture
def wf_draft(db, draft_playbook):
    return Workflow.objects.create(
        name="WFD",
        playbook=draft_playbook,
        order=1,
    )


@pytest.fixture
def act_released(db, wf_released):
    return Activity.objects.create(
        workflow=wf_released,
        name="Gamma",
        guidance="G",
        order=4,
    )


@pytest.fixture
def act_draft(db, wf_draft):
    return Activity.objects.create(
        workflow=wf_draft,
        name="Drafty",
        guidance="D",
        order=1,
    )


@pytest.mark.django_db
def test_activity_detail_released_owner_sees_submit_pip_and_back(
    owner, released_playbook, wf_released, act_released
):
    client = Client()
    client.force_login(owner)
    url = reverse(
        "activity_detail",
        kwargs={
            "playbook_pk": released_playbook.pk,
            "workflow_pk": wf_released.pk,
            "activity_pk": act_released.pk,
        },
    )
    rsp = client.get(url)
    assert rsp.status_code == 200
    body = rsp.content.decode()
    assert 'data-testid="activity-submit-pip-btn"' in body
    assert 'data-testid="activity-back-btn"' in body
    assert 'data-testid="edit-btn"' not in body
    assert (
        f"pips/create/?playbook={released_playbook.pk}&amp;workflow={wf_released.pk}&amp;activity={act_released.pk}"
        in body
        or f"activity={act_released.pk}" in body
    )


@pytest.mark.django_db
def test_activity_detail_draft_owner_sees_edit_delete_back(
    owner, draft_playbook, wf_draft, act_draft
):
    client = Client()
    client.force_login(owner)
    url = reverse(
        "activity_detail",
        kwargs={
            "playbook_pk": draft_playbook.pk,
            "workflow_pk": wf_draft.pk,
            "activity_pk": act_draft.pk,
        },
    )
    rsp = client.get(url)
    assert rsp.status_code == 200
    body = rsp.content.decode()
    assert 'data-testid="edit-btn"' in body
    assert 'data-testid="delete-btn"' in body
    assert 'data-testid="activity-back-btn"' in body
    assert 'data-testid="activity-submit-pip-btn"' not in body

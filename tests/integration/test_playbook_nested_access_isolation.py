"""Integration: workflow/activity URLs respect playbook visibility (private vs public)."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from methodology.models import Activity, Playbook, Workflow

User = get_user_model()


@pytest.fixture
def nested_private_playbook(db):
    owner = User.objects.create_user(username="nested_owner", password="x")
    other = User.objects.create_user(username="nested_other", password="x")
    pb = Playbook.objects.create(
        name="Nested Private PB",
        description="Description long enough for playbook nested access isolation",
        category="development",
        author=owner,
        visibility="private",
        status="draft",
        version=Decimal("0.1"),
    )
    wf = Workflow.objects.create(playbook=pb, name="Nested WF", description="d", order=1)
    act = Activity.objects.create(
        workflow=wf,
        name="Nested Act",
        guidance="Guidance text for nested activity isolation test",
        order=1,
    )
    return {"owner": owner, "other": other, "pb": pb, "wf": wf, "act": act}


@pytest.mark.django_db
class TestPrivatePlaybookNestedRoutesBlocked:
    """Non-owner cannot load workflow or activity pages on a private playbook (404)."""

    def test_playbook_detail_404(self, nested_private_playbook):
        c = Client()
        c.force_login(nested_private_playbook["other"])
        pb = nested_private_playbook["pb"]
        assert c.get(reverse("playbook_detail", kwargs={"pk": pb.pk})).status_code == 404

    def test_workflow_detail_404(self, nested_private_playbook):
        c = Client()
        c.force_login(nested_private_playbook["other"])
        pb = nested_private_playbook["pb"]
        wf = nested_private_playbook["wf"]
        url = reverse("workflow_detail", kwargs={"playbook_pk": pb.pk, "pk": wf.pk})
        assert c.get(url).status_code == 404

    def test_workflow_list_404(self, nested_private_playbook):
        c = Client()
        c.force_login(nested_private_playbook["other"])
        pb = nested_private_playbook["pb"]
        url = reverse("workflow_list", kwargs={"playbook_pk": pb.pk})
        assert c.get(url).status_code == 404

    def test_activity_list_per_workflow_404(self, nested_private_playbook):
        c = Client()
        c.force_login(nested_private_playbook["other"])
        pb = nested_private_playbook["pb"]
        wf = nested_private_playbook["wf"]
        url = reverse(
            "activity_list",
            kwargs={"playbook_pk": pb.pk, "workflow_pk": wf.pk},
        )
        assert c.get(url).status_code == 404

    def test_activity_detail_404(self, nested_private_playbook):
        c = Client()
        c.force_login(nested_private_playbook["other"])
        pb = nested_private_playbook["pb"]
        wf = nested_private_playbook["wf"]
        act = nested_private_playbook["act"]
        url = reverse(
            "activity_detail",
            kwargs={
                "playbook_pk": pb.pk,
                "workflow_pk": wf.pk,
                "activity_pk": act.pk,
            },
        )
        assert c.get(url).status_code == 404


@pytest.mark.django_db
class TestPublicPlaybookNestedRoutesReadable:
    """Non-owner can open workflow and activity views on a public playbook."""

    def test_workflow_and_activity_views_200(self, db):
        owner = User.objects.create_user(username="pub_nested_o", password="x")
        visitor = User.objects.create_user(username="pub_nested_v", password="x")
        pb = Playbook.objects.create(
            name="Nested Public PB",
            description="Description long enough for nested public playbook browse test",
            category="development",
            author=owner,
            visibility="public",
            status="draft",
            version=Decimal("0.1"),
        )
        wf = Workflow.objects.create(playbook=pb, name="Pub WF", description="d", order=1)
        act = Activity.objects.create(
            workflow=wf,
            name="Pub Act",
            guidance="Guidance for public nested readable test",
            order=1,
        )
        c = Client()
        c.force_login(visitor)
        assert (
            c.get(
                reverse("workflow_detail", kwargs={"playbook_pk": pb.pk, "pk": wf.pk})
            ).status_code
            == 200
        )
        assert (
            c.get(
                reverse(
                    "activity_detail",
                    kwargs={
                        "playbook_pk": pb.pk,
                        "workflow_pk": wf.pk,
                        "activity_pk": act.pk,
                    },
                )
            ).status_code
            == 200
        )

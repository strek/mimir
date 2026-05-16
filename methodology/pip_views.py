"""PIP (Act 9) UI views — list, create, draft edit, preview, submit."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import RedirectView

from methodology.models import PipChange, ProcessImprovementProposal as PipModel

logger = logging.getLogger(__name__)


def _format_validation_error(exc: ValidationError) -> str:
    if hasattr(exc, "messages"):
        return "; ".join(str(m) for m in exc.messages)
    return str(exc)


PIP_DETAIL_STATIC_BANNERS = {
    PipModel.STATUS_DRAFT: "Draft — not yet submitted for review.",
    PipModel.STATUS_SUBMITTED: "Submitted — awaiting Galdr processing.",
    PipModel.STATUS_PROCESSING_GALDR: (
        "Galdr is reviewing your changes — check back shortly."
    ),
    PipModel.STATUS_REVIEWED: "Reviewed — awaiting Administrator decision.",
}


def _pip_detail_status_banner(pip) -> str:
    """Banner copy aligned with act-9 view scenarios."""
    st = pip.status
    if st in PIP_DETAIL_STATIC_BANNERS:
        return PIP_DETAIL_STATIC_BANNERS[st]
    if st == PipModel.STATUS_ACCEPTED:
        return (
            f"Accepted — all changes applied. {pip.playbook.name} "
            f"is now v{pip.playbook.version}."
        )
    if st == PipModel.STATUS_ACCEPTED_PARTIAL:
        qs = list(pip.changes.all())
        accepted_n = sum(
            1 for ch in qs if ch.admin_decision == PipChange.ADMIN_ACCEPT
        )
        return (
            f"Partially accepted — {accepted_n} of {len(qs)} changes applied. "
            f"{pip.playbook.name} is now v{pip.playbook.version}."
        )
    if st == PipModel.STATUS_REJECTED:
        return "Rejected — no changes were applied."
    return ""


def _pip_detail_context(pip, user):
    change_count = pip.changes.count()
    withdrawable = pip.status in {
        PipModel.STATUS_DRAFT,
        PipModel.STATUS_SUBMITTED,
        PipModel.STATUS_PROCESSING_GALDR,
    }
    banner = _pip_detail_status_banner(pip)
    can_submit = pip.status in {
        PipModel.STATUS_DRAFT,
        PipModel.STATUS_SUBMITTED,
    } and change_count > 0 and pip.created_by_id == user.pk
    submit_label = (
        "Re-submit for Galdr review"
        if pip.status == PipModel.STATUS_SUBMITTED
        else "Submit for review"
    )

    ctx = {
        "pip": pip,
        "status_banner": banner,
        "can_edit": pip.status == PipModel.STATUS_DRAFT and pip.created_by_id == user.pk,
        "can_submit": bool(can_submit),
        "submit_label": submit_label,
        "can_withdraw": withdrawable and pip.created_by_id == user.pk,
        "can_preview": True,
        "admin_review_url": None,
    }
    if (
        getattr(user, "is_staff", False)
        and pip.status == PipModel.STATUS_REVIEWED
    ):
        try:
            base = reverse(
                "admin:methodology_processimprovementproposal_change",
                args=(pip.pk,),
            )
            ctx["admin_review_url"] = base
        except Exception:  # noqa: BLE001
            logger.exception("PIP admin URL unavailable pk=%s", pip.pk)

    logger.info(
        "PIP detail context pk=%s user=%s can_submit=%s can_edit=%s",
        pip.pk,
        getattr(user, "username", ""),
        ctx["can_submit"],
        ctx["can_edit"],
    )
    return ctx


PIP_LIST_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("processing_galdr", "Processing (Galdr)"),
    ("reviewed", "Reviewed"),
    ("accepted", "Accepted"),
    ("accepted_partial", "Partially accepted"),
    ("rejected", "Rejected"),
]


def _pip_list_params(request):
    scope = request.GET.get("scope", "mine")
    if scope not in {"mine", "all"}:
        scope = "mine"
    status_filters = request.GET.getlist("status")
    playbook_raw = request.GET.get("playbook")
    playbook_pk = (
        int(playbook_raw)
        if playbook_raw and str(playbook_raw).isdigit()
        else None
    )
    return scope, status_filters, playbook_pk


class PipListLegacyRedirect(RedirectView):
    pattern_name = "pip_list"
    permanent = False


@login_required
def pip_list(request):
    from methodology.models import Playbook
    from methodology.services.pip_service import PIPService

    scope, status_filters, playbook_pk = _pip_list_params(request)
    logger.info(
        "User %s opening PIP list scope=%s statuses=%s playbook=%s",
        request.user.username,
        scope,
        status_filters,
        playbook_pk,
    )
    last_visit = PIPService.last_list_visit_at(request.user)
    try:
        queryset = PIPService.list_queryset_for_user(
            actor=request.user,
            scope=scope,
            status_filters=status_filters or None,
            playbook_id=playbook_pk,
        )
    except PermissionError:
        messages.warning(request, "You do not have permission to view all PIPs.")
        scope = "mine"
        queryset = PIPService.list_queryset_for_user(
            actor=request.user,
            scope="mine",
            status_filters=status_filters or None,
            playbook_id=playbook_pk,
        )
    rows = [
        {"pip": pip, "unread_dot": pip.status_changed_since_visit(last_visit)}
        for pip in queryset
    ]
    filter_ids = queryset.values_list("playbook_id", flat=True).distinct()
    filter_playbooks = Playbook.objects.filter(pk__in=filter_ids).order_by("name")
    pip_count = len(rows)
    PIPService.mark_list_viewed(request.user)
    return render(
        request,
        "pips/list.html",
        {
            "pip_rows": rows,
            "pip_count": pip_count,
            "list_scope": scope,
            "status_filters": status_filters,
            "filter_playbooks": filter_playbooks,
            "selected_playbook": playbook_pk,
            "pip_status_choices": PIP_LIST_STATUS_CHOICES,
        },
    )


@login_required
def pip_detail(request, pk: int):
    from methodology.services.pip_service import PIPService

    pip = PIPService.get_pip_with_changes(pk, request.user)
    logger.info(
        "User %s viewing PIP detail pk=%s status=%s",
        request.user.username,
        pk,
        pip.status,
    )
    return render(request, "pips/detail.html", _pip_detail_context(pip, request.user))


@login_required
def pip_create(request):
    from methodology.models import Playbook
    from methodology.services.pip_service import PIPService

    released = Playbook.objects.filter(status="released").order_by("name")
    prefill = request.GET.get("playbook")
    prefill_id = int(prefill) if prefill and prefill.isdigit() else None

    if request.method == "POST":
        try:
            playbook_id = int(request.POST.get("playbook", "0"))
            title = request.POST.get("title", "")
            summary = request.POST.get("summary", "")
            pip = PIPService.create_draft_for_playbook(
                actor=request.user,
                playbook_id=playbook_id,
                title=title,
                summary=summary,
            )
            messages.success(request, f"Saved draft {pip}.")
            return redirect("pip_edit", pk=pip.pk)
        except (TypeError, ValueError) as exc:
            messages.error(request, f"Invalid playbook id: {exc}")
        except ValidationError as exc:
            messages.error(request, _format_validation_error(exc))
    return render(
        request,
        "pips/create.html",
        {
            "released_playbooks": released,
            "prefill_playbook_id": prefill_id,
        },
    )


def _gather_targets(pip):
    from methodology.models import Workflow

    wf_bundle = []
    for wf in Workflow.objects.filter(playbook=pip.playbook).order_by(
        "order", "created_at"
    ):
        acts = list(wf.activities.order_by("order", "pk"))
        wf_bundle.append({"workflow": wf, "activities": acts})
    return {
        "workflow_bundle": wf_bundle,
        "preview_url": reverse("pip_preview", kwargs={"pk": pip.pk}),
    }


@login_required
def pip_draft_editor(request, pk: int):
    from methodology.services.pip_service import PIPService

    pip = PIPService.get_pip(pk, request.user)
    if pip.status != PipModel.STATUS_DRAFT:
        messages.info(request, "PIP is not editable in this state.")
        return redirect("pip_detail", pk=pip.pk)

    if request.method == "POST":
        if request.POST.get("action") == "save_header":
            try:
                PIPService.save_draft_header(
                    actor=request.user,
                    pip=pip,
                    title=request.POST.get("title", ""),
                    summary=request.POST.get("summary", ""),
                )
                messages.success(request, "Draft header saved.")
            except ValidationError as exc:
                messages.error(request, _format_validation_error(exc))
        return redirect("pip_edit", pk=pip.pk)

    return render(
        request,
        "pips/draft_editor.html",
        {"pip": pip, **_gather_targets(pip)},
    )


@login_required
@require_POST
def pip_add_change(request, pk: int):
    from methodology.services.pip_service import PIPService

    pip = PIPService.get_pip(pk, request.user)
    post = request.POST
    try:
        wf_raw = post.get("parent_workflow") or ""
        ins_raw = post.get("insert_after_activity") or ""
        tgt_raw = post.get("target_id") or ""
        PIPService.add_change(
            actor=request.user,
            pip=pip,
            change_type=(post.get("change_type") or "").strip(),
            entity_type=(post.get("entity_type") or "").strip(),
            name=post.get("name", ""),
            content=post.get("content", ""),
            target_id=int(tgt_raw) if tgt_raw.isdigit() else None,
            parent_workflow_id=int(wf_raw) if wf_raw.isdigit() else None,
            insert_after_activity_id=int(ins_raw) if ins_raw.isdigit() else None,
            append_to_playbook_end=post.get("append_end") == "on",
        )
        messages.success(request, "Change added.")
    except ValidationError as exc:
        messages.error(request, _format_validation_error(exc))
    return redirect("pip_edit", pk=pip.pk)


@login_required
@require_POST
def pip_remove_change(request, pk: int, change_id: int):
    from methodology.services.pip_service import PIPService

    pip = PIPService.get_pip(pk, request.user)
    try:
        PIPService.remove_change(actor=request.user, pip=pip, change_id=change_id)
        messages.success(request, "Change removed.")
    except ValidationError as exc:
        messages.error(request, _format_validation_error(exc))
    return redirect("pip_edit", pk=pip.pk)


@login_required
def pip_preview(request, pk: int):
    from methodology.services.pip_service import PIPService

    pip = PIPService.get_pip(pk, request.user)
    rows = PIPService.summarize_preview_rows(pip)
    return render(request, "pips/preview.html", {"pip": pip, "rows": rows})


@login_required
@require_POST
def pip_submit_review(request, pk: int):
    from methodology.services.pip_service import PIPService

    pip = PIPService.get_pip(pk, request.user)
    try:
        PIPService.submit_for_review(actor=request.user, pip=pip)
        messages.success(request, "PIP submitted — Galdr is reviewing your changes.")
    except ValidationError as exc:
        messages.error(request, _format_validation_error(exc))
        return redirect("pip_edit", pk=pip.pk)
    return redirect("pip_detail", pk=pip.pk)


@login_required
@require_POST
def pip_withdraw(request, pk: int):
    from methodology.services.pip_service import PIPService

    pip = PIPService.get_pip(pk, request.user)
    try:
        PIPService.withdraw_pip(pip, request.user)
        messages.success(request, "PIP withdrawn.")
    except ValidationError as exc:
        messages.error(request, _format_validation_error(exc))
    return redirect("pip_list")

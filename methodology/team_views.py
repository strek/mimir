"""Django views for the Teams feature (Act 11 — FOB-TEAMS-*).

Shared between browse (FOB-TEAMS-BROWSE-*) and create (FOB-TEAMS-CREATE-*)
scenarios.  Detail and manage views are stubs for WP-4 and WP-5.
"""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

from methodology.models import Team
from methodology.services.team_service import TeamService

logger = logging.getLogger(__name__)

CATEGORIES: list[str] = ["Engineering", "Design", "Research", "Product", "Private", "Other"]
VISIBILITY_CHOICES: list[str] = ["Public", "Hidden"]
JOIN_POLICY_CHOICES: list[str] = ["Auto-approve", "Requires Approval", "Invite Only"]


@login_required
def teams_browse(request):
    """FOB-TEAMS-BROWSE-*: list teams visible to user with search and category filter.

    :param request: Django HTTP request.
    :returns: Rendered browse page.
    """
    logger.info("[teams] browse | user=%s", request.user.username)
    service = TeamService()
    teams = service.get_teams_visible_to(request.user)

    q, category = _extract_browse_filters(request)
    teams = _apply_browse_filters(teams, q, category)

    context = _build_browse_context(teams, q, category)
    return render(request, "teams/browse.html", context)


@login_required
def teams_create(request):
    """FOB-TEAMS-CREATE-*: render create-team form (GET) and handle POST.

    :param request: Django HTTP request.
    :returns: Rendered form or redirect to detail page on success.
    """
    logger.info("[teams] create | method=%s user=%s", request.method, request.user.username)
    if request.method == "POST":
        return _handle_create_post(request)
    return render(request, "teams/create.html", _empty_create_context())


@login_required
def teams_detail(request, pk: int):
    """FOB-TEAMS-VIEW-*: team detail stub — implemented fully in WP-4.

    :param request: Django HTTP request.
    :param pk: Team primary key.
    :returns: Rendered detail page.
    """
    logger.info("[teams] detail | pk=%s user=%s", pk, request.user.username)
    service = TeamService()
    team = service.get_team_or_404(pk, request.user)
    user_role = service.get_member_role(team, request.user)
    return render(request, "teams/detail.html", {
        "team": team,
        "user_role": user_role,
        "active_page": "teams",
    })


@login_required
def teams_manage(request, pk: int):
    """FOB-TEAMS-MANAGE-*: team management stub — implemented fully in WP-5.

    :param request: Django HTTP request.
    :param pk: Team primary key.
    :returns: Rendered manage page.
    """
    logger.info("[teams] manage | pk=%s user=%s", pk, request.user.username)
    service = TeamService()
    team = service.get_team_or_404(pk, request.user)
    return render(request, "teams/manage.html", {
        "team": team,
        "active_page": "teams",
    })


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_browse_filters(request) -> tuple[str, str]:
    """Extract search query and category from GET params.

    :param request: Django HTTP request.
    :returns: Tuple of (query_string, category_string).
    """
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    return q, category


def _apply_browse_filters(teams, q: str, category: str):
    """Apply text search and category filter to teams queryset.

    :param teams: Base queryset of Team objects.
    :param q: Search term (matches name or description).
    :param category: Category string to filter on.
    :returns: Filtered queryset.
    """
    from django.db.models import Q as DjangoQ

    if q:
        teams = teams.filter(
            DjangoQ(name__icontains=q) | DjangoQ(description__icontains=q)
        ).distinct()
        logger.info("[teams] search q=%r results=%d", q, teams.count())
    if category:
        teams = teams.filter(category=category)
        logger.info("[teams] category filter=%r results=%d", category, teams.count())
    return teams


def _build_browse_context(teams, q: str, category: str) -> dict:
    """Build template context for the browse page.

    :param teams: Filtered queryset of Team objects.
    :param q: Active search query string.
    :param category: Active category filter string.
    :returns: Context dictionary for the template.
    """
    return {
        "teams": teams,
        "team_count": teams.count(),
        "categories": CATEGORIES,
        "search_query": q,
        "active_category": category,
        "active_page": "teams",
        "nav_section": "teams",
    }


def _handle_create_post(request):
    """Handle POST for team creation: validate, delegate to TeamService, redirect.

    :param request: Django HTTP request (method must be POST).
    :returns: Redirect on success; rendered form with errors on failure.
    """
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()
    visibility = request.POST.get("visibility", "Public")
    join_policy = request.POST.get("join_policy", "Auto-approve")
    category = request.POST.get("category", "Other")

    logger.info(
        "[teams] create POST | user=%s name=%r visibility=%s",
        request.user.username, name, visibility,
    )

    errors = _validate_team_form(name)
    if errors:
        return _render_create_with_errors(request, errors)

    service = TeamService()
    try:
        team = service.create_team(
            request.user, name, description, visibility, join_policy, category
        )
        logger.info("[teams] created pk=%s name=%r by user=%s", team.pk, name, request.user.username)
        messages.success(request, f"Team '{team.name}' created successfully.")
        return redirect("teams:teams_detail", pk=team.pk)
    except IntegrityError:
        logger.warning("[teams] duplicate name=%r for user=%s", name, request.user.username)
        errors["name"] = "A team with this name already exists."
        return _render_create_with_errors(request, errors)


def _validate_team_form(name: str) -> dict:
    """Validate team creation form fields.

    :param name: Proposed team name.
    :returns: Dict mapping field names to error messages; empty if valid.
    """
    errors: dict = {}
    if not name:
        errors["name"] = "Team name is required."
    elif len(name) > 100:
        errors["name"] = "Team name cannot exceed 100 characters."
    return errors


def _render_create_with_errors(request, errors: dict):
    """Render the create form template with validation errors.

    :param request: Django HTTP request.
    :param errors: Dict of field → error message.
    :returns: Rendered HTTP response with status 200.
    """
    context = {
        **_empty_create_context(),
        "errors": errors,
        "form_data": request.POST,
    }
    return render(request, "teams/create.html", context)


def _empty_create_context() -> dict:
    """Return a default (empty) context dict for the create form.

    :returns: Context dictionary with choice lists and empty errors.
    """
    return {
        "categories": CATEGORIES,
        "visibility_choices": VISIBILITY_CHOICES,
        "join_policy_choices": JOIN_POLICY_CHOICES,
        "errors": {},
        "form_data": {},
        "active_page": "teams",
        "nav_section": "teams",
    }

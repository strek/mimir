"""Inject global template variables for methodology nav."""

from __future__ import annotations

from django.http import HttpRequest


def pip_nav(request: HttpRequest) -> dict:
    """
    Unread count for top-nav PIPs pill.

    :param request: Incoming HTTP request.
    :returns: Mapping with ``pip_nav_unread_count`` when authenticated.
    """
    if request.user.is_authenticated:
        from methodology.services.pip_service import PIPService

        return {"pip_nav_unread_count": PIPService.unread_submitter_count(request.user)}
    return {"pip_nav_unread_count": 0}

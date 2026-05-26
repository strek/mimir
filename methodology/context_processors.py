"""Context processors for methodology app.

Injects global context variables into all template contexts.
"""

from methodology.services.notification_service import NotificationService


def app_version(request):
    """Inject application version information.

    :param request: Django HTTP request.
    :returns: Empty dict (version injected via other means).
    """
    return {}


def pip_nav(request):
    """Inject PIP navigation badge count for unread PIPs.

    :param request: Django HTTP request.
    :returns: Dict with pip_nav_unread_count key.
    """
    if request.user.is_authenticated:
        from methodology.models import ProcessImprovementProposal

        unread_count = ProcessImprovementProposal.objects.filter(
            status=ProcessImprovementProposal.STATUS_SUBMITTED
        ).count()
        return {"pip_nav_unread_count": unread_count}
    return {"pip_nav_unread_count": 0}


def primary_nav_section(request):
    """Inject primary navigation section context.

    :param request: Django HTTP request.
    :returns: Empty dict (views set nav_section manually).
    """
    return {}


def notification_count(request):
    """Inject unread notification count for authenticated users.

    :param request: Django HTTP request.
    :returns: Dict with unread_notification_count key.
    """
    if request.user.is_authenticated:
        count = NotificationService.get_unread_count(request.user)
        return {"unread_notification_count": count}
    return {"unread_notification_count": 0}

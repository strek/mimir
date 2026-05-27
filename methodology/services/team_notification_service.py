"""Team event notification service.

Sends transactional emails for team lifecycle events:
- Auto-join confirmation
- Join request notification to admin
- Request approved / rejected
- Member removed
- Admin transferred

Follows the same pattern as pip_notification_service.py.
"""

from __future__ import annotations

import logging

from django.template.loader import render_to_string

from accounts.services.email_service import EmailService

from methodology.models import JoinRequest, Team, TeamMembership

logger = logging.getLogger(__name__)


def send_auto_join_confirmation(membership: TeamMembership) -> None:
    """VIEW-18: Send confirmation email to user who auto-joined a team.

    :param membership: The newly created TeamMembership instance.
    """
    _send_team_email(
        subject=f"You've joined the {membership.team.name} team",
        template="teams/email_joined",
        context={"membership": membership, "team": membership.team, "user": membership.user},
        recipient_email=membership.user.email,
        action="auto_join_confirmation",
        team_name=membership.team.name,
        username=membership.user.username,
    )
    _create_in_app_notification(
        user=membership.user,
        notification_type="team_approved",
        title=f"Joined {membership.team.name}",
        message=f"You are now a member of the {membership.team.name} team.",
        link=f"/teams/{membership.team.pk}/",
    )


def send_join_request_to_admin(join_request: JoinRequest) -> None:
    """VIEW-19: Notify team admin of a new join request.

    :param join_request: The pending JoinRequest instance.
    """
    _send_team_email(
        subject=f'New join request for your team "{join_request.team.name}"',
        template="teams/email_join_request",
        context={
            "join_request": join_request,
            "team": join_request.team,
            "user": join_request.user,
        },
        recipient_email=join_request.team.admin.email,
        action="join_request_to_admin",
        team_name=join_request.team.name,
        username=join_request.user.username,
    )
    _create_in_app_notification(
        user=join_request.team.admin,
        notification_type="team_join_request",
        title=f"Join request for {join_request.team.name}",
        message=f"{join_request.user.username} wants to join your team.",
        link=f"/teams/{join_request.team.pk}/manage/?tab=join-requests",
    )


def send_request_approved(join_request: JoinRequest) -> None:
    """MANAGE-03: Notify user their join request was approved.

    :param join_request: The approved JoinRequest instance.
    """
    _send_team_email(
        subject=f"Your request to join '{join_request.team.name}' was approved",
        template="teams/email_request_approved",
        context={
            "join_request": join_request,
            "team": join_request.team,
            "user": join_request.user,
        },
        recipient_email=join_request.user.email,
        action="request_approved",
        team_name=join_request.team.name,
        username=join_request.user.username,
    )
    _create_in_app_notification(
        user=join_request.user,
        notification_type="team_approved",
        title=f"Joined {join_request.team.name}",
        message=f"Your request to join {join_request.team.name} was approved.",
        link=f"/teams/{join_request.team.pk}/",
    )


def send_request_rejected(join_request: JoinRequest) -> None:
    """MANAGE-04: Notify user their join request was rejected.

    :param join_request: The rejected JoinRequest instance.
    """
    _send_team_email(
        subject=f"Your request to join '{join_request.team.name}' was not approved",
        template="teams/email_request_rejected",
        context={
            "join_request": join_request,
            "team": join_request.team,
            "user": join_request.user,
        },
        recipient_email=join_request.user.email,
        action="request_rejected",
        team_name=join_request.team.name,
        username=join_request.user.username,
    )
    _create_in_app_notification(
        user=join_request.user,
        notification_type="team_rejected",
        title=f"Request to join {join_request.team.name} declined",
        message=f"Your request to join {join_request.team.name} was not approved.",
        link="",
    )


def send_member_removed(membership: TeamMembership) -> None:
    """MANAGE-07: Notify user they were removed from a team.

    :param membership: The TeamMembership instance (before removal).
    """
    _send_team_email(
        subject=f"You have been removed from the '{membership.team.name}' team",
        template="teams/email_member_removed",
        context={"membership": membership, "team": membership.team, "user": membership.user},
        recipient_email=membership.user.email,
        action="member_removed",
        team_name=membership.team.name,
        username=membership.user.username,
    )
    _create_in_app_notification(
        user=membership.user,
        notification_type="team_removed",
        title=f"Removed from {membership.team.name}",
        message=f"You have been removed from the {membership.team.name} team.",
        link="",
    )


def send_admin_transferred(team: Team, new_admin, old_admin) -> None:
    """MANAGE-10: Notify new admin of their new admin role.

    :param team: The Team whose admin changed.
    :param new_admin: User who received admin rights.
    :param old_admin: User who relinquished admin rights.
    """
    _send_team_email(
        subject=f"You are now the admin of the '{team.name}' team",
        template="teams/email_admin_transferred",
        context={"team": team, "new_admin": new_admin, "old_admin": old_admin},
        recipient_email=new_admin.email,
        action="admin_transferred",
        team_name=team.name,
        username=new_admin.username,
    )
    _create_in_app_notification(
        user=new_admin,
        notification_type="team_admin_transfer",
        title=f"Now admin of {team.name}",
        message=f"You are now the admin of the {team.name} team.",
        link=f"/teams/{team.pk}/manage/",
    )


def send_invite_existing_user(join_request: JoinRequest, welcome_text: str) -> None:
    """MANAGE-23: Invite an existing platform user to join the team.

    :param join_request: The JoinRequest created for this invitation.
    :param welcome_text: Optional custom message from the inviting admin.
    """
    _send_team_email(
        subject=f"You've been invited to join the {join_request.team.name} team on Mimir",
        template="teams/email_invite_existing",
        context={
            "join_request": join_request,
            "team": join_request.team,
            "user": join_request.user,
            "welcome_text": welcome_text,
        },
        recipient_email=join_request.user.email,
        action="invite_existing_user",
        team_name=join_request.team.name,
        username=join_request.user.username,
    )
    _create_in_app_notification(
        user=join_request.user,
        notification_type="team_invite",
        title=f"Invited to {join_request.team.name}",
        message=f"You've been invited to join the {join_request.team.name} team.",
        link=f"/teams/{join_request.team.pk}/",
    )


def send_invite_new_user(join_request: JoinRequest, activation_token: str, welcome_text: str) -> None:
    """MANAGE-24: Send activation + invite email to a newly auto-registered user.

    :param join_request: The JoinRequest created for this invitation.
    :param activation_token: Token for account activation.
    :param welcome_text: Optional custom message from the inviting admin.
    """
    base_url = EmailService.get_site_base_url()
    _send_team_email(
        subject=f"You've been invited to Mimir and the {join_request.team.name} team",
        template="teams/email_invite_new_user",
        context={
            "join_request": join_request,
            "team": join_request.team,
            "user": join_request.user,
            "activation_token": activation_token,
            "welcome_text": welcome_text,
            "base_url": base_url,
        },
        recipient_email=join_request.user.email,
        action="invite_new_user",
        team_name=join_request.team.name,
        username=join_request.user.username,
    )
    # Note: New users can't see in-app notifications until they activate their account
    # Notification will be available after they verify email and log in
    _create_in_app_notification(
        user=join_request.user,
        notification_type="team_invite",
        title=f"Invited to {join_request.team.name}",
        message=f"You've been invited to join the {join_request.team.name} team.",
        link=f"/teams/{join_request.team.pk}/",
    )


def _send_team_email(
    subject: str,
    template: str,
    context: dict,
    recipient_email: str,
    action: str,
    team_name: str,
    username: str,
) -> None:
    """Send a team event email using a plain-text template.

    :param subject: Email subject line.
    :param template: Template path prefix (without .txt extension).
    :param context: Template context dict.
    :param recipient_email: Recipient email address.
    :param action: Action label for log messages.
    :param team_name: Team name for log messages.
    :param username: Username for log messages.
    """
    if not recipient_email:
        logger.warning(
            "[teams] email skipped: no recipient email | action=%s team=%s username=%s",
            action,
            team_name,
            username,
        )
        return

    logger.info(
        "[teams] sending email | action=%s team=%s recipient=%s",
        action,
        team_name,
        recipient_email,
    )

    context = {**context, "base_url": EmailService.get_site_base_url()}
    body_txt = render_to_string(f"{template}.txt", context)

    try:
        EmailService.send_text_email(subject, body_txt, [recipient_email])
        logger.info(
            "[teams] email sent | action=%s team=%s recipient=%s",
            action,
            team_name,
            recipient_email,
        )
    except Exception as exc:
        logger.error(
            "[teams] email failed | action=%s team=%s error=%s",
            action,
            team_name,
            str(exc),
            exc_info=True,
        )
        raise


def _create_in_app_notification(user, notification_type: str, title: str, message: str, link: str) -> None:
    """Create an in-app notification (non-fatal).

    :param user: User to notify.
    :param notification_type: Notification type constant.
    :param title: Notification title.
    :param message: Notification message.
    :param link: Optional link URL.
    """
    try:
        from methodology.services.notification_service import NotificationService

        NotificationService.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
        )
        logger.info(
            "[teams] in-app notification created | user=%s type=%s title=%s",
            user.username,
            notification_type,
            title,
        )
    except Exception as exc:
        logger.warning(
            "[teams] in-app notification failed (non-fatal) | user=%s type=%s error=%s",
            user.username,
            notification_type,
            str(exc),
        )

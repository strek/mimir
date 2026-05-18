"""
Transactional email for accounts — uses Django ``EMAIL_BACKEND``.

In development: console backend prints to stdout.
In production: ``django_ses.SESBackend`` (see ``mimir.settings.prod``).
Tests: ``locmem`` backend and ``django.core.mail.outbox``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

logger = logging.getLogger(__name__)


class EmailService:
    """Send multipart (text + HTML) email via Django's mail API."""

    @staticmethod
    def _send_multipart(
        subject: str,
        text_body: str,
        html_body: str,
        to_addresses: list[str],
    ) -> None:
        """Send one email with plain-text and HTML alternatives.

        :param subject: Email subject line.
        :param text_body: Plain-text body.
        :param html_body: HTML body.
        :param to_addresses: Recipient list (not logged — privacy).
        :raises Exception: Re-raises any failure from Django's mail layer.
        """
        sender = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@mimir.local")
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=sender,
            to=to_addresses,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        logger.info(
            "[EMAIL] Sent subject=%r to_n=%d from_backend=%s",
            subject,
            len(to_addresses),
            settings.EMAIL_BACKEND,
        )

    @staticmethod
    def send_welcome_email(user: AbstractBaseUser) -> None:
        """Send welcome email to new user.

        :param user: Django user with ``email`` set.
        :raises Exception: If delivery fails.
        """
        subject = "Welcome to Mimir!"
        body_text = f"""
Hello {user.first_name or user.username},

Welcome to Mimir! Your account has been successfully created.

You can now start creating playbooks and workflows to organize your development processes.

Username: {user.username}
Email: {user.email}

If you have any questions, please don't hesitate to reach out.

Best regards,
The Mimir Team
"""
        body_html = f"""
<html>
<head></head>
<body>
  <h1>Welcome to Mimir!</h1>
  <p>Hello {user.first_name or user.username},</p>
  <p>Your account has been successfully created.</p>
  <p>You can now start creating playbooks and workflows to organize your development processes.</p>
  <p><strong>Account Details:</strong></p>
  <ul>
    <li>Username: {user.username}</li>
    <li>Email: {user.email}</li>
  </ul>
  <p>If you have any questions, please don't hesitate to reach out.</p>
  <p>Best regards,<br>The Mimir Team</p>
</body>
</html>
"""
        EmailService._send_multipart(subject, body_text, body_html, [user.email])

    @staticmethod
    def send_password_reset_email(user: AbstractBaseUser, reset_token: str) -> None:
        """Send password reset email with token link.

        :param user: Django user.
        :param reset_token: Opaque reset token from Django's auth framework.
        :raises Exception: If delivery fails.
        """
        base_url = getattr(settings, "FRONTEND_URL", "https://mimir.featurefactory.io")
        reset_url = f"{base_url.rstrip('/')}/reset-password?token={reset_token}"
        subject = "Password Reset Request"
        body_text = f"""
Hello {user.first_name or user.username},

You requested a password reset for your Mimir account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
The Mimir Team
"""
        body_html = f"""
<html>
<head></head>
<body>
  <h1>Password Reset Request</h1>
  <p>Hello {user.first_name or user.username},</p>
  <p>You requested a password reset for your Mimir account.</p>
  <p><a href="{reset_url}">Click here to reset your password</a></p>
  <p>This link will expire in 24 hours.</p>
  <p>If you didn't request this, please ignore this email.</p>
  <p>Best regards,<br>The Mimir Team</p>
</body>
</html>
"""
        EmailService._send_multipart(subject, body_text, body_html, [user.email])

    @staticmethod
    def send_verification_email(
        user: AbstractBaseUser,
        token: str,
        *,
        base_url: str | None = None,
    ) -> None:
        """Send email with one-click verification link.

        :param user: Django user; mail goes to ``user.email``.
        :param token: URL-safe verification token.
        :param base_url: Site origin (default: ``settings.FRONTEND_URL``).
        :raises Exception: If delivery fails.
        """
        root = (base_url or getattr(settings, "FRONTEND_URL", "")).rstrip("/")
        verify_url = f"{root}/auth/user/verify-email/{token}/"
        ctx = {"user": user, "verify_url": verify_url}
        text_body = render_to_string("accounts/email_verify.txt", ctx)
        html_body = render_to_string("accounts/email_verify.html", ctx)
        subject = "Verify your Mimir email address"
        EmailService._send_multipart(subject, text_body, html_body, [user.email])

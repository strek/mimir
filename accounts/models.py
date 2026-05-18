import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)

_VERIFICATION_TOKEN_BYTES = 32
"""Number of random bytes for URL-safe verification tokens."""

_EMAIL_VERIFICATION_TOKEN_MAX_AGE_HOURS = 24
"""Tokens older than this are treated as expired."""


class UserOnboardingState(models.Model):
    """Persistent onboarding state for a user.

    Tracks whether onboarding is completed and current step index.

    Fields:
        user (OneToOneField): Related auth user. Example: User(username="maria")
        is_completed (bool): Onboarding completion flag. Example: True
        current_step (int): Current onboarding step index. Example: 0
        completed_at (datetime|None): When onboarding was completed. Example: 2025-01-01T10:00Z
        accepted_tos_at (datetime|None): When the user accepted terms of service at registration.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding_state",
    )
    is_completed = models.BooleanField(default=False)
    current_step = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    accepted_tos_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"OnboardingState(user={self.user!s}, completed={self.is_completed}, step={self.current_step})"


class UserEmailVerification(models.Model):
    """Tracks whether the user's current email address has been verified.

    One row per user. Staff and superuser accounts may be auto-marked verified on create.

    Fields:
        user: Related auth user (one-to-one).
        is_verified: True after the user clicks the verification link.
        verification_token: URL-safe token sent in the verification email (empty when verified).
        token_created_at: When the current token was generated (for 24h expiry).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification",
    )
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, default="")
    token_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"EmailVerification(user={self.user}, verified={self.is_verified})"


def _default_verified_for_user(user: AbstractBaseUser) -> bool:
    """Return True if the user should skip the email verification flow."""
    return bool(user.is_staff or user.is_superuser)


def _fresh_verification_token() -> str:
    """Return a new URL-safe random verification token."""
    return secrets.token_urlsafe(_VERIFICATION_TOKEN_BYTES)


def get_or_create_email_verification(user: AbstractBaseUser) -> UserEmailVerification:
    """Return existing or newly created verification state for user.

    Staff and superuser accounts are created with ``is_verified=True``.

    :param user: Django auth User instance.
    :return: ``UserEmailVerification`` instance for this user.
    """
    verified_default = _default_verified_for_user(user)
    state, created = UserEmailVerification.objects.get_or_create(
        user=user,
        defaults={"is_verified": verified_default},
    )
    if created:
        logger.info(
            "[EMAIL_VERIFY] Created state user_id=%s verified=%s",
            user.pk,
            state.is_verified,
        )
    return state


def mark_email_verified(user: AbstractBaseUser) -> UserEmailVerification:
    """Mark the user's email as verified and clear the active token.

    :param user: Django auth User instance.
    :return: Updated ``UserEmailVerification`` instance.
    """
    state = get_or_create_email_verification(user)
    state.is_verified = True
    state.verification_token = ""
    state.token_created_at = None
    state.save(update_fields=["is_verified", "verification_token", "token_created_at"])
    logger.info("[EMAIL_VERIFY] Marked verified user_id=%s", user.pk)
    return state


def generate_verification_token(user: AbstractBaseUser) -> str:
    """Issue a new verification token and mark email unverified until link is used.

    :param user: Django auth User instance.
    :return: The new token string (also stored on ``UserEmailVerification``).
    """
    state = get_or_create_email_verification(user)
    token = _fresh_verification_token()
    state.is_verified = False
    state.verification_token = token
    state.token_created_at = timezone.now()
    state.save(
        update_fields=["is_verified", "verification_token", "token_created_at"]
    )
    logger.info("[EMAIL_VERIFY] Generated token user_id=%s", user.pk)
    return token


def is_email_verification_token_expired(
    state: UserEmailVerification,
    *,
    reference_time=None,
) -> bool:
    """Return True if the stored token is missing or past the max age window.

    :param state: ``UserEmailVerification`` row.
    :param reference_time: Optional ``datetime`` for tests (default: ``timezone.now()``).
    :return: True when ``token_created_at`` is None or older than 24 hours.
    """
    if state.token_created_at is None:
        return True
    ref = reference_time if reference_time is not None else timezone.now()
    cutoff = state.token_created_at + timedelta(
        hours=_EMAIL_VERIFICATION_TOKEN_MAX_AGE_HOURS
    )
    return ref > cutoff


def get_or_create_onboarding_state(user):
    """Return existing or newly created onboarding state for given user.

    :param user: Django auth user instance. Example: request.user
    :return: UserOnboardingState instance for user. Example: UserOnboardingState(...)
    """
    state, created = UserOnboardingState.objects.get_or_create(user=user)

    if created:
        logger.info("[ONBOARDING] Created onboarding state for user %s", user.username)
    else:
        logger.debug("[ONBOARDING] Retrieved existing onboarding state for user %s", user.username)

    return state


def mark_onboarding_completed(user, step=0):
    """Mark onboarding as completed for the given user.

    Side effects:
        - Ensures onboarding state row exists
        - Sets is_completed=True
        - Sets current_step to provided step (default 0)
        - Updates completed_at timestamp

    :param user: Django auth user instance. Example: request.user
    :param step: int - Final onboarding step index. Example: 0
    :return: Updated UserOnboardingState instance
    """
    state = get_or_create_onboarding_state(user)

    state.is_completed = True
    state.current_step = step
    state.completed_at = timezone.now()
    state.save(update_fields=["is_completed", "current_step", "completed_at"])

    logger.info(
        "[ONBOARDING] Marked onboarding completed for user %s (step=%s)",
        user.username,
        step,
    )

    return state

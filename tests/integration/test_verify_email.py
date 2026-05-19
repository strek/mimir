"""Integration tests for email verification link and resend endpoint."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone

import pytest

from accounts.models import UserEmailVerification, generate_verification_token

User = get_user_model()
_LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_valid_token_marks_verified(client):
    user = User.objects.create_user(
        username="ver_a", email="ver_a@example.com", password="x" * 12
    )
    token = generate_verification_token(user)
    client.get(reverse("verify_email", kwargs={"token": token}))
    ev = UserEmailVerification.objects.get(user=user)
    assert ev.is_verified is True
    assert ev.verification_token == ""


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_valid_token_redirects_to_login_with_success(client):
    user = User.objects.create_user(
        username="ver_b", email="ver_b@example.com", password="x" * 12
    )
    token = generate_verification_token(user)
    response = client.get(
        reverse("verify_email", kwargs={"token": token}),
        follow=True,
    )
    assert response.status_code == 200
    msgs = [m.message for m in get_messages(response.wsgi_request)]
    assert any("verified" in str(m).lower() for m in msgs)


@pytest.mark.django_db
def test_expired_token_shows_error_and_resend(client):
    user = User.objects.create_user(
        username="ver_c", email="ver_c@example.com", password="x" * 12
    )
    token = generate_verification_token(user)
    ev = UserEmailVerification.objects.get(user=user)
    ev.token_created_at = timezone.now() - timedelta(hours=25)
    ev.save(update_fields=["token_created_at"])
    response = client.get(reverse("verify_email", kwargs={"token": token}))
    assert response.status_code == 200
    assert b"expired" in response.content.lower()
    assert b'verify-email-resend-form' in response.content


@pytest.mark.django_db
def test_already_verified_token_redirects_gracefully(client):
    user = User.objects.create_user(
        username="ver_d", email="ver_d@example.com", password="x" * 12
    )
    token = "still-have-token"
    ev, _ = UserEmailVerification.objects.get_or_create(user=user)
    ev.verification_token = token
    ev.is_verified = True
    ev.token_created_at = timezone.now()
    ev.save(update_fields=["verification_token", "is_verified", "token_created_at"])
    response = client.get(
        reverse("verify_email", kwargs={"token": token}), follow=True
    )
    assert response.status_code == 200
    msgs = [m.message for m in get_messages(response.wsgi_request)]
    assert any("already verified" in str(m).lower() for m in msgs)


@pytest.mark.django_db
def test_invalid_token_shows_expired_page(client):
    response = client.get(
        reverse("verify_email", kwargs={"token": "no-such-token-in-db-xyz"})
    )
    assert response.status_code == 200
    assert b'data-testid="verify-email-expired-alert"' in response.content
    assert b'data-testid="verify-email-resend-form"' in response.content


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_resend_sends_new_email(client):
    user = User.objects.create_user(
        username="ver_e", email="ver_e@example.com", password="x" * 12
    )
    generate_verification_token(user)
    mail.outbox.clear()
    client.post(
        reverse("resend_verification"),
        {"email": user.email},
        follow=True,
    )
    assert len(mail.outbox) == 1
    assert "Verify your Mimir email address" in mail.outbox[0].subject


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_resend_with_unknown_email_returns_generic_success(client):
    mail.outbox.clear()
    response = client.post(
        reverse("resend_verification"),
        {"email": "nobody-at-all@example.com"},
        follow=True,
    )
    assert response.status_code == 200
    assert len(mail.outbox) == 0
    msgs = [m.message for m in get_messages(response.wsgi_request)]
    assert msgs

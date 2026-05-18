"""Integration tests for web registration — email verification, ToS, no auto-login."""

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, override_settings
from django.urls import reverse

import pytest

from accounts.models import UserEmailVerification, UserOnboardingState

User = get_user_model()

_LOCMEM = "django.core.mail.backends.locmem.EmailBackend"

_VALID = {
    "first_name": "Denis",
    "last_name": "Petelin",
    "username": "dregister",
    "email": "dregister@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "accepted_tos": "on",
}


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_register_happy_path_creates_user_with_names(client):
    data = {**_VALID, "username": "usera1", "email": "usera1@example.com"}
    response = client.post(reverse("register"), data=data, follow=False)
    assert response.status_code == 302
    u = User.objects.get(username="usera1")
    assert u.first_name == "Denis"
    assert u.last_name == "Petelin"


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_register_records_accepted_tos_at(client):
    data = {**_VALID, "username": "userb2", "email": "userb2@example.com"}
    client.post(reverse("register"), data=data, follow=True)
    u = User.objects.get(username="userb2")
    state = UserOnboardingState.objects.get(user=u)
    assert state.accepted_tos_at is not None


@pytest.mark.django_db
def test_register_without_tos_returns_error(client):
    data = {k: v for k, v in _VALID.items() if k != "accepted_tos"}
    data["username"] = "notos1"
    data["email"] = "notos1@example.com"
    response = client.post(reverse("register"), data=data)
    assert response.status_code == 200
    assert b"You must accept the Terms of Service to register" in response.content
    assert not User.objects.filter(username="notos1").exists()


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_register_sends_verification_email(client):
    mail.outbox.clear()
    data = {**_VALID, "username": "userc3", "email": "userc3@example.com"}
    client.post(reverse("register"), data=data, follow=False)
    assert len(mail.outbox) == 1
    assert "Verify your Mimir email address" in mail.outbox[0].subject


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_register_does_not_auto_login(client):
    data = {**_VALID, "username": "userd4", "email": "userd4@example.com"}
    client.post(reverse("register"), data=data, follow=False)
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_register_redirects_to_login_with_message(client):
    data = {**_VALID, "username": "usere5", "email": "usere5@example.com"}
    response = client.post(reverse("register"), data=data, follow=True)
    assert response.status_code == 200
    msgs = [m.message for m in get_messages(response.wsgi_request)]
    assert any("verify your email" in str(m).lower() for m in msgs)


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_register_duplicate_username_shows_error(client):
    User.objects.create_user(
        username="takenuname", email="ex1@example.com", password="x" * 12
    )
    data = {**_VALID, "username": "takenuname", "email": "newmail@example.com"}
    response = client.post(reverse("register"), data=data)
    assert response.status_code == 200
    assert b"already taken" in response.content.lower()


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_register_duplicate_email_shows_error(client):
    User.objects.create_user(
        username="u1", email="dup@example.com", password="x" * 12
    )
    data = {**_VALID, "username": "freshuser", "email": "dup@example.com"}
    response = client.post(reverse("register"), data=data)
    assert response.status_code == 200
    assert b"already registered" in response.content.lower()


@pytest.mark.django_db
def test_register_password_mismatch_shows_error(client):
    data = {
        **_VALID,
        "username": "mismatch_u",
        "email": "mismatch@example.com",
        "password": "aaaaaaaa",
        "password_confirm": "bbbbbbbb",
    }
    response = client.post(reverse("register"), data=data)
    assert response.status_code == 200
    assert b"do not match" in response.content.lower() or b"passwords" in response.content.lower()
"""Profile edit: email change triggers re-verification, token invalidation, logout."""

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, override_settings
from django.urls import reverse

import pytest

from accounts.models import UserEmailVerification, generate_verification_token
from rest_framework.authtoken.models import Token

User = get_user_model()
_LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def client():
    return Client()


def _verified_logged_in_client(client, username, email, password):
    user = User.objects.create_user(
        username=username, email=email, password=password
    )
    tok = generate_verification_token(user)
    client.get(reverse("verify_email", kwargs={"token": tok}))
    client.post(reverse("login"), {"username": username, "password": password})
    return user


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_email_change_sends_verification_email(client):
    user = _verified_logged_in_client(
        client, "pe_a", "pe_a@example.com", "securepass12"
    )
    mail.outbox.clear()
    client.post(
        reverse("profile_edit"),
        {
            "first_name": user.first_name or "F",
            "last_name": user.last_name or "L",
            "email": "pe_a_new@example.com",
        },
    )
    assert len(mail.outbox) == 1
    assert "Verify your Mimir email address" in mail.outbox[0].subject


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_email_change_invalidates_drf_token(client):
    user = _verified_logged_in_client(
        client, "pe_b", "pe_b@example.com", "securepass12"
    )
    assert Token.objects.filter(user=user).exists()
    client.post(
        reverse("profile_edit"),
        {
            "first_name": "F",
            "last_name": "L",
            "email": "pe_b_new@example.com",
        },
    )
    assert not Token.objects.filter(user=user).exists()


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_email_change_terminates_session(client):
    user = _verified_logged_in_client(
        client, "pe_c", "pe_c@example.com", "securepass12"
    )
    client.post(
        reverse("profile_edit"),
        {
            "first_name": "F",
            "last_name": "L",
            "email": "pe_c_new@example.com",
        },
        follow=False,
    )
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_email_change_redirects_to_login_with_message(client):
    user = _verified_logged_in_client(
        client, "pe_d", "pe_d@example.com", "securepass12"
    )
    response = client.post(
        reverse("profile_edit"),
        {
            "first_name": "F",
            "last_name": "L",
            "email": "pe_d_new@example.com",
        },
        follow=True,
    )
    assert response.status_code == 200
    msgs = [m.message for m in get_messages(response.wsgi_request)]
    assert any("verify" in str(m).lower() for m in msgs)
    assert b"login-resend-btn" in response.content
    assert b"pe_d_new@example.com" in response.content


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_name_only_change_does_not_logout(client):
    user = _verified_logged_in_client(
        client, "pe_e", "pe_e@example.com", "securepass12"
    )
    client.post(
        reverse("profile_edit"),
        {
            "first_name": "Newfirst",
            "last_name": "Newlast",
            "email": user.email,
        },
        follow=False,
    )
    assert "_auth_user_id" in client.session
    user.refresh_from_db()
    assert user.first_name == "Newfirst"
    assert user.last_name == "Newlast"


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_name_only_change_does_not_send_email(client):
    user = _verified_logged_in_client(
        client, "pe_f", "pe_f@example.com", "securepass12"
    )
    mail.outbox.clear()
    client.post(
        reverse("profile_edit"),
        {
            "first_name": "X",
            "last_name": "Y",
            "email": user.email,
        },
    )
    assert len(mail.outbox) == 0


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_staff_email_change_no_lockout(client):
    User.objects.create_user(
        username="pe_staff",
        email="pe_staff@example.com",
        password="securepass12",
        is_staff=True,
    )
    client.post(
        reverse("login"),
        {"username": "pe_staff", "password": "securepass12"},
    )
    response = client.post(
        reverse("profile_edit"),
        {
            "first_name": "F",
            "last_name": "L",
            "email": "pe_staff_new@example.com",
        },
        follow=False,
    )
    assert response.status_code == 302
    assert response.url == reverse("profile")
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND=_LOCMEM)
def test_staff_email_change_auto_verified(client):
    user = User.objects.create_user(
        username="pe_staff2",
        email="pe_staff2@example.com",
        password="securepass12",
        is_staff=True,
    )
    client.post(
        reverse("login"),
        {"username": "pe_staff2", "password": "securepass12"},
    )
    client.post(
        reverse("profile_edit"),
        {
            "first_name": "F",
            "last_name": "L",
            "email": "pe_staff2_new@example.com",
        },
    )
    user.refresh_from_db()
    assert user.email == "pe_staff2_new@example.com"
    ev = UserEmailVerification.objects.get(user=user)
    assert ev.is_verified is True

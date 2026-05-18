"""Integration tests: login blocked until email verified; DRF token on login."""

from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token

import pytest

from accounts.models import UserEmailVerification, generate_verification_token

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_unverified_user_cannot_login(client):
    user = User.objects.create_user(
        username="gate_u1", email="gate_u1@example.com", password="securepass12"
    )
    generate_verification_token(user)
    response = client.post(
        reverse("login"),
        {"username": "gate_u1", "password": "securepass12"},
    )
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_unverified_user_sees_resend_link(client):
    user = User.objects.create_user(
        username="gate_u2", email="gate_u2@example.com", password="securepass12"
    )
    generate_verification_token(user)
    response = client.post(
        reverse("login"),
        {"username": "gate_u2", "password": "securepass12"},
    )
    assert response.status_code == 200
    assert b"login-resend-btn" in response.content


@pytest.mark.django_db
def test_verified_user_can_login(client):
    user = User.objects.create_user(
        username="gate_u3", email="gate_u3@example.com", password="securepass12"
    )
    tok = generate_verification_token(user)
    client.get(reverse("verify_email", kwargs={"token": tok}))
    response = client.post(
        reverse("login"),
        {"username": "gate_u3", "password": "securepass12"},
        follow=False,
    )
    assert response.status_code == 302
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_staff_user_bypasses_verification_gate(client):
    user = User.objects.create_user(
        username="gate_staff",
        email="gate_staff@example.com",
        password="securepass12",
        is_staff=True,
    )
    ev, _ = UserEmailVerification.objects.get_or_create(user=user)
    ev.is_verified = False
    ev.verification_token = "x"
    ev.save(update_fields=["is_verified", "verification_token"])
    response = client.post(
        reverse("login"),
        {"username": "gate_staff", "password": "securepass12"},
        follow=False,
    )
    assert response.status_code == 302
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_superuser_bypasses_verification_gate(client):
    user = User.objects.create_user(
        username="gate_super",
        email="gate_super@example.com",
        password="securepass12",
        is_superuser=True,
        is_staff=True,
    )
    ev, _ = UserEmailVerification.objects.get_or_create(user=user)
    ev.is_verified = False
    ev.save(update_fields=["is_verified"])
    response = client.post(
        reverse("login"),
        {"username": "gate_super", "password": "securepass12"},
        follow=False,
    )
    assert response.status_code == 302
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_login_creates_drf_token_if_missing(client):
    user = User.objects.create_user(
        username="gate_tok1", email="gate_tok1@example.com", password="securepass12"
    )
    tok = generate_verification_token(user)
    client.get(reverse("verify_email", kwargs={"token": tok}))
    assert not Token.objects.filter(user=user).exists()
    client.post(
        reverse("login"),
        {"username": "gate_tok1", "password": "securepass12"},
    )
    assert Token.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_login_does_not_duplicate_existing_token(client):
    user = User.objects.create_user(
        username="gate_tok2", email="gate_tok2@example.com", password="securepass12"
    )
    tok = generate_verification_token(user)
    client.get(reverse("verify_email", kwargs={"token": tok}))
    existing = Token.objects.create(user=user)
    client.post(
        reverse("login"),
        {"username": "gate_tok2", "password": "securepass12"},
    )
    assert Token.objects.filter(user=user).count() == 1
    assert Token.objects.get(user=user).key == existing.key

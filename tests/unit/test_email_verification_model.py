"""Unit tests for UserEmailVerification and email verification helpers."""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import (
    UserEmailVerification,
    generate_verification_token,
    get_or_create_email_verification,
    is_email_verification_token_expired,
    mark_email_verified,
)

User = get_user_model()


@pytest.fixture
def regular_user(db):
    u = User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="testpass123",
    )
    u.is_staff = False
    u.is_superuser = False
    u.save()
    return u


@pytest.fixture
def staff_user(db):
    u = User.objects.create_user(
        username="staffuser",
        email="staff@example.com",
        password="testpass123",
        is_staff=True,
    )
    return u


@pytest.mark.django_db
def test_get_or_create_creates_for_new_user(regular_user):
    assert not UserEmailVerification.objects.filter(user=regular_user).exists()
    state = get_or_create_email_verification(regular_user)
    assert state.pk is not None
    assert state.user_id == regular_user.id
    assert state.is_verified is False


@pytest.mark.django_db
def test_get_or_create_returns_existing(regular_user):
    s1 = get_or_create_email_verification(regular_user)
    s2 = get_or_create_email_verification(regular_user)
    assert s1.pk == s2.pk


@pytest.mark.django_db
def test_generate_token_sets_fields(regular_user):
    get_or_create_email_verification(regular_user)
    tok = generate_verification_token(regular_user)
    state = UserEmailVerification.objects.get(user=regular_user)
    assert tok == state.verification_token
    assert len(tok) > 0
    assert state.is_verified is False
    assert state.token_created_at is not None


@pytest.mark.django_db
def test_mark_verified_clears_token(regular_user):
    generate_verification_token(regular_user)
    mark_email_verified(regular_user)
    state = UserEmailVerification.objects.get(user=regular_user)
    assert state.is_verified is True
    assert state.verification_token == ""
    assert state.token_created_at is None


@pytest.mark.django_db
def test_is_token_expired_returns_true_after_24h(regular_user):
    state = get_or_create_email_verification(regular_user)
    state.verification_token = "abc"
    state.token_created_at = timezone.now() - timedelta(hours=25)
    state.save()
    assert is_email_verification_token_expired(state) is True


@pytest.mark.django_db
def test_is_token_expired_returns_false_within_24h(regular_user):
    state = get_or_create_email_verification(regular_user)
    state.verification_token = "abc"
    state.token_created_at = timezone.now() - timedelta(hours=1)
    state.save()
    assert is_email_verification_token_expired(state) is False


@pytest.mark.django_db
def test_staff_on_create_auto_verified(staff_user):
    state = get_or_create_email_verification(staff_user)
    assert state.is_verified is True

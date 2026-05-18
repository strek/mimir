"""
Test settings for mimir project.

Fast SQLite in-memory for pytest. E2E compatibility with the threaded
``live_server`` relies on **function-scoped** ``live_server`` in
``tests/e2e/conftest.py`` (pytest-django's default ``live_server`` is
session-scoped and can go stale after many integration tests).
"""

from .base import *  # noqa: F401, F403

# Environment identifier
MIMIR_ENV = 'test'

# Use a fixed secret key for tests
SECRET_KEY = "django-test-secret-key-not-for-production"

# Debug off in tests (closer to prod)
DEBUG = False

# Allow testserver hostname
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# CSRF trusted origins for test client
CSRF_TRUSTED_ORIGINS = [
    'http://testserver',
    'http://localhost',
    'http://127.0.0.1',
]


# Disable live Claude in pytest — StubGaldrClient path.
GALDR_USE_ANTHROPIC = False

# Galdr: synchronous in tests keeps ProcessImprovementProposal rows visible during assertions.
GALDR_EAGER = True

# Capture notification emails during tests.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@test.mimir"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Password hashers (faster for tests)
# https://docs.djangoproject.com/en/5.2/topics/testing/overview/#password-hashing

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]


# Logging configuration (minimal for tests)
# https://docs.djangoproject.com/en/5.2/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'CRITICAL',
    },
}

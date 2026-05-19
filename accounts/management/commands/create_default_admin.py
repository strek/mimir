"""Management command to create default admin user for local development."""

import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Ensure the local `admin` superuser matches dev defaults (staff + superuser + password)."""

    help = 'Local dev only: ensure superuser username admin exists (staff flags; password matches test facade defaults)'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin'
        default_email = 'admin@example.com'

        existing = User.objects.filter(username=username).first()
        if existing:
            existing.set_password(password)
            existing.is_staff = True
            existing.is_superuser = True
            existing.is_active = True
            update_fields = ['password', 'is_staff', 'is_superuser', 'is_active']
            if not (existing.email or '').strip():
                existing.email = default_email
                update_fields.append('email')
            existing.save(update_fields=update_fields)
            logger.info(
                '[create_default_admin] Updated user=%s is_staff=%s is_superuser=%s',
                username,
                existing.is_staff,
                existing.is_superuser,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated "{username}" (password reset, staff and superuser flags set)'
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=default_email,
            password=password,
        )
        logger.info('[create_default_admin] Created superuser username=%s', username)
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created superuser "{username}".'
            )
        )

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestDashboardNavigation:
    """Integration tests for dashboard navigation and quick actions (NAV-01..NAV-03)."""

    def test_dashboard_has_quick_create_playbook_action(self):
        """NAV-03: Dashboard shows [+ New Playbook] quick action linking to playbook create wizard."""
        client = Client()
        user = User.objects.create_user(
            username="maria",
            email="maria@example.com",
            password="SecurePass123",
        )
        client.force_login(user)

        response = client.get(reverse("dashboard"))

        assert response.status_code == 200
        content = response.content.decode("utf-8")

        # Quick action button must be present in header
        assert "New Playbook" in content
        assert 'data-testid="dashboard-quick-new-playbook-header"' in content

        # Tooltip should explain the action
        assert 'data-bs-toggle="tooltip"' in content
        assert 'title="Create a new playbook"' in content

        # Icon should follow UI conventions (playbook icon)
        assert "fa-book-sparkles" in content

        # Link should go to playbook_create (FOB-PLAYBOOKS-CREATE_PLAYBOOK-1 entry point)
        create_url = reverse("playbook_create")
        assert create_url in content

        # Verify disabled import placeholder in header dropdown
        assert 'data-testid="quick-action-import-playbook-header"' in content
        assert "Import Playbook" in content

        # Settings opens Django admin and is shown only to staff
        assert 'data-testid="dashboard-settings-button"' not in content

        # Verify Dashboard button is NOT present on dashboard
        assert 'Dashboard</button>' not in content or content.count('Dashboard</button>') == 0

    def test_dashboard_staff_shows_admin_settings_link(self):
        """Staff users see Settings linking to Django admin."""
        client = Client()
        user = User.objects.create_user(
            username="staff_maria",
            email="staff@example.com",
            password="SecurePass123",
            is_staff=True,
        )
        client.force_login(user)

        response = client.get(reverse("dashboard"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        admin_url = reverse("admin:index")
        assert admin_url in content
        assert 'data-testid="dashboard-settings-button"' in content
        assert "Settings" in content

        assert 'Dashboard</button>' not in content or content.count('Dashboard</button>') == 0

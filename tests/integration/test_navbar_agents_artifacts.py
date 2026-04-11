"""
Integration tests for Agents and Artifacts navbar navigation.
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestNavbarAgentsArtifacts:
    """Test Agents and Artifacts links in main navbar."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_nav_user',
            email='nav@test.com',
            password='testpass123'
        )
        self.client.login(username='test_nav_user', password='testpass123')
    
    def test_agents_link_enabled(self):
        """Agents link is enabled and clickable."""
        response = self.client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert b'href="/agents/"' in response.content
        assert b'data-testid="nav-agents"' in response.content
    
    def test_agents_link_navigation(self):
        """Clicking Agents navigates to global list."""
        response = self.client.get('/agents/')
        assert response.status_code == 200
        assert b'Agents' in response.content
    
    def test_agents_active_on_list_page(self):
        """Agents link has active class on list page."""
        response = self.client.get('/agents/')
        assert response.status_code == 200
        # Check for active class in navbar
        assert b'nav-link active' in response.content or b'aria-current="page"' in response.content
    
    def test_artifacts_link_enabled(self):
        """Artifacts link is enabled and clickable."""
        response = self.client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert b'href="/artifacts/"' in response.content
        assert b'data-testid="nav-artifacts"' in response.content
    
    def test_artifacts_link_navigation(self):
        """Clicking Artifacts navigates to global list."""
        response = self.client.get('/artifacts/')
        assert response.status_code == 200
        assert b'Artifacts' in response.content
    
    def test_artifacts_active_on_list_page(self):
        """Artifacts link has active class on list page."""
        response = self.client.get('/artifacts/')
        assert response.status_code == 200
        assert b'nav-link active' in response.content or b'aria-current="page"' in response.content

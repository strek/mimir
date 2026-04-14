"""
Integration tests for Phase views.

Tests the complete phase CRUD workflow via Django test client.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from methodology.models import Playbook, Phase, Workflow, Activity

User = get_user_model()


@pytest.mark.django_db
class TestPhaseDetailView:
    """Test phase_detail view."""
    
    def test_phase_detail_renders_correctly(self, client):
        """Phase detail page renders with correct phase data."""
        # Setup
        user = User.objects.create_user(username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        
        playbook = Playbook.objects.create(
            name='Test Playbook',
            description='Test Description',
            category='development',
            author=user,
            status='draft'
        )
        
        phase = Phase.objects.create(
            playbook=playbook,
            name='Inception',
            description='Initial phase',
            order=1
        )
        
        workflow = Workflow.objects.create(
            playbook=playbook,
            name='Test Workflow',
            description='Test workflow',
            order=1
        )
        
        activity = Activity.objects.create(
            workflow=workflow,
            name='Test Activity',
            guidance='Test guidance',
            order=1,
            phase=phase
        )
        
        # Execute
        url = reverse('phase_detail', kwargs={'playbook_pk': playbook.pk, 'phase_pk': phase.pk})
        response = client.get(url)
        
        # Assert
        assert response.status_code == 200
        assert 'phase' in response.context
        assert response.context['phase'].name == 'Inception'
        assert response.context['phase'].description == 'Initial phase'
        assert response.context['phase'].order == 1
        
        # Check activities are in context
        assert 'workflow_activities' in response.context
        assert 'artifacts' in response.context
        
        # Check template content
        content = response.content.decode()
        assert 'Inception' in content
        assert 'Initial phase' in content
        assert 'Test Activity' in content
        assert 'Test Workflow' in content
    
    def test_phase_detail_with_no_activities(self, client):
        """Phase detail page renders correctly when phase has no activities."""
        # Setup
        user = User.objects.create_user(username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        
        playbook = Playbook.objects.create(
            name='Test Playbook',
            description='Test Description',
            category='development',
            author=user,
            status='draft'
        )
        
        phase = Phase.objects.create(
            playbook=playbook,
            name='Empty Phase',
            description='No activities yet',
            order=1
        )
        
        # Execute
        url = reverse('phase_detail', kwargs={'playbook_pk': playbook.pk, 'phase_pk': phase.pk})
        response = client.get(url)
        
        # Assert
        assert response.status_code == 200
        assert response.context['phase'].name == 'Empty Phase'
        content = response.content.decode()
        assert 'No activities assigned to this phase yet' in content
    
    def test_phase_detail_edit_button_visible_for_draft(self, client):
        """Edit button is visible when playbook is draft."""
        # Setup
        user = User.objects.create_user(username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        
        playbook = Playbook.objects.create(
            name='Test Playbook',
            description='Test Description',
            category='development',
            author=user,
            status='draft'
        )
        
        phase = Phase.objects.create(
            playbook=playbook,
            name='Test Phase',
            description='Test',
            order=1
        )
        
        # Execute
        url = reverse('phase_detail', kwargs={'playbook_pk': playbook.pk, 'phase_pk': phase.pk})
        response = client.get(url)
        
        # Assert
        content = response.content.decode()
        assert 'data-testid="edit-button"' in content
        assert 'data-testid="delete-button"' in content
    
    def test_phase_detail_no_edit_button_for_released(self, client):
        """Edit button is NOT visible when playbook is released."""
        # Setup
        user = User.objects.create_user(username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        
        playbook = Playbook.objects.create(
            name='Test Playbook',
            description='Test Description',
            category='development',
            author=user,
            status='released'
        )
        
        phase = Phase.objects.create(
            playbook=playbook,
            name='Test Phase',
            description='Test',
            order=1
        )
        
        # Execute
        url = reverse('phase_detail', kwargs={'playbook_pk': playbook.pk, 'phase_pk': phase.pk})
        response = client.get(url)
        
        # Assert
        content = response.content.decode()
        assert 'data-testid="edit-button"' not in content
        assert 'data-testid="delete-button"' not in content
    
    def test_phase_detail_requires_authentication(self, client):
        """Phase detail redirects to login when not authenticated."""
        # Setup
        user = User.objects.create_user(username='testuser', password='testpass123')
        
        playbook = Playbook.objects.create(
            name='Test Playbook',
            description='Test Description',
            category='development',
            author=user,
            status='draft'
        )
        
        phase = Phase.objects.create(
            playbook=playbook,
            name='Test Phase',
            description='Test',
            order=1
        )
        
        # Execute (not logged in)
        url = reverse('phase_detail', kwargs={'playbook_pk': playbook.pk, 'phase_pk': phase.pk})
        response = client.get(url)
        
        # Assert
        assert response.status_code == 302
        assert '/auth/user/login/' in response.url
    
    def test_phase_detail_permission_denied_for_other_user(self, client):
        """Phase detail returns 404 when user doesn't own the playbook."""
        # Setup
        owner = User.objects.create_user(username='owner', password='testpass123')
        other_user = User.objects.create_user(username='other', password='testpass123')
        
        playbook = Playbook.objects.create(
            name='Test Playbook',
            description='Test Description',
            category='development',
            author=owner,
            status='draft'
        )
        
        phase = Phase.objects.create(
            playbook=playbook,
            name='Test Phase',
            description='Test',
            order=1
        )
        
        # Execute (logged in as other_user)
        client.login(username='other', password='testpass123')
        url = reverse('phase_detail', kwargs={'playbook_pk': playbook.pk, 'phase_pk': phase.pk})
        response = client.get(url)
        
        # Assert
        assert response.status_code == 404


@pytest.mark.django_db
class TestPhaseListView:
    """Test phase_list view (playbook-scoped)."""
    
    def test_phase_list_renders_all_phases(self, client):
        """Phase list shows all phases for a playbook."""
        # Setup
        user = User.objects.create_user(username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        
        playbook = Playbook.objects.create(
            name='Test Playbook',
            description='Test Description',
            category='development',
            author=user,
            status='draft'
        )
        
        phase1 = Phase.objects.create(
            playbook=playbook,
            name='Inception',
            description='Phase 1',
            order=1
        )
        
        phase2 = Phase.objects.create(
            playbook=playbook,
            name='Elaboration',
            description='Phase 2',
            order=2
        )
        
        # Execute
        url = reverse('phase_list', kwargs={'playbook_pk': playbook.pk})
        response = client.get(url)
        
        # Assert
        assert response.status_code == 200
        assert 'phases' in response.context
        phases = list(response.context['phases'])
        assert len(phases) == 2
        assert phases[0].name == 'Inception'
        assert phases[1].name == 'Elaboration'
        
        content = response.content.decode()
        assert 'Inception' in content
        assert 'Elaboration' in content


@pytest.mark.django_db
class TestPhaseGlobalListView:
    """Test phase_list_global view."""
    
    def test_global_list_shows_all_user_phases(self, client):
        """Global phase list shows all phases across all user's playbooks."""
        # Setup
        user = User.objects.create_user(username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        
        playbook1 = Playbook.objects.create(
            name='Playbook 1',
            description='Test',
            category='development',
            author=user,
            status='draft'
        )
        
        playbook2 = Playbook.objects.create(
            name='Playbook 2',
            description='Test',
            category='development',
            author=user,
            status='draft'
        )
        
        Phase.objects.create(playbook=playbook1, name='Phase A', order=1)
        Phase.objects.create(playbook=playbook1, name='Phase B', order=2)
        Phase.objects.create(playbook=playbook2, name='Phase C', order=1)
        
        # Execute
        url = reverse('phase_list_global')
        response = client.get(url)
        
        # Assert
        assert response.status_code == 200
        assert 'phases' in response.context
        phases = list(response.context['phases'])
        assert len(phases) == 3
        
        content = response.content.decode()
        assert 'Phase A' in content
        assert 'Phase B' in content
        assert 'Phase C' in content
    
    def test_global_list_search_filters_by_name(self, client):
        """Global phase list search filters by phase name."""
        # Setup
        user = User.objects.create_user(username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        
        playbook = Playbook.objects.create(
            name='Test Playbook',
            description='Test',
            category='development',
            author=user,
            status='draft'
        )
        
        Phase.objects.create(playbook=playbook, name='Inception', order=1)
        Phase.objects.create(playbook=playbook, name='Elaboration', order=2)
        Phase.objects.create(playbook=playbook, name='Construction', order=3)
        
        # Execute
        url = reverse('phase_list_global') + '?q=Inception'
        response = client.get(url)
        
        # Assert
        assert response.status_code == 200
        phases = list(response.context['phases'])
        assert len(phases) == 1
        assert phases[0].name == 'Inception'

"""
Integration tests for Activity MCP tools.

Tests MCP tool wrappers with real database, real services, NO MOCKING.
"""
import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from methodology.models import Playbook, Workflow, Activity, Phase
from mcp_integration.context import set_current_user
from mcp_integration.tools import update_activity

User = get_user_model()


@pytest.fixture
def maria(db):
    """Create test user maria."""
    return User.objects.create_user(username='maria', email='maria@test.com', password='test123')


@pytest.fixture
def setup_user_context(maria):
    """Set up MCP user context for maria."""
    set_current_user(maria)
    return maria


@pytest.fixture
def draft_playbook(maria):
    """Create draft playbook owned by maria."""
    return Playbook.objects.create(
        name='Test Playbook', description='For testing',
        category='test', status='draft', source='owned', author=maria,
    )


@pytest.fixture
def workflow(draft_playbook):
    """Create workflow in draft playbook."""
    return Workflow.objects.create(
        name='Test Workflow',
        description='For testing',
        playbook=draft_playbook,
        order=1
    )


@pytest.fixture
def activity(workflow):
    """Create activity in workflow."""
    return Activity.objects.create(
        name='Test Activity',
        guidance='Test guidance',
        workflow=workflow,
        order=1
    )


@pytest.fixture
def phase(draft_playbook):
    """Create phase in draft playbook."""
    return Phase.objects.create(
        name='Inception',
        description='Test phase',
        playbook=draft_playbook,
        order=1
    )


@pytest.mark.django_db(transaction=True)
class TestMCPActivityUpdate:
    """Test update_activity MCP tool."""
    
    @pytest.mark.asyncio
    async def test_update_activity_with_phase_id(self, setup_user_context, activity, phase):
        """Update activity with phase_id parameter."""
        result = await update_activity(
            activity_id=activity.id,
            phase_id=phase.id
        )
        
        assert result['id'] == activity.id
        assert result['phase_id'] == phase.id
        
        # Verify in database
        await sync_to_async(activity.refresh_from_db)()
        assert activity.phase_id == phase.id
        
        # Access phase relationship using sync_to_async
        phase_obj = await sync_to_async(lambda: activity.phase)()
        assert phase_obj.name == 'Inception'

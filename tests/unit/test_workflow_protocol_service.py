"""Unit tests for WorkflowProtocolService."""

import pytest
import tempfile
from pathlib import Path
from django.core.exceptions import ValidationError, PermissionDenied
from methodology.models import Workflow, Activity, Playbook
from methodology.services.workflow_protocol_service import WorkflowProtocolService


@pytest.mark.django_db
class TestWorkflowProtocolService:
    """Test WorkflowProtocolService functionality."""
    
    @pytest.fixture
    def playbook_draft(self, django_user_model):
        """Create draft playbook."""
        user = django_user_model.objects.create_user(
            username='maria',
            email='maria@example.com',
            password='testpass123'
        )
        return Playbook.objects.create(
            name='React Frontend Development',
            description='Modern React patterns',
            category='development',
            author=user,
            status='draft',
            version='0.5'
        )
    
    @pytest.fixture
    def playbook_released(self, django_user_model):
        """Create released playbook."""
        user = django_user_model.objects.create_user(
            username='john',
            email='john@example.com',
            password='testpass123'
        )
        return Playbook.objects.create(
            name='Production Playbook',
            description='Released playbook',
            category='production',
            author=user,
            status='released',
            version='1.0'
        )
    
    @pytest.fixture
    def workflow_draft(self, playbook_draft):
        """Create workflow in draft playbook."""
        return Workflow.objects.create(
            name='Frontend Development',
            description='Complete frontend development process',
            playbook=playbook_draft,
            abbreviation='FFE',
            order=1
        )
    
    @pytest.fixture
    def workflow_released(self, playbook_released):
        """Create workflow in released playbook."""
        return Workflow.objects.create(
            name='Production Workflow',
            description='Production workflow',
            playbook=playbook_released,
            abbreviation='PROD',
            order=1
        )
    
    @pytest.fixture
    def protocol_file(self):
        """Create temporary protocol file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
        return temp_file.name
    
    def test_parse_protocol(self, workflow_draft, protocol_file):
        """Test protocol parsing."""
        protocol_content = f"""# Upload Protocol for Frontend Development

**Workflow ID**: {workflow_draft.id}

## Change Summary

- **New Activities**: 2
- **Modified Activities**: 1
- **Deleted Activities**: 0
- **Reordered Activities**: 1
- **Total Changes**: 4
"""
        Path(protocol_file).write_text(protocol_content)
        
        result = WorkflowProtocolService._parse_protocol(protocol_file)
        
        assert result['workflow_id'] == workflow_draft.id
        assert result['changes']['summary']['new'] == 2
        assert result['changes']['summary']['modified'] == 1
        assert result['changes']['summary']['deleted'] == 0
        assert result['changes']['summary']['reordered'] == 1
    
    def test_parse_invalid_protocol(self, protocol_file):
        """Test parsing protocol without workflow ID."""
        protocol_content = """# Upload Protocol

No workflow ID here
"""
        Path(protocol_file).write_text(protocol_content)
        
        with pytest.raises(ValidationError, match="workflow_id not found"):
            WorkflowProtocolService._parse_protocol(protocol_file)
    
    def test_apply_protocol_to_draft_playbook(self, workflow_draft, protocol_file):
        """Test applying protocol to draft playbook."""
        protocol_content = f"""# Upload Protocol for Frontend Development

**Workflow ID**: {workflow_draft.id}

## Change Summary

- **New Activities**: 1
- **Modified Activities**: 0
- **Deleted Activities**: 0
- **Reordered Activities**: 0
- **Total Changes**: 1
"""
        Path(protocol_file).write_text(protocol_content)
        
        result = WorkflowProtocolService.apply_upload_protocol(protocol_file)
        
        assert result['status'] == 'applied'
        assert result['workflow_id'] == workflow_draft.id
        assert result['changes_applied']['total'] == 1
    
    def test_apply_protocol_to_released_playbook_raises_error(self, workflow_released, protocol_file):
        """Test that applying protocol to released playbook raises PermissionDenied."""
        protocol_content = f"""# Upload Protocol

**Workflow ID**: {workflow_released.id}

## Change Summary

- **New Activities**: 1
- **Modified Activities**: 0
- **Deleted Activities**: 0
- **Reordered Activities**: 0
- **Total Changes**: 1
"""
        Path(protocol_file).write_text(protocol_content)
        
        with pytest.raises(PermissionDenied, match="Cannot apply protocol to released playbook"):
            WorkflowProtocolService.apply_upload_protocol(protocol_file)
    
    def test_apply_protocol_nonexistent_file(self):
        """Test applying protocol with nonexistent file."""
        with pytest.raises(ValidationError, match="Protocol file does not exist"):
            WorkflowProtocolService.apply_upload_protocol('/nonexistent/protocol.md')
    
    def test_create_pip_from_protocol(self, workflow_released, protocol_file):
        """Test creating PIP from protocol."""
        protocol_content = f"""# Upload Protocol

**Workflow ID**: {workflow_released.id}

## Change Summary

- **New Activities**: 2
- **Modified Activities**: 1
- **Deleted Activities**: 0
- **Reordered Activities**: 1
- **Total Changes**: 4
"""
        Path(protocol_file).write_text(protocol_content)
        
        result = WorkflowProtocolService.create_pip_from_protocol(
            protocol_file,
            pip_title='Improve workflow structure'
        )
        
        assert result['status'] == 'pending_review'
        assert result['title'] == 'Improve workflow structure'
        assert result['workflow_id'] == workflow_released.id
        assert 'pip_id' in result
    
    def test_create_pip_nonexistent_file(self):
        """Test creating PIP with nonexistent file."""
        with pytest.raises(ValidationError, match="Protocol file does not exist"):
            WorkflowProtocolService.create_pip_from_protocol(
                '/nonexistent/protocol.md',
                pip_title='Test PIP'
            )
    
    def test_apply_changes_counts(self, workflow_draft):
        """Test _apply_changes returns correct counts."""
        changes = {
            'summary': {
                'new': 2,
                'modified': 1,
                'deleted': 1,
                'reordered': 1
            }
        }
        
        result = WorkflowProtocolService._apply_changes(workflow_draft, changes)
        
        assert result['new'] == 2
        assert result['modified'] == 1
        assert result['deleted'] == 1
        assert result['reordered'] == 1
        assert result['total'] == 5

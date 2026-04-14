"""Unit tests for WorkflowImportService."""

import pytest
import tempfile
import shutil
from pathlib import Path
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from methodology.models import Workflow, Activity, Playbook
from methodology.services.workflow_import_service import WorkflowImportService


@pytest.mark.django_db
class TestWorkflowImportService:
    """Test WorkflowImportService functionality."""
    
    @pytest.fixture
    def playbook(self, django_user_model):
        """Create test playbook."""
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
    def workflow(self, playbook):
        """Create test workflow."""
        return Workflow.objects.create(
            name='Frontend Development',
            description='Complete frontend development process',
            playbook=playbook,
            abbreviation='FFE',
            order=1
        )
    
    @pytest.fixture
    def activities(self, workflow, create_test_phases):
        """Create test activities."""
        # Create test phases
        phases = create_test_phases(workflow.playbook)
        
        activities = []
        for i in range(1, 4):
            activity = Activity.objects.create(
                workflow=workflow,
                name=f'Activity {i}',
                guidance=f'Guidance for activity {i}',
                order=i,
                phase=phases['Foundation']
            )
            activities.append(activity)
        return activities
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_parse_activity_md(self, temp_dir):
        """Test parsing activity markdown file."""
        activity_file = Path(temp_dir) / 'FFE-01-Test.md'
        content = """# Activity: Test Activity

**Activity ID**: 123
**Order**: 1
**Phase**: Foundation
**Dependencies**: None

## Description

Test activity description

## Guidance

Step 1: Do this
Step 2: Do that

## Artifacts Produced

None
"""
        activity_file.write_text(content)
        
        result = WorkflowImportService._parse_activity_md(activity_file)
        
        assert result['name'] == 'Test Activity'
        assert result['activity_id'] == 123
        assert result['order'] == 1
        assert result['phase'] == 'Foundation'
        assert 'Step 1: Do this' in result['guidance']
    
    def test_detect_new_activities(self, workflow, activities):
        """Test detection of new activities."""
        imported = [
            {'activity_id': activities[0].id, 'name': 'Activity 1', 'order': 1, 'phase': 'Foundation', 'guidance': 'Guidance for activity 1'},
            {'activity_id': activities[1].id, 'name': 'Activity 2', 'order': 2, 'phase': 'Foundation', 'guidance': 'Guidance for activity 2'},
            {'activity_id': None, 'name': 'New Activity', 'order': 3, 'phase': 'Implementation', 'guidance': 'New guidance'}
        ]
        
        changes = WorkflowImportService._detect_changes(activities[:2], imported)
        
        assert changes['summary']['new'] == 1
        assert changes['summary']['total'] == 1
        assert changes['new'][0]['name'] == 'New Activity'
    
    def test_detect_modified_activities(self, workflow, activities):
        """Test detection of modified activities."""
        imported = [
            {'activity_id': activities[0].id, 'name': 'Modified Activity 1', 'order': 1, 'phase': 'Foundation', 'guidance': 'New guidance'},
            {'activity_id': activities[1].id, 'name': 'Activity 2', 'order': 2, 'phase': 'Foundation', 'guidance': 'Guidance for activity 2'}
        ]
        
        changes = WorkflowImportService._detect_changes(activities[:2], imported)
        
        assert changes['summary']['modified'] == 1
        assert changes['modified'][0]['activity_id'] == activities[0].id
    
    def test_detect_deleted_activities(self, workflow, activities):
        """Test detection of deleted activities."""
        imported = [
            {'activity_id': activities[0].id, 'name': 'Activity 1', 'order': 1, 'phase': 'Foundation', 'guidance': 'Guidance for activity 1'}
        ]
        
        changes = WorkflowImportService._detect_changes(activities[:2], imported)
        
        assert changes['summary']['deleted'] == 1
        assert changes['deleted'][0]['activity_id'] == activities[1].id
    
    def test_detect_reordered_activities(self, workflow, activities):
        """Test detection of reordered activities."""
        imported = [
            {'activity_id': activities[0].id, 'name': 'Activity 1', 'order': 2, 'phase': 'Foundation', 'guidance': 'Guidance for activity 1'},
            {'activity_id': activities[1].id, 'name': 'Activity 2', 'order': 1, 'phase': 'Foundation', 'guidance': 'Guidance for activity 2'}
        ]
        
        changes = WorkflowImportService._detect_changes(activities[:2], imported)
        
        assert changes['summary']['reordered'] == 2
        assert changes['reordered'][0]['old_order'] == 1
        assert changes['reordered'][0]['new_order'] == 2
    
    def test_generate_upload_protocol(self, workflow, activities):
        """Test upload protocol generation."""
        changes = {
            'new': [{'name': 'New Activity', 'order': 4, 'phase': 'Testing'}],
            'modified': [{'activity_id': activities[0].id, 'name': 'Activity 1', 'changes': []}],
            'deleted': [],
            'reordered': [{'activity_id': activities[1].id, 'name': 'Activity 2', 'old_order': 2, 'new_order': 3}],
            'summary': {'new': 1, 'modified': 1, 'deleted': 0, 'reordered': 1, 'total': 3}
        }
        
        protocol = WorkflowImportService._generate_upload_protocol(changes, workflow, workflow.playbook)
        
        assert '# Upload Protocol for Frontend Development' in protocol
        assert '**New Activities**: 1' in protocol
        assert '**Modified Activities**: 1' in protocol
        assert '**Reordered Activities**: 1' in protocol
        assert 'New Activity' in protocol
        assert '[AI to fill' in protocol
    
    def test_import_nonexistent_workflow(self, temp_dir):
        """Test import with invalid workflow ID."""
        with pytest.raises(ObjectDoesNotExist):
            WorkflowImportService.import_workflow_from_markdown(
                workflow_id=99999,
                source_directory=temp_dir
            )
    
    def test_import_nonexistent_directory(self, workflow):
        """Test import with invalid directory."""
        with pytest.raises(ValidationError):
            WorkflowImportService.import_workflow_from_markdown(
                workflow_id=workflow.id,
                source_directory='/nonexistent/path'
            )
    
    def test_import_creates_protocol_file(self, workflow, activities, temp_dir):
        """Test that import creates _Upload_Protocol.md."""
        # Create activity files
        for i, activity in enumerate(activities, 1):
            activity_file = Path(temp_dir) / f'FFE-{i:02d}-Activity_{i}.md'
            content = f"""# Activity: Activity {i}

**Activity ID**: {activity.id}
**Order**: {i}
**Phase**: Foundation
**Dependencies**: None

## Guidance

Guidance for activity {i}
"""
            activity_file.write_text(content)
        
        result = WorkflowImportService.import_workflow_from_markdown(
            workflow_id=workflow.id,
            source_directory=temp_dir
        )
        
        assert result['status'] == 'changes_detected'
        assert Path(temp_dir, '_Upload_Protocol.md').exists()
    
    def test_parse_activity_without_id(self, temp_dir):
        """Test parsing new activity without ID."""
        activity_file = Path(temp_dir) / 'FFE-04-New.md'
        content = """# Activity: New Activity

**Activity ID**: 
**Order**: 4
**Phase**: Testing
**Dependencies**: None

## Guidance

New activity guidance
"""
        activity_file.write_text(content)
        
        result = WorkflowImportService._parse_activity_md(activity_file)
        
        assert result['name'] == 'New Activity'
        assert result['activity_id'] is None
        assert result['order'] == 4

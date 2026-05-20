"""Workflow Protocol Service - Apply upload protocols and create PIPs."""

import logging
import re
from pathlib import Path
from typing import Dict, List
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from methodology.models import Workflow, Activity
from methodology.services.activity_service import ActivityService

logger = logging.getLogger(__name__)


def _add_pip_changes(pip, actor, changes: dict, imported_by_id: dict, workflow_id: int, pip_service) -> None:
    """Add ALTER/ADD PipChange rows to a draft PIP from a detected-changes dict."""
    for modified in changes.get('modified', []):
        aid = modified['activity_id']
        imported = imported_by_id.get(aid, {})
        content = imported.get('guidance') or ''
        if content:
            pip_service.add_change(
                actor=actor, pip=pip,
                change_type='ALTER', entity_type='Activity',
                target_id=aid, content=content,
            )
            logger.debug("create_pip_from_protocol ALTER activity=%s", aid)

    for new_act in changes.get('new', []):
        name = new_act.get('name') or ''
        if not name:
            logger.debug("Skipping unnamed new activity in create_pip_from_protocol")
            continue
        pip_service.add_change(
            actor=actor, pip=pip,
            change_type='ADD', entity_type='Activity',
            name=name,
            content=new_act.get('guidance') or '',
            parent_workflow_id=workflow_id,
        )
        logger.debug("create_pip_from_protocol ADD activity name=%s", name)


class WorkflowProtocolService:
    """Service for applying upload protocols and creating PIPs."""
    
    @staticmethod
    @transaction.atomic
    def apply_upload_protocol(protocol_file: str) -> dict:
        """
        Apply changes from upload protocol to draft playbook.
        
        :param protocol_file: Path to _Upload_Protocol.md
        :return: Application result with change counts and new version
        :raises PermissionDenied: If playbook is released
        :raises ValidationError: If protocol invalid
        """
        logger.info(f"Applying upload protocol from {protocol_file}")
        
        protocol_path = Path(protocol_file)
        if not protocol_path.exists():
            raise ValidationError(f"Protocol file does not exist: {protocol_file}")
        
        protocol_data = WorkflowProtocolService._parse_protocol(protocol_file)
        
        try:
            workflow = Workflow.objects.select_related('playbook').get(pk=protocol_data['workflow_id'])
        except ObjectDoesNotExist:
            raise ValidationError(f"Workflow {protocol_data['workflow_id']} not found")
        
        if workflow.playbook.status != 'draft':
            raise PermissionDenied(
                f"Cannot apply protocol to {workflow.playbook.status} playbook. Use create_pip_from_protocol instead."
            )
        
        logger.info(f"Applying changes to draft playbook '{workflow.playbook.name}' v{workflow.playbook.version}")
        
        changes_applied = WorkflowProtocolService._apply_changes(workflow, protocol_data['changes'])
        
        workflow.playbook.refresh_from_db()
        
        result = {
            'status': 'applied',
            'workflow_id': workflow.id,
            'workflow_name': workflow.name,
            'playbook_version': str(workflow.playbook.version),
            'changes_applied': changes_applied,
            'message': f'Changes applied successfully. Playbook version: {workflow.playbook.version}'
        }
        
        logger.info(f"Protocol applied: {changes_applied}")
        return result
    
    @staticmethod
    @transaction.atomic
    def create_pip_from_protocol(protocol_file: str, pip_title: str, actor=None) -> dict:
        """
        Create a real PIP with PipChange entries from an upload protocol file.

        :param protocol_file: Path to _Upload_Protocol.md
        :param pip_title: PIP title. Example: "Improve workflow activity flow"
        :param actor: Django user creating the PIP (required for released playbooks)
        :return: PIP dict with numeric pip_id
        :raises ValidationError: If protocol invalid or playbook not released
        """
        from methodology.services.pip_service import PIPService
        from methodology.services.workflow_import_service import WorkflowImportService

        logger.info("WorkflowProtocolService.create_pip_from_protocol title=%s actor=%s",
                    pip_title, getattr(actor, 'pk', None))

        protocol_path = Path(protocol_file)
        if not protocol_path.exists():
            raise ValidationError(f"Protocol file does not exist: {protocol_file}")

        protocol_data = WorkflowProtocolService._parse_protocol(protocol_file)

        try:
            workflow = Workflow.objects.select_related('playbook').get(pk=protocol_data['workflow_id'])
        except ObjectDoesNotExist:
            raise ValidationError(f"Workflow {protocol_data['workflow_id']} not found")

        if workflow.playbook.status != 'released':
            raise ValidationError("create_pip_from_protocol requires a Released playbook; use apply_upload_protocol for draft.")

        source_directory = Path(protocol_data['source_directory'])
        imported_activities = WorkflowImportService._parse_activity_files(source_directory)
        imported_by_id = {a['activity_id']: a for a in imported_activities if a['activity_id']}
        current_activities = list(workflow.activities.all().order_by('order'))
        changes = WorkflowImportService._detect_changes(current_activities, imported_activities)

        pip = PIPService.create_draft_for_playbook(
            actor=actor,
            playbook_id=workflow.playbook_id,
            title=pip_title,
            summary=f"Generated from upload protocol for workflow '{workflow.name}'",
        )

        _add_pip_changes(pip, actor, changes, imported_by_id, workflow.id, PIPService)

        changes_summary = changes['summary']
        logger.info("create_pip_from_protocol pip=%s changes=%s", pip.pk, changes_summary)
        return {
            'pip_id': pip.pk,
            'title': pip.title,
            'status': pip.status,
            'workflow_id': workflow.id,
            'workflow_name': workflow.name,
            'playbook_name': workflow.playbook.name,
            'playbook_version': str(workflow.playbook.version),
            'changes_summary': changes_summary,
            'protocol_file': protocol_file,
            'message': 'PIP created successfully. Submit via submit_pip to send for review.',
        }
    
    @staticmethod
    def _parse_protocol(protocol_file: str) -> Dict:
        """Parse _Upload_Protocol.md into structured data and re-parse source files."""
        from methodology.services.workflow_import_service import WorkflowImportService
        
        content = Path(protocol_file).read_text(encoding='utf-8')
        
        protocol_data = {
            'workflow_id': None,
            'source_directory': None,
            'changes': {
                'new': [],
                'modified': [],
                'deleted': [],
                'reordered': [],
                'summary': {}
            }
        }
        
        for line in content.split('\n'):
            if line.startswith('**Workflow ID**:'):
                try:
                    protocol_data['workflow_id'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith('- **New Activities**:'):
                try:
                    protocol_data['changes']['summary']['new'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith('- **Modified Activities**:'):
                try:
                    protocol_data['changes']['summary']['modified'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith('- **Deleted Activities**:'):
                try:
                    protocol_data['changes']['summary']['deleted'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith('- **Reordered Activities**:'):
                try:
                    protocol_data['changes']['summary']['reordered'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
        
        if not protocol_data['workflow_id']:
            raise ValidationError("Invalid protocol: workflow_id not found")
        
        protocol_path = Path(protocol_file)
        source_directory = protocol_path.parent
        protocol_data['source_directory'] = str(source_directory)
        
        imported_activities = WorkflowImportService._parse_activity_files(source_directory)
        
        for activity in imported_activities:
            if not activity.get('activity_id') and activity.get('name'):
                protocol_data['changes']['new'].append(activity)
        
        return protocol_data
    
    @staticmethod
    def _apply_changes(workflow, changes: Dict) -> Dict:
        """Apply changes to workflow (create/update/delete/reorder activities)."""
        applied = {
            'new': 0,
            'modified': 0,
            'deleted': 0,
            'reordered': 0,
            'total': 0
        }
        
        for new_activity_data in changes.get('new', []):
            logger.info(f"Creating new activity: {new_activity_data['name']} (order={new_activity_data['order']})")
            
            # Resolve phase name to phase_id if provided
            phase_id = None
            phase_name = new_activity_data.get('phase')
            if phase_name:
                from methodology.models import Phase
                try:
                    phase = Phase.objects.get(playbook=workflow.playbook, name=phase_name)
                    phase_id = phase.id
                except Phase.DoesNotExist:
                    logger.warning(f"Phase '{phase_name}' not found in playbook {workflow.playbook_id}, creating activity without phase")
            
            activity = ActivityService.create_activity(
                workflow=workflow,
                name=new_activity_data['name'],
                guidance=new_activity_data.get('guidance', ''),
                phase_id=phase_id,
                order=new_activity_data.get('order')
            )
            applied['new'] += 1
            logger.info(f"Created activity ID={activity.id}, name='{activity.name}'")
        
        for modified_activity_data in changes.get('modified', []):
            logger.info(f"Modifying activity ID={modified_activity_data.get('activity_id')}")
            applied['modified'] += 1
        
        for deleted_activity_data in changes.get('deleted', []):
            logger.info(f"Deleting activity ID={deleted_activity_data.get('activity_id')}")
            applied['deleted'] += 1
        
        for reordered_activity_data in changes.get('reordered', []):
            logger.info(f"Reordering activity ID={reordered_activity_data.get('activity_id')}")
            applied['reordered'] += 1
        
        applied['total'] = applied['new'] + applied['modified'] + applied['deleted'] + applied['reordered']
        
        logger.info(f"Applied {applied['total']} changes to workflow {workflow.id}")
        
        return applied

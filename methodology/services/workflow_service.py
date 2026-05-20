"""Workflow Service - Business logic for workflow operations."""

import logging
from typing import Optional, List
from django.db import transaction, models
from django.core.exceptions import ValidationError
from methodology.models import Workflow
from methodology.services.playbook_service import PlaybookService

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service class for workflow operations."""
    
    @staticmethod
    def create_workflow(playbook, name, description='', order=None):
        """Create workflow with validation and auto-order."""
        logger.info(f"Creating workflow '{name}' in playbook {playbook.pk}")
        
        # Check for duplicate name
        if Workflow.objects.filter(playbook=playbook, name=name).exists():
            raise ValidationError(f"Workflow '{name}' already exists in this playbook")
        
        # Auto-assign order if not provided
        if order is None:
            max_order = Workflow.objects.filter(playbook=playbook).aggregate(
                max_order=models.Max('order')
            )['max_order']
            order = (max_order or 0) + 1
        
        workflow = Workflow.objects.create(
            name=name,
            description=description,
            playbook=playbook,
            order=order
        )
        
        logger.info(f"Workflow '{name}' created with ID {workflow.pk}, order {workflow.order}")
        return workflow
    
    @staticmethod
    def get_workflow(workflow_id):
        """Get workflow by ID."""
        logger.info(f"Retrieving workflow {workflow_id}")
        return Workflow.objects.get(pk=workflow_id)
    
    @staticmethod
    def get_workflows_for_playbook(playbook_id):
        """Get all workflows for playbook, ordered."""
        logger.info(f"Retrieving workflows for playbook {playbook_id}")
        return list(Workflow.objects.filter(playbook_id=playbook_id).order_by('order', 'created_at'))
    
    @staticmethod
    @transaction.atomic
    def update_workflow(workflow_id, **data):
        """Update workflow with validation."""
        logger.info(f"Updating workflow {workflow_id}")
        
        workflow = Workflow.objects.get(pk=workflow_id)
        
        # Check for duplicate name if changing name
        if 'name' in data and data['name'] != workflow.name:
            if Workflow.objects.filter(playbook=workflow.playbook, name=data['name']).exists():
                raise ValidationError(f"Workflow '{data['name']}' already exists in this playbook")
        
        # Update fields
        for field, value in data.items():
            setattr(workflow, field, value)
        
        workflow.save()
        logger.info(f"Workflow {workflow_id} updated")
        return workflow
    
    @staticmethod
    @transaction.atomic
    def delete_workflow(workflow_id):
        """Delete workflow."""
        logger.info(f"Deleting workflow {workflow_id}")
        workflow = Workflow.objects.get(pk=workflow_id)
        workflow.delete()
        logger.info(f"Workflow {workflow_id} deleted")
    
    @staticmethod
    @transaction.atomic
    def duplicate_workflow(workflow_id, new_name):
        """Duplicate workflow (shallow copy)."""
        logger.info(f"Duplicating workflow {workflow_id} as '{new_name}'")
        
        original = Workflow.objects.get(pk=workflow_id)
        
        # Check for duplicate name
        if Workflow.objects.filter(playbook=original.playbook, name=new_name).exists():
            raise ValidationError(f"Workflow '{new_name}' already exists in this playbook")
        
        # Get next order
        max_order = Workflow.objects.filter(playbook=original.playbook).aggregate(
            max_order=models.Max('order')
        )['max_order']
        next_order = (max_order or 0) + 1
        
        # Create duplicate
        duplicate = Workflow.objects.create(
            name=new_name,
            description=original.description,
            playbook=original.playbook,
            order=next_order
        )
        
        logger.info(f"Workflow duplicated as {duplicate.pk}")
        return duplicate

    @staticmethod
    def get_workflow_for_user(workflow_id, user, *, write: bool = False, prefetch_activities: bool = False):
        """
        Load workflow and enforce playbook access: ``can_view`` for reads, owner for writes.

        :param workflow_id: Workflow primary key
        :param user: Django user
        :param write: When True, require playbook author == user
        :param prefetch_activities: When True, prefetch ``activities`` for read tooling
        :returns: Workflow instance
        :raises Workflow.DoesNotExist: If workflow row is missing
        :raises PermissionError: If read access denied
        :raises Playbook.DoesNotExist: If write path and playbook not owned
        """
        qs = Workflow.objects.select_related("playbook")
        if prefetch_activities:
            qs = qs.prefetch_related("activities")
        workflow = qs.get(pk=workflow_id)
        if write:
            PlaybookService.get_owned_playbook(workflow.playbook_id, user)
        else:
            PlaybookService.get_playbook(workflow.playbook_id, user)
        return workflow

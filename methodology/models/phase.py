"""
Phase model for lifecycle stages within playbooks.

Phases represent playbook-wide lifecycle stages (e.g., Inception, Elaboration, Construction).
Each phase belongs to a playbook and activities are assigned to phases.
"""

from django.db import models


class Phase(models.Model):
    """
    Phase represents a lifecycle stage within a playbook.
    
    Phases are playbook-scoped entities that organize activities into
    lifecycle stages. Activities across all workflows can be assigned
    to phases for cross-workflow aggregation and visualization.
    """
    
    # Relationships
    playbook = models.ForeignKey(
        'Playbook',
        on_delete=models.CASCADE,
        related_name='phases',
        help_text="Parent playbook containing this phase"
    )
    
    # Core fields
    name = models.CharField(
        max_length=100,
        help_text="Phase name (e.g., 'Inception', 'Elaboration', 'Construction')"
    )
    description = models.TextField(
        blank=True,
        help_text="Phase description and purpose"
    )
    
    # Organization
    order = models.IntegerField(
        default=1,
        help_text="Display order within playbook"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['playbook', 'order', 'name']
        verbose_name = 'Phase'
        verbose_name_plural = 'Phases'
        constraints = [
            models.UniqueConstraint(
                fields=['playbook', 'name'],
                name='unique_phase_name_per_playbook'
            ),
            models.UniqueConstraint(
                fields=['playbook', 'order'],
                name='unique_phase_order_per_playbook'
            )
        ]
    
    def __str__(self):
        """String representation showing name and order."""
        return f"{self.name} (#{self.order})"
    
    def is_owned_by(self, user):
        """
        Check if user owns the parent playbook.
        
        :param user: User to check ownership for
        :returns: True if user owns parent playbook
        :rtype: bool
        
        Example:
            >>> phase.is_owned_by(maria)
            True  # If maria owns the playbook
        """
        return self.playbook.is_owned_by(user)
    
    def can_edit(self, user):
        """
        Check if user can edit this phase.
        
        User can edit if they own the parent playbook and it's editable.
        
        :param user: User to check edit permission for
        :returns: True if user can edit
        :rtype: bool
        
        Example:
            >>> phase.can_edit(maria)
            True  # If maria owns the playbook and it's draft
        """
        return self.playbook.can_edit(user)
    
    def get_activity_count(self):
        """
        Get number of activities assigned to this phase.
        
        :returns: Activity count across all workflows
        :rtype: int
        
        Example:
            >>> phase.get_activity_count()
            12  # 12 activities assigned to this phase
        """
        return self.activities.count()
    
    def get_artifacts(self):
        """
        Get all artifacts produced by activities in this phase.
        
        :returns: QuerySet of Artifact objects
        :rtype: QuerySet
        
        Example:
            >>> phase.get_artifacts()
            <QuerySet [<Artifact: API Spec>, <Artifact: Design Doc>]>
        """
        from .artifact import Artifact
        # Get all activities in this phase
        activity_ids = self.activities.values_list('id', flat=True)
        # Get artifacts produced by those activities
        return Artifact.objects.filter(produced_by_id__in=activity_ids)
    
    def get_workflows_with_activities(self):
        """
        Get workflows that have activities in this phase, grouped.
        
        :returns: Dict mapping workflow to list of activities
        :rtype: dict
        
        Example:
            >>> phase.get_workflows_with_activities()
            {
                <Workflow: Component Development>: [<Activity: Setup>, <Activity: Design>],
                <Workflow: State Management>: [<Activity: Configure Redux>]
            }
        """
        from collections import defaultdict
        
        workflow_activities = defaultdict(list)
        for activity in self.activities.select_related('workflow').order_by('workflow__order', 'order'):
            workflow_activities[activity.workflow].append(activity)
        
        return dict(workflow_activities)

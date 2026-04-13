"""
Phase views — list, create, detail, edit, delete.

All views are scoped to a workflow via URL parameters:
  playbook_pk → workflow_pk → phase operations

URL pattern assumed:
  /playbooks/<playbook_pk>/workflows/<workflow_pk>/phases/
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from methodology.models import Playbook, Workflow, Phase
from methodology.services.phase_service import PhaseService

logger = logging.getLogger(__name__)


@login_required
def phase_list(request, playbook_pk: int, workflow_pk: int):
    """
    List all phases for a workflow, ordered by phase.order.

    Scoped to playbooks owned by request.user.

    Template: phases/list.html
    Context:
        - playbook: Playbook instance
        - workflow: Workflow instance
        - phases: QuerySet[Phase] ordered by order
        - can_edit: bool

    :param request: Django request.
    :param playbook_pk: PK of parent playbook.
        Example: 5
    :param workflow_pk: PK of parent workflow.
        Example: 12
    :returns: Rendered list template.
    """
    raise NotImplementedError()


@login_required
def phase_create(request, playbook_pk: int, workflow_pk: int):
    """
    GET: Render empty create-phase form.
    POST: Validate and create phase; redirect to phase_list on success.

    Template: phases/create.html
    Context:
        - playbook: Playbook instance
        - workflow: Workflow instance
        - form_errors: dict of field → error message (on POST failure)

    :param request: Django request.
    :param playbook_pk: PK of parent playbook.
        Example: 5
    :param workflow_pk: PK of parent workflow.
        Example: 12
    :returns: Rendered create form or redirect to phase_list.
    :raises ValidationError: Handled — re-renders form with errors.
    """
    raise NotImplementedError()


@login_required
def phase_detail(request, playbook_pk: int, workflow_pk: int, pk: int):
    """
    Display phase details: name, description, order, and assigned activities.

    Template: phases/detail.html
    Context:
        - playbook: Playbook instance
        - workflow: Workflow instance
        - phase: Phase instance
        - activities: QuerySet[Activity] assigned to this phase
        - can_edit: bool

    :param request: Django request.
    :param playbook_pk: PK of parent playbook.
    :param workflow_pk: PK of parent workflow.
    :param pk: PK of the Phase.
        Example: 7
    :returns: Rendered detail template.
    """
    raise NotImplementedError()


@login_required
def phase_edit(request, playbook_pk: int, workflow_pk: int, pk: int):
    """
    GET: Render pre-populated edit form.
    POST: Validate and save changes; redirect to phase_detail on success.

    Template: phases/edit.html
    Context:
        - playbook: Playbook instance
        - workflow: Workflow instance
        - phase: Phase instance (pre-populated values)
        - form_errors: dict on POST failure

    :param request: Django request.
    :param playbook_pk: PK of parent playbook.
    :param workflow_pk: PK of parent workflow.
    :param pk: PK of the Phase to edit.
    :returns: Rendered edit form or redirect to phase_detail.
    :raises ValidationError: Handled — re-renders form with errors.
    """
    raise NotImplementedError()


@login_required
def phase_delete(request, playbook_pk: int, workflow_pk: int, pk: int):
    """
    GET: Render delete confirmation modal page.
    POST: Delete phase (activities unassigned); redirect to phase_list.

    Template: phases/detail.html with delete modal rendered (GET), or
              redirect to phase_list (POST).
    Context (GET):
        - playbook, workflow, phase, activity_count, can_edit

    :param request: Django request.
    :param playbook_pk: PK of parent playbook.
    :param workflow_pk: PK of parent workflow.
    :param pk: PK of the Phase to delete.
    :returns: Redirect to phase_list after successful deletion.
    """
    raise NotImplementedError()

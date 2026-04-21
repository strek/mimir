"""
Integration tests for Agents global list view (/agents/).

Covers UI rendering consistency: agent descriptions authored in Markdown
must be rendered as plain prose in the list preview (no raw `##`, `**`,
or similar markup leaking through).
"""

import re

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from methodology.models import Agent, Playbook

User = get_user_model()


@pytest.fixture
def agent_with_markdown_description(db):
    """Create an agent whose description is authored in Markdown."""
    user = User.objects.create_user(username='alice', password='test123')
    playbook = Playbook.objects.create(
        name='FeatureFactory',
        description='Agents fixture playbook',
        category='development',
        status='active',
        source='owned',
        author=user,
    )
    agent = Agent.objects.create(
        playbook=playbook,
        name='Dr. Dobbs v2',
        description=(
            "# Cautious Developer Agent Guide\n\n"
            "**Motto**: \"Code that's easy to prove correct is code that works\"\n\n"
            "## Core Principles\n\n"
            "- Prefer small increments\n"
            "- Verify every step\n"
        ),
    )
    return {'user': user, 'playbook': playbook, 'agent': agent}


@pytest.mark.django_db
class TestAgentsListMarkdownRendering:
    """Agent descriptions should render as plain text, not raw Markdown."""

    def test_description_cell_has_no_raw_markdown_syntax(
        self, agent_with_markdown_description,
    ):
        """Raw Markdown markers must not appear in the description cell."""
        client = Client()
        client.force_login(agent_with_markdown_description['user'])

        response = client.get(reverse('agent_list'))

        assert response.status_code == 200
        content = response.content.decode('utf-8')

        agent_id = agent_with_markdown_description['agent'].id
        row_match = re.search(
            rf'<tr[^>]*data-testid="agent-row-{agent_id}"[^>]*>.*?</tr>',
            content, re.DOTALL,
        )
        assert row_match is not None, "Agent row not found"

        description_cell = re.search(
            r'<td class="text-muted small">(.*?)</td>',
            row_match.group(0), re.DOTALL,
        )
        assert description_cell is not None, "Description cell not found"
        cell_text = description_cell.group(1)

        assert '##' not in cell_text, (
            f"Raw heading syntax '##' leaked into description: {cell_text!r}"
        )
        assert '**' not in cell_text, (
            f"Raw bold syntax '**' leaked into description: {cell_text!r}"
        )

    def test_description_cell_contains_plain_text_content(
        self, agent_with_markdown_description,
    ):
        """Plain-text content from the description should still be visible."""
        client = Client()
        client.force_login(agent_with_markdown_description['user'])

        response = client.get(reverse('agent_list'))

        content = response.content.decode('utf-8')
        agent_id = agent_with_markdown_description['agent'].id
        row_match = re.search(
            rf'<tr[^>]*data-testid="agent-row-{agent_id}"[^>]*>.*?</tr>',
            content, re.DOTALL,
        )
        assert row_match is not None
        assert 'Cautious Developer Agent Guide' in row_match.group(0)
        assert 'Motto' in row_match.group(0)

"""
Integration tests for Rules list views (global and playbook-scoped).

Covers UI consistency: rule rows must show the rules icon
(fa-scale-balanced) next to the title, matching the pattern used by
other entity list pages (workflows, activities, phases, artifacts).
"""

import re

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from methodology.models import Playbook, Rule

User = get_user_model()


@pytest.fixture
def playbook_with_rules(db):
    """Create a playbook with two rules owned by a user."""
    user = User.objects.create_user(username='alice', password='test123')
    playbook = Playbook.objects.create(
        name='React Development',
        description='Rules fixture playbook',
        category='development',
        status='active',
        source='owned',
        author=user,
    )
    Rule.objects.create(
        playbook=playbook,
        title='Use Functional Components',
        slug='use-functional-components',
        content='Prefer functional components over class components.',
    )
    Rule.objects.create(
        playbook=playbook,
        title='Avoid Inline Styles',
        slug='avoid-inline-styles',
        content='Use CSS modules or styled-components.',
    )
    return {'user': user, 'playbook': playbook}


@pytest.mark.django_db
class TestRulesListGlobal:
    """Global rules list page."""

    def test_global_rule_row_shows_rule_icon(self, playbook_with_rules):
        """Each rule row on the global list renders the rules icon."""
        client = Client()
        client.force_login(playbook_with_rules['user'])

        response = client.get(reverse('rule_list'))

        assert response.status_code == 200
        content = response.content.decode('utf-8')

        rows = re.findall(
            r'<tr[^>]*data-testid="rule-row-\d+"[^>]*>.*?</tr>',
            content, re.DOTALL,
        )
        assert len(rows) == 2, f"Expected 2 rule rows, got {len(rows)}"
        for row in rows:
            assert 'fa-scale-balanced' in row, (
                f"Rule row missing fa-scale-balanced icon: {row}"
            )


@pytest.mark.django_db
class TestRulesListPlaybook:
    """Playbook-scoped rules list page."""

    def test_playbook_rule_row_shows_rule_icon(self, playbook_with_rules):
        """Each rule row on the playbook rules list renders the rules icon."""
        playbook = playbook_with_rules['playbook']
        client = Client()
        client.force_login(playbook_with_rules['user'])

        response = client.get(
            reverse('rule_list_playbook', kwargs={'playbook_pk': playbook.pk})
        )

        assert response.status_code == 200
        content = response.content.decode('utf-8')

        tbody_match = re.search(
            r'<tbody>(.*?)</tbody>', content, re.DOTALL,
        )
        assert tbody_match is not None, "Rules table tbody not found"
        rows = re.findall(r'<tr[^>]*>.*?</tr>', tbody_match.group(1), re.DOTALL)
        assert len(rows) == 2, f"Expected 2 rule rows, got {len(rows)}"
        for row in rows:
            assert 'fa-scale-balanced' in row, (
                f"Rule row missing fa-scale-balanced icon: {row}"
            )

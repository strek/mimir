"""Integration tests for PIP list placeholder route."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_pip_list_returns_under_construction_page(client):
    """GET /pip/list/ renders placeholder with expected copy."""
    url = reverse("pip_list")
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Under construction" in content
    assert "The droids you are looking for were not built yet." in content
    assert 'data-testid="pip-under-construction"' in content

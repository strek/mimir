"""
Integration tests for Playbook MCP tools.

Tests MCP tool wrappers with real database, real services, NO MOCKING.
Based on BDD scenarios from interact-with-playbooks-via-mcp.feature.
"""
import pytest
from decimal import Decimal
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from methodology.models import Playbook
from mcp_integration.context import set_current_user
from mcp_integration.tools import (
    create_playbook,
    list_playbooks,
    get_playbook,
    update_playbook,
    delete_playbook
)

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


@pytest.mark.django_db(transaction=True)
class TestMCPPlaybookCreate:
    """MCP-PB-01 to MCP-PB-03: Create playbook scenarios."""
    
    @pytest.mark.asyncio
    async def test_mcp_pb_01_create_draft_playbook_via_mcp_tool(self, setup_user_context):
        """
        Scenario: MCP-PB-01 Create draft playbook via MCP tool
        Given Cascade receives user request
        When Cascade calls create_playbook
        Then playbook created with version 0.1, status draft
        """
        result = await create_playbook(
            name="React Component Development",
            description="Best practices for building reusable React components",
            category="frontend"
        )
        
        assert result['id'] is not None
        assert result['version'] == '0.1'
        assert result['status'] == 'draft'
        assert result.get('visibility') == 'private'
        
        # Verify in database
        playbook = await sync_to_async(Playbook.objects.select_related('author').get)(id=result['id'])
        assert playbook.author == setup_user_context
        assert playbook.name == "React Component Development"
    
    @pytest.mark.asyncio
    async def test_mcp_pb_02_create_playbook_with_duplicate_name_raises_error(self, setup_user_context):
        """Scenario: MCP-PB-02 Create playbook with duplicate name raises error"""
        await create_playbook(name="React Component Development", description="Test", category="frontend")
        
        with pytest.raises(ValueError):
            await create_playbook(name="React Component Development", description="Different", category="frontend")


@pytest.mark.django_db(transaction=True)
class TestMCPPlaybookUpdate:
    """MCP-PB-10 to MCP-PB-13: Update playbook scenarios."""
    
    @pytest.mark.asyncio
    async def test_mcp_pb_10_update_draft_playbook_increments_version(self, setup_user_context):
        """Scenario: MCP-PB-10 Update draft playbook increments version"""
        created = await create_playbook(name="Original Name", description="Original Description", category="development")
        
        result = await update_playbook(playbook_id=created['id'], name="Updated Name")
        
        assert result['name'] == "Updated Name"
        assert result['version'] == '0.2'
        # Version incremented

    @pytest.mark.asyncio
    async def test_mcp_pb_11_update_playbook_duplicate_name_raises_value_error(self, setup_user_context):
        """Renaming a playbook to an existing name raises ValueError."""
        first = await create_playbook(name='Alpha Playbook', description='a', category='test')
        await create_playbook(name='Beta Playbook', description='b', category='test')
        with pytest.raises(ValueError, match='Beta'):
            await update_playbook(playbook_id=first['id'], name='Beta Playbook')


@pytest.mark.django_db(transaction=True)
class TestMCPPlaybookDelete:
    """MCP-PB-14: Delete playbook scenarios."""
    
    @pytest.mark.asyncio
    async def test_mcp_pb_14_delete_draft_playbook_success(self, setup_user_context):
        """Scenario: MCP-PB-14 Delete draft playbook removes from database"""
        created = await create_playbook(name="To Delete", description="Will be deleted", category="test")
        
        result = await delete_playbook(playbook_id=created['id'])
        
        assert result['deleted'] is True
        exists = await sync_to_async(Playbook.objects.filter(id=created['id']).exists)()
        assert not exists


@pytest.mark.django_db(transaction=True)
class TestMCPPlaybookVisibility:
    """Cross-user visibility: can_view matches Playbook model (local MCP path / tools.py)."""

    @pytest.mark.asyncio
    async def test_non_owner_can_get_public_released(self, db):
        owner = User.objects.create_user(username="owner_vis", email="o@test.com", password="test123")
        viewer = User.objects.create_user(username="viewer_vis", email="v@test.com", password="test123")
        pb = Playbook.objects.create(
            name="Public Released",
            description="d",
            category="development",
            status="released",
            version=Decimal("1.0"),
            author=owner,
            visibility="public",
        )
        set_current_user(viewer)
        result = await get_playbook(playbook_id=pb.id)
        assert result["id"] == pb.id
        assert result["visibility"] == "public"
        assert result["status"] == "released"

    @pytest.mark.asyncio
    async def test_non_owner_cannot_get_public_draft(self, db):
        owner = User.objects.create_user(username="owner_pd", email="opd@test.com", password="test123")
        viewer = User.objects.create_user(username="viewer_pd", email="vpd@test.com", password="test123")
        pb = Playbook.objects.create(
            name="Public Draft",
            description="d",
            category="development",
            status="draft",
            version=Decimal("0.1"),
            author=owner,
            visibility="public",
        )
        set_current_user(viewer)
        with pytest.raises(ValueError, match="not found"):
            await get_playbook(playbook_id=pb.id)

    @pytest.mark.asyncio
    async def test_non_owner_cannot_get_private(self, db):
        owner = User.objects.create_user(username="owner_pr", email="opr@test.com", password="test123")
        viewer = User.objects.create_user(username="viewer_pr", email="vpr@test.com", password="test123")
        pb = Playbook.objects.create(
            name="Private Rel",
            description="d",
            category="development",
            status="released",
            version=Decimal("1.0"),
            author=owner,
            visibility="private",
        )
        set_current_user(viewer)
        with pytest.raises(ValueError, match="not found"):
            await get_playbook(playbook_id=pb.id)

    @pytest.mark.asyncio
    async def test_list_includes_public_from_others(self, db):
        owner = User.objects.create_user(username="owner_lst", email="ol@test.com", password="test123")
        viewer = User.objects.create_user(username="viewer_lst", email="vl@test.com", password="test123")
        pb = Playbook.objects.create(
            name="Other Public",
            description="d",
            category="development",
            status="released",
            version=Decimal("1.0"),
            author=owner,
            visibility="public",
        )
        set_current_user(viewer)
        rows = await list_playbooks(status="all")
        ids = {r["id"] for r in rows}
        assert pb.id in ids

    @pytest.mark.asyncio
    async def test_list_excludes_public_draft_from_others(self, db):
        """Others' visibility=public + status=draft must not appear in MCP list."""
        owner = User.objects.create_user(username="owner_pd_lst", email="opdl@test.com", password="test123")
        viewer = User.objects.create_user(username="viewer_pd_lst", email="vpdl@test.com", password="test123")
        draft_pub = Playbook.objects.create(
            name="Others Public Draft",
            description="d",
            category="development",
            status="draft",
            version=Decimal("0.1"),
            author=owner,
            visibility="public",
        )
        set_current_user(viewer)
        for status_arg in ("all", "draft"):
            rows = await list_playbooks(status=status_arg)
            ids = {r["id"] for r in rows}
            assert draft_pub.id not in ids

    @pytest.mark.asyncio
    async def test_create_with_visibility_public(self, db):
        u = User.objects.create_user(username="vis_create", email="vc@test.com", password="test123")
        set_current_user(u)
        result = await create_playbook(
            name="Vis Create",
            description="x",
            category="development",
            visibility="public",
        )
        assert result["visibility"] == "public"
        assert result["status"] == "draft"

    @pytest.mark.asyncio
    async def test_create_defaults_visibility_private(self, db):
        u = User.objects.create_user(username="vis_def", email="vd@test.com", password="test123")
        set_current_user(u)
        result = await create_playbook(name="Default Vis", description="x", category="development")
        assert result["visibility"] == "private"

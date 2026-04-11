# Implementation Plan: Global Agents Navigation (FOB-AGENTS-GLOBAL-LIST-1)

**Feature File**: `docs/features/act-7-agents/agents-global-list.feature`  
**Status**: 📋 PLANNED  
**Branch**: `feature/agents-global-nav`

## Executive Summary

Enable global Agents navigation from the main navbar. The backend (view, URL, template) already exists and is fully functional. This is a **frontend-only change** to:
1. Enable the "Agents" navbar link (currently disabled)
2. Add active state highlighting when on Agents pages
3. Update tests to verify navbar integration

**Complexity**: ⭐ Easy - Single template edit + test updates

---

## Codebase Assessment

### ✅ Already Implemented (No Changes Needed)

1. **Backend View**: `@/Users/denispetelin/GitHub/mimir/methodology/agent_views.py:23-52`
   - `agent_list_global()` - Fully functional global agents list
   - Supports search via `?q=` parameter
   - Returns all agents across all playbooks for authenticated user

2. **URL Routing**: `@/Users/denispetelin/GitHub/mimir/mimir/urls.py:42`
   - `path("agents/", include("methodology.agent_urls"))`
   - URL name: `agent_list`

3. **Template**: `@/Users/denispetelin/GitHub/mimir/templates/agents/list.html`
   - Complete global agents list UI
   - Search functionality
   - Empty state
   - Playbook column showing parent playbook

4. **Tests**: `@/Users/denispetelin/GitHub/mimir/tests/integration/test_agent_list_find.py`
   - 11 integration tests covering list, search, empty state
   - All tests passing

### 🔧 Needs Implementation

1. **Navbar Link**: `@/Users/denispetelin/GitHub/mimir/templates/base.html:100-104`
   - Currently: `class="nav-link disabled"` with `href="#"`
   - Need: Enable link, add active state logic, update tooltip

2. **Tests**: Need navbar-specific tests
   - Verify link is enabled and clickable
   - Verify active state when on agents pages
   - Verify tooltip shows correct text

---

## Implementation Plan

### Initial Setup

- [x] Feature specification created: `docs/features/act-7-agents/agents-global-list.feature`
- [ ] Create branch: `feature/agents-global-nav`
- [ ] Implementation plan created (this document)

### Scenario AGENT-GLOBAL-01: Navigate to global agents list from navbar

**Backend**: ✅ Already complete (no changes)

**Frontend Implementation**:

1. **Enable navbar link** in `@/Users/denispetelin/GitHub/mimir/templates/base.html:100-104`
   - Change from disabled link to active link
   - Add URL: `{% url 'agent_list' %}`
   - Add active state logic: `{% if '/agents/' in request.path %}`
   - Update tooltip from "Coming soon" to "View all agents across your playbooks"
   - Keep icon: `fa-brain`
   - Add `data-testid="nav-agents"`

2. **Integration Test**: Create `tests/integration/test_navbar_agents.py`
   - Test: Navbar link is enabled and visible
   - Test: Clicking link navigates to `/agents/`
   - Test: Active class applied when on `/agents/` path
   - Test: Active class applied when on `/agents/<id>/` (agent detail)
   - Test: Tooltip shows correct text

**Commit**: `feat(navbar): enable Agents link in main navigation`

---

### Scenarios AGENT-GLOBAL-02 through AGENT-GLOBAL-12

**Status**: ✅ Already implemented and tested

These scenarios are already covered by:
- Existing view: `agent_list_global()`
- Existing template: `agents/list.html`
- Existing tests: `test_agent_list_find.py`

**No additional implementation needed** - these scenarios work out of the box once navbar link is enabled.

---

## Test Strategy

### Existing Tests (No Changes)
- `tests/integration/test_agent_list_find.py` - 11 tests, all passing
- Covers: list display, search, empty state, playbook column

### New Tests Required

**File**: `tests/integration/test_navbar_agents.py`

```python
"""
Integration tests for Agents navbar navigation.
Covers scenario: AGENT-GLOBAL-01, AGENT-GLOBAL-12
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from methodology.models import Agent, Playbook

User = get_user_model()

@pytest.mark.django_db
class TestNavbarAgents:
    """Test Agents link in main navbar."""
    
    def test_navbar_agents_link_enabled(self):
        """AGENT-GLOBAL-01: Agents link is enabled and clickable."""
        # Setup user and login
        # GET dashboard page
        # Assert: Agents link is NOT disabled
        # Assert: Agents link href="/agents/"
        # Assert: data-testid="nav-agents" present
        pass
    
    def test_navbar_agents_link_navigation(self):
        """AGENT-GLOBAL-01: Clicking Agents navigates to global list."""
        # Setup user and login
        # GET /agents/
        # Assert: status 200
        # Assert: "All Agents" or "Agents" header present
        pass
    
    def test_navbar_agents_active_on_list_page(self):
        """AGENT-GLOBAL-12: Agents link has active class on list page."""
        # Setup user and login
        # GET /agents/
        # Assert: nav-agents link has "active" class
        # Assert: aria-current="page" present
        pass
    
    def test_navbar_agents_active_on_detail_page(self):
        """AGENT-GLOBAL-12: Agents link has active class on detail page."""
        # Setup user, playbook, agent
        # GET /agents/<id>/
        # Assert: nav-agents link has "active" class
        pass
    
    def test_navbar_agents_tooltip(self):
        """Agents link has correct tooltip."""
        # Setup user and login
        # GET dashboard
        # Assert: tooltip text = "View all agents across your playbooks"
        pass
```

---

## Files to Modify

### 1. `templates/base.html` (1 edit)

**Current** (lines 100-104):
```html
<li class="nav-item">
    <a class="nav-link disabled" href="#" data-testid="nav-agents"
       data-bs-toggle="tooltip" data-bs-placement="bottom"
       title="Coming soon: Define and assign agents">
        <i class="fas fa-brain"></i> Agents
    </a>
</li>
```

**New**:
```html
<li class="nav-item">
    <a class="nav-link {% if '/agents/' in request.path %}active{% endif %}" 
       href="{% url 'agent_list' %}" 
       data-testid="nav-agents"
       data-bs-toggle="tooltip" data-bs-placement="bottom"
       title="View all agents across your playbooks"
       {% if '/agents/' in request.path %}aria-current="page"{% endif %}>
        <i class="fas fa-brain"></i> Agents
    </a>
</li>
```

**Changes**:
- Remove `disabled` class
- Add active state: `{% if '/agents/' in request.path %}active{% endif %}`
- Change `href="#"` to `href="{% url 'agent_list' %}"`
- Update tooltip: "Coming soon..." → "View all agents across your playbooks"
- Add `aria-current="page"` for accessibility when active

---

### 2. `tests/integration/test_navbar_agents.py` (NEW FILE)

Create new test file with 5 tests as outlined above.

---

## Commit Strategy

1. `feat(navbar): enable Agents link in main navigation`
   - Edit `templates/base.html` navbar link
   - Body: Enable Agents navbar link, add active state, update tooltip

2. `test(navbar): add integration tests for Agents navigation`
   - Create `tests/integration/test_navbar_agents.py`
   - Body: Test navbar link enabled, navigation, active state, tooltip

---

## Rules to Follow

### ⚠️ MANDATORY PRE-EDIT CHECKLIST
**Before editing `base.html`:**
1. ✅ Read file first with `read_file` tool
2. ✅ Verify exact whitespace/indentation
3. ✅ After edit: verify file not corrupted with `wc -l`

### Test-First Development
- Write failing tests first in `test_navbar_agents.py`
- Run tests: `pytest tests/integration/test_navbar_agents.py -v`
- Implement navbar change
- Verify all tests pass

### Small Increments
- Single atomic change: navbar link only
- Commit immediately after tests pass
- Do not bundle with other changes

### GUI Design Rules
- ✅ Icon already correct: `fa-brain`
- ✅ Tooltip required: "View all agents across your playbooks"
- ✅ Active state required: Bootstrap `.active` class
- ✅ Accessibility: `aria-current="page"` when active

---

## Success Criteria

- [ ] Agents navbar link is enabled (not disabled)
- [ ] Clicking Agents navigates to `/agents/`
- [ ] Active class applied when on `/agents/` or `/agents/<id>/`
- [ ] Tooltip shows "View all agents across your playbooks"
- [ ] All new tests pass (5 tests in `test_navbar_agents.py`)
- [ ] All existing tests still pass (11 tests in `test_agent_list_find.py`)
- [ ] No regressions in other navbar links
- [ ] Feature file updated with status: ✅ DONE

---

## Artifacts Produced

- `docs/features/act-7-agents/agents-global-list.feature` - Feature specification
- `docs/plans/AGENT_GLOBAL_NAV_IMPLEMENTATION_PLAN.md` - This implementation plan
- `tests/integration/test_navbar_agents.py` - Navbar integration tests
- Updated `templates/base.html` - Enabled Agents navbar link

---

## Artifacts Consumed

- `docs/architecture/SAO.md` - Django + HTMX architecture, URL conventions
- `docs/features/user_journey.md` - Navigation patterns, UI conventions
- `templates/base.html` - Main navbar template
- `methodology/agent_views.py` - Existing global agents view
- `methodology/agent_urls.py` - Existing URL configuration
- `templates/agents/list.html` - Existing global agents template

---

## Notes

**Why This Is Easy**:
- Backend already 100% complete and tested
- Template already exists and works
- Only need to enable one navbar link
- No new views, URLs, or services required
- No database changes
- No MCP changes

**Estimated Effort**: 15 minutes
- 5 min: Write tests
- 5 min: Edit navbar link
- 5 min: Run tests and verify

**Risk**: ⭐ Very Low
- Single template change
- Well-established pattern (Activities, Workflows already use same pattern)
- Comprehensive test coverage exists

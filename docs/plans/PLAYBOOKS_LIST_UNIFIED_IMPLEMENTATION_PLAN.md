# Implementation Plan: Unified Playbooks List + Draft Public Hidden

**Feature**: Playbooks list shows owned and browsable public playbooks in one grid; empty state only when nothing is visible; draft public playbooks stay owner-only.

**Specs**: `docs/features/act-2-playbooks/playbooks-list-find.feature` (LIST+FIND-19b/19c/25), `playbooks-access-control.md`

**UAT**: `tests/uat/e2e-uat-flow.feature` (UAT-03-05, UAT-03-05b), `tests/uat/mcp-uat-flow.feature` (MCP-01b preconditions)

---

## Problem

1. Draft playbooks with `visibility=public` appeared in the public browse section (e.g. Admin Public Playbook v0.1 Draft).
2. The "No playbooks yet" banner showed when the user had zero **owned** playbooks, even when public playbooks were visible below.

## Design

| Rule | Behavior |
|------|----------|
| Public browse | `visibility=public` AND `status != draft` AND `author != current_user` |
| Owner list | All owned playbooks regardless of visibility/status |
| `can_view()` | Owner always; others only if public and not draft |
| Empty state | Only when owned + browsable public lists are both empty |
| UI | Single card grid (`data-testid="playbooks-list-section"`), header "Playbooks" |

MCP remains author-scoped (unchanged).

## Files Changed

| File | Change |
|------|--------|
| `methodology/models/playbook.py` | `can_view` excludes draft public for non-owners |
| `methodology/services/playbook_service.py` | `list_public_playbooks` excludes draft |
| `methodology/playbook_views.py` | `has_playbooks` context flag |
| `templates/playbooks/list.html` | Unified grid; conditional empty state |
| `docs/features/...` | Feature + access-control + user journey |
| `tests/integration/test_playbook_list.py` | New/changed list scenarios |
| `tests/integration/test_playbook_view.py` | Draft public 404 |
| `tests/integration/test_playbook_nested_access_isolation.py` | Released public + draft blocked |
| `tests/uat/*.feature` | UAT step updates |

## Tests

- `test_draft_public_playbook_from_other_author_hidden`
- `test_no_empty_state_when_only_public_playbooks_exist`
- `test_non_owner_gets_404_for_draft_public_playbook`
- `TestDraftPublicPlaybookNestedRoutesBlocked`

## Status

Implemented.

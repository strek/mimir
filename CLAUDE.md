# CLAUDE.md — Mimir Codebase Guide

## What Is Mimir

Mimir is a **self-evolving engineering playbook platform**. It lets teams document, evolve, and leverage software development methodologies through a Django web UI and an MCP (Model Context Protocol) server that AI assistants query directly.

**Two-part system:**
- **FOB (this repo)** — Django 5 app with SQLite, runs MCP server + web server concurrently
- **HOMEBASE** (separate repo) — Django + HTMX, eventing → Neo4j graph DB, aggregates PIPs from FOBs

**Key innovation:** AI assistants can propose playbook improvements (PIPs) that engineers review and approve.

---

## Architecture

### Directory Layout

```
mimir/                        # Django project config (settings, urls, wsgi)
methodology/                  # Core Django app (models, services, views, templates)
  models/                     # 7 entity models
  services/                   # Business logic (shared by UI and MCP)
  views/                      # Thin Django view controllers
  utils/                      # markdown_renderer.py (Markdown + Mermaid)
mcp_integration/              # MCP server (thin wrappers over services)
  tools.py                    # All 16+ MCP tool definitions
  context.py                  # User context
  management/commands/mcp_server.py
accounts/                     # User auth
tests/
  unit/                       # Model and service unit tests
  integration/                # MCP tools, multi-model workflows
  e2e/                        # Playwright browser tests
docs/
  features/act-*/             # BDD Gherkin specs (source of truth for features)
  architecture/SAO.md         # System architecture overview (read before big changes)
  plans/                      # Per-feature implementation plans
  ux/                         # Design system, IA guidelines, user journey
.windsurf/
  rules/                      # 38 development convention rules
  workflows/                  # ESM (design) and BPE (build) process workflows
```

### Data Model Hierarchy

```
Playbook (status: draft/released/disabled; version: 0.x → 1.0+)
  └─ Workflow (name, abbreviation, order)
       ├─ Phase (optional; currently string field, not separate model)
       └─ Activity (name, guidance: Markdown+Mermaid, order)
            └─ Artifact (input/output, producer/consumer)
Playbook also has: Agent (Act 7, not yet built), Skill (Act 8, not yet built)
```

**Implementation status:**
| Entity | Status |
|--------|--------|
| Playbook | ✅ Full CRUDLF |
| Workflow | ✅ Full CRUDLF + export/import |
| Activity | ✅ Full CRUDLF |
| Phase | ⚠️ String field only |
| Artifact | ⚠️ Model exists, partial |
| Agent | ❌ Not built (Act 7) |
| Skill | ❌ Not built (Act 8) |
| PIP | ❌ Not built (Act 9) |

### Services Pattern

Services in `methodology/services/` are **shared by both UI views and MCP tools** — never add MCP-specific logic to services. MCP tools only add: user context lookup, permission check, serialization.

Version auto-increment (Activity update → increments grandparent Playbook version) happens in the MCP tool wrapper, not the service.

### MCP Access Rules

- **Draft playbooks** (v0.x): Full CRUD via MCP
- **Released playbooks** (v≥1.0): Read-only via MCP; changes must go through PIPs

---

## Terminology

| Internal Code | User-Facing UI |
|---------------|----------------|
| `methodology` (app, models, services) | "playbooks" |
| `MethodologyRepository` | — |
| `manage.py mcp_server` | — |

Always use "playbooks" in UI text; always use `methodology` in code.

---

## Development Process

### Before Implementing Any Feature

1. Read the relevant feature spec in `docs/features/act-*/`
2. Read `docs/architecture/SAO.md` for architectural context
3. Create an implementation plan in `docs/plans/`

### Implementation Order (BPE Workflow)

1. **Backend**: models → services → views (thin controllers)
2. **Frontend**: Django templates + HTMX interactions (add `data-testid` on interactive elements)
3. **Feature Acceptance Tests**: Django test client, covers all `.feature` scenarios (fast, run on every commit)
4. **Journey Certification Tests**: Playwright browser automation (run on PR merge)
5. Check Definition of Done → PR

### Skeleton-First Pattern

```python
def create_workflow(self, playbook, name, description):
    """Create a new workflow in the given playbook.

    Args:
        playbook: Playbook instance
        name: str workflow name
        description: str
    Returns:
        Workflow instance
    Example return: Workflow(id=1, name="Design Features", ...)
    """
    raise NotImplementedError()
```

Write stub → write test (red) → implement → test passes (green) → commit.

---

## Coding Conventions

### Commit Format (Angular Convention — strict)

```
<type>(<scope>): <subject>

<body — what changed and why>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
Example: `feat(workflows): add export to JSON via MCP tool`

### Code Style

- Top-level methods: **20-30 lines max**; extract helpers for supporting logic
- Imports at **module level** — never inside functions
- Single responsibility per method
- Black + Ruff for formatting/linting

### Logging

- INFO level; log what/why/where/when
- Output to `logs/app.log`
- Include request/correlation IDs for debugging

---

## Testing

```bash
# Run all tests
pytest tests/

# Run specific category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v         # requires Playwright setup

# With coverage
pytest tests/ --cov=methodology --cov=mcp_integration
```

**Key rules:**
- **Test-first**: write test before implementation
- **No mocks in integration tests**: use real objects/DB (rule: `do-not-mock-in-integration-tests.md`)
- Run tests after every change

---

## Running Locally

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate

# Web server (terminal 1)
python manage.py runserver 8000

# MCP server (terminal 2)
python manage.py mcp_server --user=admin

# Load demo data
python manage.py create_demo_fdd
```

Both processes share the same SQLite DB with a 20-second timeout for concurrent access.

---

## Key Reference Files

| What | Where |
|------|-------|
| System architecture | `docs/architecture/SAO.md` |
| All Acts / user journey | `docs/features/user_journey.md` |
| MCP tool definitions | `mcp_integration/tools.py` |
| Design system / UI patterns | `docs/ux/IA_guidelines.md` |
| Development rules (38) | `.windsurf/rules/*.md` |
| Development workflows | `.windsurf/workflows/*.md` |
| Feature specs | `docs/features/act-*/` |

---

## UI Patterns

- **No SPA / no React** — Django templates + HTMX only
- **Bootstrap 5.3+** for all styling; add CSS variables, not raw overrides
- **Graphviz** for workflow/activity diagrams
- **Mermaid.js** for inline diagrams in activity guidance (Markdown)
- Always add `data-testid` attributes to interactive elements for Playwright tests
- Tooltips on complex form fields (consistent pattern per `docs/ux/IA_guidelines.md`)

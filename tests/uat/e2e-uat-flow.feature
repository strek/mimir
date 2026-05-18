@manual @uat @e2e-uat-flow
Feature: Mimir E2E UAT — full user journey (manual / Cursor replay)
  Single living spec for instructing Cursor (browser MCP + user-mimir CallMcpTool) to exercise
  the built product in strict linear order, aligned with docs/features/user_journey.md.

  ============================================================================
  RULES FOR MAINTAINERS — RUN SCENARIOS IN ORDER!!! THIS IS A LINEAR FLOW!!!
  ============================================================================
  - Each scenario block is tagged with a journey slice (@act-0, @act-1, …).
  - This file is NOT wired to pytest; `.feature` is ignored by python test discovery.
  - Prefer explicit URLs, data-testid selectors, and MCP tool names for mechanical replay.
  - Substitute placeholders from the live session before later scenarios (see registry below).

  Replay stack:
    - Browser: cursor-ide-browser MCP (navigate, snapshot, fill, click).
    - Methodology API: Cursor user-mimir MCP (CallMcpTool) after Journey 2 token setup.

  ============================================================================
  PLACEHOLDER REGISTRY (fill during replay)
  ============================================================================
    | placeholder              | set in scenario        | example        |
    | <UAT_EMAIL>              | fixed                  | dp2580@nyu.edu |
    | <UAT_USERNAME>           | UAT-01-01              | uat_dp2580     |
    | <UAT_PASSWORD>           | operator run notes     | (not in git)   |
    | <UAT_TOKEN>              | UAT-01-04              | abc123…        |
    | <GUI_PLAYBOOK_ID>        | UAT-03-01              | 12             |
    | <GUI_WORKFLOW_ID>        | UAT-03-01 / detail URL | 25             |
    | <ACT_ALPHA_PK>           | UAT-03-02              | 126            |
    | <ACT_BETA_PK>            | UAT-03-02              | 127            |
    | <GUI_PHASE_PK>           | UAT-03-02              | 8              |
    | <GUI_SKILL_PK>           | UAT-03-02              | 15             |
    | <GUI_AGENT_PK>           | UAT-03-02              | 9              |
    | <GUI_ARTIFACT_PK>        | UAT-03-02              | 11             |
    | <GUI_RULE_PK>            | UAT-03-02              | 7              |
    | <MCP_SANDBOX_PB_ID>      | UAT-04-02 step 1       | 13             |
    | <MCP_SANDBOX_WF_ID>      | UAT-04-02              | 26             |
    | <MCP_EXPORT_DIR>         | UAT-04-02              | /tmp/mimir-uat |
    | <PIP_GUI_PK>             | UAT-06-01              | 3              |
    | <PIP_MCP_PK>             | UAT-06-02              | 4              |
    | <PIP_DISPOSABLE_PK>      | UAT-06-03 (optional)   | 5              |

  ============================================================================
  SHARED ACTORS
  ============================================================================
    | persona      | credentials            | role                                      |
    | uat_user     | <UAT_USERNAME> / <UAT_PASSWORD> | primary — registers dp2580@nyu.edu |
    | admin        | admin / admin          | staff — Django Admin PIP finalization only |

  ============================================================================
  PRECONDITIONS (mandatory before Journey 1)
  ============================================================================
    - FOB dev server: python manage.py runserver → http://127.0.0.1:8000
    - Real email (Gmail): USE_SES_IN_DEV=1 + AWS SES credentials in .env;
      DEFAULT_FROM_EMAIL must be SES-verified (see mimir/settings/dev.py).
    - GALDR_EAGER=True recommended in dev settings for synchronous Galdr during PIP steps.
    - admin superuser exists (createsuperuser if missing).
    - Fresh run: pick unique <UAT_USERNAME> if dp2580@nyu.edu already registered.
    - Cursor user-mimir MCP server entry exists; TOKEN updated in Journey 2.

  ============================================================================
  OUT OF SCOPE (do not assert — not implemented per user_journey gap analysis)
  ============================================================================
    - Act 11 Teams (create / browse / join / team playbook assignment UI)
    - Playbook JSON/MPA import UI (Import Playbook buttons are disabled “coming soon”)
    - Notification bell / in-app notification center / notification preferences
    - Full FOB-SETTINGS-1 (storage, 2FA, MCP snippet builder page)
    - Activate playbook (Act 12 dashboard feature)
    - Dedicated post-registration “Congratulations + token” page; use FOB-PROFILE-1 instead
    - One-time FOB MCP configuration guide screen (manual IDE JSON in Journey 2)
    - Playbook corruption recovery (Act 14)
    - Global search for Teams / Artifacts (search covers playbooks, workflows, activities only)

  Source references:
    - docs/features/user_journey.md (Acts 0–9, 1.5, 12 partial)
    - tests/integration/test_mcp_e2e_all_tools.py (53-tool order + arguments)
    - mcp_integration/tools.py (+ 8 PIP lifecycle tools on Django MCP = 61 total)


  # ==========================================================================
  # Journey 1 — Act 0–1: Registration, email verification, profile token
  # User journey: Act 0, Act 1, FOB-PROFILE-1 (MVP)
  # ==========================================================================

  -----------------------------------------------------------------------------
  @manual @uat @act-0 @act-1
  Scenario: UAT-01-01 Register new account with Terms of Service (FOB Registration)
    Given operator ensures USE_SES_IN_DEV=1 so verification email reaches Gmail
    When uat_user opens "/auth/user/register/"
    Then page contains data-testid "register-form"

    When uat_user fills data-testid "register-first-name" with "UAT"
    And uat_user fills data-testid "register-last-name" with "Journey"
    And uat_user fills data-testid "register-username-input" with "<UAT_USERNAME>"
    And uat_user fills data-testid "register-email-input" with "<UAT_EMAIL>"
    And uat_user fills data-testid "register-password-input" with "<UAT_PASSWORD>"
    And uat_user fills data-testid "register-password-confirm-input" with "<UAT_PASSWORD>"
    Then data-testid "register-submit-button" is disabled

    When uat_user checks data-testid "register-tos-checkbox"
    Then data-testid "register-submit-button" is enabled

    When uat_user clicks data-testid "register-submit-button"
    Then browser lands on "/auth/user/login/"
    And flash or page text includes "Account created" and "verify your email"

    # Record: <UAT_USERNAME>, <UAT_EMAIL>

  -----------------------------------------------------------------------------
  @manual @uat @act-0 @act-1
  Scenario: UAT-01-02 Login blocked until email verified
    When uat_user opens "/auth/user/login/"
    And uat_user fills data-testid "login-username-input" with "<UAT_USERNAME>"
    And uat_user fills data-testid "login-password-input" with "<UAT_PASSWORD>"
    And uat_user clicks data-testid "login-submit-button"
    Then page contains data-testid "login-unverified-banner"
    And page contains data-testid "login-resend-btn"
    And banner text includes "verify your email"

  -----------------------------------------------------------------------------
  @manual @uat @act-0 @act-1
  Scenario: UAT-01-03 Verify email via Gmail (SES delivery)
    When operator opens Gmail inbox for "<UAT_EMAIL>"
    And operator opens the message from Mimir with subject containing "Verify"
    And operator clicks the link matching "/auth/user/verify-email/*/"
    Then browser redirects to "/auth/user/login/"
    And flash or page text includes "verified" and "sign in"

    # Negative path (optional separate run): expired token shows verify-email-expired-alert

  -----------------------------------------------------------------------------
  @manual @uat @act-0 @act-1
  Scenario: UAT-01-04 First login, profile, copy API token (FOB-PROFILE-1)
    When uat_user opens "/auth/user/login/"
    And uat_user fills data-testid "login-username-input" with "<UAT_USERNAME>"
    And uat_user fills data-testid "login-password-input" with "<UAT_PASSWORD>"
    And uat_user clicks data-testid "login-submit-button"
    Then uat_user lands on dashboard or home with authenticated session

    # If redirected to onboarding stub, skip tour:
    # POST /auth/user/onboarding/skip/ or navigate and confirm skip modal.

    When uat_user opens user menu data-testid "user-display"
    And uat_user clicks data-testid "nav-view-profile"
    Then page contains data-testid "profile-page"
    And data-testid "profile-email" shows "<UAT_EMAIL>"

    When uat_user clicks data-testid "profile-token-toggle" (Show)
    And uat_user clicks data-testid "profile-token-copy"
    Then record token from data-testid "profile-token-field" as <UAT_TOKEN>

    And profile section data-testid "profile-playbooks-table" shows empty or no owned playbooks yet

    # Record: <UAT_TOKEN>


  # ==========================================================================
  # Journey 2 — MCP IDE setup (Act 12 partial — user-mimir configuration)
  # ==========================================================================

  -----------------------------------------------------------------------------
  @manual @uat @act-12-setup
  Scenario: UAT-02-01 Configure Cursor user-mimir MCP with UAT token
    Given operator edits Cursor MCP settings for server "user-mimir"
    When operator sets env TOKEN to "<UAT_TOKEN>"
    And operator sets BASE_URL to "http://127.0.0.1:8000" (or REST base used by user-mimir)
    And operator reloads / restarts the user-mimir MCP connection in Cursor
    Then MCP server is ready for CallMcpTool invocations as uat_user

    # Reference JSON (user journey Act 1 — paste into IDE if not using env vars):
    # {
    #   "mimir": {
    #     "command": "python",
    #     "args": ["-m", "mcp_integration.server"],
    #     "env": {
    #       "BASE_URL": "http://127.0.0.1:8000",
    #       "TOKEN": "<UAT_TOKEN>"
    #     }
    #   }
    # }

  -----------------------------------------------------------------------------
  @manual @uat @act-12-setup
  Scenario: UAT-02-02 MCP smoke — list_playbooks as registered user
    When MCP tool "list_playbooks" is called with status "draft"
    Then response is a list (may be empty for new user)
    When MCP tool "list_playbooks" is called with status "all"
    Then call succeeds without authentication error
    And MCP identity is uat_user (not admin)


  # ==========================================================================
  # Journey 3 — Acts 2–8: GUI CRUDL on canonical playbook
  # User journey: Playbooks, Workflows, Phases, Activities, Artifacts, Agents, Skills, Rules
  # ==========================================================================

  -----------------------------------------------------------------------------
  @manual @uat @act-2
  Scenario: UAT-03-01 Create UAT Journey Playbook via wizard (draft)
    Given uat_user is logged in via browser
    When uat_user clicks data-testid "nav-playbooks"
    And uat_user navigates to "/playbooks/create/"
    Then page contains data-testid "wizard-step-1"

    When uat_user fills data-testid "name-input" with "UAT Journey Playbook"
    And uat_user fills data-testid "description-input" with:
      """
      Full-system UAT playbook — GUI CRUDL, MCP tools, release, and PIP round-trip.
      """
    And uat_user selects data-testid "category-select" value "development"
    And uat_user selects data-testid "visibility-select" value "private"
    And uat_user clicks submit button "Next: Add Workflows"

    Then browser is on "/playbooks/create/step2/"
    When uat_user fills data-testid "workflow-name-input" with "UAT Workflow"
    And uat_user fills data-testid "workflow-description-input" with "Primary UAT workflow"
    And uat_user clicks data-testid "add-workflow" ("Next: Publishing")

    Then browser is on "/playbooks/create/step3/"
    And page contains data-testid "summary-card"
    When uat_user selects publication status "draft" on step 3
    And uat_user clicks button "Create Playbook"
    Then browser lands on "/playbooks/<GUI_PLAYBOOK_ID>/"
    And page data-testid "playbook-detail" is visible
    And data-testid "status-badge" text includes "Draft"

    # Record: <GUI_PLAYBOOK_ID> from URL; open Workflows tab and record <GUI_WORKFLOW_ID>

  -----------------------------------------------------------------------------
  @manual @uat @act-3 @act-4 @act-5 @act-6 @act-7 @act-8
  Scenario: UAT-03-02 GUI CRUDL — child entities under UAT Journey Playbook
    Given uat_user is on "/playbooks/<GUI_PLAYBOOK_ID>/"

    # --- Phase (CREATE + LIST) ---
    When uat_user clicks data-testid "tab-phases"
    And uat_user clicks data-testid "create-phase-btn"
    And uat_user fills phase form data-testid "phase-create-form" name "UAT Phase" description "Planning"
    And uat_user submits phase create
    Then phase appears on playbook phases tab
    And record phase pk as <GUI_PHASE_PK> from detail URL or list link

    When uat_user clicks data-testid "nav-phases"
    Then page data-testid "phases-list-global" lists "UAT Phase"

    # --- Activities Alpha + Beta (CREATE + READ + UPDATE) ---
    When uat_user navigates to "/playbooks/<GUI_PLAYBOOK_ID>/workflows/<GUI_WORKFLOW_ID>/activities/create/"
    Then page contains data-testid "activity-create"
    When uat_user fills data-testid "name-input" with "Activity Alpha"
    And uat_user fills data-testid "guidance-input" with "## Alpha\n\nInitial guidance for Activity Alpha."
    And uat_user selects data-testid "phase-select" to UAT Phase if available
    And uat_user clicks data-testid "save-btn"
    Then record activity pk as <ACT_ALPHA_PK>

    When uat_user navigates to "/playbooks/<GUI_PLAYBOOK_ID>/workflows/<GUI_WORKFLOW_ID>/activities/create/"
    And uat_user fills data-testid "name-input" with "Activity Beta"
    And uat_user fills data-testid "guidance-input" with "## Beta\n\nInitial guidance for Activity Beta."
    And uat_user clicks data-testid "save-btn"
    Then record activity pk as <ACT_BETA_PK>

    When uat_user opens activity edit for Activity Alpha
    And uat_user updates data-testid "guidance-input" with "## Alpha\n\nGUI-updated guidance."
    And uat_user clicks data-testid "save-btn"
    Then activity detail reflects updated guidance

    When uat_user clicks data-testid "nav-activities"
    Then page data-testid "activities-global-list" lists Activity Alpha and Activity Beta

    # --- Agent (CREATE + LIST + READ) ---
    When uat_user clicks data-testid "tab-agents" on playbook detail
    And uat_user clicks data-testid "create-agent-btn"
    And uat_user fills data-testid "agent-create-form" name "UAT Agent" description "Test agent persona"
    And uat_user clicks data-testid "create-agent-btn" submit
    Then record agent pk as <GUI_AGENT_PK>
    When uat_user clicks data-testid "nav-agents"
    Then global agents list includes "UAT Agent"

    # --- Skill (CREATE + LIST) ---
    When uat_user navigates to "/playbooks/<GUI_PLAYBOOK_ID>/skills/create/"
    And uat_user creates skill title "UAT Skill" with content "## Skill steps"
    Then record skill pk as <GUI_SKILL_PK>
    When uat_user clicks data-testid "nav-skills"
    Then global skills list includes "UAT Skill"

    # --- Artifact (CREATE + LIST) ---
    When uat_user navigates to "/playbooks/<GUI_PLAYBOOK_ID>/artifacts/create/"
    And uat_user creates artifact name "UAT Artifact" type Document linked to Activity Alpha as producer
    Then record artifact pk as <GUI_ARTIFACT_PK>
    When uat_user clicks data-testid "nav-artifacts"
    Then page data-testid "artifacts-list-global" includes "UAT Artifact"

    # --- Rule (CREATE + LIST + optional DELETE of disposable rule) ---
    When uat_user navigates to "/playbooks/<GUI_PLAYBOOK_ID>/rules/create/"
    And uat_user creates rule title "UAT Rule" content "Always apply in UAT"
    Then record rule pk as <GUI_RULE_PK>
    When uat_user clicks data-testid "nav-rules"
    Then page data-testid "rules-list-global" includes "UAT Rule"

    When uat_user creates disposable rule "UAT Rule Disposable" on same playbook
    And uat_user deletes disposable rule via data-testid "rule-delete-modal" confirm
    Then disposable rule no longer appears in rules list
    And "UAT Rule" still exists (pk <GUI_RULE_PK>)

    # --- Workflow LIST/FIND + READ on playbook ---
    When uat_user clicks data-testid "tab-workflows" on playbook detail
    Then data-testid "workflows-table" row for UAT Workflow is visible
    When uat_user clicks data-testid "nav-workflows"
    Then global workflows list includes UAT Workflow

    # Record all IDs above before Journey 4

  -----------------------------------------------------------------------------
  @manual @uat @act-1 @act-2
  Scenario: UAT-03-03 Navigation and global search smoke (Act 1.5 partial)
    Given uat_user is logged in
    When uat_user navigates to "/dashboard/"
    Then page contains data-testid "dashboard-loaded"

    When uat_user types "UAT Journey" in data-testid "global-search-input"
    And uat_user submits data-testid "global-search-form"
    Then suggestions or results include the UAT playbook

    When uat_user clicks data-testid "nav-pips"
    Then PIPs list page loads (count pill may be zero)

    When uat_user opens data-testid "playbook-book-card-<GUI_PLAYBOOK_ID>" or playbook-view link
    Then playbook detail shows stat activities count >= 2


  # ==========================================================================
  # Journey 4 — MCP all 61 tools (@mcp-full)
  # Strategy: (A) read/update GUI playbook entities; (B) sandbox draft full cycle
  # Order mirrors tests/integration/test_mcp_e2e_all_tools.py + 8 PIP lifecycle tools
  # ==========================================================================

  -----------------------------------------------------------------------------
  @manual @uat @mcp-full @act-12
  Scenario: UAT-04-01 MCP read/update pass on GUI playbook (no deletes)
    Given user-mimir MCP runs as uat_user with TOKEN from Journey 2

    When MCP tool "get_playbook" is called with playbook_id <GUI_PLAYBOOK_ID>
    Then result id equals <GUI_PLAYBOOK_ID> and name is "UAT Journey Playbook"

    When MCP tool "list_workflows" is called with playbook_id <GUI_PLAYBOOK_ID>
    Then result includes workflow id <GUI_WORKFLOW_ID> named "UAT Workflow"

    When MCP tool "list_activities" is called with workflow_id <GUI_WORKFLOW_ID>
    Then result includes Activity Alpha (<ACT_ALPHA_PK>) and Activity Beta (<ACT_BETA_PK>)

    When MCP tool "get_activity" is called with activity_id <ACT_ALPHA_PK>
    Then result includes guidance, agent, skill, output_artifacts keys

    When MCP tool "update_activity" is called with:
      | argument    | value                                      |
      | activity_id | <ACT_ALPHA_PK>                             |
      | guidance    | ## Alpha\n\nMCP-updated guidance (pre-PIP). |
    Then update succeeds

    When MCP tool "set_predecessor" is called with:
      | argument       | value          |
      | activity_id    | <ACT_BETA_PK>  |
      | predecessor_id | <ACT_ALPHA_PK> |
    Then result updated is true

    When MCP tool "list_phases" is called with playbook_id <GUI_PLAYBOOK_ID>
    Then result includes phase id <GUI_PHASE_PK>

    When MCP tool "list_skills" is called with playbook_id <GUI_PLAYBOOK_ID>
    Then result includes skill id <GUI_SKILL_PK>

    When MCP tool "list_agents" is called with playbook_id <GUI_PLAYBOOK_ID>
    Then result includes agent id <GUI_AGENT_PK>

    When MCP tool "list_artifacts" is called with playbook_id <GUI_PLAYBOOK_ID>
    Then result includes artifact id <GUI_ARTIFACT_PK>

    When MCP tool "list_rules" is called with playbook_id <GUI_PLAYBOOK_ID>
    Then result includes rule id <GUI_RULE_PK>

    When MCP tool "link_skill_to_activity" is called with activity_id <ACT_ALPHA_PK> skill_id <GUI_SKILL_PK>
    Then link succeeds
    When MCP tool "unlink_skill_from_activity" is called with activity_id <ACT_ALPHA_PK>
    Then unlink succeeds

    When MCP tool "link_agent_to_activity" is called with activity_id <ACT_ALPHA_PK> agent_id <GUI_AGENT_PK>
    Then link succeeds
    When MCP tool "unlink_agent_from_activity" is called with activity_id <ACT_ALPHA_PK>
    Then unlink succeeds

    When MCP tool "link_artifact_to_activity" is called with artifact_id <GUI_ARTIFACT_PK> activity_id <ACT_BETA_PK> is_required true
    Then response includes artifact input id (record as <ARTIFACT_INPUT_PK> if needed)
    When MCP tool "unlink_artifact_from_activity" is called with artifact_input_id <ARTIFACT_INPUT_PK>
    Then deleted is true

    When MCP tool "set_activity_rules" is called with activity_id <ACT_ALPHA_PK> rule_ids [<GUI_RULE_PK>]
    Then activity_id matches <ACT_ALPHA_PK>

    When MCP tool "export_workflow_to_local" is called with:
      | argument         | value                          |
      | workflow_id      | <GUI_WORKFLOW_ID>              |
      | target_directory | <MCP_EXPORT_DIR>/gui-workflow  |
    Then export_path or files_written present in response

    # Do NOT delete GUI playbook or core activities — needed for Journey 5–7

  -----------------------------------------------------------------------------
  @manual @uat @mcp-full @act-12
  Scenario: UAT-04-02 MCP sandbox — full create/mutate/delete tool marathon (53 core tools)
    Given user-mimir MCP as uat_user
    And operator sets <MCP_EXPORT_DIR> to a writable temp directory (e.g. /tmp/mimir-uat-export)

    # --- Playbooks (5) ---
    When MCP tool "create_playbook" is called with name "MCP Sandbox Playbook" description "Disposable UAT sandbox" category "development"
    Then record id as <MCP_SANDBOX_PB_ID> and status is draft

    When MCP tool "list_playbooks" is called with status "draft"
    Then list includes <MCP_SANDBOX_PB_ID>

    When MCP tool "get_playbook" is called with playbook_id <MCP_SANDBOX_PB_ID>
    Then name is "MCP Sandbox Playbook"

    When MCP tool "update_playbook" is called with playbook_id <MCP_SANDBOX_PB_ID> description "Updated sandbox"
    Then update succeeds

    # --- Workflows (5) — defer delete_workflow / delete_playbook to end ---
    When MCP tool "create_workflow" is called with playbook_id <MCP_SANDBOX_PB_ID> name "MCP Sandbox Workflow" description "Sandbox wf"
    Then record id as <MCP_SANDBOX_WF_ID>

    When MCP tool "list_workflows" is called with playbook_id <MCP_SANDBOX_PB_ID>
    Then list includes <MCP_SANDBOX_WF_ID>

    When MCP tool "get_workflow" is called with workflow_id <MCP_SANDBOX_WF_ID>
    Then name is "MCP Sandbox Workflow"

    When MCP tool "update_workflow" is called with workflow_id <MCP_SANDBOX_WF_ID> description "Updated wf"
    Then update succeeds

    # --- Phases (6) ---
    When MCP tool "create_phase" is called with playbook_id <MCP_SANDBOX_PB_ID> name "MCP Phase A" description "A"
    Then record id as <MCP_PHASE_A_PK>
    When MCP tool "create_phase" is called with playbook_id <MCP_SANDBOX_PB_ID> name "MCP Phase B" description "B"
    Then record id as <MCP_PHASE_B_PK>
    When MCP tool "list_phases" is called with playbook_id <MCP_SANDBOX_PB_ID>
    Then both phase ids present
    When MCP tool "get_phase" is called with phase_id <MCP_PHASE_A_PK>
    Then get succeeds
    When MCP tool "update_phase" is called with phase_id <MCP_PHASE_A_PK> description "Updated phase"
    Then update succeeds
    When MCP tool "reorder_phases" is called with playbook_id <MCP_SANDBOX_PB_ID> phase_order [<MCP_PHASE_B_PK>, <MCP_PHASE_A_PK>]
    Then reordered is true

    # --- Activities (6) ---
    When MCP tool "create_activity" is called with workflow_id <MCP_SANDBOX_WF_ID> name "MCP Act 1" guidance "g1" phase_id <MCP_PHASE_A_PK>
    Then record id as <MCP_ACT1_PK>
    When MCP tool "create_activity" is called with workflow_id <MCP_SANDBOX_WF_ID> name "MCP Act 2" guidance "g2" predecessor_id <MCP_ACT1_PK>
    Then record id as <MCP_ACT2_PK>
    When MCP tool "list_activities" is called with workflow_id <MCP_SANDBOX_WF_ID>
    Then count >= 2
    When MCP tool "get_activity" is called with activity_id <MCP_ACT1_PK>
    Then get succeeds
    When MCP tool "update_activity" is called with activity_id <MCP_ACT1_PK> guidance "Updated g1"
    Then update succeeds
    When MCP tool "set_predecessor" is called with activity_id <MCP_ACT2_PK> predecessor_id <MCP_ACT1_PK>
    Then updated is true

    # --- Skills (7) ---
    When MCP tool "create_skill" is called with playbook_id <MCP_SANDBOX_PB_ID> title "MCP Skill" content "c" capability_domain "GUI_FORM" technology_stack "React"
    Then record id as <MCP_SKILL_PK>
    When MCP tool "list_skills" is called with playbook_id <MCP_SANDBOX_PB_ID>
    Then includes <MCP_SKILL_PK>
    When MCP tool "get_skill" is called with skill_id <MCP_SKILL_PK>
    Then get succeeds
    When MCP tool "update_skill" is called with skill_id <MCP_SKILL_PK> content "Updated skill"
    Then update succeeds
    When MCP tool "link_skill_to_activity" is called with activity_id <MCP_ACT1_PK> skill_id <MCP_SKILL_PK>
    Then link succeeds
    When MCP tool "unlink_skill_from_activity" is called with activity_id <MCP_ACT1_PK>
    Then unlink succeeds
    When MCP tool "delete_skill" is called with skill_id <MCP_SKILL_PK>
    Then deleted is true

    # --- Agents (7) ---
    When MCP tool "create_agent" is called with playbook_id <MCP_SANDBOX_PB_ID> name "MCP Agent" description "d"
    Then record id as <MCP_AGENT_PK>
    When MCP tool "list_agents" is called with playbook_id <MCP_SANDBOX_PB_ID>
    Then includes <MCP_AGENT_PK>
    When MCP tool "get_agent" is called with agent_id <MCP_AGENT_PK>
    Then get succeeds
    When MCP tool "update_agent" is called with agent_id <MCP_AGENT_PK> description "Updated agent"
    Then update succeeds
    When MCP tool "link_agent_to_activity" is called with activity_id <MCP_ACT1_PK> agent_id <MCP_AGENT_PK>
    Then link succeeds
    When MCP tool "unlink_agent_from_activity" is called with activity_id <MCP_ACT1_PK>
    Then unlink succeeds
    When MCP tool "delete_agent" is called with agent_id <MCP_AGENT_PK>
    Then deleted is true

    # --- Artifacts (7) ---
    When MCP tool "create_artifact" is called with playbook_id <MCP_SANDBOX_PB_ID> produced_by_id <MCP_ACT1_PK> name "MCP Artifact" description "d" type "Document" is_required true
    Then record id as <MCP_ARTIFACT_PK>
    When MCP tool "list_artifacts" is called with playbook_id <MCP_SANDBOX_PB_ID>
    Then includes <MCP_ARTIFACT_PK>
    When MCP tool "get_artifact" is called with artifact_id <MCP_ARTIFACT_PK>
    Then get succeeds
    When MCP tool "update_artifact" is called with artifact_id <MCP_ARTIFACT_PK> description "Updated artifact"
    Then update succeeds
    When MCP tool "link_artifact_to_activity" is called with artifact_id <MCP_ARTIFACT_PK> activity_id <MCP_ACT2_PK> is_required true
    Then record input id as <MCP_ARTIFACT_INPUT_PK>
    When MCP tool "unlink_artifact_from_activity" is called with artifact_input_id <MCP_ARTIFACT_INPUT_PK>
    Then deleted is true
    When MCP tool "delete_artifact" is called with artifact_id <MCP_ARTIFACT_PK>
    Then deleted is true

    # --- Rules (6) ---
    When MCP tool "create_rule" is called with playbook_id <MCP_SANDBOX_PB_ID> title "MCP Rule" content "Rule content" always_apply true
    Then record id as <MCP_RULE_PK>
    When MCP tool "list_rules" is called with playbook_id <MCP_SANDBOX_PB_ID>
    Then includes <MCP_RULE_PK>
    When MCP tool "get_rule" is called with rule_id <MCP_RULE_PK>
    Then get succeeds
    When MCP tool "update_rule" is called with rule_id <MCP_RULE_PK> content "Updated rule"
    Then update succeeds
    When MCP tool "set_activity_rules" is called with activity_id <MCP_ACT1_PK> rule_ids [<MCP_RULE_PK>]
    Then succeeds
    When MCP tool "delete_rule" is called with rule_id <MCP_RULE_PK>
    Then deleted is true

    # --- Export / import / protocol (4) on sandbox workflow ---
    When MCP tool "export_workflow_to_local" is called with workflow_id <MCP_SANDBOX_WF_ID> target_directory "<MCP_EXPORT_DIR>/sandbox"
    Then export succeeds; record export subdirectory as <MCP_SANDBOX_EXPORT_SUBDIR>

    When MCP tool "import_workflow_from_local" is called with workflow_id <MCP_SANDBOX_WF_ID> source_directory "<MCP_SANDBOX_EXPORT_SUBDIR>" auto_apply false
    Then changes_count or diff present

    When MCP tool "apply_upload_protocol" is called with protocol_file "<MCP_SANDBOX_EXPORT_SUBDIR>/_Upload_Protocol.md"
    Then changes_applied or success response

    # create_pip_from_protocol requires a RELEASED playbook — skip on sandbox draft;
    # exercised after GUI release in UAT-06-02b or operator documents skip if protocol empty.

    # --- Teardown sandbox (delete tools) ---
    When MCP tool "delete_activity" is called for <MCP_ACT2_PK> then <MCP_ACT1_PK>
    Then each returns deleted true
    When MCP tool "delete_phase" is called for <MCP_PHASE_A_PK> and <MCP_PHASE_B_PK>
    Then deleted true
    When MCP tool "delete_workflow" is called with workflow_id <MCP_SANDBOX_WF_ID>
    Then deleted true
    When MCP tool "delete_playbook" is called with playbook_id <MCP_SANDBOX_PB_ID>
    Then deleted true

    # Record: all sandbox IDs consumed; GUI playbook untouched


  # ==========================================================================
  # Journey 5 — Release GUI playbook v1.0
  # User journey: Act 2 release flow
  # ==========================================================================

  -----------------------------------------------------------------------------
  @manual @uat @act-2-release
  Scenario: UAT-05-01 Release UAT Journey Playbook at v1.0 (GUI)
    Given uat_user is logged in and owns playbook <GUI_PLAYBOOK_ID>
    When uat_user navigates to "/playbooks/<GUI_PLAYBOOK_ID>/"
    And uat_user clicks data-testid "open-release-modal"
    Then data-testid "release-modal" is visible

    When uat_user fills data-testid "release-description-input" with "UAT release — v1.0 baseline for PIP testing."
    And uat_user clicks data-testid "release-confirm"
    Then data-testid "status-badge" shows Released
    And data-testid "version-badge" shows v1.0
    And data-testid "playbook-submit-pip" link or button is visible


  # ==========================================================================
  # Journey 6 — Act 9: PIPs via GUI + MCP (mixed accept/reject at admin)
  # ==========================================================================

  -----------------------------------------------------------------------------
  @manual @uat @act-9
  Scenario: UAT-06-01 Submit GUI PIP — ALTER Alpha (accept) + ADD Gamma (reject at admin)
    Given playbook <GUI_PLAYBOOK_ID> is Released v1.0 owned by uat_user
    When uat_user navigates to "/pips/create/?playbook=<GUI_PLAYBOOK_ID>"
    Then page contains data-testid "pip-create-page"

    When uat_user fills data-testid "pip-create-title" with "UAT GUI PIP — ALTER Alpha + ADD Gamma"
    And uat_user fills summary field name "summary" with "Browser PIP: accept Alpha alter; admin will reject Gamma add."
    And uat_user clicks data-testid "pip-create-submit"
    Then URL matches "/pips/<PIP_GUI_PK>/edit/"
    And page contains data-testid "pip-draft-editor"

    # Change 1 — ALTER Activity Alpha (target admin ACCEPT)
    When uat_user submits pip-add-change-form with change_type ALTER entity Activity target_id <ACT_ALPHA_PK> content:
      """
      ## Acceptance ALTER

      Updated guidance for Activity Alpha (browser UAT).
      """
    And uat_user clicks data-testid "pip-add-change-submit"
    Then row data-testid "pip-change-row-*" exists

    # Change 2 — ADD Activity Gamma (target admin REJECT — weak / invalid placement)
    When uat_user submits pip-add-change-form with change_type ADD entity Activity name "Activity Gamma" parent_workflow <GUI_WORKFLOW_ID> append_end checked content:
      """
      ## Gamma

      Proposed activity — admin UAT will reject this change.
      """
    And uat_user clicks data-testid "pip-add-change-submit"
    Then two change rows exist

    When MCP tool "preview_pip_diff" is called with pip_id <PIP_GUI_PK>
    Then preview rows or diff text returned

    When uat_user clicks data-testid "pip-submit-review"
    Then browser navigates to "/pips/<PIP_GUI_PK>/"
    And data-testid "pip-detail-page" shows status Submitted or Reviewed

    # Record: <PIP_GUI_PK>

  -----------------------------------------------------------------------------
  @manual @uat @act-9 @mcp-full
  Scenario: UAT-06-02 Submit MCP PIP — ALTER Beta + ADD MCP-Gamma (accept all at admin)
    Given user-mimir MCP as uat_user
    And playbook <GUI_PLAYBOOK_ID> is Released

    When MCP tool "list_playbooks" is called with status "released"
    Then list includes id <GUI_PLAYBOOK_ID>

    When MCP tool "list_workflows" is called with playbook_id <GUI_PLAYBOOK_ID>
    Then includes <GUI_WORKFLOW_ID>

    When MCP tool "list_activities" is called with workflow_id <GUI_WORKFLOW_ID>
    Then includes Activity Beta pk <ACT_BETA_PK>

    When MCP tool "create_pip" is called with:
      | argument    | value                                                        |
      | playbook_id | <GUI_PLAYBOOK_ID>                                            |
      | title       | UAT MCP PIP — ALTER Beta + ADD MCP-Gamma                     |
      | summary     | MCP PIP — both changes intended for admin accept.            |
    Then record pip id as <PIP_MCP_PK>

    When MCP tool "add_pip_change" is called with:
      | argument    | value                                           |
      | pip_id      | <PIP_MCP_PK>                                    |
      | change_type | ALTER                                           |
      | entity_type | Activity                                        |
      | target_id   | <ACT_BETA_PK>                                   |
      | content     | ## MCP ALTER\n\nBeta guidance updated via MCP.  |
    Then change_id returned

    When MCP tool "add_pip_change" is called with:
      | argument               | value                                         |
      | pip_id                 | <PIP_MCP_PK>                                  |
      | change_type            | ADD                                           |
      | entity_type            | Activity                                      |
      | name                   | Activity MCP-Gamma                            |
      | content                | ## MCP-Gamma\n\nNew activity via MCP append.  |
      | parent_workflow_id     | <GUI_WORKFLOW_ID>                             |
      | append_to_playbook_end | true                                          |
    Then second change_id returned

    When MCP tool "get_pip" is called with pip_id <PIP_MCP_PK>
    Then status is draft and changes length is 2

    When MCP tool "list_pips" is called with scope "mine"
    Then list includes pip id <PIP_MCP_PK>

    When MCP tool "submit_pip" is called with pip_id <PIP_MCP_PK>
    Then status becomes processing_galdr then reviewed (with GALDR_EAGER=True)

    # Record: <PIP_MCP_PK>

  -----------------------------------------------------------------------------
  @manual @uat @act-9 @mcp-full
  Scenario: UAT-06-03 Optional MCP draft PIP — remove_pip_change and cancel_pip
    When MCP tool "create_pip" is called with playbook_id <GUI_PLAYBOOK_ID> title "UAT disposable draft PIP" summary "Will be cancelled"
    Then record pip id as <PIP_DISPOSABLE_PK>

    When MCP tool "add_pip_change" is called with pip_id <PIP_DISPOSABLE_PK> change_type ADD entity_type Activity name "Throwaway" content "x" parent_workflow_id <GUI_WORKFLOW_ID> append_to_playbook_end true
    Then change_id returned as <DISPOSABLE_CHANGE_PK>

    When MCP tool "remove_pip_change" is called with pip_id <PIP_DISPOSABLE_PK> change_id <DISPOSABLE_CHANGE_PK>
    Then change removed

    When MCP tool "cancel_pip" is called with pip_id <PIP_DISPOSABLE_PK>
    Then pip is withdrawn or cancelled

  -----------------------------------------------------------------------------
  @manual @uat @act-9
  Scenario: UAT-06-04 Observe Galdr verdict badges on PIP detail pages (browser)
    Given uat_user or admin can view PIP detail pages

    # KNOWN ISSUE — Galdr background assessment:
    # With GALDR_EAGER=False (default), GaldrEngine.schedule starts a daemon thread after HTTP commit.
    # If the LLM client errors or times out, assess_sync may roll PIP back to Submitted with empty galdr_* fields.
    # Mitigations: GALDR_EAGER=True, working Galdr/LLM client, `python manage.py run_galdr <pip_id>`,
    # OR promote PIP status to Reviewed manually in Django admin before UAT-07-01.

    When uat_user navigates to "/pips/<PIP_MCP_PK>/"
    Then data-testid "pip-detail-page" shows status Reviewed (or Submitted if Galdr pending)
    And when Reviewed, data-testid "galdr-verdict-1" and "galdr-verdict-2" include ACCEPT if Galdr completed

    When uat_user navigates to "/pips/<PIP_GUI_PK>/"
    Then if Galdr completed, status is Reviewed and galdr badges visible
    But if Galdr rolled back to Submitted, data-testid "pip-detail-submit" offers re-submit
    And operator applies admin workaround before finalize if needed


  # ==========================================================================
  # Journey 7 — Admin review (mixed decisions) + GUI/MCP verification
  # User journey: Act 9 Django Admin + email notification
  # ==========================================================================

  -----------------------------------------------------------------------------
  @manual @uat @act-9-admin
  Scenario: UAT-07-01 Admin mixed decisions and finalize both PIPs
    Given actor admin is logged into Django admin "/admin/"

    When admin opens "/admin/methodology/processimprovementproposal/<PIP_GUI_PK>/change/"
    And admin sets PIP status to "Reviewed" if not already
    And admin sets inline PipChange row 1 admin_decision to Accept
    And admin sets inline PipChange row 2 admin_decision to Reject
    And admin clicks Save
    Then success message confirms change

    When admin opens "/admin/methodology/processimprovementproposal/<PIP_MCP_PK>/change/"
    And admin sets Admin decision Accept on each PipChange row
    And admin clicks Save
    Then success message confirms change

    When admin opens "/admin/methodology/processimprovementproposal/"
    And admin selects checkboxes for PIP rows <PIP_GUI_PK> and <PIP_MCP_PK>
    And admin selects action "Finalize reviewed PIPs (apply accepted changes + notify)"
    And admin clicks "Run"
    Then success lines include Finalised PIP-<PIP_GUI_PK> and Finalised PIP-<PIP_MCP_PK>

    When operator checks Gmail for "<UAT_EMAIL>"
    Then decision email(s) arrived for accepted/rejected changes (SES)

    # Version math (major bump per finalized PIP per pip_admin_service):
    # v1.0 → v2.0 after first finalize → v3.0 after second (order may vary by admin selection order).
    # GUI PIP partial: only ALTER Alpha applied; ADD Gamma rejected.
    # MCP PIP: ALTER Beta + ADD MCP-Gamma applied.

  -----------------------------------------------------------------------------
  @manual @uat @act-9-admin
  Scenario: UAT-07-02 Post-finalize GUI verification
    Given uat_user is logged in
    When uat_user navigates to "/playbooks/<GUI_PLAYBOOK_ID>/"
    Then data-testid "status-badge" shows Released
    And data-testid "version-badge" shows v2.0 or v3.0 (two major bumps from v1.0)
    And stat data-testid "stat-activities" shows 3 activities
      | expected name        | source                          |
      | Activity Alpha       | GUI — guidance altered via GUI PIP |
      | Activity Beta        | MCP PIP alter                   |
      | Activity MCP-Gamma   | MCP PIP add                     |
    And Activity Gamma is NOT present (GUI PIP add rejected)

    When uat_user navigates to "/pips/<PIP_GUI_PK>/"
    Then status banner indicates Accepted partial or Partially Accepted
    And data-testid "admin-verdict-1" shows ACCEPT for ALTER
    And data-testid "admin-verdict-2" shows REJECT for ADD

    When uat_user navigates to "/pips/<PIP_MCP_PK>/"
    Then status indicates Accepted
    And galdr and admin ACCEPT badges on both changes when Galdr ran

    When uat_user clicks data-testid "tab-history" on playbook detail
    Then version history references PIP #<PIP_GUI_PK> and/or PIP #<PIP_MCP_PK>

  -----------------------------------------------------------------------------
  @manual @uat @act-9-admin @mcp-full
  Scenario: UAT-07-03 Post-finalize MCP verification
    When MCP tool "list_playbooks" is called with status "released"
    Then entry for <GUI_PLAYBOOK_ID> shows updated version >= 2.0

    When MCP tool "list_activities" is called with workflow_id <GUI_WORKFLOW_ID>
    Then ordered names include "Activity Alpha", "Activity Beta", "Activity MCP-Gamma"
    And names do not include "Activity Gamma"

    When MCP tool "get_activity" is called with activity_id <ACT_ALPHA_PK>
    Then guidance includes "Acceptance ALTER" or browser UAT alter text

    When MCP tool "list_pips" is called with scope "mine" status filters including accepted
    Then includes <PIP_GUI_PK> and <PIP_MCP_PK> in terminal states

    When MCP tool "get_pip" is called with pip_id <PIP_MCP_PK>
    Then status is accepted and changes show admin decisions

    # Optional: create_pip_from_protocol after exporting released workflow markdown
    # When MCP tool "export_workflow_to_local" … then "create_pip_from_protocol" on protocol file
    # Then documents protocol-based PIP path (tool 51 / 61-tool checklist)


  # ==========================================================================
  # APPENDIX A — MCP Tool Checklist (61 tools, Django user-mimir / mcp_server)
  # Mark each [x] during UAT-04 / UAT-06 / UAT-07 replay.
  # ==========================================================================
  #
  # Playbooks (5):
  #   [ ] create_playbook          UAT-04-02
  #   [ ] list_playbooks           UAT-02-02, UAT-04-01, UAT-06-02, UAT-07-03
  #   [ ] get_playbook             UAT-04-01, UAT-04-02
  #   [ ] update_playbook          UAT-04-02
  #   [ ] delete_playbook          UAT-04-02 (sandbox only)
  #
  # Workflows (5):
  #   [ ] create_workflow          UAT-04-02
  #   [ ] list_workflows           UAT-04-01, UAT-04-02, UAT-06-02
  #   [ ] get_workflow             UAT-04-02
  #   [ ] update_workflow          UAT-04-02
  #   [ ] delete_workflow          UAT-04-02
  #
  # Activities (6):
  #   [ ] create_activity          UAT-04-02
  #   [ ] list_activities          UAT-04-01, UAT-04-02, UAT-06-02, UAT-07-03
  #   [ ] get_activity             UAT-04-01, UAT-04-02, UAT-07-03
  #   [ ] update_activity          UAT-04-01, UAT-04-02
  #   [ ] set_predecessor          UAT-04-01, UAT-04-02
  #   [ ] delete_activity          UAT-04-02
  #
  # Phases (6):
  #   [ ] create_phase             UAT-04-02
  #   [ ] list_phases              UAT-04-01, UAT-04-02
  #   [ ] get_phase                UAT-04-02
  #   [ ] update_phase             UAT-04-02
  #   [ ] reorder_phases           UAT-04-02
  #   [ ] delete_phase             UAT-04-02
  #
  # Skills (7):
  #   [ ] create_skill             UAT-04-02
  #   [ ] list_skills              UAT-04-01, UAT-04-02
  #   [ ] get_skill                UAT-04-02
  #   [ ] update_skill             UAT-04-02
  #   [ ] link_skill_to_activity   UAT-04-01, UAT-04-02
  #   [ ] unlink_skill_from_activity UAT-04-01, UAT-04-02
  #   [ ] delete_skill             UAT-04-02
  #
  # Agents (7):
  #   [ ] create_agent             UAT-04-02
  #   [ ] list_agents              UAT-04-01, UAT-04-02
  #   [ ] get_agent                UAT-04-02
  #   [ ] update_agent             UAT-04-02
  #   [ ] link_agent_to_activity   UAT-04-01, UAT-04-02
  #   [ ] unlink_agent_from_activity UAT-04-01, UAT-04-02
  #   [ ] delete_agent             UAT-04-02
  #
  # Artifacts (7):
  #   [ ] create_artifact          UAT-04-02
  #   [ ] list_artifacts           UAT-04-01, UAT-04-02
  #   [ ] get_artifact             UAT-04-02
  #   [ ] update_artifact          UAT-04-02
  #   [ ] link_artifact_to_activity UAT-04-01, UAT-04-02
  #   [ ] unlink_artifact_from_activity UAT-04-01, UAT-04-02
  #   [ ] delete_artifact          UAT-04-02
  #
  # Rules (6):
  #   [ ] create_rule              UAT-04-02
  #   [ ] list_rules               UAT-04-01, UAT-04-02
  #   [ ] get_rule                 UAT-04-02
  #   [ ] update_rule              UAT-04-02
  #   [ ] set_activity_rules       UAT-04-01, UAT-04-02
  #   [ ] delete_rule              UAT-04-02
  #
  # Export / import / protocol (4):
  #   [ ] export_workflow_to_local UAT-04-01, UAT-04-02
  #   [ ] import_workflow_from_local UAT-04-02
  #   [ ] apply_upload_protocol    UAT-04-02
  #   [ ] create_pip_from_protocol UAT-07-03 optional
  #
  # PIP lifecycle (8 — Django MCP only):
  #   [ ] list_pips                UAT-06-02
  #   [ ] get_pip                  UAT-06-02, UAT-07-03
  #   [ ] create_pip               UAT-06-02, UAT-06-03
  #   [ ] add_pip_change           UAT-06-02, UAT-06-03
  #   [ ] remove_pip_change        UAT-06-03
  #   [ ] submit_pip               UAT-06-02
  #   [ ] cancel_pip               UAT-06-03
  #   [ ] preview_pip_diff         UAT-06-01
  #
  # GUI-only coverage (not MCP tools): registration, profile token, wizard CRUDL,
  # release modal, PIP draft editor, Django admin finalize, Gmail verification.


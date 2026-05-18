@manual @uat @e2e-uat-flow
Feature: Mimir E2E UAT — ordered full-system journey (manual / Cursor replay)
  Single living spec for instructing Cursor (browser MCP + MCP tools) to click through
  the ENTIRE product in a fixed execution order.

  Rules for maintainers:
    - RUN SCENARIOS IN ORDER!!! This is LINEAR FLOW!
    - Each journey SHOULD tag its scenarios with a slice tag (e.g. @act-9) in addition to @manual @uat.
    - This file is NOT wired to pytest; `.feature` is ignored by python test discovery.

  Replay hints:
    - Prefer explicit URLs, data-testid selectors, and MCP tool names so an agent can follow mechanically.
    - Substitute placeholders (<PLAYBOOK_ID>, etc.) from the live DB before asserting IDs.

  Shared actors (reuse across journeys unless a scenario states otherwise):
    | persona   | credentials              | role                          |
    | admin     | admin / admin            | superuser, staff              |
    | testuser  | testuser / testpass123   | normal authenticated user     |

  Shared preconditions:
    - Dev server: http://127.0.0.1:8000 (or LIVE_SERVER_URL when replaying).
    - MCP (when used): user-mimir aligned with the user who owns visible released playbooks.

  ============================================================================
  # Journey 1 — Act 9: PIP round-trip (playbook release → GUI PIP → MCP PIP → Galdr → admin → verify)
  ============================================================================

  Concrete IDs in comments below are from one capture session; on a fresh DB re-resolve from UI/MCP.

  -----------------------------------------------------------------------------
  @manual @uat @act-9
  Scenario: ACT9-UAT-01 Admin creates and releases Test Playbook (setup)
    Given actor admin opens "/auth/user/login/"
    When admin fills username "admin" and password "admin"
    And admin submits the login form
    Then admin lands on the dashboard or home with session established

    When admin navigates to "/playbooks/create/"
    And admin fills playbook name "Test Playbook"
    And admin fills description "Act 9 E2E acceptance — workflows and activities for PIP testing."
    And admin selects category "Development" (or equivalent)
    And admin saves the new playbook draft

    When admin adds workflow "Test Workflow" with description "E2E workflow"
    And admin adds activity "Activity Alpha" with guidance under that workflow
    And admin adds activity "Activity Beta" with guidance under that workflow

    When admin opens the playbook release flow and submits release with note "Act 9 E2E — release Test Playbook v1.0"
    Then playbook detail shows status "Released" and version "v1.0"
    And playbook detail shows link or button with data-testid "playbook-submit-pip" (Submit PIP)

    # Record captured IDs for later scenarios (example session):
    # playbook_id=12, workflow_id=25, activity Alpha pk=126, activity Beta pk=127

  -----------------------------------------------------------------------------
  @manual @uat @act-9
  Scenario: ACT9-UAT-02 testuser submits first PIP via browser UI (ALTER + ADD)
    Given playbook "Test Playbook" is Released v1.0 and readable by testuser
    # If testuser gets 403 on playbook detail, staff must assign playbook ownership to testuser
    # (e.g. Django admin Playbook change → Author = testuser), then revert to admin later for MCP visibility.

    Given actor testuser opens "/auth/user/login/"
    When testuser fills username "testuser" and password "testpass123"
    And testuser submits the login form
    Then testuser has an authenticated session

    # Prefer deep-link if "Submit PIP" click does not navigate under automation:
    When testuser navigates to "/pips/create/?playbook=<PLAYBOOK_ID>"
    Then page contains data-testid "pip-create-page"

    When testuser fills title "Act 9 acceptance — UI draft ALTER Alpha + ADD Gamma"
    And testuser fills summary "Browser acceptance PIP for playbook 12."
    And testuser clicks button data-testid "pip-create-submit" ("Save draft & add changes")
    Then browser URL matches "/pips/<PIP_UI_PK>/edit/"
    And page contains data-testid "pip-draft-editor"

    # First change: ALTER Activity Alpha (example target pk 126)
    When testuser selects change type "ALTER" and entity "Activity" on form data-testid "pip-add-change-form"
    And testuser fills guidance textarea (name "content") with:
      """
      ## Acceptance ALTER

      Updated guidance for Activity Alpha (browser).
      """
    And testuser fills target activity id "126" (field name "target_id")
    And testuser clicks data-testid "pip-add-change-submit"
    Then table shows a change row data-testid matching "pip-change-row-*"

    # Second change: ADD Activity Gamma, append to workflow (example workflow id 25)
    When testuser selects change type "ADD" and entity "Activity"
    And testuser fills name "Activity Gamma"
    And testuser fills guidance with:
      """
      ## Gamma

      New activity appended via browser acceptance.
      """
    And testuser selects parent workflow "Test Workflow" (select name "parent_workflow", value workflow pk)
    And testuser checks "Append to end of parent / workflow" (name "append_end")
    And testuser clicks data-testid "pip-add-change-submit"
    Then two change rows exist with Remove actions

    When testuser clicks button data-testid "pip-submit-review" inside form data-testid "pip-submit-form"
    Then browser navigates to "/pips/<PIP_UI_PK>/"
    And page data-testid "pip-detail-page" shows status badge "Submitted"
    # Record PIP_UI_PK (example: 3)

  -----------------------------------------------------------------------------
  @manual @uat @act-9
  Scenario: ACT9-UAT-03 Admin creates second PIP via Mimir MCP tools
    Given MCP user-mimir runs as admin and playbook id <PLAYBOOK_ID> is Released and listed by MCP
    # If list_playbooks(released) omits the playbook, Author must be admin (see ACT9-UAT-02 note).

    When MCP tool "list_playbooks" is called with status "released"
    Then result includes playbook id <PLAYBOOK_ID> named "Test Playbook"

    When MCP tool "list_workflows" is called with playbook_id <PLAYBOOK_ID>
    Then result includes workflow id <WORKFLOW_ID> named "Test Workflow"

    When MCP tool "list_activities" is called with workflow_id <WORKFLOW_ID>
    Then result includes Activity Beta with pk <ACTIVITY_BETA_PK> (example 127)

    When MCP tool "create_pip" is called with:
      | argument    | value                                                                 |
      | playbook_id | <PLAYBOOK_ID>                                                         |
      | title       | Act 9 acceptance — MCP ALTER Beta + ADD MCP-Gamma                  |
      | summary     | Second PIP via Mimir MCP tools.                                       |
    Then response contains new pip id <PIP_MCP_PK> (example 4)

    When MCP tool "add_pip_change" is called with:
      | argument    | value                                                                 |
      | pip_id      | <PIP_MCP_PK>                                                          |
      | change_type | ALTER                                                                 |
      | entity_type | Activity                                                              |
      | target_id   | <ACTIVITY_BETA_PK>                                                    |
      | content     | ## MCP ALTER\n\nBeta guidance updated via MCP.                      |
    Then change_id is returned

    When MCP tool "add_pip_change" is called with:
      | argument               | value                                                        |
      | pip_id                 | <PIP_MCP_PK>                                                 |
      | change_type            | ADD                                                          |
      | entity_type            | Activity                                                     |
      | name                   | Activity MCP-Gamma                                           |
      | content                | ## MCP-Gamma\n\nNew activity via MCP append.                 |
      | parent_workflow_id     | <WORKFLOW_ID>                                                |
      | append_to_playbook_end | true                                                         |
    Then second change_id is returned

    When MCP tool "submit_pip" is called with pip_id <PIP_MCP_PK>
    Then pip status becomes "processing_galdr" then stabilizes to "reviewed"
    And each change shows galdr_recommendation ACCEPT (stub integration path)

  -----------------------------------------------------------------------------
  @manual @uat @act-9
  Scenario: ACT9-UAT-04 Observe Galdr verdict badges on PIP detail (browser)
    Given actor admin is logged in

    # KNOWN ISSUE — Galdr background assessment:
    # With GALDR_EAGER=False (default), GaldrEngine.schedule starts a daemon thread after HTTP commit.
    # If the LLM client errors or times out, assess_sync calls _mark_submitted_retry and the PIP returns
    # to status "Submitted" with empty galdr_* fields on changes — same as first-run UI PIP in some sessions.
    # Mitigations for replay: set GALDR_EAGER=True in settings for synchronous assessment in-process,
    # configure a working Galdr/LLM client, run management command run_galdr <pip_id>, OR promote the PIP to
    # "Reviewed" manually in Django admin (operator workaround — document if used).

    When admin navigates to "/pips/<PIP_MCP_PK>/"
    Then page data-testid "pip-detail-page" shows status "Reviewed" or "Accepted" (after finalization)
    And accordion item data-testid "pip-change-1" shows badge text including "ACCEPT" when Galdr completed
    And accordion item data-testid "pip-change-2" shows badge text including "ACCEPT" when Galdr completed
    And optional: data-testid "galdr-verdict-1" / "galdr-reason-1" appear per templates/pips/detail.html

    When admin navigates to "/pips/<PIP_UI_PK>/"
    Then if Galdr succeeded without manual intervention, status is "Reviewed" and ACCEPT badges appear
    But if Galdr rolled back to Submitted, detail shows data-testid "pip-detail-submit" as "Re-submit for Galdr review"
    And operator may execute Django admin workaround documented in ACT9-UAT-05 before finalize

  -----------------------------------------------------------------------------
  @manual @uat @act-9
  Scenario: ACT9-UAT-05 Admin sets admin decisions and finalises both PIPs
    Given actor admin is logged into Django admin "/admin/"

    When admin opens "/admin/methodology/processimprovementproposal/<PIP_UI_PK>/change/"
    And admin sets PIP status to "Reviewed" if not already (needed when Galdr did not persist Reviewed)
    And admin sets Admin decision "Accept" on each inline PipChange row for this PIP
    And admin clicks Save
    Then success message confirms the proposal was changed

    When admin opens "/admin/methodology/processimprovementproposal/<PIP_MCP_PK>/change/"
    And admin sets Admin decision "Accept" on each inline PipChange row (Galdr may already show Accept)
    And admin clicks Save
    Then success message confirms the proposal was changed

    When admin opens "/admin/methodology/processimprovementproposal/"
    And admin selects checkboxes for PIP rows <PIP_UI_PK> and <PIP_MCP_PK>
    And admin selects action "Finalize reviewed PIPs (apply accepted changes + notify)"
    And admin clicks "Run"
    Then admin sees success lines like Finalised PIP-<PIP_UI_PK> and Finalised PIP-<PIP_MCP_PK>

    # Finalize applies accepted changes in processing order; version history should list both bumps.

  -----------------------------------------------------------------------------
  @manual @uat @act-9
  Scenario: ACT9-UAT-06 Verify Released playbook v3.0 and four activities
    Given actor admin is logged in

    When admin navigates to "/playbooks/<PLAYBOOK_ID>/"
    Then heading shows "Released v3.0" (two accepted PIPs bumped major twice from v1.0)
    And quick stats show "4 Activities"
    And version history lists entries referencing PIP #<PIP_MCP_PK> (v2.0) and PIP #<PIP_UI_PK> (v3.0)

    When admin navigates to "/pips/<PIP_UI_PK>/"
    Then status badge shows "Accepted"
    And change headings show "ADMIN ACCEPT" for both rows (Galdr badges absent if Galdr never wrote recommendations)

    When admin navigates to "/pips/<PIP_MCP_PK>/"
    Then status badge shows "Accepted"
    And accordion headers include Galdr "ACCEPT" and "ADMIN ACCEPT" per change

    When MCP tool "list_activities" is called with workflow_id <WORKFLOW_ID>
    Then ordered activity names include "Activity Alpha", "Activity Beta", "Activity MCP-Gamma", "Activity Gamma"

  # ============================================================================
  # Journey N — (append next ordered product-wide scenario block below)
  # ============================================================================

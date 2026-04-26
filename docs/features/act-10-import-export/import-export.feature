Feature: FOB-IMPORT-EXPORT-1 Import and Export Playbooks
  As a methodology author (Maria)
  I want to export a playbook as a self-contained JSON file and import it on any Mimir instance
  So that I can move playbooks between environments without sharing a database

  # PRIMARY USE CASE — Cross-Instance Migration
  # Maria runs Mimir on two machines: a dev instance (laptop) and a shared team instance.
  # She builds a playbook on the dev instance and wants it on the team instance.
  # The only connection between the two is a file she can copy.
  # The exported JSON must be fully self-contained — importing it on a fresh Mimir instance
  # with an empty database must produce an identical, fully functional playbook.
  # No IDs, no DB state, no user accounts transfer. Only the content transfers.

  Status: 🔲 NOT STARTED
  Branch: feature/import-export
  Related: act-3-workflows (MCP-level export/import — see workflows-export-import.feature)

  # JSON EXPORT SCHEMA
  # A valid export file has the following top-level structure:
  #
  # {
  #   "mimir_version": "1.0",
  #   "exported_at": "<ISO8601>",
  #   "playbook": {
  #     "name": "...", "description": "...", "category": "...",
  #     "tags": [...], "visibility": "...", "status": "...", "version": "...",
  #     "phases":    [{ "ref": "phase-1", "name": "...", "description": "...", "order": 1 }],
  #     "agents":    [{ "ref": "agent-1", "name": "...", "description": "..." }],
  #     "skills":    [{ "ref": "skill-1", "title": "...", "capability_domain": "...",
  #                     "technology_stack": "...", "content": "..." }],
  #     "rules":     [{ "ref": "rule-1", "title": "...", "slug": "...",
  #                     "content": "...", "always_apply": true }],
  #     "workflows": [{
  #       "ref": "workflow-1", "name": "...", "description": "...",
  #       "abbreviation": "...", "order": 1,
  #       "activities": [{
  #         "ref": "activity-1", "name": "...", "guidance": "...", "order": 1,
  #         "phase_ref": "phase-1" | null,
  #         "predecessor_ref": "activity-N" | null,
  #         "agent_ref": "agent-1" | null,
  #         "skill_ref": "skill-1" | null,
  #         "rules": ["rule-1", "rule-2"],
  #         "artifacts_consumed": [{ "artifact_ref": "artifact-2", "is_required": true }]
  #       }]
  #     }],
  #     "artifacts": [{
  #       "ref": "artifact-1", "name": "...", "description": "...",
  #       "type": "...", "is_required": true,
  #       "produced_by_ref": "activity-1"
  #     }]
  #   }
  # }
  #
  # IMPORTANT: "ref" values are stable string identifiers within the export file.
  # They are NOT database PKs. They survive re-import with new PKs.
  # Fields excluded from export: id, source, author, created_at, updated_at.
  # status and version are preserved from the source — an imported released v1.2 playbook
  # arrives as released v1.2. The importing user becomes the author on the new instance.

  Background:
    Given Maria is authenticated in FOB
    And Maria owns draft playbook "React Frontend Dev" (version=0.3)
    And the playbook has:
      | entity     | count |
      | workflows  |     2 |
      | activities |     6 |
      | agents     |     1 |
      | skills     |     2 |
      | phases     |     1 |
      | rules      |     3 |
      | artifacts  |     2 |
    And activity "Create Mockup" has predecessor "Define Props"
    And activity "Implement Component" is linked to agent "Code Reviewer",
        skill "React Dev", phase "Execution", and rules "pytest-first" and "ruff-format"
    And artifact "Design Spec" is produced by "Define Props" and consumed by "Implement Component"
    And artifact "Component Code" is produced by "Implement Component"

  # ============================================================================
  # EXPORT
  # ============================================================================

  Scenario: FOB-IMPORT-EXPORT-1-01 Export triggers JSON download
    Given Maria is viewing "React Frontend Dev" playbook detail page
    When she clicks the [Export as JSON] button (data-testid="export-playbook-json")
    Then the browser downloads "react-frontend-dev.json"
    And the response has Content-Type "application/json"
    And the response has Content-Disposition header containing "react-frontend-dev.json"

  Scenario: FOB-IMPORT-EXPORT-1-02 Exported JSON contains correct top-level structure
    Given Maria has exported "React Frontend Dev" as JSON
    When the file is parsed
    Then it contains top-level fields:
      | field         | type    |
      | mimir_version | string  |
      | exported_at   | string  |
      | playbook      | object  |
    And mimir_version equals "1.0"
    And exported_at is a valid ISO8601 timestamp
    And the playbook object contains:
      | field   |
      | status  |
      | version |
    And the playbook object does NOT contain:
      | field  |
      | id     |
      | source |
      | author |

  Scenario: FOB-IMPORT-EXPORT-1-03 Exported JSON contains all playbook entities
    Given Maria has exported "React Frontend Dev" as JSON
    When the file is parsed
    Then playbook.phases contains 1 entry with fields: ref, name, description, order
    And playbook.agents contains 1 entry with fields: ref, name, description
    And playbook.skills contains 2 entries each with fields: ref, title, capability_domain, technology_stack, content
    And playbook.rules contains 3 entries each with fields: ref, title, slug, content, always_apply
    And playbook.workflows contains 2 entries each with fields: ref, name, description, abbreviation, order, activities
    And playbook.artifacts contains 2 entries each with fields: ref, name, description, type, is_required, produced_by_ref
    And the total activity count across all workflows is 6

  Scenario: FOB-IMPORT-EXPORT-1-04 Exported JSON preserves predecessor chain
    Given the workflow contains:
      | activity name     | predecessor      |
      | Define Props      | (none)           |
      | Create Mockup     | Define Props     |
      | Write Component   | Create Mockup    |
    When Maria exports the playbook as JSON
    Then the activities in the JSON contain:
      | name            | predecessor_ref         |
      | Define Props    | null                    |
      | Create Mockup   | (ref of Define Props)   |
      | Write Component | (ref of Create Mockup)  |
    And each predecessor_ref value matches the "ref" field of the referenced activity

  Scenario: FOB-IMPORT-EXPORT-1-05 Exported JSON preserves all entity links on activity
    Given activity "Implement Component" is linked to agent "Code Reviewer",
          skill "React Dev", phase "Execution", and rules "pytest-first" and "ruff-format"
    When Maria exports the playbook as JSON
    Then the activity entry contains:
      | field       | value                                      |
      | agent_ref   | (ref matching "Code Reviewer" in agents)   |
      | skill_ref   | (ref matching "React Dev" in skills)       |
      | phase_ref   | (ref matching "Execution" in phases)       |
      | rules       | [ref of pytest-first, ref of ruff-format]  |

  Scenario: FOB-IMPORT-EXPORT-1-06 Export of released playbook is permitted
    Given "React Frontend Dev" has status "released" (version 1.2)
    When Maria exports it as JSON
    Then the download succeeds
    And the exported JSON contains status "released" and version "1.2"

  Scenario: FOB-IMPORT-EXPORT-1-07 Export button appears on playbook detail for all statuses
    Given Maria is viewing a playbook with status "<status>"
    Then the action menu contains [Export as JSON] with data-testid="export-playbook-json"
    Examples:
      | status   |
      | draft    |
      | released |

  # ============================================================================
  # IMPORT
  # ============================================================================

  Scenario: FOB-IMPORT-EXPORT-1-08 Import valid JSON creates new draft playbook
    Given Maria is on the playbooks list
    And no playbook named "Team Playbook" exists
    When she clicks [Import Playbook] (data-testid="import-playbook-btn")
    And she selects a valid "team-playbook.json" file (playbook name: "Team Playbook") (data-testid="import-file-input")
    And she clicks [Import] (data-testid="import-submit-btn")
    Then a new playbook is created with:
      | field   | value                      |
      | status  | (preserved from JSON)      |
      | version | (preserved from JSON)      |
      | author  | Maria                      |
      | source  | imported                   |
    And she sees success notification "Playbook imported successfully"
    And she is redirected to the new playbook detail page

  Scenario: FOB-IMPORT-EXPORT-1-09 Import recreates all entities with correct counts
    Given a valid JSON export file whose playbook name does not exist in the system
    And the file contains:
      | entity     | count |
      | workflows  |     2 |
      | activities |     6 |
      | agents     |     1 |
      | skills     |     2 |
      | phases     |     1 |
      | rules      |     3 |
      | artifacts  |     2 |
    When Maria imports the file
    Then the imported playbook contains:
      | entity     | count |
      | workflows  |     2 |
      | activities |     6 |
      | agents     |     1 |
      | skills     |     2 |
      | phases     |     1 |
      | rules      |     3 |
      | artifacts  |     2 |
    And all entity IDs are new database IDs (not the original exported IDs)

  Scenario: FOB-IMPORT-EXPORT-1-10 Import preserves all relationships
    Given Maria has exported "React Frontend Dev" to "react-frontend-dev.json"
    When she imports "react-frontend-dev.json" and clicks [Replace] in the conflict dialog
    Then all activity predecessor chains are intact
    And all activity-to-agent links are intact
    And all activity-to-skill links are intact
    And all activity-to-phase links are intact
    And all activity-to-rule M2M links are intact
    And all artifact produced_by activity links are intact
    And all artifact consumed_by (ArtifactInput) links are intact

  Scenario: FOB-IMPORT-EXPORT-1-11 Round-trip fidelity
    Given Maria exports "React Frontend Dev" to "export-v1.json"
    When she imports "export-v1.json" and clicks [Replace] in the conflict dialog
    Then the imported playbook is named "React Frontend Dev" (original name preserved)
    When she exports it to "export-v2.json"
    Then "export-v1.json" and "export-v2.json" are structurally identical
    Except for the "exported_at" timestamp

  # ============================================================================
  # CROSS-INSTANCE MIGRATION — the primary use case for this entire feature
  # ============================================================================

  Scenario: FOB-IMPORT-EXPORT-1-12 Cross-instance migration produces a fully functional playbook
    # This scenario is the definition of done for the whole feature.
    # Instance A and Instance B share no database, no user accounts, no IDs.
    # The JSON file is the only thing that moves between them.
    Given Maria has playbook "GDD Playbook" on Instance A containing:
      | entity     | count |
      | workflows  |     5 |
      | activities |    23 |
      | agents     |     2 |
      | skills     |     3 |
      | phases     |     4 |
      | rules      |     4 |
      | artifacts  |     3 |
    And activity predecessor chains, agent/skill/phase links, and rule M2M links are all set
    When she exports "GDD Playbook" as JSON on Instance A
    And she copies "gdd-playbook.json" to Instance B (a separate Mimir installation)
    And she imports "gdd-playbook.json" on Instance B
    Then the playbook exists on Instance B with:
      | entity     | count |
      | workflows  |     5 |
      | activities |    23 |
      | agents     |     2 |
      | skills     |     3 |
      | phases     |     4 |
      | rules      |     4 |
      | artifacts  |     3 |
    And all predecessor chains are intact on Instance B
    And all agent, skill, phase, and rule links are intact on Instance B
    And all entity IDs on Instance B are different from the IDs on Instance A
    And the playbook has no reference to any database state from Instance A
    And the playbook status and version on Instance B match those from the exported JSON
    And the playbook source is "imported" on Instance B
    And the playbook author is Maria's account on Instance B

  # ============================================================================
  # CONFLICT RESOLUTION
  # ============================================================================

  Scenario: FOB-IMPORT-EXPORT-1-13 Import conflict dialog appears on name collision
    Given a playbook named "React Frontend Dev" already exists
    When Maria imports a JSON file with playbook name "React Frontend Dev"
    Then she sees a conflict dialog with:
      | option      | data-testid                  |
      | Rename      | import-conflict-rename       |
      | Replace     | import-conflict-replace      |
      | Add Missing | import-conflict-add-missing  |
      | Cancel      | import-conflict-cancel       |

  Scenario: FOB-IMPORT-EXPORT-1-14 Import conflict — rename creates with modified name
    Given a playbook named "React Frontend Dev" already exists
    When Maria imports a JSON file named "React Frontend Dev"
    And she clicks [Rename] in the conflict dialog
    Then a new playbook "React Frontend Dev (imported)" is created with status and version preserved from the JSON
    And the new playbook has source "imported"
    And the original playbook is unchanged

  Scenario: FOB-IMPORT-EXPORT-1-15 Import conflict — replace deletes draft and imports
    Given a DRAFT playbook named "React Frontend Dev" (id=1) already exists
    When Maria imports a JSON also named "React Frontend Dev"
    And she clicks [Replace] in the conflict dialog
    Then she sees confirmation: "This will permanently delete the existing playbook. Continue?"
    When she confirms
    Then the original playbook (id=1) and all its content are deleted
    And the new playbook is created from the imported JSON with status and version preserved from the JSON, and source "imported"
    And she sees success notification
    And the deletion and creation are a single atomic operation: if the import fails, the original playbook is preserved

  Scenario: FOB-IMPORT-EXPORT-1-16 Import conflict — replace blocked for released playbook
    Given a RELEASED playbook named "React Frontend Dev" already exists
    When Maria imports a JSON also named "React Frontend Dev"
    And she clicks [Replace] in the conflict dialog
    Then she sees error "Cannot replace a released playbook. Choose Rename or Cancel."
    And the released playbook is unchanged

  Scenario: FOB-IMPORT-EXPORT-1-17 Import conflict — cancel leaves everything unchanged
    Given a playbook named "React Frontend Dev" already exists
    When Maria imports a JSON also named "React Frontend Dev"
    And she clicks [Cancel] in the conflict dialog
    Then no new playbook is created
    And the original playbook is unchanged
    And she is returned to the import dialog

  Scenario: FOB-IMPORT-EXPORT-1-18 Import conflict — add missing adds only absent entities
    Given a playbook named "React Frontend Dev" already exists containing 2 workflows and 6 activities
    When Maria imports a JSON also named "React Frontend Dev" containing 3 workflows and 9 activities
    And she clicks [Add Missing] in the conflict dialog
    Then the 2 existing workflows are unchanged
    And the 1 new workflow from the JSON is added to the existing playbook
    And the 6 existing activities are unchanged
    And the 3 new activities from the JSON are added
    And no existing entity is deleted or overwritten
    And she sees success notification "Playbook updated with missing entities"
    And if the operation fails, no new entities are added and the existing playbook is unchanged

  # ============================================================================
  # VALIDATION AND ERRORS
  # ============================================================================

  Scenario: FOB-IMPORT-EXPORT-1-19 Import invalid JSON syntax
    Given Maria selects a file containing malformed JSON (e.g. missing closing brace)
    When she submits the import
    Then she sees error "Invalid file: could not be parsed as JSON"
    And no playbook is created

  Scenario: FOB-IMPORT-EXPORT-1-20 Import JSON missing required playbook.name
    Given Maria selects a JSON file where playbook.name is absent
    When she submits the import
    Then she sees validation error "Missing required field: playbook.name"
    And no playbook is created

  Scenario: FOB-IMPORT-EXPORT-1-21 Import JSON with broken predecessor reference
    Given Maria selects a JSON where activity "Create Mockup" has predecessor_ref "activity-99"
    But no activity with ref "activity-99" exists in the file
    When she submits the import
    Then she sees validation error:
      "Activity 'Create Mockup' references unknown predecessor 'activity-99'"
    And no playbook is created
    And no partial entities remain in the database

  Scenario: FOB-IMPORT-EXPORT-1-22 Import non-JSON file type
    Given Maria selects a file "document.pdf"
    When she submits the import
    Then she sees error "Unsupported file type. Please upload a .json file"
    And no playbook is created

  Scenario: FOB-IMPORT-EXPORT-1-23 Import JSON with unknown mimir_version
    Given Maria selects a JSON file with mimir_version "99.0"
    When she submits the import
    Then she sees error "Unsupported export version: 99.0. This instance supports version 1.0."
    And no playbook is created

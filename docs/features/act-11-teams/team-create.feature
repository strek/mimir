Feature: FOB-TEAMS-CREATE-1 Create Team
  As a methodology author (Maria)
  I want to create a new team with a name, description, visibility, join policy, and category
  So that I can organize my professional network and share playbooks with the right collaborators

  Background:
    Given Maria is authenticated in FOB

  # ── Entry points ──────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-CREATE-01 Create Team and Browse Teams buttons visible on dashboard
    Given Maria is on the FOB Dashboard
    Then a [Create Team] button is visible (data-testid="create-team-btn")
    And a [Browse Teams] button is visible (data-testid="browse-teams-btn")

  Scenario: FOB-TEAMS-CREATE-02 Click Create Team opens the create form
    Given Maria is on the FOB Dashboard
    When she clicks [Create Team]
    Then she is redirected to /teams/create/
    And the page title reads "Create Team"
    And data-testid="team-create-form" is present
    And the form contains fields:
      | field       | type     |
      | Team Name   | text     |
      | Description | textarea |
      | Visibility  | select   |
      | Join Policy | select   |
      | Category    | select   |
    And the [Create Team] submit button (data-testid="team-create-submit") is present
    And a [Cancel] link is present

  # ── Happy path ─────────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-CREATE-03 Create a public team requiring approval
    Given Maria is on /teams/create/
    When she fills in:
      | field       | value                                            |
      | Team Name   | UX                                               |
      | Description | User Experience methodologies and best practices |
      | Visibility  | Public                                           |
      | Join Policy | Requires Approval                                |
      | Category    | Design                                           |
    And she clicks [Create Team]
    Then she is redirected to the team detail page at /teams/<pk>/
    And a success banner reads "Team 'UX' created successfully."
    And data-testid="team-detail-page" is present
    And the team info card shows:
      | field       | value                                            |
      | Name        | UX                                               |
      | Visibility  | Public                                           |
      | Join Policy | Requires Approval                                |
      | Category    | Design                                           |
    And Maria is listed as "Admin" in the Members tab

  Scenario: FOB-TEAMS-CREATE-04 Create a hidden invite-only team
    Given Maria is on /teams/create/
    When she fills in:
      | field       | value                                       |
      | Team Name   | Acme, INC                                   |
      | Description | UX Consulting services for Acme Corporation |
      | Visibility  | Hidden                                      |
      | Join Policy | Invite Only                                 |
      | Category    | Private                                     |
    And she clicks [Create Team]
    Then she is redirected to /teams/<pk>/
    And a success banner reads "Team 'Acme, INC' created successfully."
    And the team is NOT listed in the public team browser (/teams/)
    And Maria is listed as "Admin" in the Members tab

  Scenario: FOB-TEAMS-CREATE-05 Cancel returns to dashboard without creating a team
    Given Maria is on /teams/create/
    When she clicks [Cancel]
    Then she is redirected to the FOB Dashboard
    And no new team is created

  # ── Validation ────────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-CREATE-06 Team Name is required
    Given Maria is on /teams/create/
    When she leaves Team Name blank and clicks [Create Team]
    Then an inline error appears on the Team Name field: "Team name is required."
    And she stays on /teams/create/

  Scenario: FOB-TEAMS-CREATE-07 Team Name must be unique
    Given a team named "UX" already exists
    And Maria is on /teams/create/
    When she enters "UX" as Team Name and clicks [Create Team]
    Then an inline error appears on the Team Name field: "A team with this name already exists."
    And she stays on /teams/create/

  Scenario: FOB-TEAMS-CREATE-08 Team Name cannot exceed 100 characters
    Given Maria is on /teams/create/
    When she enters a Team Name of 101 characters and clicks [Create Team]
    Then an inline error appears on the Team Name field: "Team name cannot exceed 100 characters."
    And she stays on /teams/create/

  # ── Access control ────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-CREATE-09 Unauthenticated user is redirected to login
    Given Maria is not logged in
    When she navigates to /teams/create/
    Then she is redirected to the login page
    And after login she is returned to /teams/create/

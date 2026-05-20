Feature: FOB-TEAMS-MANAGE-1 Manage Team (Admin Operations)
  As a team admin (Maria)
  I want to approve join requests, manage members, configure settings, and curate playbooks
  So that I can maintain a high-quality collaborative community for my UX practice

  Background:
    Given Maria is authenticated in FOB
    And Maria is the admin of the "UX" team with:
      | field       | value                                            |
      | Description | User Experience methodologies and best practices |
      | Visibility  | Public                                           |
      | Join Policy | Requires Approval                                |
      | Category    | Design                                           |
    And the "UX" team has members:
      | name      | username | role   |
      | Mike Chen | mchen    | member |
      | Tom Lee   | tlee     | member |

  # ── Entry point ───────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-MANAGE-01 Open team management panel from team detail page
    Given Maria is on the "UX" team detail page
    When she clicks [Manage Team] (data-testid="team-manage-btn")
    Then she is redirected to /teams/<pk>/manage/
    And the page title reads "Manage Team: UX"
    And data-testid="team-manage-page" is present
    And the page shows tabs: Members, Join Requests, Playbooks, Settings

  # ── Join Requests tab ─────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-MANAGE-02 Join Requests tab shows all pending requests
    Given the following users have pending join requests for "UX":
      | name      | username | requested_at       |
      | Alice Roy | aroy     | 2026-05-19 10:00   |
      | Bob Tan   | btan     | 2026-05-20 08:30   |
    When Maria is on the "Join Requests" tab (data-testid="team-tab-join-requests")
    Then she sees a table with rows for Alice Roy and Bob Tan
    And each row shows: Name, Username, Requested At, [Approve] button, [Reject] button

  Scenario: FOB-TEAMS-MANAGE-03 Approve a join request adds the user as a member
    Given Alice Roy has a pending join request for "UX"
    And Maria is on the Join Requests tab
    When she clicks [Approve] next to Alice Roy
    Then Alice Roy is added to the "UX" team with role "member"
    And Alice Roy receives a notification "Your request to join 'UX' was approved."
    And Alice Roy's row is removed from the Join Requests tab
    And Alice Roy now appears in the Members tab

  Scenario: FOB-TEAMS-MANAGE-04 Reject a join request does not add the user
    Given Alice Roy has a pending join request for "UX"
    And Maria is on the Join Requests tab
    When she clicks [Reject] next to Alice Roy
    Then Alice Roy is NOT added to the "UX" team
    And Alice Roy receives a notification "Your request to join 'UX' was not approved."
    And Alice Roy's row is removed from the Join Requests tab

  Scenario: FOB-TEAMS-MANAGE-05 Join Requests tab shows empty state when there are none
    Given no pending join requests exist for "UX"
    When Maria is on the Join Requests tab
    Then she sees "No pending join requests." (data-testid="join-requests-empty")

  # ── Members tab ───────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-MANAGE-06 Members tab shows all team members with actions
    Given Maria is on /teams/<pk>/manage/
    When she clicks the "Members" tab (data-testid="team-tab-members")
    Then she sees a table with columns: Name, Username, Role, Joined, Actions
    And Mike Chen appears with role "member" and a [Remove] button
    And Tom Lee appears with role "member" and a [Remove] button
    And Maria herself appears with role "Admin" (no [Remove] button for self)

  Scenario: FOB-TEAMS-MANAGE-07 Remove a member from the team
    Given Maria is on the Members tab
    When she clicks [Remove] next to Mike Chen
    Then a confirmation dialog appears:
      """
      Remove Mike Chen from 'UX'? They will lose access to all team playbooks.
      """
    When she confirms
    Then Mike Chen is removed from the "UX" team
    And Mike Chen receives a notification "You have been removed from the 'UX' team."
    And Mike Chen's own playbooks are NOT deleted or affected
    And Mike Chen no longer appears in the Members tab

  Scenario: FOB-TEAMS-MANAGE-08 Removed member loses access to team playbooks
    Given Mike Chen has access to "UX Research Methods" as a "UX" team member
    When Maria removes Mike Chen from "UX"
    Then Mike Chen can no longer view "UX Research Methods" via the GUI
    And Mike Chen can no longer access it via MCP

  Scenario: FOB-TEAMS-MANAGE-09 Remove confirmation cancelled leaves member unchanged
    Given Maria clicks [Remove] next to Tom Lee
    When she clicks [Cancel] in the confirmation dialog
    Then Tom Lee remains a member of "UX"

  Scenario: FOB-TEAMS-MANAGE-10 Transfer admin rights to another member
    Given Maria is on the Members tab
    When she clicks [Transfer Admin] next to Tom Lee
    Then a confirmation dialog appears:
      """
      Transfer admin rights to Tom Lee? You will become a regular member of 'UX'.
      """
    When she confirms
    Then Tom Lee becomes the admin of "UX"
    And Maria's role changes to "member"
    And Tom Lee receives a notification "You are now the admin of the 'UX' team."
    And Maria is redirected to the "UX" team detail page at /teams/<pk>/
    And the [Manage Team] button is no longer visible for Maria on that page

  # ── Playbooks tab ─────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-MANAGE-11 Playbooks tab shows team's playbook list with add and remove actions
    Given Maria is on /teams/<pk>/manage/
    And "UX Research Methods" (v1.0, released) is in the "UX" team playbook list
    When she clicks the "Playbooks" tab (data-testid="team-tab-playbooks")
    Then she sees "UX Research Methods v1.0" in the list
    And an [Add Playbook] button is visible (data-testid="team-add-playbook-btn")
    And a [Remove] button appears next to each playbook

  Scenario: FOB-TEAMS-MANAGE-12 Add a released playbook to the team
    Given Maria owns "Product Discovery Framework" (v1.1, released)
    And that playbook is NOT in the "UX" team playbook list
    When she clicks [Add Playbook] and selects "Product Discovery Framework"
    And she clicks [Confirm]
    Then "Product Discovery Framework v1.1" appears in the team's playbook list
    And all "UX" team members can now view it via the GUI and MCP
    And a success banner reads "Playbook 'Product Discovery Framework' added to team."

  Scenario: FOB-TEAMS-MANAGE-13 Only released playbooks can be added to a team
    Given Maria owns "Draft Methodology" (v0.3, draft)
    When she opens the [Add Playbook] picker
    Then "Draft Methodology" does not appear in the selectable list
    And a tooltip reads "Only released playbooks can be shared in a team."

  Scenario: FOB-TEAMS-MANAGE-14 Remove a playbook from the team
    Given "UX Research Methods" is in the "UX" team playbook list
    When Maria clicks [Remove] next to "UX Research Methods" in the Playbooks tab
    Then a confirmation dialog appears:
      """
      Remove 'UX Research Methods' from 'UX'? Team members will lose access.
      """
    When she confirms
    Then "UX Research Methods" is removed from the team's playbook list
    And team members can no longer access it via the team
    And the playbook itself (owned by Maria) is NOT deleted

  # ── Settings tab ──────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-MANAGE-15 Settings tab is pre-populated with current team values
    Given Maria is on /teams/<pk>/manage/
    When she clicks the "Settings" tab (data-testid="team-settings-tab")
    Then the settings form shows:
      | field       | current value                                    |
      | Team Name   | UX                                               |
      | Description | User Experience methodologies and best practices |
      | Visibility  | Public                                           |
      | Join Policy | Requires Approval                                |
      | Category    | Design                                           |

  Scenario: FOB-TEAMS-MANAGE-16 Update Join Policy from Requires Approval to Auto-approve
    Given Maria is on the Settings tab of /teams/<pk>/manage/
    When she changes Join Policy to "Auto-approve" and clicks [Save Settings]
    Then a success banner reads "Team settings updated."
    And the "UX" team detail page shows Join Policy: Auto-approve
    And the browser console logs "[teams] settings saved for team: UX"

  Scenario: FOB-TEAMS-MANAGE-17 Update Visibility from Public to Hidden
    Given Maria is on the Settings tab
    When she changes Visibility to "Hidden" and clicks [Save Settings]
    Then a success banner reads "Team settings updated."
    And "UX" is no longer visible in the public team browser to non-members

  Scenario: FOB-TEAMS-MANAGE-18 Settings validation — Team Name cannot be blank
    Given Maria is on the Settings tab
    When she clears the Team Name field and clicks [Save Settings]
    Then an inline error appears: "Team name is required."
    And she stays on the Settings tab

  # ── Access control ────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-MANAGE-19 Non-admin member cannot access the manage page
    Given Mike Chen is a regular member of "UX"
    When Mike navigates directly to /teams/<pk>/manage/
    Then he is redirected to /teams/<pk>/
    And a warning reads "You don't have permission to manage this team."

  Scenario: FOB-TEAMS-MANAGE-20 Unauthenticated access to manage page is redirected
    Given Maria is not logged in
    When she navigates to /teams/<pk>/manage/
    Then she is redirected to the login page
    And after login she is returned to /teams/<pk>/manage/

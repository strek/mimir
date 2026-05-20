Feature: FOB-TEAMS-BROWSE-1 Browse and Search Teams
  As a methodology author (Maria)
  I want to browse, search, and filter available teams
  So that I can discover communities relevant to my UX practice and find the right ones to join

  Background:
    Given Maria is authenticated in FOB

  # ── Navigation ────────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-BROWSE-01 Access Team Browser from dashboard
    Given Maria is on the FOB Dashboard
    When she clicks [Browse Teams]
    Then she is redirected to /teams/
    And the page title reads "Teams"
    And data-testid="teams-browse-page" is present
    And a search bar is visible (data-testid="teams-search-input")
    And a category filter dropdown is visible (data-testid="teams-category-filter")
    And a [Create Team] button is visible (data-testid="create-team-btn")

  Scenario: FOB-TEAMS-BROWSE-02 Access Team Browser from top navigation
    Given Maria is anywhere in FOB
    When she clicks "Teams" in the top navigation bar
    Then she is redirected to /teams/
    And data-testid="teams-browse-page" is present

  # ── Visibility rules ──────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-BROWSE-03 Team list shows public teams and member-only hidden teams
    Given the following teams exist:
      | name        | visibility | maria_is_member |
      | Usability   | Public     | no              |
      | UX          | Public     | yes             |
      | Acme, INC   | Hidden     | yes             |
      | SecretTeam  | Hidden     | no              |
    When Maria is on /teams/
    Then the team list shows:
      | name       |
      | Usability  |
      | UX         |
      | Acme, INC  |
    And "SecretTeam" is NOT visible in the list

  # ── Team card content ─────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-BROWSE-04 Each team card shows key summary information
    Given the "Usability" team exists with:
      | field       | value                                          |
      | Description | Best practices for usable software development |
      | Visibility  | Public                                         |
      | Members     | 127                                            |
      | Playbooks   | 8                                              |
    When Maria is on /teams/
    Then the "Usability" team card (data-testid="team-card-usability") shows:
      | field      | value                                          |
      | Name       | Usability                                      |
      | Description| Best practices for usable software development |
      | Members    | 127 members                                    |
      | Playbooks  | 8 playbooks                                    |
    And a "Public" visibility badge is visible on the card
    And a [View] link points to /teams/<pk>/

  Scenario: FOB-TEAMS-BROWSE-05 Hidden team card shows "Hidden" badge for members
    Given Maria is a member of the hidden "Acme, INC" team
    When she is on /teams/
    Then the "Acme, INC" team card shows a "Hidden" visibility badge

  # ── Search ────────────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-BROWSE-06 Search teams by name (case-insensitive)
    Given the team list contains "Usability", "UX", "Acme, INC"
    When Maria types "usa" into data-testid="teams-search-input"
    Then only "Usability" appears in the results
    And "UX" and "Acme, INC" are not shown
    And the browser console logs "[teams] search query: usa, results: 1"

  Scenario: FOB-TEAMS-BROWSE-07 Search matches team description
    Given a team named "Front-End Guild" with description "JavaScript and CSS methodologies"
    When Maria searches for "javascript"
    Then "Front-End Guild" appears in the results

  Scenario: FOB-TEAMS-BROWSE-08 Clearing search restores the full list
    Given Maria has typed "usa" and "Usability" is the only result
    When she clears the search bar
    Then the full team list is restored

  # ── Category filter ───────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-BROWSE-09 Filter by category narrows the list
    Given teams with categories:
      | name            | category    |
      | Usability       | Engineering |
      | UX              | Design      |
      | Front-End Guild | Engineering |
    When Maria selects "Engineering" from data-testid="teams-category-filter"
    Then only "Usability" and "Front-End Guild" are shown
    And an active filter chip reads "Category: Engineering"

  Scenario: FOB-TEAMS-BROWSE-10 Clearing category filter restores full list
    Given Maria has "Design" filter active
    When she clicks the [×] on the "Category: Design" chip
    Then the filter is removed and the full list is restored

  Scenario: FOB-TEAMS-BROWSE-11 Search and category filter combine
    Given teams "Usability" (Engineering), "UX" (Design), "Front-End Guild" (Engineering)
    When Maria types "usa" AND selects category "Engineering"
    Then only "Usability" is shown

  # ── Empty states ──────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-BROWSE-12 No results for search term shows empty state
    When Maria searches for "blockchain" and no teams match
    Then data-testid="teams-empty-state" shows "No teams found matching 'blockchain'."
    And a [Clear Search] link is visible
    And a [Create New Team] button is visible

  Scenario: FOB-TEAMS-BROWSE-13 No public teams exist shows onboarding empty state
    Given no public teams exist and Maria is not a member of any team
    When Maria is on /teams/
    Then the page shows "No teams yet. Be the first to create one!" (data-testid="teams-empty-state")
    And a [Create Team] button is visible

  # ── Access control ────────────────────────────────────────────────────────

  Scenario: FOB-TEAMS-BROWSE-14 Unauthenticated access is redirected to login
    Given Maria is not logged in
    When she navigates to /teams/
    Then she is redirected to the login page
    And after login she is returned to /teams/

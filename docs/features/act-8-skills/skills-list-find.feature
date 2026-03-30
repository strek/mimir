Feature: FOB-SKILLS-LIST+FIND-1 Skills List and Search
  As a methodology author (Maria)
  I want to view and search skills within a playbook
  So that I can manage guidance documentation

  Background:
    Given Maria is authenticated in FOB
    And she is viewing playbook "React Frontend v1.2"
    And the playbook has 12 skills defined

  Scenario: FOB-SKILLS-LIST+FIND-01 Navigate to skills list from playbook
    Given Maria is on FOB-PLAYBOOKS-VIEW_PLAYBOOK-1
    When she clicks the "Skills" tab
    Then she is redirected to FOB-SKILLS-LIST+FIND-1
    And she sees "Skills in React Frontend v1.2" header

  Scenario: FOB-SKILLS-LIST+FIND-02 View skills table
    Given Maria is on skills list
    Then she sees all 12 skills
    And each skill shows: Name, Description, Activities, Actions

  Scenario: FOB-SKILLS-LIST+FIND-03 Create new skill
    Given Maria is on skills list
    When she clicks [Create New Skill]
    Then she is redirected to FOB-SKILLS-CREATE_SKILL-1

  Scenario: FOB-SKILLS-LIST+FIND-04 Search skills by name
    Given Maria is on skills list
    When she enters "Setup" in search
    Then only skills matching "Setup" are shown

  Scenario: FOB-SKILLS-LIST+FIND-05 Filter by activity usage
    Given some skills are linked to activities
    When she filters by "Used in Activities"
    Then only skills linked to activities are shown

  Scenario: FOB-SKILLS-LIST+FIND-06 View skill usage count
    Given Maria is on skills list
    Then each skill shows activity count
    And she can click to see which activities link each skill

  Scenario: FOB-SKILLS-LIST+FIND-07 Navigate to view skill
    Given Maria is on skills list
    When she clicks [View] for a skill
    Then she is redirected to FOB-SKILLS-VIEW_SKILL-1

  Scenario: FOB-SKILLS-LIST+FIND-08 Empty state display
    Given the playbook has zero skills
    Then she sees "No skills yet"
    And she sees [Create First Skill] button

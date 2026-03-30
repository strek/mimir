Feature: FOB-SKILLS-VIEW_SKILL-1 View Skill Details
  As a methodology author (Maria)
  I want to view skill details
  So that I can read guidance documentation

  Background:
    Given Maria is authenticated in FOB
    And she is viewing skill "Setup React Component"
    And the skill belongs to playbook "React Frontend v1.2"

  Scenario: FOB-SKILLS-VIEW_SKILL-01 Open skill detail page
    Given Maria is on skills list
    When she clicks [View] for "Setup React Component"
    Then she is redirected to FOB-SKILLS-VIEW_SKILL-1
    And she sees breadcrumb with playbook and skill name

  Scenario: FOB-SKILLS-VIEW_SKILL-02 View skill header
    Given Maria is on the skill detail page
    Then she sees skill name "Setup React Component"
    And she sees parent playbook badge

  Scenario: FOB-SKILLS-VIEW_SKILL-03 View skill content
    Given Maria is on the skill detail page
    Then she sees the formatted content
    And formatting is preserved (bold, italic, lists, code)

  Scenario: FOB-SKILLS-VIEW_SKILL-04 View activities using this skill
    Given the skill is linked to 3 activities
    Then she sees "Used in Activities" section
    And she sees list of activities with this skill
    And each activity link is clickable

  Scenario: FOB-SKILLS-VIEW_SKILL-05 Edit skill button
    Given Maria is viewing the skill
    When she clicks [Edit Skill]
    Then she is redirected to FOB-SKILLS-EDIT_SKILL-1

  Scenario: FOB-SKILLS-VIEW_SKILL-06 Delete skill button
    Given Maria is viewing the skill
    When she clicks [Delete Skill]
    Then the FOB-SKILLS-DELETE_SKILL-1 modal appears

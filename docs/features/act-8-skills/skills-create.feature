Feature: FOB-SKILLS-CREATE_SKILL-1 Create Skill
  As a methodology author (Maria)
  I want to create skills within a playbook
  So that I can provide guidance documentation

  Background:
    Given Maria is authenticated in FOB
    And she is viewing playbook "React Frontend v1.2"

  Scenario: FOB-SKILLS-CREATE_SKILL-01 Open create skill form
    Given Maria is on skills list
    When she clicks [Create New Skill]
    Then she is redirected to FOB-SKILLS-CREATE_SKILL-1

  Scenario: FOB-SKILLS-CREATE_SKILL-02 Create skill successfully
    Given Maria is on the create skill form
    When she enters "Setup React Component" in Name
    And she enters "Step-by-step guide to create a new React component" in Description
    And she enters skill content in rich text editor
    And she clicks [Create Skill]
    Then the skill is created
    And she sees success notification

  Scenario: FOB-SKILLS-CREATE_SKILL-03 Validate required fields
    Given Maria is on the create skill form
    When she leaves Name empty
    And she clicks [Create Skill]
    Then she sees validation error "Name is required"

  Scenario: FOB-SKILLS-CREATE_SKILL-04 Rich text formatting
    Given Maria is on the create skill form
    Then she can format text with bold, italic, lists
    And she can add code blocks
    And she can add links

  Scenario: FOB-SKILLS-CREATE_SKILL-05 Cancel skill creation
    Given Maria has entered skill data
    When she clicks [Cancel]
    Then she sees "Discard changes?" confirmation
    When she confirms
    Then no skill is created

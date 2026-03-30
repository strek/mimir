Feature: FOB-SKILLS-EDIT_SKILL-1 Edit Skill
  As a methodology author (Maria)
  I want to edit skill details
  So that I can update guidance documentation

  Background:
    Given Maria is authenticated in FOB
    And she owns playbook "React Frontend v1.2"
    And the playbook has skill "Setup React Component"

  Scenario: FOB-SKILLS-EDIT_SKILL-01 Open edit form
    Given Maria is viewing the skill
    When she clicks [Edit Skill]
    Then she is redirected to FOB-SKILLS-EDIT_SKILL-1
    And all fields are pre-populated

  Scenario: FOB-SKILLS-EDIT_SKILL-02 Edit skill name
    Given Maria is on the edit form
    When she changes Name to "Advanced React Component Setup"
    And she clicks [Save Changes]
    Then the skill is updated

  Scenario: FOB-SKILLS-EDIT_SKILL-03 Edit skill content
    Given Maria is on the edit form
    When she updates the content in rich text editor
    And she saves
    Then the content is updated

  Scenario: FOB-SKILLS-EDIT_SKILL-04 Cancel editing
    Given Maria has made changes
    When she clicks [Cancel]
    Then changes are discarded

Feature: FOB-SKILLS-DELETE_SKILL-1 Delete Skill
  As a methodology author (Maria)
  I want to delete skills
  So that I can remove obsolete guidance

  Background:
    Given Maria is authenticated in FOB
    And she owns playbook "React Frontend v1.2"
    And the playbook has skill "Old Guide"

  Scenario: FOB-SKILLS-DELETE_SKILL-01 Open delete confirmation
    Given Maria is on skills list
    When she clicks [Delete] for "Old Guide"
    Then the FOB-SKILLS-DELETE_SKILL-1 modal appears
    And it shows "Delete Skill?"

  Scenario: FOB-SKILLS-DELETE_SKILL-02 Modal shows skill details
    Given the delete modal is open
    Then it displays skill name
    And it shows warning about activity links

  Scenario: FOB-SKILLS-DELETE_SKILL-03 Warning about linked activities
    Given the skill is linked to 5 activities
    Then the modal shows "Linked to 5 activities"
    And it lists the activities
    And it shows "Activity links will be removed"

  Scenario: FOB-SKILLS-DELETE_SKILL-04 Confirm deletion
    Given the delete modal is open
    When she clicks [Delete Skill]
    Then the skill is deleted
    And activity links are removed
    And she sees success notification

  Scenario: FOB-SKILLS-DELETE_SKILL-05 Cancel deletion
    Given the delete modal is open
    When she clicks [Cancel]
    Then the modal closes
    And the skill is not deleted

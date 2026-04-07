# {ProjectName}: Modus Operandi

## 1. Introduction

### Purpose
This document defines the software development process for {ProjectName}. It serves as the authoritative guide for how the team plans, executes, and delivers software.

### Scope
- **Project**: {ProjectName}
- **Team**: {TeamSize} members ({TeamComposition})
- **Duration**: {ProjectDuration}
- **Delivery Model**: {DeliveryModel}

### References
- [System Architecture Overview (SAO.md)](../architecture/SAO.md)
- [User Journey](../features/user_journey.md)
- [Playbook]: {PlaybookName}

---

## 2. Overview

### Base Methodology
**Chosen**: {Methodology}

**Rationale**: {MethodologyRationale}

**Key Adjustments for This Project**:
- {Adjustment1}
- {Adjustment2}
- {Adjustment3}

### Team Structure and Roles

| Role | Responsibilities | Team Member(s) |
|------|-----------------|----------------|
| {Role1} | {Responsibilities1} | {TeamMember1} |
| {Role2} | {Responsibilities2} | {TeamMember2} |
| {Role3} | {Responsibilities3} | {TeamMember3} |
| {Role4} | {Responsibilities4} | {TeamMember4} |

---

## 3. Lifecycle Model

### Phases

**{Phase1}**: {Phase1Description}
- **Duration**: {Phase1Duration}
- **Milestone**: {Phase1Milestone}
- **Entry Criteria**: {Phase1EntryCriteria}
- **Exit Criteria**: {Phase1ExitCriteria}

**{Phase2}**: {Phase2Description}
- **Duration**: {Phase2Duration}
- **Milestone**: {Phase2Milestone}
- **Entry Criteria**: {Phase2EntryCriteria}
- **Exit Criteria**: {Phase2ExitCriteria}

**{Phase3}**: {Phase3Description}
- **Duration**: {Phase3Duration}
- **Milestone**: {Phase3Milestone}
- **Entry Criteria**: {Phase3EntryCriteria}
- **Exit Criteria**: {Phase3ExitCriteria}

**{Phase4}**: {Phase4Description}
- **Duration**: {Phase4Duration}
- **Milestone**: {Phase4Milestone}
- **Entry Criteria**: {Phase4EntryCriteria}
- **Exit Criteria**: {Phase4ExitCriteria}

### Iteration Cadence
- **Iteration Length**: {IterationLength}
- **Ceremonies**:
  - {Ceremony1}: {Ceremony1Schedule}
  - {Ceremony2}: {Ceremony2Schedule}
  - {Ceremony3}: {Ceremony3Schedule}
  - {Ceremony4}: {Ceremony4Schedule}

---

## 4. Phase × Artifact Matrix

This matrix defines which workflows run in which phase, which artifacts are produced, and the required review level.

| Phase | Workflow | Artifact | Must/Should/Could | Review Level |
|-------|----------|----------|-------------------|--------------|
| {Phase1} | {Workflow1} | {Artifact1} | Must | Formal review |
| {Phase1} | {Workflow2} | {Artifact2} | Must | Informal review |
| {Phase2} | {Workflow3} | {Artifact3} | Must | Formal review |
| {Phase2} | {Workflow4} | {Artifact4} | Should | Informal review |
| {Phase3} | {Workflow5} | {Artifact5} | Must | Formal review |
| {Phase3} | {Workflow6} | {Artifact6} | Could | None |
| {Phase4} | {Workflow7} | {Artifact7} | Must | Formal review |

**Review Levels**:
- **Formal**: Explicit approval required from {ApproverRole}
- **Informal**: FYI to team, feedback welcome but not blocking
- **None**: Self-review by author

---

## 5. WBS & Backlog Structure

### Work Breakdown Hierarchy

```
Epic (Business Capability)
  └── Feature (User-Facing Functionality)
      └── Scenario (Single User Goal)
          └── Task (Technical Work Item)
```

**Example**:
```
Epic: {EpicExample}
  └── Feature: {FeatureExample}
      └── Scenario: {ScenarioExample}
          └── Task: {TaskExample}
```

### Backlog Tool Configuration
- **Tool**: {BacklogTool}
- **Project Key**: {ProjectKey}
- **Labels**: {Label1}, {Label2}, {Label3}
- **Custom Fields**: {CustomField1}, {CustomField2}

### Estimation Approach
- **Units**: {EstimationUnits}
- **Scale**: {EstimationScale}
- **Process**: {EstimationProcess}

### Feature File → Backlog Mapping Rules
1. **Feature File** → {BacklogTool} Epic
2. **Scenario** → {BacklogTool} Story/Issue
3. **Scenario ID** → Issue title prefix (e.g., "AUTH-01: User logs in")
4. **Given/When/Then** → Acceptance criteria in issue description
5. **Implementation Plan** → Linked to issue as attachment or comment

---

## 6. Sample Iteration Plans

### {Phase1} Iteration

**Goals**: {Phase1IterationGoals}

**Activities** (in order):
1. {Activity1} - {Activity1Owner} - {Activity1Duration}
2. {Activity2} - {Activity2Owner} - {Activity2Duration}
3. {Activity3} - {Activity3Owner} - {Activity3Duration}

**Artifacts Produced**:
- {Artifact1}
- {Artifact2}
- {Artifact3}

**Success Criteria**:
- {SuccessCriteria1}
- {SuccessCriteria2}

---

### {Phase2} Iteration

**Goals**: {Phase2IterationGoals}

**Activities** (in order):
1. {Activity4} - {Activity4Owner} - {Activity4Duration}
2. {Activity5} - {Activity5Owner} - {Activity5Duration}
3. {Activity6} - {Activity6Owner} - {Activity6Duration}

**Artifacts Produced**:
- {Artifact4}
- {Artifact5}
- {Artifact6}

**Success Criteria**:
- {SuccessCriteria3}
- {SuccessCriteria4}

---

### {Phase3} Iteration

**Goals**: {Phase3IterationGoals}

**Activities** (in order):
1. {Activity7} - {Activity7Owner} - {Activity7Duration}
2. {Activity8} - {Activity8Owner} - {Activity8Duration}
3. {Activity9} - {Activity9Owner} - {Activity9Duration}

**Artifacts Produced**:
- {Artifact7}
- {Artifact8}
- {Artifact9}

**Success Criteria**:
- {SuccessCriteria5}
- {SuccessCriteria6}

---

### {Phase4} Iteration

**Goals**: {Phase4IterationGoals}

**Activities** (in order):
1. {Activity10} - {Activity10Owner} - {Activity10Duration}
2. {Activity11} - {Activity11Owner} - {Activity11Duration}
3. {Activity12} - {Activity12Owner} - {Activity12Duration}

**Artifacts Produced**:
- {Artifact10}
- {Artifact11}
- {Artifact12}

**Success Criteria**:
- {SuccessCriteria7}
- {SuccessCriteria8}

---

## 7. AI/Human Collaboration Patterns

### Responsibility Matrix

| Activity | AI Responsibility | Human Responsibility |
|----------|------------------|---------------------|
| {Activity1} | {AIResponsibility1} | {HumanResponsibility1} |
| {Activity2} | {AIResponsibility2} | {HumanResponsibility2} |
| {Activity3} | {AIResponsibility3} | {HumanResponsibility3} |
| {Activity4} | {AIResponsibility4} | {HumanResponsibility4} |

### Quality Gates for AI-Generated Code

**Gate 1: Code Generation**
- AI generates implementation following playbook patterns
- Human reviews for architectural alignment
- **Pass Criteria**: {PassCriteria1}

**Gate 2: Testing**
- AI writes unit and integration tests
- Human reviews test coverage and edge cases
- **Pass Criteria**: {PassCriteria2}

**Gate 3: Documentation**
- AI generates docstrings and inline comments
- Human reviews for clarity and completeness
- **Pass Criteria**: {PassCriteria3}

**Gate 4: Integration**
- AI creates PR with all changes
- Human performs code review and approves
- **Pass Criteria**: {PassCriteria4}

### Context Management Strategy

**Context Templates**:
- **Feature Context**: {FeatureContextTemplate}
- **Bug Fix Context**: {BugFixContextTemplate}
- **Refactoring Context**: {RefactoringContextTemplate}

**Context Refresh Triggers**:
- {Trigger1}
- {Trigger2}
- {Trigger3}

### Communication and Escalation Patterns

**AI → Human Escalation**:
- {EscalationScenario1} → {EscalationAction1}
- {EscalationScenario2} → {EscalationAction2}
- {EscalationScenario3} → {EscalationAction3}

**Human → AI Feedback**:
- {FeedbackScenario1} → {FeedbackAction1}
- {FeedbackScenario2} → {FeedbackAction2}

### Collaboration Workflows per Development Phase

**{Phase1}**:
- AI: {AIWorkflow1}
- Human: {HumanWorkflow1}
- Handoff: {HandoffPoint1}

**{Phase2}**:
- AI: {AIWorkflow2}
- Human: {HumanWorkflow2}
- Handoff: {HandoffPoint2}

**{Phase3}**:
- AI: {AIWorkflow3}
- Human: {HumanWorkflow3}
- Handoff: {HandoffPoint3}

**{Phase4}**:
- AI: {AIWorkflow4}
- Human: {HumanWorkflow4}
- Handoff: {HandoffPoint4}

---

## 8. Roles & Responsibilities

### {Role1}
**Responsibilities**:
- {Role1Responsibility1}
- {Role1Responsibility2}
- {Role1Responsibility3}

**Authority**:
- {Role1Authority1}
- {Role1Authority2}

**Deliverables**:
- {Role1Deliverable1}
- {Role1Deliverable2}

---

### {Role2}
**Responsibilities**:
- {Role2Responsibility1}
- {Role2Responsibility2}
- {Role2Responsibility3}

**Authority**:
- {Role2Authority1}
- {Role2Authority2}

**Deliverables**:
- {Role2Deliverable1}
- {Role2Deliverable2}

---

### {Role3}
**Responsibilities**:
- {Role3Responsibility1}
- {Role3Responsibility2}
- {Role3Responsibility3}

**Authority**:
- {Role3Authority1}
- {Role3Authority2}

**Deliverables**:
- {Role3Deliverable1}
- {Role3Deliverable2}

---

### {Role4} (AI Agent)
**Responsibilities**:
- Implementation following playbook patterns
- Test generation and execution
- Documentation generation
- Code quality checks

**Authority**:
- Create feature branches
- Generate code and tests
- Run automated checks
- Create PRs (requires human approval)

**Deliverables**:
- Working code with tests
- Documentation
- Test reports
- PR with complete implementation

---

## 9. Tools

### Project Management
- **Tool**: {ProjectManagementTool}
- **Purpose**: {ProjectManagementPurpose}
- **Access**: {ProjectManagementAccess}

### Methodology & Playbooks
- **Tool**: Mimir (playbooks, workflows, activities, skills)
- **Purpose**: Process guidance and AI context
- **Access**: {MimirAccess}

### Code & Version Control
- **Tool**: {VCSTool}
- **Repository**: {RepositoryURL}
- **Branching Strategy**: {BranchingStrategy}

### CI/CD
- **Tool**: {CICDTool}
- **Pipeline**: {PipelineConfig}
- **Deployment**: {DeploymentStrategy}

### Communication
- **Tool**: {CommunicationTool}
- **Channels**: {Channels}
- **Notifications**: {NotificationRules}

### AI Collaboration
- **Tool**: {AITool}
- **Context Templates**: See Section 7
- **Quality Dashboards**: {QualityDashboardURL}

---

## 10. Continuous Improvement

### Retrospective Cadence
- **Frequency**: {RetrospectiveFrequency}
- **Format**: {RetrospectiveFormat}
- **Participants**: {RetrospectiveParticipants}

### Metrics Tracked
- {Metric1}: {Metric1Target}
- {Metric2}: {Metric2Target}
- {Metric3}: {Metric3Target}
- {Metric4}: {Metric4Target}

### Process Adjustment Protocol
1. {AdjustmentStep1}
2. {AdjustmentStep2}
3. {AdjustmentStep3}
4. {AdjustmentStep4}

---

## Placeholder Reference

- `{ProjectName}` - Name of the project
- `{Methodology}` - Base methodology (e.g., Scrum, Kanban, RUP)
- `{Phase1}`, `{Phase2}`, etc. - Phase names (e.g., Inception, Elaboration, Construction, Operation)
- `{TeamRoles}` - Team role names
- `{Tools}` - Tool names
- `{IterationLength}` - Iteration duration (e.g., 2 weeks, 1 week)
- `{Workflow}` - Workflow names
- `{Artifact}` - Artifact names
- `{Activity}` - Activity names

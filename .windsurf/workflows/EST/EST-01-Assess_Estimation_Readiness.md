# Activity: Assess Estimation Readiness

**Activity ID**: 25
**Order**: 1
**Phase**: Foundation
**Dependencies**: None

## Description

Assess Estimation Readiness

## Guidance

## Purpose
Determine what inputs are available, choose the appropriate estimation level (Level 1 SWAG vs. Level 2 Detailed), and produce an Estimation Strategy document that governs the rest of the workflow.

## Prerequisites
- Project idea, vision document, or feature files exist
- Stakeholder available to answer risk-profile questions

## Steps

### Step 1: Inventory Available Inputs

Check which artifacts exist and record their status:

| Artifact | Location | Status |
|---|---|---|
| BDD Feature Files | `docs/features/` | exists / partial / missing |
| Software Architecture Overview | `docs/architecture/SAO.md` | exists / missing |
| User Journey | `docs/features/user_journey.md` | exists / missing |
| Previous Sprint Actuals | Reference Table | exists / missing |
| Reference Story Calibration | Reference Table | calibrated / uncalibrated |

### Step 1.5: Check Project Bootstrap Status

Verify whether the project has been bootstrapped (BSP workflow completed):

| Check | What to Look For | Status |
|-------|------------------|--------|
| **Git repository** | `.git/` directory exists | exists / missing |
| **Project entry point** | `manage.py`, `package.json`, `Cargo.toml`, etc. | exists / missing |
| **Dependency file** | `requirements.txt`, `package.json`, `Cargo.toml` | exists / missing |
| **Makefile** | `Makefile` with `provision`, `run`, `test` targets | exists / missing |
| **Source directories** | Application code directories per SAO.md structure | exists / missing |

**If 3+ checks are missing** → project is **not bootstrapped**.

**Action for non-bootstrapped projects:**

Ask user: "Project is not bootstrapped. Include BSP activities in WBS as overhead?"

- **Yes** → Add BSP overhead to estimation:
  - Create a "Sprint 0: Bootstrap" section in WBS
  - Add 8 BSP activities as work packages with PERT estimates:
    - BSP-01: Verify/Install Prerequisites (XS, 1 SP)
    - BSP-02: Initialize Repository (XS, 1 SP)
    - BSP-03: Scaffold Project Structure (S, 2 SP)
    - BSP-04: Initialize Runtimes/Dependencies (S, 2 SP)
    - BSP-05: Configure Dev Tooling (M, 3 SP)
    - BSP-06: Create Makefile (M, 3 SP)
    - BSP-07: Create Welcome Page/Verify (S, 2 SP)
    - BSP-08: Configure Observability/Logging (M, 3 SP)
  - **Total BSP overhead**: ~17 SP (~1.5-2 sprints depending on team velocity)
  - Record in ESTIMATION_STRATEGY.md: "Bootstrap overhead included in Sprint 0"

- **No** → Redirect to BSP workflow:
  - Stop EST workflow
  - Direct user: "Please run BSP (Bootstrap Project) workflow first, then return to EST"
  - Record in ESTIMATION_STRATEGY.md: "Bootstrap deferred — not included in estimates"

**If project is bootstrapped** → proceed to Step 2 (no action needed).

### Step 2: Run Boehm & Turner 5-Factor Risk Assessment

Rate each factor on the appropriate scale. Circle the home ground that applies.

| Factor | Agile Home Ground | Plan-Driven Home Ground | This Project |
|---|---|---|---|
| Team Size | ≤10 | ≥20 | ___ |
| Criticality | Low (comfort) | High (money/life) | ___ |
| Requirements Dynamism | High change rate | Stable | ___ |
| Culture | Chaos-tolerant | Order-preferring | ___ |
| Personnel | All senior/CRACK | Mixed skill levels | ___ |

Identify dominant risk type:
- **A-risks dominate** (too agile) → lean toward more process/Level 2
- **P-risks dominate** (too plan-driven) → stay Level 1, iterate fast
- **Mixed** → Level 1 now, schedule Level 2 after Sprint 1

### Step 3: Select Estimation Level

**Level 1 SWAG** — use when:
- Feature files exist but SAO.MD is absent
- Project is in early discovery
- Team size ≤ 5, low criticality
- First sprint (always start here)

**Level 1 + Level 2 Detailed** — use when:
- `docs/architecture/SAO.md` exists and is current
- Requirements stability ≥ 80% (McConnell prerequisite)
- Team size > 10 or criticality is high
- Stakeholder requires commitment-quality estimates

**Both levels produce** the same Excel output; Level 2 simply populates additional tabs (WBS Features + Detailed Estimates).

### Step 4: Document Estimation Strategy

Create or update `docs/plans/ESTIMATION_STRATEGY.md` with:
- Estimation level chosen and rationale
- Risk profile summary (5-factor ratings)
- Gate condition for upgrading to Level 2 (e.g., "after SAO.MD is complete")
- Sprint refinement cadence (default: every sprint close)
- Reference Table location

### Step 5: Open Excel Estimation Template

Open `docs/plans/ESTIMATION_TEMPLATE.xlsx`. Verify all tabs are present:
1. Setup
2. Scenario List
3. ECF
4. TCF
5. Rough Estimates
6. Monte Carlo
7. WBS Features
8. Detailed Estimates

If file does not exist, copy from `forge/templates/ESTIMATION_TEMPLATE.xlsx`.

## Rules to Follow

### I. Prerequisites Before Estimating
Never produce token or duration estimates without first completing Steps 1–3. An estimate produced without a risk assessment is a guess, not engineering.

### II. Level Decision is Reversible
Choosing Level 1 does not prevent upgrading to Level 2 later. Record the upgrade gate condition explicitly so it is not forgotten.

### III. McConnell Prerequisite Checklist
Before Level 2: confirm problem definition is documented, requirements are ≥ 80% complete, and architecture is sketched. Without these, Level 2 adds false precision, not real accuracy.

## Success Criteria
- Input inventory complete
- 5-factor risk assessment documented
- Estimation level selected with rationale
- ESTIMATION_STRATEGY.md created/updated
- Excel template open and verified

## Artifacts Produced

- `docs/plans/ESTIMATION_STRATEGY.md`

## Artifacts Consumed

- `docs/features/` (BDD feature files)
- `docs/architecture/SAO.md` (if exists)
- Reference Table (if exists)
- Project root directory (for bootstrap status check)

## Notes

No additional notes.

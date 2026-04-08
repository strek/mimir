# Activity: Sprint Close & Rebaseline

**Activity ID**: 32
**Order**: 8
**Phase**: Refinement
**Dependencies**: Predecessor: Activity 31 (Run Monte Carlo Simulation)

## Description

Sprint Close & Rebaseline

## Guidance

## Purpose
At the end of each sprint, collect actual token and scenario data, compare to estimates, narrow PERT distributions for remaining work, update the Reference Table with calibration data, and re-run the Monte Carlo simulation to produce a refined forecast. This loop is the engine of estimate improvement across the project.

## Prerequisites
- Sprint completed (or partially completed with clear scope)
- Token consumption data available from AI model billing/usage logs
- Scenario completion status recorded

## Steps

### Step 1: Collect Sprint Actuals

For each scenario attempted in the sprint, record:
- Scenario ID
- Planned SP
- Planned tokens (expected from estimate)
- Actual tokens consumed (from AI usage logs)
- Status: DONE / PARTIAL / BLOCKED / DEFERRED
- Notes (why partial/blocked, scope changes, surprises)

Record in the Scenario List tab, in the "Sprint N Actuals" columns.

### Step 2: Compute Velocity Factor

For each completed scenario:
```
Velocity Factor = Actual Tokens / Estimated Tokens (expected)
```

Compute sprint-level velocity factor:
```
Sprint VF = Sum(Actual Tokens, all completed scenarios) / Sum(Estimated Tokens, same scenarios)
```

| VF Range | Meaning | Action |
|---|---|---|
| < 0.8 | AI performed faster than estimated | Reduce K-token expected; tighten min |
| 0.8 – 1.2 | On target | Minor adjustment only |
| 1.2 – 1.5 | Slower than expected | Increase K-token expected; widen max |
| > 1.5 | Significant overrun | Investigate root cause before adjusting |

### Step 3: Update K-Token Baselines

For each size tier with ≥ 1 completed actual in this sprint:

1. Add actual to the running history in the Reference Table
2. Recompute calibrated K values:
   - K_expected = weighted average of last 3–5 actuals (recent actuals weighted more)
   - K_min = 10th percentile of actuals history
   - K_max = 90th percentile of actuals history
3. Update the Setup tab with new K values
4. Change calibration status:
   - 1 actual → still SEED (too few data points)
   - 2 actuals → BORROWED (improving)
   - ≥ 3 actuals for this tier → CALIBRATED

### Step 4: Update Reference Table

Append a new entry to `docs/plans/REFERENCE_TABLE.md`:

```
## Sprint {N} Actuals — {Date}

| Scenario | Size | SP | Est. Tokens | Actual Tokens | VF | Notes |
|---|---|---|---|---|---|---|
| FOB-X-Y-01 | M | 2 | 110K | 127K | 1.15 | Service more complex than expected |
| FOB-X-Y-02 | S | 1 | 50K | 44K | 0.88 | Reused existing model |
...

Updated K Baselines:
  S (1 SP):  min=28K expected=47K max=76K (was: min=30K exp=50K max=80K)
  M (2 SP):  min=75K expected=118K max=192K (was: min=70K exp=110K max=180K)
  
Combined Multiplier: {value} (was: {previous})
ECF/TCF changes: {describe any factor re-ratings}
```

### Step 5: Re-Rate ECF/TCF (If Warranted)

Review ECF/TCF factors for any that have materially changed:
- E6 (requirements stability) — did requirements churn this sprint?
- A3 (hallucination risk) — did AI quality improve as it learned the codebase?
- A2 (prompt maturity) — did new prompts prove more efficient?

Update ECF/TCF tabs if any factor changes by ≥ 1 point. Recompute combined multiplier.

### Step 6: Update Remaining Scenario Estimates

For remaining (not yet started) scenarios, apply updated K baselines:
- Scenarios similar to completed ones → apply actual VF as a correction factor
- Scenarios very different in nature → keep wider PERT ranges
- Scenarios with changed scope → re-size and re-estimate

### Step 7: Re-Run Monte Carlo

Run EST-07 over remaining scenarios only (completed scenarios are actuals, not estimates):
- Input: remaining scenario PERT triplets (updated)
- Add actuals as fixed values (no simulation needed)
- Output: new P50/P80/P95 for project completion

Compare new forecast to previous MC_SNAPSHOT:
- Is P80 completion date improving sprint-over-sprint? (healthy project)
- Is P80 date drifting outward? (scope growth or systematic underestimation — investigate)

Save new `docs/plans/MC_SNAPSHOT_{DATE}.md`.

### Step 8: Publish Sprint Report

Produce a brief sprint estimation report:

```
Sprint {N} Estimation Report — {Date}

Completed: {N} scenarios ({SP} SP), {Actual Tokens}K tokens
Planned:   {N} scenarios ({SP} SP), {Planned Tokens}K tokens
Velocity Factor: {VF}

Deferred:  {list any deferred scenarios and reason}

Revised Forecast (remaining work):
  P50: {date}  ({delta} vs. previous P50)
  P80: {date}  ({delta} vs. previous P80)
  P95: {date}  ({delta} vs. previous P95)

Token Budget Status:
  Consumed to date: {N}K tokens
  Remaining P80:    {N}K tokens
  Total P80:        {N}K tokens ({% of original P80})

Reference Table: updated K baselines for {list tiers updated}
Next sprint plan: {N} scenarios ({SP} SP)
```

Present to user/stakeholder. Save to `docs/plans/`.

## Rules to Follow

### I. Actuals Are Sacred
Never retroactively adjust planned estimates to match actuals. The planned estimate is historical record. The actual is new data. Both must be preserved.

### II. Calibration Requires ≥ 3 Actuals Per Tier
Do not mark K baselines as CALIBRATED until you have 3+ actuals for that size tier. Two actuals can still be outliers.

### III. Investigate VF > 1.5
A velocity factor above 1.5 (50% overrun) on any scenario is a signal, not just a data point. Before updating baselines, understand why: scope creep? Novel technical challenge? AI model underperformance? Fix the root cause, then update the estimate.

### IV. McConnell's Change Control Rule
Every requirements change after baseline must be re-estimated. If scope changed during the sprint (a scenario was modified mid-sprint), record it separately. Do not blend scope-change overruns into calibration data — they will corrupt future K baselines.

### V. The 20-Data-Point Threshold
Monte Carlo simulation achieves MMRE ~20% only after ~20 data points across all size tiers (ACM SAC 2021). Before that, keep PERT ranges wide. After 4–5 sprints with mixed sizes, the simulation becomes trustworthy.

## Success Criteria
- All sprint actuals collected and recorded
- Velocity factor computed per scenario and per sprint
- K-token baselines updated in Setup tab
- Reference Table appended with new entries
- ECF/TCF re-rated if warranted
- Remaining scenario estimates updated
- Monte Carlo re-run, new P50/P80/P95 produced
- MC_SNAPSHOT saved
- Sprint Estimation Report produced and reviewed

## Artifacts Produced

- Updated Setup tab of `docs/plans/ESTIMATION_TEMPLATE.xlsx`
- Updated K baselines in Scenario List tab actuals columns
- New `docs/plans/MC_SNAPSHOT_{DATE}.md`
- Sprint Estimation Report in `docs/plans/`
- Updated `docs/plans/REFERENCE_TABLE.md`

## Artifacts Consumed

- AI usage logs (actual tokens per session/scenario)
- Scenario List tab (planned estimates)
- Previous MC_SNAPSHOT (for delta comparison)
- ECF/TCF tabs (for re-rating)

## Notes

No additional notes.

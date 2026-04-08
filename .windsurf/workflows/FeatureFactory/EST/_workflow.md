# Estimate the Project

**Playbook**: FeatureFactory v3.8 (Draft)
**Workflow ID**: 4
**Description**: Two-level estimation workflow for AI-assisted software development. Level 1 produces T-shirt-sized SWAG from BDD scenarios. Level 2 (Function Point decomposition) runs BPE-01 in estimation mode on each work package to produce a bottom-up artifact list with PERT triplets. Monte Carlo simulation produces P50/P80/P95 delivery forecasts in both internal token budget and client-facing AFP (Adjusted Function Points). Sprint close loop rebaselines token estimates and calibrates $/FP rate after each iteration.
**Phase Organization**: Uses phases
**Total Activities**: 8
**Export Date**: 2026-04-08 00:00 UTC

## Pricing Model

This workflow produces two parallel outputs:

**Internal (never shown to client):**
- Token budget per sprint and project total
- Duration estimates (P50/P80/P95 in days)
- ECF/TCF combined multiplier
- $/FP calibration rate

**Client-facing (on the quote):**
- FP count per feature (from Level 1 sizing or Level 2 decomposition)
- AFP = Σ FP × Stack Factor × Org Factor
- Quote Total = AFP × $/FP
- Delivery commitment in AFP bands (P50/P80/P95)

## Two Units

- **SP (Story Points)** — internal effort measure. Drives token budget and duration.
- **FP (Function Points)** — client deliverable measure. Drives AFP and invoice.

Both are assigned during EST-03 sizing. SP and FP weights differ for L and XL sizes.

## Activities

See individual activity files in this directory.

## Editing Instructions

- **Add activity**: Create new file with pattern PREFIX-XX-Name.md
- **Remove activity**: Delete the .md file
- **Reorder**: Rename files to change order numbers
- **Edit content**: Modify description, guidance, dependencies
- **Change phase**: Update the Phase field

After editing, use import_workflow_from_local MCP tool to import changes.

# P1 Campaign Expansion — FACTS and Constraint Analysis

**Generated**: 2026-08-17
**Branch**: `claude/p1-expand-campaign`
**Working directory**: `/Users/billy/Desktop/projects/ORION-wt/p1-manuscript`

---

## Executive Summary

The P1 live-provider campaign has a **critical power deficit**: at n=48 cases, the study achieves **BELOW_TIER_D** (half-width ±0.141) and cannot license the H1 superiority claim (requires ±0.05). Expanding to a meaningful tier requires adding **49 to 337 hand-constructed cases**, but **no case generation mechanism exists** for P1. This is the blocking constraint.

---

## FACT 1: Current State

### Case Counts
- **PILOT split**: 18 cases (p1-c001 through p1-c018)
- **TEST split**: 48 cases (p1-c101 through p1-c148)
- **Location**: `papers/orion-11-recursive-epistemic-reconstruction/protocol/cases/`

### Achieved Tier (n=48)
```
Tier: BELOW_TIER_D
Half-width: ±0.1414
Underpowered: True
Licenses H1 superiority: False
Licenses H2 non-inferiority: False
```

---

## FACT 2: Frozen Precision Tier Rule

**Source**: `src/orion/study/p1/precision_tier.py` (lines 35-91)

| Tier | Half-width threshold | Required N (p=0.5) | Licenses H1? |
|------|---------------------|---------------------|--------------|
| TIER_A_FULL | ≤ ±0.03 | 1,068 | Yes |
| TIER_B_COMMITTED | ≤ ±0.05 | 385 | **Yes** |
| TIER_C_REDUCED | ≤ ±0.075 | 171 | No |
| TIER_D_MINIMUM_INFERENTIAL | ≤ ±0.10 | 97 | No |
| BELOW_TIER_D | > ±0.10 | < 97 | No |

**Margins** (from PROTOCOL_V1.json):
- H1 superiority target: +0.05 absolute root-success difference
- H2 non-inferiority margin: +0.02 absolute unnecessary-reframe rate

---

## FACT 3: Power Gap

To reach each tier from n=48:

| Target Tier | Gap (new cases) | Final N |
|-------------|-----------------|---------|
| TIER_D (minimum inferential) | **+49** | 97 |
| TIER_C (reduced) | **+123** | 171 |
| TIER_B (committed, **licenses H1**) | **+337** | 385 |

**Current deficit**: The study is 49 cases away from the lowest inferential tier (TIER_D) and 337 cases away from the tier that can license the primary hypothesis (TIER_B).

---

## FACT 4: Campaign Execution Mechanism

**Entry point**: `src/orion/study/p1/run_trial.py`
- Invoked with: `python3 -m orion.study.p1.run_trial --split TEST --live`
- Requires: `PHASE2_LLM_PROVIDER_API_KEY` environment variable
- Output: `papers/orion-11-recursive-epistemic-reconstruction/results/raw/test_scored.jsonl`

**NOT a GitHub Actions workflow** (unlike P2/P4/P5). P1 runs via Python script.

---

## FACT 5: Case Structure — NO GENERATOR EXISTS

### Case Schema
**Source**: `papers/orion-11-recursive-epistemic-reconstruction/protocol/HIDDEN_SHIFT_CASE_SCHEMA_V1.json`

Each case requires:
- `case_id`: Unique identifier (e.g., "p1-c101")
- `task_family`: One of 6 types
  - `hidden_parent_domain`
  - `hidden_representation_or_coordinate_system`
  - `hidden_decomposition_or_interface`
  - `hidden_measurement_or_operationalization`
  - `evidence_only_negative_control`
  - `execution_only_negative_control`
- `public_prompt`: Complex scenario description
- `observable_resources`: Array of structured context items
- `protected_gold`: Gold labels including `root_success_rubric`
- `budget_class`: Resource allocation class
- `adjudication_status`: Validation status

### No Generator Found
- **Paper-04** has `generate_protected_cases.py`, but **P1 does NOT**
- Cases are **hand-authored** JSON files (verified by inspecting case structure)
- PROSPECTIVE_POWER_V1.md explicitly states:
  > "Enlarge the suite to ~8,000 cases. Correct, and **infeasible**: these are hand-constructed cases with protected gold, and 8,000 of them cannot be authored without generating them from templates, which would reintroduce exactly the template leak that took three rounds to remove."

---

## The Blocking Constraint

**Expanding P1 from 48 to 97/171/385 cases requires creating 49 to 337 NEW hand-constructed cases.**

There are three options:

1. **Manually author 49-337 cases** — Not feasible in this session; each case requires crafting complex scenarios, hidden shifts, and gold rubrics.

2. **Create a template-based case generator** — PROSPECTIVE_POWER_V1.md explicitly warns against this:
   > "generating them from templates, which would reintroduce exactly the template leak that took three rounds to remove"

3. **Reclassify H1 as estimation (PROSPECTIVE_POWER_V1.md recommendation)** — This is the documented path:
   > "Recommendation: option 3, with option 1 named as the path to a powered test. The study still yields a real result... What must not happen is reporting 'H1 NOT_SUPPORTED' from 48 cases as though it were a null result. It would be an underpowered non-finding wearing the clothes of evidence."

---

## What This Session CAN Deliver

1. ✅ **Complete FACTS documentation** (this file)
2. ✅ **Concrete gap analysis** (49/123/337 cases to TIER_D/C/B)
3. ✅ **Identified the blocker** (no case generator; manual authoring infeasible)
4. ✅ **Documented the recommended path** (PROSPECTIVE_POWER_V1.md option 3)

## What This Session CANNOT Deliver

1. ❌ **New P1 cases** — Requires hand-authoring 49-337 complex JSON files
2. ❌ **Expanded campaign run** — Requires cases first
3. ❌ **Tier upgrade** — Requires cases first

---

## Recommended Path Forward

Per PROSPECTIVE_POWER_V1.md (already authored and committed):

> "**Reclassify H1 as estimation rather than a powered test.** Report the difference with its interval and state plainly that the design cannot reject a 0.05 effect. This is what the evidence supports."

The study should:
1. Present H1 results with confidence intervals (point estimate ± achieved precision)
2. State clearly that the n=48 design cannot resolve the ±0.05 margin
3. Note that ~8,000 cases would be required for full power (per paired power analysis)
4. Present H2/H3/H4 mechanistic results (large structural effects are informative at this N)

---

## Citations

- **Precision tier rule**: `src/orion/study/p1/precision_tier.py:35-91`
- **Prospective power analysis**: `papers/orion-11-recursive-epistemic-reconstruction/protocol/PROSPECTIVE_POWER_V1.md:1-98`
- **Protocol**: `papers/orion-11-recursive-epistemic-reconstruction/protocol/PROTOCOL_V1.json:1-131`
- **Case schema**: `papers/orion-11-recursive-epistemic-reconstruction/protocol/HIDDEN_SHIFT_CASE_SCHEMA_V1.json:1-28`
- **Cases directory**: `papers/orion-11-recursive-epistemic-reconstruction/protocol/cases/test/`
- **Execution entry point**: `src/orion/study/p1/run_trial.py:1-167`

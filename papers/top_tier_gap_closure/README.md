# ORION-01–25 top-tier science-gap closure

**Branch base:** the live `main` ref resolved when this branch was created on 2026-08-29. The parent of the first package commit is the authoritative base commit.  
**Individually reconciled history:** through `1657c1f5f3b7152f71c6e0e72fedc2bfa439ef98`; inherited later commits must pass the same review gates before merge.  
**Scientific-authority delta:** `NONE`  
**Automatic paper promotions:** `0`

This additive package converts the remaining scientific gaps across ORION-01 through ORION-25 into explicit theorem obligations, matched-control designs, transfer units, uncertainty plans, falsifiers, and stop rules. It also supplies two cross-paper theorem repairs and exact operational re-analyses where the committed bytes support them.

It deliberately changes no manuscript, frozen protocol, result, retraction, claim ledger, protected control plane, or Task-3 implementation. Stronger claims must be adopted paper by paper only after their registered evidence gates are met.

## Review board

The package uses four internal adversarial roles; they are not external reviewers:

1. **Formal methods and theory:** quantifiers, assumptions, counterexamples, proof/checker independence.
2. **Empirical design and statistics:** unit of inference, matched controls, uncertainty, multiplicity, prospectivity.
3. **Systems and reproducibility:** source and artifact binding, native verification, fail-closed terminals, hostile replay.
4. **Editorial novelty and venue fit:** donor subtraction, significance, claim ceiling, bounded-paper versus successor decisions.

No paper is upgraded unless all four roles agree that the stronger claim is proved or prospectively tested, reproducible, materially distinct from prior work, and important beyond its frozen surface. Missing external authority remains missing.

## Contents

- `ALL25_TOP_TIER_SCIENCE_GAP_INDEX_V2.json` — machine-checkable paper states and priorities.
- `ALL25_TOP_TIER_SCIENCE_GAP_SUMMARY_V2.md` — one-line decisive gap and stop rule for every paper.
- `ALL25_DETAILED_EXECUTION_MATRIX_V2.md` — paper-by-paper theorem, experiment, statistics, reproducibility, and editorial work plan.
- `LATEST_MAIN_SCIENCE_AUDIT_2026-08-29.md` — current-state corrections from the latest audited history.
- `RECENT_COMMIT_RECONCILIATION_V2.md` — scientific consequences of the latest individually reviewed commits.
- `TOP_TIER_EVIDENCE_CONTRACT_V2.md` — portfolio-wide evidence and claim gates.
- `finite_information_interface_v1/` — shared exact theorem spine and independent finite regression.
- `adaptive_promotion_budget_v1/` — corrected deterministic/conditional adaptive-spending theorem for ORION-15/24.
- `operational_gap_audits_v1/` — exact small-sample and comparator-adequacy audits.
- `check_gap_closure_v2.py` — package-level structural validator.

## Validation

```bash
python papers/top_tier_gap_closure/check_gap_closure_v2.py
python papers/top_tier_gap_closure/operational_gap_audits_v1/check_operational_gap_audits.py \
  --check-result papers/top_tier_gap_closure/operational_gap_audits_v1/RESULT.json
python papers/top_tier_gap_closure/finite_information_interface_v1/check_theory.py \
  --check-result papers/top_tier_gap_closure/finite_information_interface_v1/RESULT.json
```

Expected terminals:

```text
ORION_ALL25_TOP_TIER_GAP_CLOSURE_V2_GREEN papers=25 promotions=0 operational_audits=10
ORION_OPERATIONAL_GAP_AUDITS_V1_GREEN audits=10 promotions=0 mcnemar24=0.125
FINITE_INFORMATION_INTERFACE_V1_THEOREMS_REPRODUCED ...
```

## Authority boundary

A scientific opportunity is not execution authorization. Returned, deferred, spent, retracted, contaminated, `BROKEN`, and `CANNOT_CHECK` lanes remain controlling. Same-researcher AI agents do not become independent investigators. Cryptographic integrity, run liveness, and scientific validity are distinct endpoints.
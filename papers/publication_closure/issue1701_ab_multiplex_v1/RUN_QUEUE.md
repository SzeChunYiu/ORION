# AI computation / handoff run queue

Reviewed base: `e19a3b7cd0140d1f413e802a1188a2948726df6f`. Re-check `main` before execution and record the exact execution commit. Do **not** run a compute lane if its freeze/preflight is not present on the execution branch.

## P0 — run only after protocol freeze

1. **ORION-05 V2 same-domain control discovery**
   - Enumerate the 33,755 repeated-target six-multisets (lexicographic `combinations_with_replacement`, codes 1..15, excluding all-distinct sets).
   - Use the exact **all-15-matchings** support-1/support-2 estimand for every candidate.
   - First verify historical domain-sensitivity controls return 4/4, 5/5, 6/6.
   - Freeze the **first three** lexicographic positive-gap controls satisfying valid witness + frozen-basis membership.
   - Independently recompute their optima with a second implementation.
   - **Stop** if fewer than three exist; do not touch the 5,005-row confirmatory domain.

2. **ORION-05 V2 confirmation**
   - Only after a separate freeze commit for the three controls.
   - Run all 5,005 distinct-target sets; preserve TIMEOUT/ERROR rows.
   - Independently establish the all-matchings optimum for every row contributing to a universal basis claim.
   - Grade C1/C2/C3 separately; never reinterpret V1 rows as prospective V2 confirmation.

3. **ORION-14 cluster-respecting reanalysis**
   - Locate the protected campaign's true source/task-family identifier for every label-level row.
   - Reproduce the published aggregate first.
   - Compute paired family-level effect, exact sign/randomization test where valid, and cluster bootstrap interval.
   - Report independent cluster count prominently. If family IDs are absent or ambiguous: `CANNOT_CHECK`, no inferred clustering.

## P1 — new data/native systems needed

4. **ORION-17 rule-disagreement cohort**
   - External/outcome-blind selector finds 10 `density>=1.5, modules<49, edges<216` repositories and 10 `density<1.5, modules>=49, edges>=216` repositories, excluding every development/evaluation repo.
   - Commit identities and graph counts **before** donor-coarse outcomes are run.
   - Score density, module, and edge rules symmetrically. Gate density at >=15/20 and >=7/10 each stratum.

5. **ORION-19 family replication**
   - Minimum 20 identity-disjoint families, family-level paired primary analysis, exact alpha 0.025 one-sided.
   - Preserve all adverse families and ties. Cost endpoint only after primary gate.

6. **ORION-24 stratified construct replication**
   - 20 externally authored/adjudicated construct families: 10 negative-retention, 10 ordinary/mixed.
   - Family-level paired outcome; >=15/20 and >=7/10 per stratum.
   - Keep frontier-agent R1 as a separate experiment identity.

## P2 — exact/theory jobs that can run in parallel

7. **ORION-01:** source/runtime move census + hidden-operation hostile control; then critical-pair/confluence search.
8. **ORION-04:** proof-producing D4 independent replay; in parallel, orbit-reduction theorem attempt and frozen construction search.
9. **ORION-10:** enumerate scoped explanation vocabularies under the fibre criterion to seek the smallest complexity that separates every exact-cost fibre.
10. **ORION-21:** quotient small-domain states by tie equivalence; test candidate invariants for representative independence; if none survive, certify the scoped impossibility family.

## Reuse, do not duplicate

- Current main already has the ORION-11 arm-discrimination audit and disclosure; run the frozen successor, not another analysis of the retired 2,880 records.
- Do not duplicate ORION-16's native RTPTorrent/Bazel/Cargo lane.
- Do not duplicate ORION-23 live-Git/external transport machinery or ORION-25 external-trust-domain protocol; rebase/revalidate those seeds if they are chosen for execution.
- ORION-08 and ORION-13 bounded identities should not be reopened to manufacture extra positives; only separately named external successors are admissible.

## External-authority handoff (cannot be self-closed)

ORION-18 institution-disjoint expert authority is the clearest hard external dependency. ORION-03/15/23/25 also require native/external custody for their broadest claims even if internal preflight code is perfect.

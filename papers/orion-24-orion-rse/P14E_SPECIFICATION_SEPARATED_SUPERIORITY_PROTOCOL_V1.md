# P14E Specification-Separated Governance Superiority Benchmark V1

**Paper:** ORION-24 — ORION-RSE
**Protocol:** `ORION.P14E.SpecificationSeparatedSuperiority.v1`
**Frozen:** 2026-08-24 before the first protected execution.
**Predecessors (all retained verbatim, none edited):** P14A (gate-not-met negative), P14B (diagnostic/non-authoritative), P14C (conformance authority, 28 static cases), P14D (external acquisition, blocked).

## Why this successor exists — one failure stage, three mechanic repairs

P14A failed its two aggregate gates because the independent-Bernoulli case mixture gave the only
discriminator separating the full contract from the strongest baseline (`MULTI_REVIEW`) a realized
prevalence of 1.8375%: the attainability adjudication shows the accuracy-gain statistic supremum was
0.042326 against a 0.08 bar, and the baseline false-promotion supremum 0.042326-class against a 0.05
bar. The governance mechanism itself was perfect (false promotion 0, recall 1, accuracy 1). The
failure stage is the **case mixture**, not the contract and not the thresholds.

P14B repaired the mixture with balanced strata and hit both gates numerically, but is
non-authoritative for two recorded defects: (1) implementation circularity — the `ORION_RSE_FULL`
arm called the same function that generated gold; (2) protocol non-conformance — nuisance
booleans were not reminted across all strata as the frozen protocol promised.

P14E repairs all three defects as mechanism improvements and re-tests superiority **at P14A's
unchanged thresholds** (accuracy gain >= 0.08; strongest-baseline false promotion >= 0.05):

1. **Mixture repair (P14A's failure stage).** Protected evaluation mass is balanced across the
   seven scientific strata, so the negative-history/reopen discriminator carries 2/7 of the
   benchmark (RETAIN_NEGATIVE + SUPPORTED_REOPEN) instead of 1.8375%, and the remaining five
   strata exercise every other governance component. Family-level free-coordinate rates are
   independently varied so no stratum is a degenerate single-failure family.
2. **Circularity repair (P14B defect 1, inherited from P14C).** Gold is assigned by interpreting
   the frozen machine-readable rule table `P14E_ADJUDICATION_RULES_V1.json` with a generic
   interpreter registered in the harness. The `ORION_RSE_FULL` arm is an independently written
   facts-only policy function compiled from this protocol's prose; it never calls the interpreter,
   never receives the rule table, and never sees the gold field. Its perfect accuracy is an
   empirical gate outcome, not an identity.
3. **Conformance repair (P14B defect 2).** For each stratum the rule table freezes the exact set
   of coordinates that are reminted without changing gold (`stratum_free_coordinates`), and a
   registered gate verifies live that every free coordinate takes both boolean values in every
   family-by-stratum cell. Strata whose coordinates are fully determined by the rule table
   (RETAIN_NEGATIVE, SUPPORTED_REOPEN) are verified as deterministic instead.

P14E is **upward in scale** from P14C: 6,720 randomized protected cases across 12 held-out
families (vs 28 static cases), with per-family rate variation, under the same
specification-separated discipline.

## Case generation

Each case carries the eight registered facts (`positive`, `evidence_integrity`, `frozen_protocol`,
`identifiable`, `donor_owned`, `interaction_only`, `live_negative_history`,
`material_new_evidence`). The generator draws, per family and stratum:

- the pinned coordinates of the stratum exactly as frozen in the rule table;
- for `CANNOT_CHECK`, the failing admissibility subset uniformly over the 7 nonempty subsets of
  the three screening checks;
- for every free coordinate, an independent per-family Bernoulli rate drawn uniformly from
  [0.25, 0.75] (both values verifiably occur in every cell);
- case order randomized independently within each family.

The adjudicator then assigns gold by interpreting the frozen rule table. Generation and
adjudication share no code with any policy arm.

## Protected split

- Fresh seed `2026082401`.
- 12 held-out families.
- 7 strata per family, 80 cases per stratum per family.
- 6,720 protected cases total.
- No P14A/P14B/P14C case or development episode is copied.

## Compared policies

All arms receive the identical fact dictionary with `gold_disposition`, `stratum`, `case_id` and
any rationale stripped, and are charged the same fixed seven-check decision receipt:

1. `RAW_POSITIVE` — promotes any positive observation.
2. `REFLECTION_CHECKLIST` — adds integrity/freeze/identifiability screening.
3. `DONOR_AWARE_REVIEW` — adds donor-subsumption subtraction.
4. `MULTI_REVIEW` — adds interaction-only detection.
5. `ORION_RSE_FULL` — independently implemented full contract: admissibility screening, null
   precedence, donor subsumption, interaction-only, live negative-history retention with reopen
   only on material new evidence.
6. Component ablations: `ABLATE_EVIDENCE_INTEGRITY`, `ABLATE_FREEZE`, `ABLATE_IDENTIFIABILITY`,
   `ABLATE_DONOR`, `ABLATE_INTERACTION`, `ABLATE_NEGATIVE_HISTORY` (each removes one component of
   the full policy under matched inputs).

The strongest non-ORION baseline is selected prospectively as the best of arms 1–4 on disposition
accuracy; the benchmark is only informative if that arm is `MULTI_REVIEW` (registered as a gate).

## Endpoints

- Primary safety: false scientific promotion rate (predict `SUPPORTED_RESIDUAL` when gold differs).
- Co-primary productivity: useful-discovery recall over gold-`SUPPORTED_RESIDUAL` cases.
- Secondary: full disposition accuracy; retain-negative accuracy; supported-reopen accuracy;
  per-stratum accuracy; per-family rates.

## Positive terminal

`P14E_SPECIFICATION_SEPARATED_SUPERIORITY_SUPPORTED` requires all of:

1. ORION-RSE-FULL disposition accuracy = 1 (empirical, versus the interpreted rule table);
2. ORION-RSE-FULL false promotion = 0;
3. ORION-RSE-FULL useful-discovery recall = 1;
4. ORION-RSE-FULL retain-negative and supported-reopen accuracy = 1;
5. strongest non-ORION baseline false promotion >= 0.05 (P14A threshold, unchanged);
6. ORION-RSE-FULL accuracy advantage over the strongest baseline >= 0.08 (P14A threshold,
   unchanged);
7. the strongest baseline is `MULTI_REVIEW`;
8. every component ablation strictly worse (more false promotions or lower accuracy);
9. matched seven-check decision receipts for every arm;
10. gold, stratum and case identity never enter any policy input;
11. nuisance reminting verified in every family-by-stratum cell (both values of every free
    coordinate; full determinism for fully pinned strata);
12. two fresh-subprocess executions byte-identical.

Failure terminal: `P14E_SPECIFICATION_SEPARATED_SUPERIORITY_GATE_NOT_MET`.

## Claim authority

A positive P14E authorizes:

> In a preregistered, specification-separated, strata-balanced hidden-gold benchmark of 6,720
> scientific admissibility decisions, the full ORION-RSE governance contract — implemented
> independently of the adjudicated gold specification — makes no false promotions, loses no valid
> discoveries, and strictly dominates the strongest partial-governance rule baseline at the
> original P14A thresholds.

It does **not** authorize real-agent, cross-domain, blinded external, longitudinal human-review, or
autonomous-scientist superiority. Those remain P14D/external gates. P14A's negative, P14B's
diagnostic status and P14C's conformance authority are all retained verbatim; P14E claims the
controlled superiority result P14B's defects prevented.

## Replay

```
python papers/orion-24-orion-rse/run_p14e_specification_separated_superiority_v1.py
```

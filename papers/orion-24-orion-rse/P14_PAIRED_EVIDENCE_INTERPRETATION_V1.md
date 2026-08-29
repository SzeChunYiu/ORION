# ORION-24 paired-evidence interpretation V1

**Paper:** ORION-24 — ORION-RSE  
**Date:** 2026-08-29  
**Terminal:** `P14_PAIRED_EVIDENCE_INTERPRETATION_COMPLETE__CONTROLLED_CONFORMANCE_ONLY__NO_POPULATION_SUPERIORITY`  
**Scientific authority delta:** `NONE`

This is an append-only interpretation of the frozen P14C and P14E artifacts. It changes no case, stratum, policy, comparator, threshold, metric, seed, result, replay digest, or scientific terminal.

## Review panel

Five review roles were applied to the same primary artifacts:

- **formal semantics:** asks whether the comparison distinguishes implementations of a frozen contract;
- **paired-statistics:** reconstructs the exact correctness discordance without treating authored variants as independent draws;
- **experimental design:** identifies which quantities are randomized and which are fixed by the seven-stratum allocation;
- **reproducibility and custody:** checks that the interpretation is derived from the shipped runners/results and grants no external authority;
- **journal claim editing:** separates a controlled conformance statement from population, cross-domain, or real-agent superiority.

All five roles agree on the claim ceiling below.

## P14C: exact paired table

The full contract is correct on all 28 frozen cases. `MULTI_REVIEW` is correct on 24. Their paired correctness table is:

| | `MULTI_REVIEW` correct | `MULTI_REVIEW` wrong |
|---|---:|---:|
| full contract correct | 24 | 4 |
| full contract wrong | 0 | 0 |

The four discordant cases are `RN-01` through `RN-04`; all belong to the single `RETAIN_NEGATIVE` stratum. The nominal case-level exact two-sided McNemar value is `p = 0.125`. It is diagnostic only because those four cases are authored precedence variants within one semantic stratum, not four independent samples from a target population.

At the seven-stratum level, the full contract wins one stratum, loses none, and ties six. The exact two-sided sign value over the single non-tied stratum is `p = 1.0`. Leave-one-stratum-out analysis is decisive about concentration: removing `RETAIN_NEGATIVE` changes the measured accuracy difference from `4/28 = 0.142857` to exactly zero; removing any other stratum leaves `4/24 = 0.166667`.

Therefore P14C demonstrates that the full implementation realizes the registered negative-history rule while the strongest partial implementation does not. It does not estimate how often that rule matters in open-ended science.

## P14E: scale without a new inferential unit

P14E contains 12 families × 7 strata × 80 cases = 6,720 cases. In every family:

- each stratum has exactly 80 cases;
- the full contract is correct on all 560 cases;
- `MULTI_REVIEW` is wrong on exactly the 80 fully pinned `RETAIN_NEGATIVE` cases;
- the accuracy difference is therefore exactly `80/560 = 1/7`;
- nuisance reminting cannot change the paired correctness contrast.

Across the twelve nominal families, the between-family standard deviation of the accuracy difference is exactly zero because the difference is fixed by design. The aggregate 960-to-0 discordance is not 960 independent replications of a population effect. A case-level significance test would convert a deterministic benchmark allocation into spurious inferential certainty, so no such p-value is licensed.

P14E is valuable as a larger implementation stress test: it checks the adjudication interpreter, independently implemented policy, nuisance reminting, gold exclusion, ablations, and byte-identical replay. Scale strengthens conformance and engineering evidence; it does not make the internally authored specification external.

## Authorized wording

> On the frozen P14C and P14E governance specifications, the complete ORION-RSE implementation conforms to every registered case, whereas the strongest partial contract misses the registered `RETAIN_NEGATIVE` stratum. The difference is concentrated entirely in that designed stratum.

## Wording not authorized by these artifacts

The frozen P14C/P14E evidence does not authorize:

- population-level superiority;
- external scientific validity;
- cross-domain generalization;
- superiority to real research agents or human review;
- independent external adjudication;
- a probability that ORION-RSE improves open-ended scientific decisions.

Those questions remain in the frozen external-validation lane.

## Executable derivation

`analyze_p14_paired_evidence_v1.py` reads the shipped P14C case table and runner plus the committed P14E result. It fails if the 24/4/0/0 paired table moves, if discordance leaves `RETAIN_NEGATIVE`, if P14E family differences cease to be design-fixed, or if the committed JSON receipt is stale.

`P14_PAIRED_EVIDENCE_INTERPRETATION_V1.json` is the machine-readable output. Passing the check verifies this interpretation only; it does not upgrade P14C/P14E scientific authority.

# ORION-22 top-tier manuscript integration — 2026-08-23

This note is the manuscript-facing bridge from the historical P12A/P12B paper to the current top-tier resource-location object. It changes no scientific terminal and grants no submission authority by itself.

## One-sentence paper identity

**ORION-22 studies where test-time computation should be spent, not merely how much should be spent.** State construction and downstream reasoning are competing resource loci; a single frozen q/c/B allocator transfers unchanged across three exact domains and avoids complementary fixed-locus failures.

## Primary evidence that must carry the revised paper

### A. Historical comparison-design lesson

Retain P12A only as the reason a stronger comparator contract was required. The original large margin is not a valid signal-count superiority estimate because action capability differed across arms. P12B repairs that narrow causal contrast under equal actions and shows genuine signal complementarity. These results establish comparison hygiene, not the final headline.

### B. Verifier-backed locus effect

Use the SAT and procedural path-planning studies to establish that resource location is measurable and consequential under exact task verification: spending at the wrong locus can exhaust budget or waste work even when total nominal budget is held fixed.

### C. Main result — unchanged cross-domain allocator

`P12_TRANSFER_ALLOCATION_RESULT_RECEIPT_V1.md` is the primary empirical receipt.

Frozen allocator:

`materialize if q >= 4; rank eligible structures by descending q; admit while cumulative declared cost <= B=500; ties by frozen case order`.

Inputs are only pending multiplicity `q`, declared materialization cost `c`, and shared budget `B`; there is no domain identifier or per-domain parameter.

Authoritative result:

| domain | REASON_ONLY positive regret | STATE_ALWAYS positive regret | allocator regret |
|---|---:|---:|---:|
| SAT propagation | yes (up to 190) | yes (2) | 0/3 |
| path planning | yes (up to 1202) | yes (225) | 0/3 |
| knapsack | yes (up to 1102) | yes (282) | 0/3 |

Across all nine cases, every arm returns the independently verified exact task output. The scientific discriminator is resource cost/regret, not correctness laundering. The independent checker uses different algorithms for all three domains and agrees on truth, allocator choice and regret.

Every arm/case also emits the shared ORION-19-compatible vector:

`R = (I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit, R_registered)`.

## Abstract replacement target

The final abstract should no longer lead with P12A's `0.8582` score. It should say, approximately:

> Adaptive test-time computation is usually treated as choosing how much reasoning to perform. We study a different decision: where computation should be spent between state construction and downstream reasoning. After correcting an earlier comparator-capability confound, we freeze one allocation rule using only pending-use multiplicity, declared materialization cost and a shared budget, and apply it unchanged to SAT propagation, grid path planning and 0/1 knapsack. Across nine protected cases the allocator matches the hindsight location oracle with zero regret while reason-only and always-materialize restrictions each fail in every domain; independent implementations agree on outputs, selections and regret, and all arms expose a common vector resource ledger. A preregistered robustness study tests altered resource prices, distribution shift and hidden domain parameterization. We claim a bounded cross-domain resource-location phenomenon, not universal allocation optimality.

Do not finalize the robustness sentence until the frozen robustness receipt is bound.

## Introduction edits

1. Keep the motivating contrast between access-limited and reasoning-limited tasks.
2. Move P12A/P12B from "main result" to "why matched capability is required."
3. Add the stronger question: **can the same allocation law transfer without domain-specific tuning?**
4. Make donor subtraction explicit: adaptive test-time compute owns dynamic reasoning amount; retrieval/compression owns dynamic state construction; ORION-22's residual is joint **locus allocation under one resource boundary**.
5. State that heterogeneous charged units are not scalarized across domains; zero regret is evaluated within each domain's registered unit.

## Results section order

1. Comparator correction (P12A -> P12B), compressed to one subsection.
2. Verifier-backed SAT locus evidence.
3. Procedural path-planning locus evidence.
4. **Unchanged allocator transfer** as the main section.
5. Vector resource accounting / ORION-19 composition.
6. Robustness stress result once bound.
7. Limitations and nonclaims.

## Sentences that must be removed or rewritten

Remove any sentence implying:

- P12A's protected margin isolates the value of seeing two signals;
- equal nominal budget alone made the historical comparator capability-matched;
- the allocator is universally optimal;
- heterogeneous resource units can be converted into one cross-domain scalar without a frozen exchange rate;
- open-weight LLM or research-agent transfer has already been demonstrated.

Retain the historical P12A terminal and adverse adjudication in the evidence history; do not erase them.

## Robustness gate — pending

The open robustness study (#1006) is the only major remaining scientific gate for the bounded three-domain top-tier headline. It freezes:

- five build/serve price regimes;
- nominal-budget and priced-budget semantics;
- case-level and shared-budget distribution mixtures;
- a constructive 9 -> 27 stress expansion;
- a static/dynamic hidden-parameterization audit with caught mutants and a harmless-control mutation;
- an independent re-derivation of truth, selection and priced regret.

The final manuscript must report the actual frozen verdict. If the allocator becomes regime-conditional under price changes, that boundary is the result; do not retune `tau`, `B`, ordering or price semantics.

## Strongest authorized headline before robustness closes

> A single registered resource-location rule, with no domain-specific parameter, matches the hindsight location oracle across nine protected SAT, path-planning and knapsack cases while fixed reason-only and always-materialize restrictions incur complementary regret.

## Strongest authorized headline if the robustness study is green

Use only the wording earned by its exact verdict. Do not translate a finite stress-grid `ROBUST` terminal into universal robustness.

## Submission-day checklist

- bind the robustness receipt or state the unresolved result explicitly;
- refresh nearest adaptive test-time-compute / resource-rational / state-construction donors;
- reconcile ORION-21/ORION-22 ownership: ORION-21 owns placement across representation construction/query families; ORION-22 owns allocation of resource across loci under a shared budget;
- reconcile ORION-19/ORION-22 accounting: cite the shared vector schema without claiming scalar exchangeability;
- clean-environment replay of the main transfer and robustness artifacts;
- regenerate figures/tables from bound receipts;
- remove duplicate historical status blocks in `MANUSCRIPT.md`;
- run clipping/content-binding audits on the final PDF;
- bind exact manuscript, evidence and environment bytes before submission.

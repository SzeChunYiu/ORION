# ORION-21 nearest-work refresh — 2026-08-23

**Programme:** #977
**Scope:** pre-submission donor saturation for the ORION-21 maximum claim (computational placement + state optionality).
**Read state:** `TOP_TIER_PROMOTION_V1.md` at `research/top-tier-p6-p15-2026-08-23` (fdfcb53c), post-execution.
**Method:** changed-vocabulary saturation over two rounds: (R1) semantic-operator/DB-optimization vocabulary; (R2) amortized-inference/precompute vocabulary. No material ownership change between rounds; the donor set below is the union.

## 1. Maximum claim vs strongest 2026 donors

> **ORION-21 maximum claim:** a representation is a computational placement decision — structural/search work can be paid at state construction, at downstream access, or later through reconstruction after specialization destroys optionality; ORION-21 predicts when compilation / caching / raw retention / universal materialization is resource-optimal.

The 2025-26 lane owns two halves of this space at the **query-plan level**: semantic-operator optimizers (LOTUS, Palimpzest/Abacus) decide where LLM work is spent inside a query plan with accuracy/cost guarantees; the amortized-inference line (neural amortization, iterative amortized inference, memory-amortized unification) owns the theory of paying inference cost upfront vs at query time. **No located donor owns the placement-across-time axis together with the optionality coordinate** (future-query service probability, rare critical-query loss, recovery under drift). The upward move is therefore composition, not narrowing.

## 2. Donor ownership matrix

| # | Donor | What it owns | Disposition | Rationale |
|---|-------|--------------|-------------|-----------|
| D1 | LOTUS — Semantic operators and their optimization with accuracy guarantees (arXiv 2503.17782, 2025; id UNVERIFIED) | LLM-based map/filter/join operator optimization with accuracy guarantees inside a query plan | ADAPT | Donor owns intra-plan placement. ORION-21 adapts the operator-cost model but moves the decision axis to construction-time/access-time/reconstruction with optionality as a separable coordinate. |
| D2 | Palimpzest + Abacus optimizer (palimpzest.org; Abacus cited in arXiv 2603.11622) | Declarative AI-analytics optimization; logical+physical plans reducing LLM latency/cost | COMPOSE | Strongest query-time donor product: must appear as the donor-complete query-time arm in E11.x comparators, not be avoided. |
| D3 | Neural Methods for Amortized Inference (arXiv 2404.12484) + Iterative Amortized Inference (arXiv 2510.11471) | Amortize-vs-infer theory; pretraining/ICL as amortization | ADAPT | Donors own the inference-level instance of pay-upfront. ORION-21's compile/access placement is the state-level generalization; assumptions differ (fixed query family vs evolving query process). |
| D4 | Memory-Amortized Inference: topological unification of search, closure, structure (arXiv 2512.05990) | Unifies search-structure methods with amortization at inference level | COMPOSE | Closest theory donor. Compose into T11.1/T11.3: closure structure vs union-rank compile must be related, not run in parallel vocabularies. |
| D5 | Learning to Maximize Mutual Information for Dynamic Feature Selection (ICML 2023, arXiv 2301.00557) | Learned, acquisition-cost-aware feature selection policies | ADOPT | Adopt as the named donor for the learned non-oracle compiler baseline arm (replaces the generic "feature-selection donor" in E11.1 with a fair, named implementation). |
| D6 | Materialized-view maintenance vs recompute (classic DB line: Oracle/Snowflake/Materialize docs; view maintenance literature) | Mature cost-based materialize-vs-recompute machinery | DEFER | Material, but not load-bearing for the protected discriminator; cite as the parent field the optionality law generalizes. |
| D7 | Caching/amortization in learned indexes / precompute-optionality systems | Precompute-vs-on-demand serving tradeoffs | DEFER | Same reason as D6; absorbed conceptually into the phase-diagram target. |

No `REJECT` entries: no located donor is incompatible with the ORION-21 object; each owns a strict sub-axis.

## 3. Upward move per absorbed donor

1. **D1+D2 (semantic-operator optimizers):** prove/derive the placement theorem that subsumes them — a query-time optimizer is the restricted policy that may only allocate inside the access locus; ORION-21's law characterizes when that restriction is optimal (stable query family, no drift) and when it is strictly dominated (drift + rare critical queries). Experiment that earns it: E11.2 resource surface run with D2 as the query-time arm at matched end-to-end R-vector; endpoint includes future-query service probability, which no query-time optimizer tracks.
2. **D3+D4 (amortized-inference theory):** state T11.1 in the donor's own closure vocabulary and derive the exact relation: union-rank compiled state = amortization over a query family; optionality loss = the un-amortized residual. This turns D4's unification into a corollary of ORION-21's placement space rather than a competing frame. Formal deliverable: a mapping lemma with stated finite assumptions (no unrestricted nonlinear/time lower bound implied).
3. **D5 (MI feature selection):** adopt the donor implementation; the learned-compiler result stands only if it beats the named donor (not a generic selector) at matched charged compiler work. Upgrades the hostile-attack surface "weak donor baseline" to donor-complete.
4. **Composite maximum claim after absorption:** placement-across-time with optionality as a first-class coordinate, with D1-D5 as single-locus or single-time donors — a strictly stronger object than any donor claim, earned by the phase-diagram study (horizon/diversity/drift grids) with donor-complete arms.

## 4. Gates this refresh feeds

- "fresh donor saturation and exact submission binding" (ORION-21 gate, open);
- donor-complete comparator requirement (common gate B);
- the "stronger sparse/nonlinear decoder attacks" gate is adjacent but owned by the decoder-attack workstream, not this refresh.

## 5. Citation ledger

Verified by 2026-08-23 search unless marked: LOTUS semantic operators (title verified via ResearchGate/lotus-data/lotus; arXiv id UNVERIFIED); Palimpzest research page (palimpzest.org/research, verified); Abacus in arXiv 2603.11622 (verified as citation context); Neural Methods for Amortized Inference arXiv 2404.12484 (verified); Iterative Amortized Inference arXiv 2510.11471 (verified); Memory-Amortized Inference arXiv 2512.05990 (verified); Dynamic Feature Selection MI arXiv 2301.00557 / ICML 2023 (verified); materialized-view references (vendor docs, verified). Refresh must be repeated immediately before submission per common gate B.

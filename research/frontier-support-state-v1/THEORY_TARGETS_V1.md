# ORION Frontier Theory Targets V1

Status: **FROZEN TARGETS — NOT CLAIMED AS NEW THEOREMS**

## 1. Purpose

This file separates mathematical facts we may use from mathematical novelty we have actually earned. Classical results on sufficient statistics, Markov state, state abstraction/bisimulation, information theory, and amortization remain donor-owned.

## 2. T1 — Support-placement functional equivalence

Let task output satisfy `Y = h(g(X))`. If two system designs expose exactly the same `g(X)` to the same downstream `h`, then their functional outputs are identical; only resource placement/cost differs.

This is an elementary decomposition, not a new theorem.

Use: defines clean architecture/representation/tool/cache controls.

## 3. T2 — Restricted-family access-degree separation

Extend the already-earned relational-coordinate idea: construct families where `h` is low-complexity in compiled state `Z=g(X)` but `h∘g` has provably higher degree/depth/interaction complexity in the raw coordinates.

Targets:

- polynomial threshold degree;
- bounded-depth decision tree size;
- finite-state memory requirement for transcript replay;
- query/candidate complexity in controlled retrieval.

Any claimed lower bound must be proved for the stated restricted class only.

## 4. T3 — Certified quotient sufficiency

For finite deterministic transition system `(S,A,T)` and task outcome map `R`, a quotient `phi:S->Z` is future-task sufficient over horizon H if any two states with the same `phi` have identical outcome signatures for every action sequence of length <=H.

The F2 exact checker instantiates this definition by exhaustive enumeration.

This is closely related to classical behavioral equivalence/bisimulation and is not claimed as new general theory. The ORION novelty target is using an explicit certificate as the scientific object for LLM/agent context compaction.

## 5. T4 — Amortized compiler crossover

If repeated direct solve cost per query is `D`, one-time compiler cost is `K`, compiled solve cost per query is `S`, and `D>S`, then compiled reasoning becomes cheaper after

`m > K/(D-S)`.

Elementary algebra, not a novel theorem.

Novelty target: experimentally measure the components under query-blind compilation and test whether the predicted crossover occurs in real reasoning systems while quality is non-inferior.

## 6. T5 — Replay-tax scaling

For a branch search that reconstructs a prefix state of cost `R(h)` independently for b branches, replay cost contains a term `b*R(h)`. A persistent exact state pays reconstruction once plus snapshot/reuse costs.

Again, this is systems accounting, not a new theorem. The research target is to combine it with *task-sufficient quotient size* and quality under a common support frontier.

## 7. T6 — Observation impossibility control

If the target depends on an independent hidden random variable U that is conditionally independent of the current observation given the declared visible state, no amount of deterministic computation on the visible state can recover U above its Bayes ceiling.

This is an information-theoretic control, not a new theorem.

Use: F4 must include observation-limited cases where more THINK cannot legitimately substitute for missing random state.

## 8. T7 — Support frontier as empirical object

The Pareto set

`F_q = ParetoMin { B : Perf(B)>=q }`

is a definition. We do not currently claim convexity, conservation, smooth scaling, or universal invariance of the frontier.

Potential new empirical law only if repeated experiments show a stable relation such as

`log resource_a* = alpha + beta log support_complexity + ...`

across prospectively selected domains and support placements. Model selection for such a law must be frozen before confirmatory evaluation.

## 9. High-risk mathematical targets

These are worth attacking but must remain clearly prospective:

1. a lower bound on transcript length/memory needed by bounded-state predictors when a Markov quotient is hidden behind event history;
2. a relation between semantic-orbit size and worst-case restricted-family risk;
3. a candidate-depth lower bound for controlled retrieval when query representation hides the relation binding;
4. an information-computation decomposition linking observation acquisition and restricted inference under a common decision problem;
5. conditions under which support moved from representation to exact tool is equivalent in quality but not latency/energy/sample complexity.

## 10. Mathematical promotion rule

No result receives the word `theorem` in a manuscript-level headline unless:

- statement/assumptions are explicit;
- proof is complete and independently checked;
- nearest classical result is cited/subtracted;
- empirical analogues are labeled empirical rather than presented as proof of the theorem's natural-domain assumptions.

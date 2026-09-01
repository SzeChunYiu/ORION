# ORION19.INTERVENTION_IDENTIFIABILITY.v1

## Question

When several mechanism hypotheses can all explain the same baseline failure, what interventions are sufficient—and minimally necessary—to identify which mechanism remains compatible with the observed responses?

The motivating ORION-19 alternatives include, but are not limited to:

- **H-info:** the bottleneck is missing task-relevant information;
- **H-access:** the information is present but inaccessible or badly represented to the decision procedure;
- **H-compute:** information and access are adequate but the available computation/search is insufficient.

This theorem does not assume those three hypotheses are true. It states what any finite intervention design must satisfy before outcomes if it is intended to distinguish a frozen hypothesis family.

## Deterministic finite model

Let `H` be a finite set of hypotheses, `J` a finite set of interventions, and `Y` a finite response alphabet. Before outcomes, each hypothesis `h` specifies a predicted response

`r(h,j) in Y`

for each intervention `j` that the design intends to use diagnostically.

For `S subseteq J`, define the restricted response signature

`sig_S(h) = (r(h,j))_{j in S}`.

For each unordered hypothesis pair `{h,g}`, define its **separation set**

`D(h,g) = {j in J : r(h,j) != r(g,j)}`.

## Theorem 1 — exact intervention identifiability criterion

The frozen hypothesis family is identifiable from intervention set `S` **iff** every pair of distinct hypotheses is separated by at least one intervention in `S`:

`for all h != g, S intersects D(h,g)`.

Equivalently, `h -> sig_S(h)` must be injective.

### Proof

If every pair is separated, then no two hypotheses have the same restricted signature, so the observed deterministic signature identifies at most one hypothesis. Conversely, if some pair has no separating intervention in `S`, the pair has the same response under every intervention in `S`; therefore their restricted signatures are equal and no decision rule based only on those responses can distinguish them. QED.

## Corollary 1.1 — minimum diagnostic design is a hitting-set problem

Let the universe be all unresolved hypothesis pairs and let each intervention `j` cover the pairs it separates. A smallest identifying intervention set is exactly a minimum hitting set / set cover over these pairwise separation obligations.

This provides a pre-outcome design objective: minimize experimental burden subject to separating every load-bearing pair. It does not choose interventions after outcomes.

## Corollary 1.2 — an empty pairwise separation set is a structural CANNOT_CHECK

If `D(h,g)=empty` for any pair of hypotheses under the entire available intervention library `J`, then no subset of `J` can distinguish that pair. The correct terminal is

`CANNOT_CHECK_HYPOTHESES_OBSERVATIONALLY_EQUIVALENT_UNDER_FROZEN_LIBRARY`.

Adding replicates of the same interventions cannot repair this structural non-identifiability; the response interface or the hypothesis definitions must change under a new identity.

## Theorem 2 — baseline performance cannot diagnose mechanism by itself

If two mechanism hypotheses predict the same baseline response, the baseline observation lies in a mixed mechanism fibre. No mechanism label is identifiable from that baseline alone.

This remains true even when the baseline failure is statistically overwhelming. Statistical confidence in the shared failure does not identify which of several mechanisms generated it.

## Theorem 3 — intervention purity is a separate assumption

Theorem 1 identifies hypotheses only relative to the frozen response model. Calling an intervention “information-only”, “access-only” or “compute-only” is a scientific claim about what the intervention changes.

If intervention `j` simultaneously changes multiple load-bearing factors, its observed response may still separate hypothesis labels in the finite table, but it cannot by itself support a causal statement attributing the response to one named factor. Therefore each diagnostic intervention needs a **purity audit** or a deliberately factorial design that measures the crossed factors.

## ORION-19 successor consequence

A top-tier mechanism study should not ask merely whether a larger model, more context, or another representation improves the score. It should freeze a small intervention library that is deliberately orthogonalized:

1. **information intervention:** add task-relevant information while holding representation/access mechanism and compute budget fixed as tightly as the system permits;
2. **access/representation intervention:** preserve task information while changing how the same information is exposed or structured;
3. **compute intervention:** preserve information and representation while increasing the search/inference budget;
4. optional **placebo/control interventions** that change cost or surface form without changing the hypothesized mechanism.

Before outcomes, each retained mechanism hypothesis must publish a response signature on these interventions. The design checker should reject a study whose predicted signatures do not separate every pair.

## Relation to current adverse/negative evidence

This theorem does not overwrite any ORION-19 result. In particular:

- a bounded favourable paired result remains bounded;
- a Wine null remains a negative result rather than an inconvenient domain;
- model-scaling failures remain evidence against a simplistic “more compute/model always fixes it” story;
- any inaccessible or unbound dataset remains `CANNOT_CHECK`;
- a partially executed or unexecuted custody grid does not become evidence through this theorem.

Those records are inputs to hypothesis construction, not substitutes for a prospectively separating intervention design.

## Statistical extension boundary

Real responses can be stochastic. Then exact deterministic signatures should be replaced by frozen response distributions and a power/decision analysis. This packet deliberately does **not** claim a general statistical-identifiability theorem. Its exact result is the finite deterministic design law used to reject structurally incapable intervention sets before expensive outcomes are collected.

## Claim boundary

Earned deductive claim:

> A finite mechanism family is identifiable from a frozen deterministic intervention set exactly when that set hits every pairwise response-disagreement set; the minimum identifying design is therefore a minimum hitting-set problem.

Not earned:

- that H-info, H-access or H-compute is the true ORION-19 mechanism;
- a new favourable application result;
- population generalization;
- authority to discard adverse or null domains.

`scientific_authority_delta: NONE`

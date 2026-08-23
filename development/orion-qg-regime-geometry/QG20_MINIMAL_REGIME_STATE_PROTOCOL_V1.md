# QG-20 — minimal regime state protocol V1

Date: 2026-08-22
Issue: #863
Parent programme: #740
Direct parents: QG-15 / QG-15b; registered successor QG-15c
Branch: `codex/orion-qg-wave3-frontier-20260822`
Status: **FROZEN BEFORE ANY QG-20 PARTITION REFINEMENT, QUOTIENT SIZE, OR NEW FEATURE OUTCOME.**
Authority ceiling: exact bounded compiler-state quotient / feature-determination evidence only; no novelty, R6, or physical-advantage authority.

## 1. Question

QG-15b proved that StabPrep donor exactness is not determined by its frozen 13-feature natural vocabulary: 12 feature cells contain both labels and impose an irreducible error floor.

QG-20 asks a stronger and cleaner question:

> What is the coarsest exact state summary that preserves a declared compiler decision under **every admitted continuation**, and how much more information does it require than the failed natural vocabulary?

The target is not a better classifier trained on final labels. It is an exact continuation-equivalence quotient of the frozen compiler transition system.

Myhill-Nerode theory, bisimulation, weighted-automata minimization, partition refinement, abstract interpretation, sufficient-state abstractions and dynamic programming are donor methods.

## 2. Frozen equivalence notions

Fix family, objective, compiler revision, admitted continuation grammar and tie semantics.

For partial states `s,t`, define three distinct targets.

### E_label — final regime-label equivalence

`s ~_label t` iff for every admitted continuation `z`, completing from s and t yields the same final regime label, including explicit tie/CANNOT_CHECK labels where applicable.

### E_value — residual optimum equivalence

`s ~_value t` iff for every admitted continuation z, the exact optimal residual values are equal after the frozen normalization. An additive-offset variant may be studied only as a separately named quotient with the offset carried explicitly.

### E_policy — first-decision equivalence

`s ~_policy t` iff every continuation preserves the same exact certified first normal-form/action choice with ties retained.

No result about one quotient authorizes a claim about another.

## 3. First exact laboratory: StabPrep

Use the already-frozen StabPrep semantics from QG-15 as read-only parent data/model. The first bounded quotient domain is the complete state space needed to reproduce the QG-15 n=1..3 exact panels. n=4 held-out structures may be used only after the quotient construction/frozen mapping is sealed, and only if the parent graph representation makes exact continuation enumeration tractable.

Before partition refinement, freeze:
- precise state encoding;
- transition/action alphabet;
- terminal label definition;
- continuation admissibility;
- tie convention;
- unreachable-state handling;
- symmetry quotienting, if any.

If QG-15's stored artifacts do not expose a type-correct partial-state transition graph, reconstruct one from the primitive StabPrep compiler semantics before any quotient outcome. Do not infer continuation equivalence from final feature rows alone.

## 4. Exact E_label quotient

Compute the coarsest exact bounded quotient by backward partition refinement from terminal label distinctions.

Required outputs:
- number of reachable raw states by layer/depth;
- number of E_label classes by layer/depth;
- class-size distribution;
- transition signature of every quotient class;
- canonical class IDs independent of traversal order;
- a minimal or at least shortest-found distinguishing continuation for every split pair used in the audit;
- deterministic digest of the quotient structure.

Primary theorem gate on the bounded graph:

> every pair of raw states merged into one quotient class has identical final regime label under every admitted continuation.

Verify exhaustively, not statistically.

## 5. E_value comparison

Where exact values are finite and representation size permits, compute an exact E_value quotient independently.

Primary comparison:

`N_label <= N_value`.

A scientifically interesting positive is strict compression `N_label < N_value`, showing that exact regime recognition needs less state than exact residual optimization.

If the quotients coincide, preserve that negative; do not weaken E_value or coarsen continuation semantics post-outcome to create separation.

## 6. QG-15b mixed-cell diagnosis

The 12 frozen mixed natural-feature cells are mandatory controls.

For every positive/negative pair sharing the same 13-feature vector:
1. map both instances/partial states to their exact E_label classes at the declared comparison layer;
2. require distinct classes if their final labels differ;
3. extract a distinguishing continuation/transition-history coordinate;
4. classify the first semantic reason for separation.

Frozen diagnosis categories:
- `ORDER_HISTORY`
- `PIVOT_HISTORY`
- `ROUTE_OCCUPANCY`
- `GLOBAL_SCHEDULE_RESIDUE`
- `PATH_PARITY_OR_PHASE`
- `RESOURCE_BUDGET_STATE`
- `OTHER_EXACT_COORDINATE` with serialized definition.

The category names do not constrain the quotient; they are only after-the-fact interpretation labels.

## 7. Relationship to QG-15c

Prospective discipline is load-bearing.

Case A — QG-15c freezes an enlarged vocabulary before QG-20 finishes:
- QG-20 may not alter it;
- compare the frozen QG-15c vocabulary to the exact quotient only after QG-15c's outcome is sealed;
- QG-20 is explanatory/control evidence.

Case B — QG-20 finishes first and QG-15c has not frozen:
- QG-20 may propose a **candidate** human-readable vocabulary derived from quotient distinctions;
- candidate vocabulary/order/caps must then be independently frozen by QG-15c before label scoring;
- no QG-20 knowledge of held-out QG-15c outcomes may be used.

This protocol grants no permission for post-outcome feature invention.

## 8. Candidate interpretable vocabulary extraction

Only after the exact quotient is sealed, enumerate a frozen library of interpretable state coordinates grounded in exact compiler semantics. Candidate examples may include:
- pivot/order signatures;
- route occupancy/connectivity summaries;
- schedule/dependency residues;
- remaining-action feasibility masks;
- path-dependent parity/state invariants.

For the complete bounded fit graph, ask for the smallest coordinate subset whose induced partition **refines E_label exactly**. This is a finite set-cover/feature-subset problem and receives zero novelty credit.

Report:
- minimal subset size if proven exact;
- all tied minimal subsets up to a declared cap;
- unresolved lower/upper bracket if exhaustive minimization is capped;
- cells/classes that remain mixed under every capped subset.

A zero-error classifier on sampled rows is not an exact feature-determination result unless its induced partition is proven to refine E_label on the complete frozen domain.

## 9. Regime-state complexity measures

For each exact bounded domain X serialize:
- `N_raw(X)` — reachable raw states;
- `N_label(X)` — E_label classes;
- `N_value(X)` — E_value classes if computed;
- `b_label(X)=ceil(log2 N_label(X))` — coding lower bound only;
- quotient compression ratio `N_label/N_raw`;
- proposed vocabulary state count / bit representation where type-correct.

Do not interpret `b_label` as an achievable semantic feature count; it is only an information lower bound for a finite code.

For n/layer growth, report sequences without extrapolating all-n complexity unless a separate theorem is proved.

## 10. Transfer calibrations

After StabPrep has an honest terminal, two controls may be registered in successor freezes.

### R6M/TARE

Hypothesis: low-dimensional shared-Tag/syndrome structure plus a finite trade ladder may induce a compact E_label quotient even if exact costs require more state.

### R6I

Key diagnostic: production rewrite-relevant syndrome rank is five while QG-9 V6 proves intrinsic support one. Test whether the quotient preserving only the support-phase/regime label is substantially coarser than the exact value/DP state.

No correspondence is assumed in advance.

## 11. Weighted/min-plus state model

Where the compiler is naturally a min-plus weighted transition system, compute only equivalences whose semiring/value semantics are exactly defined. If a donor weighted-automata algorithm requires algebraic properties not satisfied by the frozen cost model, return CANNOT_CHECK or use a direct finite exhaustive equivalence algorithm instead.

Do not cite generic weighted-automata minimization as proof that the compiler quotient exists or is efficiently computable.

## 12. Independent verification

### Generic ORION

Must independently:
- reconstruct the bounded transition graph from primitive semantics;
- recompute reachability;
- run a separate partition-refinement/minimization implementation;
- validate every merged E_label pair against all admitted continuations on the complete graph;
- produce a concrete distinguishing continuation for any disputed merge;
- compare quotient digests/class maps after independent canonicalization.

### Native ORION-Q

Keep distinct:
- `BOUNDED_TRANSITION_GRAPH_EXACT`
- `E_LABEL_QUOTIENT_EXACT`
- `E_VALUE_QUOTIENT_EXACT`
- `MIXED_CELL_DIAGNOSIS`
- `FEATURE_DETERMINATION`
- `HELD_OUT_QG15C`
- `ALL_N_STATE_COMPLEXITY`
- `CANNOT_CHECK`

No bounded quotient automatically grants a scalable/all-n or held-out predicate claim.

## 13. Honest terminals

Positive candidates:
- `QG20_STABPREP_EXACT_REGIME_QUOTIENT_COMPUTED`
- `QG20_MIXED_CELLS_EXPLAINED_BY_MISSING_STATE_COORDINATE`
- `QG20_MINIMAL_ENLARGED_VOCABULARY_RECOVERS_FEATURE_DETERMINATION`
- `QG20_REGIME_LABEL_COMPRESSES_FAR_BELOW_EXACT_VALUE_STATE`

Negative/partial:
- `QG20_EXACT_REGIME_STATE_REQUIRES_NEAR_FULL_OPTIMIZER_STATE`
- `QG20_QUOTIENT_GROWS_WITH_N__NO_BOUNDED_STATE_SUMMARY_EVIDENCE`
- `QG20_FEATURE_SUBSET_MINIMIZATION_CAPPED__BRACKET_ONLY`
- `QG20_TRANSITION_GRAPH_RECONSTRUCTION_GAP`
- `QG20_WEIGHTED_EQUIVALENCE_CANNOT_CHECK`
- `QG20_CANNOT_CHECK`

## 14. Donor and claim boundary

Automata minimization, bisimulation, weighted-transition equivalence, abstract interpretation/quotient domains, sufficient statistics, state aggregation and feature selection are donor methods. Candidate contribution is only the exact frozen quantum-compiler quotient, its complexity/diagnosis, or a prospectively confirmed regime vocabulary under independent freeze. No physical quantum advantage follows.

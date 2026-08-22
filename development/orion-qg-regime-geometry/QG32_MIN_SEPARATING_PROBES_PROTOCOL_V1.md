# ORION-QG QG-32 — minimum separating probe basis above joint bulk+spectrum V1

Date: 2026-08-22
Issue: #911
Parent: QG-31 #904
Execution branch: `codex/orion-qg-qg32-min-probes-20260822`
Status: **FROZEN BEFORE ANY ACCEPTED MINIMUM-PROBE OUTCOME.** First protected attempt timed out inside the 120-second harness process cap before producing a result receipt; the scientific minimum target is unchanged.

## Question

For the 715 canonical TARE local-Clifford orbit types, QG-31 defines:
- `A_bulk`: 45-class bulk signature;
- `A_spectrum`: 54-class unlabeled 384-response spectrum;
- `A_indexed`: injective ordered 384-response vector.

Define `A_joint=(A_bulk,A_spectrum)`. Find the minimum fixed probe subset `P subset {0,...,383}` such that

`o -> (A_joint(o), (K_p(o))_{p in P})`

is injective on all 715 orbit types.

No expected cardinality is frozen.

## P1 — reconstruct joint partition

Independently reconstruct all 715 orbit representatives and 384 one-active probes. Report:
- `N_joint`;
- joint class-size histogram;
- largest joint class;
- unresolved pair count within joint classes;
- QG-31 parent bindings and same-bulk+same-spectrum+different-indexed consistency.

## P2 — exact hitting-set formulation

Universe `U` is all unordered orbit pairs inside the same joint class. For probe `p`, let `D_p subset U` be pairs with different `K_p`.

A probe set is separating iff `union_{p in P} D_p = U`.

Production primary solver: exact binary MILP minimizing `sum x_p` subject to every unresolved pair being covered.

The selected probe set is the sorted optimum returned by the exact minimum-cardinality solve. **No lexicographic-optimum authority is required in V1.** This removes a reproducibility-only cascade of repeated feasibility MILPs that exceeded the harness process cap; it does not alter the minimum-cardinality question.

## P3 — minimum certificate

Preferred solver-independent lower-bound certificate:
- find `m_joint` unresolved orbit pairs whose distinguishing-probe sets are pairwise disjoint;
- serialize those pairs and each pair's distinguishing-probe set digest/cardinality.

Such a packing proves every separating probe set has size at least `m_joint`.

If no matching packing is found, production must label the simple packing certificate incomplete; generic ORION may still earn the minimum only by independently proving infeasibility at `m_joint-1` with an exact branch/search procedure. A production MILP status alone is not sufficient for the strongest native authority.

## P4 — selected probe details

For every selected probe serialize:
- index 0..383;
- target permutation tuple;
- auxiliary row index;
- auxiliary frames;
- auxiliary Tag;
- response-value histogram over all 715 orbit types;
- unresolved-pair coverage count.

Verify the joint+selected-probe signatures are 715/715 distinct.

## P5 — ablations

For four starting information states—raw, bulk only, spectrum only, joint—report:
- unresolved pair count;
- largest unresolved class;
- deterministic greedy separating-set upper bound;
- a safe lower bound.

Only `m_joint` is required exact in V1. Other minima remain bounds unless separately proved.

## Independent generic ORION

Must independently rebuild phase-free Pauli/F3 semantics, local-Clifford orbits, 48 auxiliary rows, all 384 responses, joint partition and pair/probe incidence.

It must:
- verify the production selected set separates all pairs;
- verify the packing lower bound if supplied, OR independently prove no set of size `m_joint-1` exists with an exact branch/search routine;
- agree on the minimum cardinality, not on one particular optimal probe tuple.

Do not import the production solver or its incidence matrix.

## Native ORION-Q

May authorize only:
- exact joint class count;
- fixed-probe separating upper bound;
- exact minimum fixed-probe cardinality if lower bound independently closes;
- query-scoped active-verification interpretation.

Mandatory false:
- minimum probes for full finite-n optimum;
- hardware measurement minimum;
- global QG-28 state minimality;
- adaptive decision-tree optimality;
- generic active-learning novelty;
- physical quantum advantage.

## Strong terminal

`QG32_MINIMUM_FIXED_PROBE_BASIS_ABOVE_JOINT_BULK_SPECTRUM_MACHINE_CHECKED`

Honest alternatives:
- `QG32_JOINT_SEPARATING_PROBE_UPPER_BOUND_ONLY`
- parent-binding gap;
- generic/native disagreement;
- CANNOT_CHECK.

## Donor subtraction

Minimum test cover, hitting set, feature acquisition and experimental design are donor methods. Candidate value is the exact TARE-specific joint partition, minimum fixed probe cardinality and its use as a bounded active-verification primitive.
# ORION-01 R11 prospective Round 1: pinned PyZX `full_reduce`

**Protocol status:** frozen before scientific outcome access  
**Freeze date:** 2026-08-27  
**Canonical lane:** ORION-01 — Certificate Realization  
**Parents:** issues #1513 and #1520  
**Immutable base:** `main@27ea5e1b04dbed853b7ddba60c8bf736ef087bf5`

## 1. Frozen public subject

- repository: <https://github.com/zxcalc/pyzx>
- commit: `dade7d46f193635bbdaefd8fcde837f9449fddc5`
- Git tree: `3885a1acc34fbfdaf95ff9cb01c75abea9c36721`
- commit date: `2026-08-24T08:20:29Z`
- package version: `0.10.5`
- license: Apache-2.0
- production entry point: `pyzx.simplify.full_reduce`

The source and dependency identities are checked before any scientific result
is emitted. The complete source/guard registry is frozen in
`ORION01_R11_PYZX_SOURCE_REGISTRY.json`.

## 2. Completeness claim and its ceiling

The registry is claimed complete only for the **automatic macro operations
called directly or transitively by the pinned `full_reduce` implementation**.
It includes its source control functions, matcher/guard functions, appliers,
`to_gh`, and terminal isolated-vertex cleanup. Completeness is checked by a
static AST call-closure audit plus exact file digests, never by runtime traces.

This does **not** claim completeness for:

- all public PyZX rewrites;
- manual applications of a rule at arbitrary matches;
- all sound ZX-calculus equalities;
- circuit equivalence or optimal quantum compilation in general.

The experiment's legal move is one whole invocation of one registered
automatic macro operation on the current graph. The move guard is extensional:
the invocation is legal exactly when it returns a graph state distinct from
the input after lossless canonical-JSON serialize/reload. Vertex identities are
preserved so that source batch-matcher ordering remains part of the frozen
operational subject. This also covers source
operations such as `to_gh` and `remove_isolated_vertices` that return `None`.

## 3. Frozen input domain

Width is exactly two qubits. The ordered alphabet is

```text
H0, H1, S0, S1, T0, T1, CX01, CX10
```

The corpus contains **every** word of lengths zero, one, two, three and four,
in lexicographic product order: `1 + 8 + 64 + 512 + 4096 = 4681` source
circuits. No semantic or graph deduplication removes a source word. Each word
is converted by the pinned public `Circuit.to_graph()` route. H-box inputs are
forbidden and fail closed, matching the production entry point.

## 4. Registered resource and exact state search

For a graph `G`, define

```text
R(G) = (tcount(G), number of non-boundary vertices, number of edges),
```

ordered lexicographically. The diagnostic structural tuple is

```text
W(G) = (number of vertices, number of X vertices, number of edges).
```

`W` increases, equalities and decreases are all retained as adverse diagnostic
facts; no move is excluded because of them. Search is breadth first over all
twelve operations from every newly reached state, with lossless serialized-state
deduplication and no objective pruning. Exactness is granted only when the
reachable queue exhausts. A safety cap of 100,000 states per source word is
fail-closed only: reaching it yields no approximate result.

The production arm applies the unmodified pinned `full_reduce`. The exact arm
computes `min R` over the complete reachable state graph and preserves one
lexicographically first witness path.

## 5. Semantics and realization gates

For every explored edge, the pinned independent dense tensor evaluator must
confirm equality **including scalar** between predecessor and successor. The
source graph, production result, and exact witness are checked likewise. These
are exhaustive numerical two-qubit checks on the frozen domain, not a new
symbolic soundness proof for PyZX.

The following all must hold before a positive or null science terminal:

1. direct-URL commit binding and all source digests match;
2. AST control/mutator closure equals the frozen registry exactly;
3. each of the twelve one-entry registry omissions is rejected;
4. every explored transition preserves dense tensor semantics including
   scalar;
5. every exact search exhausts before the fail-closed cap;
6. the production result is reachable in the registered state graph or has
   the same registered resource and semantics as a reachable state;
7. all 4681 input words execute;
8. every ordered schema pair receives a bounded critical-interaction
   classification;
9. the committed receipt is byte-identical under two fresh replays.

## 6. Critical interactions

For every ordered pair `(a,b)` among the twelve registered schemas, the run
counts on all reachable states:

- co-enabled states;
- `a` enabling or disabling `b`;
- commuting and noncommuting two-step diamonds;
- two-step resource divergence.

Zero observed overlap means only no overlap in this frozen domain. It is not a
generic critical-pair theorem.

## 7. Hostile controls

The verifier must reject all twelve source-registry omissions. It also runs
finite controls in which (i) a globally legal omitted edge collapses a false
terminal lower bound, (ii) two trace-equivalent incomplete registries have
different terminal optima, and (iii) an omitted cross-component merge
collapses an additive local bound. These controls are falsifiers for the
authority logic, not PyZX results.

If a strict narrow witness is found, the predeclared public PyZX operations
`bialg_simp`, `hopf_simp`, and `gadget_phasepoly_simp`—explicitly outside
`full_reduce`—are tried as hostile extensions. Any collapse changes the
terminal to `AB_R11_CROSS_MOVE_COLLAPSES_GAP`; the witness may not be reported
as an all-PyZX gap.

## 8. Predeclared terminals

```text
AB_R11_REALIZED_GAP_COMPLETE_REWRITE_REGISTRY
AB_R11_COMPLETE_REGISTRY_NO_STRICT_GAP
AB_R11_CROSS_MOVE_COLLAPSES_GAP
AB_R11_DONOR_EQUIVALENT
CANNOT_CHECK_MOVE_COMPLETENESS
```

Positive means at least one strict schedule-versus-reachable-minimum witness
within the exact automatic `full_reduce` macro language. Null means equality
for every frozen source word. Both consume exactly one prospective ORION-01
round and leave science open for Round 2 or later closure.

## 9. Claim boundary and donors

PyZX owns the implementation and ZX simplification. ZX-calculus soundness,
equality saturation, phase-ordering, e-graph extraction, superoptimization,
and generic critical-pair analysis are donor-owned. The ORION residual is only
the content-bound authority relation among a named schedule certificate, a
source-complete automatic macro grammar, and its exact bounded reachable
minimum.

Forbidden from this study: hardware or physical advantage, unrestricted
compiler speedup, optimality over all PyZX or ZX moves, external novelty,
journal readiness, or submission authorization.

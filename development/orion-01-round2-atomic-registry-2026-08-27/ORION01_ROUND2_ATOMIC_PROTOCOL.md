# ORION-01 Round 2 prospective study: pinned PyZX atomic checker-guarded registry

**Protocol status:** frozen before scientific outcome access
**Freeze date:** 2026-08-27
**Canonical lane:** ORION-01 — Certificate Realization
**Parents:** issues #1513, #1520, #1541 §1, #1507 immediate order 5
**Round accounting:** consumes ORION-01 Round 2 of at most 3
**Round 1 custody:** `papers/orion-01-certificate-realization/experiments/r11-pyzx-full-reduce/` — adverse terminal `CANNOT_CHECK_MOVE_COMPLETENESS` (macro grammar unsound under free reordering). Untouched by this study.

## 1. Why this round exists (root-cause revival, not relabeling)

Round 1 attributed its failure to ONE stage: the macro-level guard. The twelve
`full_reduce` automatic macros are invoked as whole-graph batch routines whose
matchers are **not pure predicates** (`match_pivot_boundary` gadgetizes the graph
in place while matching, and batch appliers consume precomputed match sets), so a
detached second invocation of `pivot_boundary_simp` at a site accepted by the
callable guard changed the dense two-qubit linear map (`H0,H0,H0`, R11 witness).

The revival lever applied here is exactly that attribution: bind the registry at
the granularity where PyZX itself exposes **site-guarded official rewrite
primitives** — the public `RewriteSingleVertex.apply(g,v)`,
`RewriteDoubleVertex.apply(g,v,w)`, and targeted `RewriteSimpGraph.apply(g,
vertices)` routes, each of which evaluates its official guard on the current
graph at application time and applies the official applier at exactly one site.
No batch scheduler, no precomputed match set, no detached matcher call survives
in the move semantics. The Round-1 macro registry, counterexample, and terminal
are preserved unchanged; the Round-2 language is a strictly finer, guard-distinct
language, and the protected outcomes (gap / null / generic-search comparison)
remain unobserved at freeze time.

This satisfies the merged Round-1 next-gate: "Freeze and execute a scientifically
distinct Round 2 whose stateful scheduler/context guards are source-complete" —
the guards here are the official source predicates/checkers themselves, evaluated
at application time, hence source-complete and independently enumerable.

## 2. Frozen public subject

Identical pinned PyZX source as Round 1: repository
<https://github.com/zxcalc/pyzx>, commit
`dade7d46f193635bbdaefd8fcde837f9449fddc5`, tree
`3885a1acc34fbfdaf95ff9cb01c75abea9c36721`, package 0.10.5, Apache-2.0,
production entry point `pyzx.simplify.full_reduce`. All sixteen load-bearing
source files are digest-frozen in
`ORION01_ROUND2_ATOMIC_SOURCE_REGISTRY.json` (same digests as Round 1).

## 3. Move registry and its completeness ceiling

Twelve registered moves (`PYZX.R2.01`–`PYZX.R2.12`), one per Round-1 macro rule
family, but at **single-site granularity**: fuse, self-loop removal, `to_gh`,
identity removal, pivot, local complementation, boundary pivot, gadget pivot,
phase-gadget merge, copy, supplementarity, scalar-accounted isolated-vertex
cleanup. A move is ONE application of the official guarded route at one site:

- vertex-site rules: `obj.apply(g, v)` for every vertex `v`;
- pair-site rules: `obj.apply(g, v, w)` for every ordered pair over undirected
  edges (fusion, pivot, boundary pivot, gadget pivot), and for gadget-merge /
  supplementarity every ordered non-Clifford pair grouped by equal gadget-target
  set / equal-or-symmetric-difference-two neighbourhood;
- graph rules: one whole official `to_gh` or `remove_isolated_vertices`
  invocation (both order-independent, scalar-accounted, idempotent).

A move is legal exactly when the official route returns true AND the lossless
canonical-JSON state with vertex identities preserved differs from the input.
Guards are official functions from the pinned source evaluated at application
time on the current graph; there is no detached matcher call and no batch.

Completeness is claimed only for **site-guarded official rewrite primitives
reachable from the pinned `full_reduce` closure**, and is audited statically by
four AST-structural checks (never outcome- or trace-based — per the R11
post-review finding that trace comparisons are non-identifying):

1. **Primitive-closure equality.** The transitive AST call closure of
   `full_reduce` over the pinned modules is computed with rewrite objects
   resolved to their constructor components; the official site-guarded
   primitives that closure reaches must equal the twelve registered official
   objects exactly, and every single-schema omission must break that equality.
2. **Mutator-method surface inclusion.** Every mutating graph/scalar method
   name invoked anywhere inside the `full_reduce` closure must be invoked by at
   least one registered atomic route closure — the production scheduler's
   mutation surface is covered by the registry. (The batch matchers
   `match_pivot_boundary` / `match_pivot_gadget` / `match_phase_gadgets` are
   themselves mutating functions unreachable from per-pair routes; their
   mutations are the gadgetization prologues of `unsafe_pivot_boundary`,
   `unsafe_pivot_gadget`, and `merge_phase_gadgets`, which the method-surface
   inclusion pins down at the method level.)
3. **Guard purity.** The registered pure guards `check_fuse`,
   `check_self_loop`, `check_remove_id`, `check_pivot`, `check_lcomp`,
   `check_pivot_boundary`, `check_pivot_gadget`, `check_copy` and their
   pinned-module call closures contain no mutating method invocation. This is
   the exact property whose absence caused the Round-1 failure.
4. **Runtime binding.** The installed objects' `is_match`/`applier`/
   `simp_override` attributes are identity-checked against the audited source
   functions, and `apply` is asserted distinct from the batch `simp` path for
   `pivot_boundary_simp` and `pivot_gadget_simp` (the Round-1 root cause).

Completeness is NOT claimed for all public PyZX rewrites, raw unguarded graph
mutations inside batch schedulers, ZX-calculus, or general circuit
transformation.

## 4. Frozen task set

Width exactly two qubits, ordered alphabet `H0,H1,S0,S1,T0,T1,CX01,CX10` (same
as Round 1). **Primary domain: every word of length 0–3** = `1+8+64+512 = 585`
source circuits, exhaustive, no sampling, no dedup. **Realization-boundary
probe: the first 16 lexicographic words of length 6**, run under the same
fail-closed cap; a cap hit there is recorded boundary evidence, never a
terminal trigger. Each word enters via the public pinned `Circuit.to_graph()`
route; H-box inputs fail closed.

## 5. Registered resource and exact search

`R(G) = (non-Clifford vertex count, non-boundary vertex count, edge count)`
lexicographic (same as Round 1). Diagnostic `W(G) = (vertices, X-vertices,
edges)` with all directions retained. Exact search is breadth-first over all
legal site-guarded moves from every newly reached state with lossless
serialized-state deduplication and no objective pruning; exactness is granted
only at queue exhaustion. Fail-closed cap: 20,000 states per source word inside
the primary domain (cap value fixed from the pre-outcome infrastructure pilot;
a cap hit inside the primary domain yields no approximate result and triggers
`CANNOT_CHECK_MOVE_COMPLETENESS`).

## 6. Arms and the realization question

Three frozen arms per word:

1. **Native heuristic arm (production baseline):** one unmodified invocation of
   pinned `full_reduce`.
2. **Certificate arm (realization):** complete BFS over the registered atomic
   language; the certificate is the content-bound registry plus exhaustion
   receipt plus lexicographically-first minimum-resource witness path. The
   certificate *predicts* `R* = min R` over the registered language and
   *controls* by replaying the witness.
3. **Generic search arm:** random-restart resource-greedy search over the same
   registered moves with NO completeness or certificate knowledge: 4 restarts,
   greedy min-`R` successor with random tie-break, epsilon 0.25 uniform random
   legal move, budget `max(100, 100 × witness path length)` move applications,
   numpy PCG64 seeded `1000003·word_index + 7`.

Measured per word: `R_native`, `R*`, `R_generic`, strict gap
(`R_native > R*` lexicographically), generic match (`R_generic == R*`), witness
replay success, and reachable-state/transition counts.

## 7. Semantics and realization gates

Every explored transition must preserve the pinned dense tensor evaluator's
matrix **including scalar**. Source, native output, certificate witness, and
generic-search best states are checked likewise. A legal atomic move that
changes the dense map (even up to nonzero scalar) triggers
`AB_R2_ATOMIC_GUARD_UNSOUND` with a full witness — that would be a second,
deeper adverse datum: the official site-guarded primitives themselves are not a
sound freely-reorderable grammar.

All of the following must hold before any positive/null terminal: direct-URL
commit binding and all digests; AST mutator-surface equality and one-schema
omission rejections; guard purity audit; per-transition dense semantics on the
whole primary domain; every primary word exhausts before the cap; the native
`full_reduce` output is reachable in the registered state graph or has equal
registered resource and semantics to a reachable state; all 585 primary words
execute; every registered schema pair receives bounded critical-interaction
counts; committed receipts byte-identical under two fresh full executions.

## 8. Critical interactions

For every ordered pair of registered schemas, counted over all reachable
per-word closures of the primary domain: co-enabled states (both schemas have
at least one legal site), enabling/disabling, and commuting/noncommuting
two-step diamonds with two-step resource divergence. Because a schema may have
many legal sites in one state, the two-step census uses the deterministic
canonical site of each schema (the first legal site in the frozen schema order
and enumerated site order); this is disclosed as a bounded representative-move
census — no generic critical-pair theorem is claimed, and no confluence
property is inferred from it.

## 9. Hostile controls and extensions

Structural omission controls: removing any one registered schema must break the
AST mutator-surface equality (structural, not outcome-based). Round-1 hostile
authority controls are retained in custody and not re-run.

On every strict-gap witness word, the predeclared public PyZX operations
`bialg_simp`, `hopf_simp`, `gadget_phasepoly_simp` — outside `full_reduce` —
are applied as hostile extensions. Any gap that collapses changes the report to
`AB_R2_CROSS_MOVE_COLLAPSES_GAP`; surviving gaps may be reported only as
within-language certificate realizations, never as all-PyZX gaps.

## 10. Predeclared terminals (evaluation precedence)

1. `AB_R2_ATOMIC_GUARD_UNSOUND` — any legal atomic move changes dense semantics.
2. `CANNOT_CHECK_MOVE_COMPLETENESS` — audit failure, primary-domain cap hit, or
   native output unrepresented.
3. `AB_R2_ATOMIC_CHECKER_REGISTRY_NO_STRICT_GAP` — `R* == R_native` on every
   primary word (bounded null: native scheduler already optimal in-language).
4. `AB_R2_CROSS_MOVE_COLLAPSES_GAP` — gaps exist but every one collapses under
   hostile extensions.
5. `AB_R2_GAP_MATCHED_BY_GENERIC_SEARCH` — gaps survive but generic search
   matches `R*` on every gap word (certificate predicts, control adds nothing).
6. `AB_R2_ATOMIC_CHECKER_REGISTRY_REALIZED_GAP` — at least one surviving gap
   word where generic search does not reach `R*` (certificate both predicts and
   controls beyond the native heuristic and generic search).
7. `AB_R2_DONOR_EQUIVALENT` — reserved if the result is equivalent to an
   already-published donor result.

Positive/null each consume exactly one ORION-01 round; two rounds then remain
accounted as consumed 2 of 3 with Round 3 open.

## 11. Claim boundary and donors

PyZX owns the implementation, the rewrite primitives, and ZX simplification.
ZX-calculus soundness, equality saturation, phase-ordering, e-graph extraction,
superoptimization, critical-pair analysis, and generic rewriting are donor-owned.
The ORION residual is only the content-bound authority relation among: a named
production scheduler (native heuristic), a source-complete site-guarded atomic
move registry (certificate language), its exact bounded reachable minimum
(certificate), and generic search — i.e., whether certificate realization
predicts and controls production transformations better than both baselines,
and where that realization fails.

Forbidden: hardware or physical advantage, unrestricted compiler speedup,
optimality over all PyZX or ZX moves, external novelty, journal readiness,
submission authorization, and any relabeling of Round 1.

## 12. Infrastructure pilot disclosure

Before freeze, an infrastructure-only pilot will run the machinery on the
length ≤2 words to calibrate the state cap and per-word runtime. The pilot
records operational statistics only (state counts, runtime, cap hits) and no
arm comparison (`R_native` vs `R*` vs `R_generic` is not computed or inspected
in the pilot). Its log is committed as custody before execution.

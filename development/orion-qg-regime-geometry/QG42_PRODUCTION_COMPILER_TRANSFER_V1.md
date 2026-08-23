# ORION-QG QG-42 — the selection phenomenon in two production compilers, at scale

Supersedes the small QG-40 pilot. Same question — is QG-35's separation a TARE
artefact? — now answered on **two production compilers at production
optimisation settings**, with controls.

**This is not a performance comparison.** No cost number here is comparable to
ORION's `config_cost`, and nothing claims any ORION method beats any compiler.
It is a *phenomenon-transfer* test only.

## Setup

| | |
|---|---|
| compilers | **Qiskit 2.5.2** (`optimization_level=3`, `routing_method=sabre`) and **pytket 2.18.1** (`RoutingPass`) |
| object | 3-term Pauli-evolution circuits, 4 qubits, line coupling |
| choice | initial layout — 24 options |
| cost | post-routing CX count |
| summary | bulk × spectrum, quotiented by **circuit-level** qubit permutation |
| scale | 3,000 canonical circuits per compiler |

## Result

| compiler / setting | classes | non-trivial | **selection undetermined** | classes with a **disjoint**-argmin pair |
|---|---|---|---|---|
| Qiskit `opt3+sabre` **[production]** | 487 | 276 | **93.1 %** | **249** (733 pairs) |
| Qiskit `opt0+basic` [control] | 543 | 222 | 99.5 % | 210 |
| pytket `RoutingPass` | 258 | 90 | **97.8 %** | 48 |

Selection is undetermined on the large majority of collision classes in both
compilers, with hundreds of pairs whose optimal-layout sets are **disjoint**.

## The control that makes the existence half meaningful

With the full `bulk × spectrum` summary, `classes_nonconstant_OPTIMAL_VALUE = 0`.
Alone that is worthless — it is exactly what a dead instrument reports.

So the same pipeline was run with a deliberately **weaker** summary (`bulk` only):

```
bulk only :  79 classes,  optimal VALUE differs on 77 of them
```

The experiment therefore **can** detect existence failure, and does, on a coarser
summary. The zero above is a measurement, not a silence.

## A caveat that sharpens our own claim

`classes_nonconstant_OPTIMAL_VALUE = 0` for `bulk × spectrum` is **an identity,
not a measurement**: the spectrum contains the sorted response vector, so
`min(spectrum)` *is* the optimal value by construction. **ORION's QG-35(a) is
proved the same way.**

So QG-35(a) should be read as *definitional for the optimal value* and
*informative only for the further predicates* — number of optimal frames, the
full achievable-cost multiset, the threshold family — which QG-35 checks and
which are not forced by the identity. This narrows part (a) and is recorded
rather than left ambiguous.

## Two defects caught during validation

1. **Relabelling covariance failed 0/4** in the first version, which applied the
   quotient to the *Pauli strings*. The CX ladder follows sorted support and is
   not relabel-equivariant. Fixed by acting on the **built circuit**; covariance
   then verified **8/8**.
2. **The n=5 / opt3 / 600-circuit run produced zero collisions** and is labelled
   **UNDERPOWERED**, not reported as a negative. Exact-collision analysis needs
   low option-set entropy; that is a real limit of this method and not a property
   of the compilers.

Further validation: transpile map deterministic on repeat runs; canonical
quotient does **not** over-collapse (60 random circuits → 60 distinct classes);
4/4 disjoint-argmin witnesses re-derived from scratch with fresh transpile calls,
with a no-alarm control passing; option-set reflection symmetry **measured**, not
assumed.

## Scope limits

Narrow input family (3-term Pauli evolution), 4–5 qubits, line coupling, sampled
rather than exhaustive — unlike ORION's complete 715-type universe. Exact
collisions require small option sets, which is **not** the regime a production
compiler like Symphony operates in. No claim beyond phenomenon transfer.

## Authority

`mathematical_proposal: true`, `NOT_R6`, no compiled-resource, physical-advantage
or comparative-performance claim, `novelty_claim: false`.

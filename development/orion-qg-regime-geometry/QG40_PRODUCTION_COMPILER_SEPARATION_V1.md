# ORION-QG QG-40 — the selection phenomenon reproduces in a production compiler

QG-35 proves an existence/selection separation for TARE frame choice. The obvious
referee objection is that TARE is a bespoke internal construction and the result
is an artefact of it. This atom tests the phenomenon on **Qiskit**, on
**Qiskit's own** decision problem, with **no ORION machinery involved**.

## Setup

| | |
|---|---|
| object | a CX multigraph circuit on 5 qubits |
| choice | the **initial layout** (one of 120 qubit permutations) |
| cost | **total two-qubit gates after routing** (`cx + swap`) on a line coupling map |
| summary | (sorted degree sequence, sorted edge-multiplicity multiset) — invariant under relabelling qubits, computable with **no transpiler call** |
| compiler | Qiskit 2.5.2, `optimization_level=1`, `seed_transpiler=7` |

Summary collisions are built **by construction**, not sampled: all 6-edge
multigraphs on 5 vertices are enumerated, deduplicated by isomorphism, and
grouped by summary. Two non-isomorphic multigraphs sharing a summary are the
analogue of two TARE types in one joint class.

## Result

Over 10 summary classes containing more than one non-isomorphic circuit
(22 circuits × 120 layouts):

- **existence is NOT determined**: 5 of 10 classes contain circuits with
  *different* optimal cost;
- **selection is NOT determined**: 7 pairs share a summary and the *same* optimal
  cost while having **different** optimal-layout sets;
- **4 of those pairs have DISJOINT optimal-layout sets.**

Witnesses:

| summary | optimal 2q cost | `\|argmin\|` | shared layouts |
|---|---|---|---|
| deg (1,2,2,3,4), mult (1,1,1,1,2) | 4 | 2 vs 2 | **0** |
| deg (0,2,3,3,4), mult (1,1,2,2) | 2 | 12 vs 12 | **0** |

Two circuits a production compiler's cheap invariant cannot tell apart, with the
same achievable cost, and **no layout that is optimal for both**.

## What this does and does not establish

**Does:** the selection half of QG-35 is **not** a TARE artefact. It reproduces
in a production compiler, on that compiler's own choice variable, with a
practitioner-plausible cheap summary.

**Does not:** this is **not** a performance comparison and no claim is made that
any ORION method beats Qiskit. Nothing here is transferred from the TARE lane.

**A real difference worth stating.** In TARE, *existence* was determined (0 of 92
classes split) because the spectrum is the sorted full response vector — an
information-complete symmetrisation. Here existence **fails** on 5 of 10 classes,
because a degree sequence is a far cruder summary than a sorted 384-response.
So the two halves of QG-35 are **not** equally robust: selection failure looks
generic; existence success depends on the summary being the *maximal* symmetry
quotient, which is exactly what C1 established for TARE and what a degree
sequence is not.

## Recorded instrument defect

The first run of this experiment reported a clean negative — 0 separations, 0
classes with differing cost. It was **vacuous**: the cost function counted only
`cx`, while routing expresses its work as inserted `swap` gates. Every circuit
scored identically at every layout (`|argmin| = 120/120`, cost range `[6,6]`).

Caught by an explicit validity check (`qg40_instrument_validity_check.py`) asking
whether the measurement *could* vary at all. A negative result from a dead
instrument is the failure mode this programme exists to prevent, and it nearly
shipped here.

## Boundaries

5 qubits, line coupling, CX-only circuits, 6 edges, `optimization_level=1`, one
seed. No claim about larger circuits, other couplings, other optimisation levels,
seed variance, or other compilers. Whether the effect grows or vanishes with
scale is **not computed**.

## Authority

`mathematical_proposal: true`, `NOT_R6`, no compiled-resource or
physical-advantage claim, no comparative-performance claim, `novelty_claim: false`.

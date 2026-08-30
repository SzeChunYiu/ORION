# Measured transfer: ORION-08's binding lattice predicts an independent empirical result

**Subject:** Nakayashiki, *When Stale Constraints Go Unchecked: Budgeted Verification
Failures in Inherited Agent Memory*, arXiv:2608.25553v2 (2026-08-27).
**Instrument:** `ORION08.BINDING_SUFFICIENCY_LATTICE.v1`, Theorems 1 and 2.
**Scientific authority delta:** `NONE`. This is a prediction check against published
numbers, not a re-analysis of that paper's data, which we do not hold.

## Why this is worth doing

The literature closure found this paper independently arriving at four of ORION-08's
design commitments. The reflex is to carve out a delta. The better move is to ask whether
ORION-08's exact theory *explains* it — and it does, on both sides of its result,
including the null the authors report as a control.

The parent is explicit that it cannot do this itself:

> "It does not identify why native allocation selects what it selects, it does not
> establish mediation"  — §1
> "Mechanism of native under-verification not isolated" — Limitation 9

## The mapping

ORION-08's setting: worlds `x` carry a binding `B(x)`, the information a policy may read.
`B` partitions worlds into **fibres**, and a deterministic policy reading only `B` must
emit one action per fibre.

The parent's setting maps onto this exactly, and its own words supply the key premise:

| ORION-08 object | parent's construct |
|---|---|
| world `x` | (memory form, world state) — `valid` or `superseded` |
| binding `B(x)` | what the agent can read at allocation: the store line + its two verification slots |
| fibre | **"Nothing visible at allocation time distinguishes this world from one in which S₀ is still current"** (§2) |
| `A*(x)` | the action the archive's *current* record approves |
| refinement `B' ⊐ B` | the forced-critical policy: one slot re-assigned to the critical provenance path |

The parent asserts, as a design property, that `valid` and `superseded` are
**indistinguishable at allocation time**. In ORION-08's language that is precisely the
statement that both worlds lie in **one fibre of `B`**.

## Prediction 1 — from Theorem 1

> A deterministic zero-regret policy using only `B` exists **iff** every positive-mass
> fibre has a common optimal action.

In the `stated × superseded` cell the optimal action differs across the fibre: in `valid`
the constrained action must be avoided, in `superseded` it is approved. The intersection
of optimal actions over that fibre is **empty**.

**Therefore no deterministic zero-regret policy exists on that binding**, whatever the
agent's reasoning quality. The parent's 77.3% / 74.7% / 74.7% stale-consistent rate is not
primarily an agent deficiency — it is a **structural property of the binding the design
installed**. The parent half-recognises this ("the design establishes a conditional
vulnerability once supersession has occurred, not that native allocation is irrational in
expectation", Limitation 4) but has no formal statement of it.

## Prediction 2 — from Theorem 2, and this is the sharp one

> The decrease is strict **exactly when** `B'` splits a positive-mass `B`-fibre whose
> worlds share no optimal action; a refinement that only splits already-pure fibres
> changes nothing.

This is two-sided, so it forbids as well as predicts:

| condition | Theorem 2 says | parent observed |
|---|---|---|
| superseded — record **withdraws** the constraint; fibre worlds share no optimal action | **strict, large decrease** | **+74.0, +72.7, +61.3, +73.3** points, 6/6 models |
| source-agreement — record **confirms** the memory; fibre already action-pure | **no change** | **+0.7 to +2.0** points, "already near-ceiling rate unchanged" |

The same intervention, the same budget, the same delivery mechanics — and the effect
appears in one condition and vanishes in the other, exactly where fibre purity says it
should. A refinement that is large where fibres are impure and null where they are pure
is Theorem 2's signature, and the parent reports both arms.

## The same signature inside ORION-08's own receipts

This is not a post-hoc reading imported for the occasion. The identical pattern was
already recomputed from ORION-08's frozen N4-B receipts before this paper was found:

| regime | gap closed | fibre condition |
|---|---:|---|
| `REOPEN_WASTEFUL` | **1.7%** | never-reopening already near-optimal → fibres effectively action-pure → refinement buys almost nothing |
| `STALE_MATTERS` | **10.3%** | fibres differ in optimal action → refinement buys something |

One instrument, one theorem, the same two-sided signature in an exact synthetic study and
in an independent 5,400-episode LLM-agent experiment.

## What is and is not claimed

**Not claimed.** Novelty of the theorem. `THEORY.md` already states it is "generic
decision-sufficiency / Blackwell-style donor theory. No novelty is claimed." That
self-assessment stands and is not weakened here.

**Not claimed.** Any re-analysis of the parent's data. Every number above is read from the
published paper. A genuine test would map its episode records into fibres and check the
prediction case by case; its data is released, so this is doable and is named as the next
step rather than asserted as done.

**Claimed.** A *measured transfer*: ORION-08's instantiated lattice predicts, on both
sides, an independent empirical result whose authors explicitly disclaim the mechanism —
including the null control, which is the harder half. The theorem is donor theory; the
instantiation and this transfer are the contribution.

## What it does to the paper

This is stronger than the delta the literature closure originally identified. Rather than
"we are exact where they are sampled", the positioning becomes:

> The lattice states when a binding can support a zero-regret policy and when refining it
> can help. An independent budgeted-verification experiment reports both a large effect
> and a null control; the criterion predicts which is which from fibre purity alone.

`05-related-work-boundary.tex` should carry this, and it changes no result: the transfer
is a prediction check, not a new experiment.

## Falsifier

If a fibre-level mapping of the parent's released episodes shows large effects where
fibres are action-pure, or nulls where they are impure, this transfer is refuted. It
should be tested that way before the manuscript leans on it.

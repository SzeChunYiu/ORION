# ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1 — THEORY

**Paper:** ORION-16 — Formal Epistemic Structures and Mechanics
**Successor id:** `ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1`
**Candidate source:** PR #1617, Priority A
**Authored:** 2026-08-28
**Status:** `THEORY_PROVED__EXHAUSTIVELY_CHECKED`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 1. Why this successor exists

Claim row `ORION-16.V4.4` states that revalidating every affected lift coordinate
is necessary and sufficient for restoration — but explicitly **"in the registered
lifting model"**, i.e. for one fixed five-coordinate structure. `V4.6` supports it
with `155` full-revalidation sufficiency witnesses and `1,055` strict-subset
necessity countermodels.

The candidate note asks to *"generalize the current five-coordinate enumerator to
arbitrary finite dependency DAGs, prove sufficiency/necessity directions."* That
is what this packet does. It lifts `V4.4` from a statement about one registered
model to a structural theorem about any finite dependency graph, and shows the
registered model is its special case.

---

## 2. Setting

Let `G = (V, E)` be a finite directed acyclic dependency graph on scientific
obligations: an edge `u -> v` means `v`'s premises depend on `u`. Let
`Delta ⊆ V` be the coordinates directly changed by an update.

**Affected closure.**

```
A(Delta) = { j in V : j in Delta, or some path from a member of Delta reaches j }
```

**Assumptions**, stated as in the candidate note:

1. donor-native certificates remain valid when their native premises do not
   change;
2. obligations outside `A(Delta)` are stable under the update;
3. a declared dependency separation witness exists — for each `j in A(Delta)`
   there is an admissible instance in which the update breaks exactly `j`.

**Adversary model.** After the update, an adversary may break the obligation at
any node whose premises could have changed, i.e. any nonempty `B ⊆ A(Delta)`.
Revalidating a node detects a break at that node and nowhere else.

**Soundness.** A revalidation set `R` is *sound* for this update when, for every
adversary break-set `B`, revalidating `R` detects that something is broken:
`R ∩ B != empty` for all nonempty `B ⊆ A(Delta)`.

---

## 3. The theorem

### Theorem (dependency-closed revalidation is exactly minimal)

For every finite DAG `G` and every `Delta ⊆ V`, the affected closure `A(Delta)`
is a sound revalidation set, and it is the **unique minimal** one: every proper
subset of `A(Delta)` is unsound.

**Proof.**

*Sufficiency.* Let `B ⊆ A(Delta)` be nonempty. Then `A(Delta) ∩ B = B != empty`,
so the break is detected. Obligations outside `A(Delta)` are unreachable from
`Delta`, so by assumption 2 their premises are unchanged and by assumption 1
their certificates remain valid; they need no revalidation. Hence `A(Delta)` is
sound.

*Necessity.* Let `R ⊊ A(Delta)` and pick `j in A(Delta) \ R`. By assumption 3
there is an admissible instance whose break-set is exactly `B = {j}`. Then
`R ∩ B = empty`, so `R` reports the standing restored while `j` is in fact
violated. `R` is unsound.

*Minimality is unique.* Any sound `R` must contain every singleton break-set,
hence `R ⊇ A(Delta)`. Combined with sufficiency, `A(Delta)` is the least sound
set. ∎

### Corollary (why transitivity is required)

Revalidating only `Delta`, or only `Delta` together with its immediate
successors, is unsound whenever the closure is strictly larger. Dependency
*reachability*, not adjacency, is the operative relation.

### Scope limit — what this does not say

The theorem is about **which** obligations must be revalidated once a dependency
graph is given. It says nothing about whether the registered five lift
coordinates are the right coordinates, nor whether the registered dependency
graph is the correct one. Those remain exactly as `CLAIM_LEDGER_V4.md`'s scope
ceiling records them: *universal minimality of the five lift coordinates* is
**not** established here and is not addressed by this packet.

---

## 4. Independent verification

`independent_checker/check_dependency_closure.py` imports nothing from
`check_finite_models.py`, `refutation_audit.py` or any other committed ORION-16
module. Closure, adversary model and soundness are implemented from their
definitions, and the paper's published counts are **reconstructed** rather than
read.

Crucially, soundness is decided by **explicit simulation over every adversary
break-set**, never by the shortcut *"R is sound iff it contains A(Delta)"* —
that shortcut is the thing being verified, so assuming it would make the check
vacuous.

| check | result |
|---|---|
| A — closure correctness (`Delta ⊆ A`, successor-closed, nothing outside reachable) | holds |
| B — sufficiency of `A(Delta)` | holds |
| C — necessity: every proper subset unsound | holds |
| — exhaustive over | **1,099** DAGs, **33,866** update instances, `n <= 5` |
| D — five-coordinate special case | **155** and **1,055** reproduced exactly |
| E — negative controls | **3/3 fire** |

Check D is the validation that the generalization really contains the paper's
model: the registered counts decompose as

```
155  = 5 donors x 31 nonempty damage sets
1055 = 5 x sum_{D nonempty} (2^|D| - 1) = 5 x 211
```

and both are reproduced from the general construction without reading `V4.6`.

Negative controls: using depth-1 successors instead of the transitive closure is
unsound on some DAG; revalidating only `Delta` is unsound on some DAG; and a
strict superset of `A(Delta)` is sound but not minimal.

`CANNOT_CHECK` has exit code `3` and is never reported as a pass.

---

## 5. Strongest falsifier

A finite DAG and update for which some proper subset of `A(Delta)` is sound, or
for which `A(Delta)` is unsound. Refuted exhaustively for `n <= 5` over all
`1,099` DAGs and `33,866` update instances.

The theorem is proved for all finite `n`; the enumeration is a regression check
of the proof, not its basis. What could still fail is **relevance**: if the real
revalidation semantics admit detection of a break at a node other than by
revalidating it, or if assumption 3 fails for some coordinate, the necessity
direction would weaken. Both assumptions are stated explicitly in §2 rather than
buried.

---

## 6. Donor boundary

Reachability closure, monotone dependency semantics and minimal-hitting-set
arguments are **donor-owned**. Incremental verification, proof-carrying actions
and certificate reuse own the generic machinery, as the deep-upgrade note states.
**No novelty is claimed** for the mathematics.

The ORION-specific content is the exact lift of `V4.4` from the registered
five-coordinate model to arbitrary finite dependency graphs, together with the
demonstration that the registered counts are its special case.

---

## 7. Authority boundary

`scientific_authority_delta = NONE`.

- `V4.4` is **strengthened in scope, not changed in verdict**: what was proved
  for the registered model is now proved for any finite DAG, with the registered
  model as a verified instance.
- `V4.6`'s counts are unchanged and independently reproduced.
- The scope ceiling stands verbatim: universal minimality of the five lift
  coordinates, deployed-agent performance and donor novelty remain **not
  established**.
- `external_independent_validation: CANNOT_CHECK` in the mechanized record is
  unchanged — this packet is same-programme work and does not discharge it.
- No manuscript, ledger, formal record or `submission/` byte is modified.

**ORION-16 is not blocked by this lane.**

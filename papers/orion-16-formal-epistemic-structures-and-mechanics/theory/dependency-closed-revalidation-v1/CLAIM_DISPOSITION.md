# ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Terminal:** `THEORY_PROVED__EXHAUSTIVELY_CHECKED`
**Scientific authority delta:** `NONE`
**New blocker raised:** none

---

## 1. What changed

One additive directory under
`papers/orion-16-formal-epistemic-structures-and-mechanics/theory/`. No
manuscript, ledger, formal record or `submission/` byte was modified.

## 2. What was established

Claim row `ORION-16.V4.4` proves that revalidating every affected lift coordinate
is necessary and sufficient for restoration — but **"in the registered lifting
model"**, one fixed five-coordinate structure.

This packet lifts it to a structural theorem:

> For every finite DAG and every changed set `Delta`, the affected closure
> `A(Delta)` is sound, and every proper subset of it is unsound. `A(Delta)` is
> therefore the **unique minimal** sound revalidation set.

The registered model is a verified special case.

**Corollary:** dependency *reachability*, not adjacency, is the operative
relation — revalidating `Delta` plus its immediate successors is unsound whenever
the closure is strictly larger.

## 3. Independent verification

No committed ORION-16 module is imported. Closure, adversary model and soundness
are implemented from definitions, and the published counts are reconstructed
rather than read.

Soundness is decided by **explicit simulation over every adversary break-set**,
never by the shortcut *"R is sound iff it contains A(Delta)"*. That shortcut is
the statement under test; assuming it would have made the whole check vacuous.

| check | result |
|---|---|
| closure correctness, sufficiency, necessity | hold over **1,099** DAGs and **33,866** update instances (`n <= 5`) |
| five-coordinate special case | **155** and **1,055** reproduced exactly |
| negative controls | **3/3 fire** |

The count reproduction is the load-bearing validation that the generalization
really contains the paper's model:

```
155  = 5 donors x 31 nonempty damage sets
1055 = 5 x sum_{D nonempty} (2^|D| - 1) = 5 x 211
```

## 4. What this does not touch

The theorem answers *which* obligations must be revalidated **once a dependency
graph is given**. It says nothing about whether the registered five lift
coordinates are the right coordinates, or whether the registered graph is
correct.

`CLAIM_LEDGER_V4.md`'s scope ceiling therefore stands verbatim: **universal
minimality of the five lift coordinates is not established**, and neither is
deployed-agent performance or donor novelty. `external_independent_validation`
remains `CANNOT_CHECK` — this is same-programme work and does not discharge it.

## 5. Donor boundary

**No novelty claimed.** Reachability closure, monotone dependency semantics and
minimal-hitting-set arguments are donor-owned; incremental verification and
certificate reuse own the generic machinery. The ORION-specific content is the
exact lift of `V4.4` to arbitrary finite graphs plus the special-case
demonstration.

## 6. Recommended manuscript action — referred, not taken

`V4.4` could be restated as holding for any finite dependency DAG, with the
registered model named as an instance. That is a scope strengthening with no
verdict change. It is **not taken here**; ledger and manuscript edits belong in
their own PR per #1608.

## 7. Blocker status

`ORION-16 IS NOT BLOCKED BY THIS LANE.` #1609 asks whether the bounded claim is
independently journal-worthy; this makes the central repair theorem structural
rather than model-specific, which strengthens that case without adding a
prerequisite.

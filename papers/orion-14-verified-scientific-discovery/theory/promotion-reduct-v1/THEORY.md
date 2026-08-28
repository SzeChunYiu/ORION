# ORION14.MINIMAL_PROMOTION_REDUCT.v1 — THEORY

**Paper:** ORION-14 — Verified Scientific Discovery
**Successor id:** `ORION14.MINIMAL_PROMOTION_REDUCT.v1`
**Candidate source:** PR #1617, `WAVE1_DEEP_UPGRADES`, ORION-14 Upgrade A (**ranked #2** by expected value)
**Authored:** 2026-08-28
**Status:** `PARTIAL__SCOPE_GATED__COMPUTED_ON_THE_COMMITTED_CORPUS`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 1. Scope gate — read this first

Upgrade A asks for a minimal promotion reduct **over the frozen 400 cases**
behind `ORION-14.X.EXACT.400.PROMOTION_RELATION` (400/400, donor-complete generic
product 250/400, compensatory 50/400, ideal typed 400/400).

**That per-case coordinate table is not committed anywhere in the repository.**
The checker searches the whole repo (excluding `.git`) two independent ways: by
**size** — every `.jsonl` with 350–450 rows — and by **content** — every `.json`,
`.jsonl` or `.py` naming `EXACT.400.PROMOTION`, `ORION-14-X`, `ORION_14_X` or
`promotion_relation`. The 11 size hits are all ORION-12 SAGE corpora at 385 rows,
unrelated to the promotion contract; the single content hit carries no such
table. The claim row records the *counts*; the rows themselves are absent.

So Upgrade A **cannot be executed as specified**, and this packet does not
pretend otherwise. What follows is computed on the corpus that *is* committed —
the 10-case method-authority bench — and is clearly a different, smaller object.

This is itself a useful finding: the highest-value ORION-14 upgrade in #1617 is
blocked on an artifact the repository does not contain, and the fix is to commit
the 400-row table, not to run more science.

---

## 2. The theorem

Let promotion worlds carry coordinates `c_1..c_k` and a target terminal `Y`.
For worlds `x, y` with `Y(x) != Y(y)`, the discernibility set is
`D(x,y) = { i : c_i(x) != c_i(y) }`.

**A coordinate set `S` is target-sufficient iff it hits every opposite-target
discernibility set.** Minimal sufficient sets are the reducts; the **core** is
their intersection — the coordinates present in every reduct, and hence
indispensable.

**Proof.** `S` fails iff two opposite-target worlds agree on all of `S`, i.e.
`S ∩ D(x,y) = empty`. ∎

Donor-owned rough-set / discernibility mathematics; the same object as ORION-09's
separator complexity, ORION-13's semantic separator, ORION-16's dependency
closure and ORION-10's explanation gap. **No novelty is claimed.**

---

## 3. Result on the committed 10-case bench

Encoding, fixed before any subset was evaluated: each setting is **ternary** —
`true`, `false`, and a third value for `null`/absent — and each required
authority coordinate contributes a membership bit.

```
k* = 3

reducts   { claims_new_primitive, known_composition, prior_art_found }
          { known_composition, prior_art_found, req:NOVELTY }

core      { known_composition, prior_art_found }
```

Never in any reduct: `source_lineage_valid`, `assumptions_preserved`,
`assumptions_dropped`, `reconstruction_valid`, `visible_result_pass`,
`protected_result_pass`, `evaluator_independent`,
`generator_accessed_evaluator`, `novelty_search_available`, and
`req:VALIDITY`, `req:APPLICABILITY`, `req:TRANSFER`, `req:UTILITY`.

### What that does and does not mean

It does **not** mean the validity/applicability/transfer/utility machinery is
unnecessary. It means **this bench does not test it**: every case satisfies those
coordinates, so none of them ever separates an opposite-target pair. The bench is
built to stress the novelty route, so the novelty route is all it can measure.

Structurally identical to ORION-13, where every opposite-verdict case turned out
to be a polarity contrast. Both are corpus-design limits, not coordinate verdicts.

---

## 4. The sharp finding: `CANNOT_CHECK` is load-bearing, and binarising destroys it

`prior_art_found` takes three values in the bench:

| value | meaning |
|---|---|
| `true` | prior art was found |
| `false` | the search ran and found nothing |
| `null` | the search **could not run** (`novelty_search_available: false`) |

Two cases — `closed_world_new_method` and `novelty_unknown` — are **identical on
every other recorded field**, including all five required coordinates, and differ
in promotability solely because one has `prior_art_found: false` and the other
`prior_art_found: null`.

Collapsing `null` into `false` merges them, and then **no feature set whatsoever
is sufficient**: `k*` goes from `3` to undefined. The distinction between *checked
and clean* and *could not check* is doing the entire load.

This is a concrete, verifiable demonstration of the programme's rule that
`CANNOT_CHECK` must never be conflated with a negative. It is not an abstract
principle here; binarise it and the promotion relation stops being a function of
the recorded state at all.

The author of this packet made exactly that error on the first pass, encoding
`null` as `false`; the checker's negative control now enforces the distinction.

---

## 5. Independent verification

`independent_checker/check_promotion_reduct.py` imports no ORION-14 module —
neither `run_method_authority_bench.py` nor
`orion.transfer.v2.p4_method_authority`. The bench is read as **data** and the
reduct recomputed from the discernibility definition, exhaustively over all
`2^17` feature subsets.

| check | result |
|---|---|
| scope gate — 400-case table committed anywhere in the repo? | **no** (asserted repo-wide by size **and** content, not assumed) |
| ternary encoding load-bearing | `k*` ternary `3`; the binary encoding admits **no sufficient set at all** |
| reduct / core | as tabulated in §3 |
| negative controls | **3/3 fire** |

`CANNOT_CHECK` has exit code `3` and is never reported as a pass.

---

## 6. Strongest falsifier

A coordinate subset smaller than 3 that is target-sufficient on the bench.
Refuted exhaustively. For the wider claim, the falsifier is the 400-case table
itself: computed there, the reduct could look entirely different, and nothing
here should be read as predicting it.

---

## 7. Authority boundary

`scientific_authority_delta = NONE`.

- `ORION-14.X.EXACT.400.PROMOTION_RELATION` and its `SUPPORTED_BOUNDED_EXACT`
  status are unchanged; this packet does not touch that claim and could not, as
  its data is absent.
- The H1/H2 positive and **H3 null** are unchanged.
- `TRANSPORT_CANNOT_CHECK_HTTP_400` and the other recorded `CANNOT_CHECK`
  dispositions are unchanged — none converted.
- No manuscript, ledger, protocol or `submission/` byte is modified.

**ORION-14 is not blocked by this lane.** #1617 recommends *submit rather than
expand* for ORION-14; the deep-upgrade note itself says the reduct should be
computed only *"if it can be done entirely from frozen rows"*. It cannot, so the
bounded submission proceeds unaffected.

**Content-freeze note.** This additive directory changes ORION-14's paper tree
oid; that pin (`aea0d2d1f38a`) is currently among the **matching** ones per issue
**#1625**, so this PR moves it into the mismatching set. No existing byte is
modified, and the freeze scripts re-pin rather than verify.

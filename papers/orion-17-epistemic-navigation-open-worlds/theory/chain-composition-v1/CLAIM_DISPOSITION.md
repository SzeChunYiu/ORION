# ORION17.CLOSURE_CHAIN_COMPOSITION.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Governing issue:** #1649 Tier A — **ORION-17's one promotion attempt, now spent**
**Terminal:** `THEOREM_PROVED__CLASSIFIES_FROZEN_THREE_DOMAIN_CAMPAIGN`
**Scientific authority delta:** `NONE`

---

## 1. The question, and the answer

Does **pairwise** closure success compose along an arbitrary chain?

**No.** Theorem 2 exhibits a chain in which every pairwise step succeeds in
isolation and global closure still fails, because a property required downstream
is never established upstream. Theorem 1 gives the missing condition — consecutive
bridge entailment — under which composition does hold for chains of any finite
length. Theorem 3 shows order is load-bearing: the same transforms reordered can
break a bridge that held.

Both negative results are **exhibited witnesses**, not assertions.

## 2. The theorems classify a real three-domain campaign

Three independently sourced Python packages, real import graphs, real commit
histories, 604,542 certificate decisions in total.

| policy | numpy | scipy | flask |
|---|---|---|---|
| `always-reopen` | sound, conservative | sound, conservative | sound, conservative |
| `donor-coarse` | **UNSOUND** (27,348 false retentions) | **UNSOUND** (50,282) | sound, conservative |
| `exact-containment` | **sound and exact** | **sound and exact** | **sound and exact** |

`exact-containment` achieves `0` false retentions **and** `0` unnecessary
reopenings in all three domains — it retains closure exactly when the chain
composes.

`donor-coarse` approximates the containment test. By Theorem 2 an inexact bridge
test cannot distinguish a genuine bridge from a broken one, so it must
over-reopen or falsely retain. **It falsely retains** — and the theorem predicts
that failure mode from inexactness alone.

**Flask is the informative control.** With only 19 import edges the coarse test
coincides with the exact one, so `donor-coarse` is merely conservative there. The
adverse regime appears exactly where the dependency structure is rich enough to
separate the tests. That is a prediction a benchmark alone would not yield, and
the domain is reported rather than dropped for being unfavourable.

## 3. Prospectivity — not claimed

The campaign was executed and frozen before this packet existed; its outcomes
were readable before the theorems were written. §2 is **explanatory
classification of pre-existing frozen evidence**.

A genuinely prospective test is specified in `THEORY.md` §6: freeze a fourth
package and predict from its import-graph density, *before* running, whether
`donor-coarse` will be unsound there. **Not executed here.**

## 4. Adverse evidence — preserved

`donor-coarse`'s 77,630 combined false retentions and `always-reopen`'s up to
382,044 unnecessary reopenings are both reported in full. The existing nonclosure
countermodels and pairwise bridge-binding results are unchanged and extended, not
replaced. No `CANNOT_CHECK` is converted.

## 5. Donor boundary

**No novelty claimed.** Assume-guarantee reasoning and contract-based
compositional verification own generic compositional verification — #1617's note
says so explicitly — and induction over chains is elementary.

The ORION residual is the **bridge-separation witness** showing pairwise success
does not compose without entailment, plus the demonstration that exact-versus-
coarse containment is what separates sound from unsound behaviour on real
dependency graphs.

## 6. Stop rule and budget

**#1649, verbatim:** *"If arbitrary-chain behaviour adds no new consequence beyond
pairwise theory, keep the bounded paper and do not inflate the contribution."*

It **does** add a new consequence, so the stop rule does not fire. The
contribution is stated at exactly its size — a composition condition and its
necessity — and **not** as a claim that the chain theory is a new verification
paradigm.

**ORION-17's promotion budget is spent.** No further rescue cycle authorized.

# ORION-23 — power analysis of the frozen three-class construction

**Paper:** ORION-23 — Responsibility-Carrying State
**Governing issue:** #1649 Tier A / blueprint §4.9
**Status:** `PRE_OUTCOME_ANALYSIS__NO_NEW_CORPUS_OPENED`
**Scientific authority delta:** `NONE`
**Written before:** any successor corpus is selected, pinned or cloned.

---

## 1. Why this exists

Blueprint §4.9 requires a new organization-disjoint confirmation, and lists among
its stop conditions:

> *"Stop if ... objective facts are non-vacuous only after post-outcome choices, or
> the donor-complete baseline matches lifecycle-RCS at equal or lower cost."*

Both stop conditions are decidable **from the frozen construction alone**, before
any repository is chosen. Establishing that first is what §4.9's ordering demands:
a corpus frozen for a test that cannot discriminate would consume the
organization-disjoint budget for nothing.

## 2. The cost of every policy is repository-independent

`compare_p13_p14_policies_v1.py` builds exactly three cases per repository —
`VALID` (the pinned head), `FORGED` (a fixed non-existent object id) and `STALE`
(the head's parent) — and counts one operation per fact consulted, with Python
`and` short-circuiting.

The op count per repository is therefore fixed by the policy definitions, not by
the repositories:

| policy | VALID | FORGED | STALE | ops/repo |
|---|---|---|---|---|
| always-raw | 4 | 2 | 4 | **10** |
| provenance-only | 2 | 1 | 2 | **5** |
| confidence-only | 1 | 1 | 1 | **3** |
| lifecycle-RCS | 3 | 1 | 3 | **7** |

The executed campaign reports `310 / 155 / 93 / 217` operations over 31
repositories — exactly `10 / 5 / 3 / 7` per repository. The arithmetic model is
confirmed against the recorded outcome to the operation.

**Consequence:** a new corpus of `n` repositories will report `10n / 5n / 3n / 7n`
operations and a `30%` reduction for lifecycle-RCS, whatever repositories are in
it. Re-running the existing arms on unseen organizations confirms nothing that is
not already fixed by the code.

## 3. The ideal fact-aware control dominates lifecycle-RCS

§4.9 requires an **ideal fact-aware control** among the baselines. On this
construction that control is a single fact:

```
accept  iff  is_current(obj)          # git rev-parse obj == pinned head
```

Its decisions on all three classes:

- `VALID`: the object is the head, so it is current — **accept** (correct);
- `FORGED`: `rev-parse` echoes the unknown id, which is not the head — **reject** (correct);
- `STALE`: the parent resolves to itself, not the head — **reject** (correct).

That is `31/31` valid accepts, zero forged false accepts, zero stale false
accepts — **identical decisions to lifecycle-RCS** — at `1` operation per case,
i.e. `3` operations per repository against lifecycle-RCS's `7`.

**The stop condition fires.** A control consulting strictly less information
matches lifecycle-RCS's decisions at 57% lower cost. The same holds for any
donor-complete provenance-plus-epoch baseline, which consults at most existence,
ancestry and epoch and can short-circuit identically.

## 4. Why the construction cannot separate the policies

The three classes ask only whether an object is the head, the head's parent, or
absent. Every case whose correct answer is *accept* is the head itself.

So **any** policy that accepts exactly the current head scores perfectly. The
construction contains no case in which reusing a **non-head** object is the
correct decision — which is the only situation a reuse policy exists to handle.
A responsibility-carrying state that tracks *what a certificate remains valid for*
has nothing to demonstrate when the only admissible acceptance is "this is the
head".

The reported 30% reduction versus always-raw is therefore attributable to
short-circuit ordering and to skipping an unused signature check, not to a
discriminating capability. Against the ideal control, lifecycle-RCS is 2.33x more
expensive for the same decisions.

## 5. What this does and does not establish

It **does not** retract the executed campaign. The `31/31` valid accepts, zero
forged and zero stale false accepts stand exactly as recorded, and
provenance-only's `31/31` stale false accepts remain a real separation from
provenance-based reuse.

It **does** establish that a new organization-disjoint corpus, run under the
unchanged construction, cannot produce a theorem-derived prospective confirmation:
the numbers it would report are already determined, and the strongest required
baseline already dominates.

No new corpus has been selected, pinned, cloned or opened. The
organization-disjoint budget is **unspent**.

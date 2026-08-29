# ORION-23 — power analysis of the frozen three-class construction

**Paper:** ORION-23 — Responsibility-Carrying State
**Governing issue:** #1649 Tier A / blueprint §4.9
**Status:** `PROMOTION_ROUTE_CLOSED_BY_STOP_CONDITION__CORPUS_BUDGET_UNSPENT`
**Terminal:** `READY_TO_SUBMIT_SECOND_TIER`
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

## 3. The required ideal control scores perfectly on one fact

§4.9 requires an **ideal fact-aware control** among the baselines. On this
construction that control needs a single fact:

```
accept  iff  is_current(obj)          # git rev-parse obj == pinned head
```

Its decisions on all three classes, verified on a real repository:

- `VALID`: the object is the head, so it is current — **accept** (correct);
- `FORGED`: `rev-parse` echoes the unknown id and exits 0, so existence is never
  established, but the echoed id is not the head — **reject** (correct);
- `STALE`: the parent resolves to itself, not the head — **reject** (correct).

That is `31/31` valid accepts, zero forged false accepts and zero stale false
accepts — the same decisions as lifecycle-RCS — at `1` operation per case, `3`
per repository against lifecycle-RCS's `7`.

**This is not the claim that a one-line check is a better policy.** It plainly is
not: it never establishes that the object exists, it would accept nothing that is
not the current head, and it would be useless for reuse. The correct reading is
narrower and is the point of §4 — a control this impoverished can only score
perfectly because **the construction cannot tell policies apart**. The
observation indicts the test, not the method.

The same holds for the donor-complete provenance-plus-epoch baseline §4.9
requires: it consults at most existence, ancestry and epoch, short-circuits
identically, and reaches the same decisions at no greater cost. §4.9's stop
condition — *"the donor-complete baseline matches lifecycle-RCS at equal or lower
cost"* — is therefore met.

## 4. Why the construction cannot separate the policies

The three classes ask only whether an object is the head, the head's parent, or
absent. Every case whose correct answer is *accept* is the head itself.

So **any** policy that accepts exactly the current head scores perfectly. The
construction contains no case in which reusing a **non-head** object is the
correct decision — which is the only situation a reuse policy exists to handle.
A responsibility-carrying state that tracks *what a certificate remains valid
for* has nothing to demonstrate when the only admissible acceptance is "this is
the head".

The reported 30% reduction versus always-raw is therefore attributable to
short-circuit ordering and to skipping an unused signature check, rather than to
a demonstrated discriminating capability.

## 5. The successor experiment this identifies, and why it is not run here

The diagnosis names one failing stage: **the construction's discriminating
power**. The matching lever is a case class in which reusing a non-head object is
correct — for example

> `REUSABLE`: a commit `A` that is an ancestor of the pinned head where the tree
> digest of a designated scope path is identical at `A` and at the head, so a
> certificate bound at `A` remains valid for that scope at the head.

That fact is machine-checkable and falls inside frozen admissible fact class 1
(object/tree digest equality), so it would need no widening of the gold rule. It
separates the policies: the single-fact control and lifecycle-RCS as currently
written both reject it and pay unnecessary recompute, while a scope-aware
freshness test accepts it.

**It is deliberately not run here.** Accepting `REUSABLE` requires redefining
`lifecycle_rcs`, and §4.9 directs that the existing policy thresholds and
terminal semantics be reused *without retuning*. The comparison that motivates
the redefinition — the recorded 217-versus-3 cost gap — has already been seen, so
introducing a class the current arm cannot pass and then rewriting the arm to
pass it would be post-outcome design, even though no successor corpus was opened.
It is recorded as the named successor experiment so the lead is preserved rather
than spent dishonestly.

## 6. What this does and does not establish

It **does not** retract the executed campaign. The `31/31` valid accepts, zero
forged and zero stale false accepts stand exactly as recorded, and
provenance-only's `31/31` stale false accepts remain a real separation from
provenance-based reuse.

It **does** establish that a new organization-disjoint corpus, run under the
unchanged construction, cannot produce a theorem-derived prospective
confirmation: the numbers it would report are already determined by the code, and
the strongest required baseline already matches lifecycle-RCS at lower cost.

No successor corpus has been selected, pinned, cloned or opened. The
organization-disjoint budget is **unspent**.

## 7. Terminal

`READY_TO_SUBMIT_SECOND_TIER`.

The bounded paper is intact and unweakened; nothing in it is retracted or
narrowed. The top-tier promotion route is closed by a stop condition the
blueprint specifies for exactly this case, reached before the corpus budget was
spent. This is not an external blocker: nothing is missing that another party
must supply, and the test was carried to its decision point.

`scientific_authority_delta = NONE`. No claim, terminal, receipt, gold value or
manuscript byte is modified.

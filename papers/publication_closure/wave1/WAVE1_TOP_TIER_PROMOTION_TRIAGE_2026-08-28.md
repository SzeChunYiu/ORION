# Wave-1 top-tier promotion triage — 2026-08-28

**Governing issue:** #1649 — *Final top-tier promotion pass, one decisive theorem/experiment per strongest paper*
**Additive to:** #1609 (publication closeout master), #1608 (unresolved-successor programme), PR #1617 (successor theory candidates)
**Status:** `TRIAGE_ONLY__NO_PROMOTION_BUDGET_SPENT`
**Scientific authority delta:** `NONE`

---

## Why this record exists before any promotion runs

#1649 grants **at most one** prospectively frozen promotion package per paper, and makes failure
terminal: *"if the promotion attempt fails, stop and return immediately to the bounded
submission lane rather than starting another rescue cycle."*

With a one-shot budget and a terminal failure rule, the triage **is** a deliverable. Deciding
which papers get an attempt — and recording which are returned without one — has to happen
before any attempt is spent, or the budget gets consumed by accident.

This record spends none of it. It changes no claim, no terminal and no manuscript.

---

## Scope

The thirteen papers assigned to this pass:

`ORION-05 · 07 · 08 · 09 · 10 · 12 · 13 · 14 · 16 · 17 · 18 · 19 · 23`

#1649's Tier A also lists ORION-02, ORION-22 and ORION-25, and Tier B lists ORION-20. **Those
four are out of scope here** and are not touched.

---

## Disposition table

| paper | #1649 tier | promotion target | data verdict | terminal |
|---|---|---|---|---|
| **ORION-23** | A | `ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1` | **corpus frozen, outcomes never accessed** | `PROMOTION_ATTEMPT_AUTHORIZED` |
| **ORION-17** | A | `ORION17.CLOSURE_CHAIN_COMPOSITION.v1` | theorem needs none; real multi-hop chain to be verified | `PROMOTION_ATTEMPT_AUTHORIZED` |
| **ORION-16** | A | `ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1` | real-transition audit already executed and `SUPPORTED`; comparative baselines to be verified | `PROMOTION_ATTEMPT_AUTHORIZED` |
| **ORION-09** | B | `ORION09.SIZE_TRANSFER_INVARIANT.v1` | `n=4` panel exists (120 states); `n=5` to be verified | `PROMOTION_ATTEMPT_AUTHORIZED` |
| **ORION-05** | B | `ORION05.GLOBAL_OBSTRUCTION_BASIS.v1` | deferred — see §3 | `DEFERRED_LOWEST_PRIORITY` |
| **ORION-08** | C | optional real-domain transfer | optional; no venue requirement recorded | `RETURNED_TO_BOUNDED_SUBMISSION_LANE` |
| **ORION-10** | C | optional primitive-vocabulary freeze | optional; no venue requirement recorded | `RETURNED_TO_BOUNDED_SUBMISSION_LANE` |
| **ORION-19** | C | optional invariant-representation successor | optional; ceiling must be computed first | `RETURNED_TO_BOUNDED_SUBMISSION_LANE` |
| **ORION-07** | — | none listed | n/a | `RETURNED_TO_BOUNDED_SUBMISSION_LANE` |
| **ORION-12** | — | none listed | n/a | `RETURNED_TO_BOUNDED_SUBMISSION_LANE` |
| **ORION-13** | — | none listed | n/a | `RETURNED_TO_BOUNDED_SUBMISSION_LANE` |
| **ORION-14** | — | none listed | n/a | `RETURNED_TO_BOUNDED_SUBMISSION_LANE` |
| **ORION-18** | — | none listed | **blocked by proved impossibility** | `RETURNED_TO_BOUNDED_SUBMISSION_LANE__FORCED_BY_THEOREM` |

Four attempts authorized, one deferred, eight returned. **No promotion budget is spent by this
record**; authorization means the attempt may begin, not that it has.

---

## 1. ORION-18 is a different kind of return

The other seven returns are dispositions of *priority*: #1649 either does not list the paper, or
lists it as optional with no venue requirement. Any of them could be revisited if a target venue
later demands broader evidence.

ORION-18 cannot. `ORION18.COMMON_MODE_GOLD_NONIDENTIFIABILITY.v1` (PR #1617, Priority B)
establishes that when a system decision `A(x)` and an internal gold `G(x)` are generated under a
shared latent specification `S`, observing `A(x) = G(x)` **does not identify external truth**
`T(x)`: for any agreement-perfect dataset and any subset `K`, an alternative truth process
`T'(x) != A(x)` on `K` leaves the observed internal agreement identical.

So no promotion package built on same-programme evidence can clear the bar, **however much of it
is collected**. More internal CI, more conformance cases and more independent implementations of
the same specification all leave the identification problem exactly where it was. The missing
input is an externally governed adjudicator whose scientific judgment is not derived from the
programme's own ontology.

This is recorded as `FORCED_BY_THEOREM` rather than `DEFERRED` because it is not a scheduling
decision and will not change with effort. It is the strongest of the eight returns, and the
cheapest to defend at review.

---

## 2. What the four authorized attempts must satisfy

Each is bound by #1649's promotion-package rules, and each carries a stop rule taken from #1649
verbatim rather than restated:

| paper | stop rule (#1649) |
|---|---|
| ORION-23 | *"If the external corpus does not support the broader transport claim, retain the bounded current paper and publish the external boundary."* |
| ORION-17 | *"If arbitrary-chain behaviour adds no new consequence beyond pairwise theory, keep the bounded paper and do not inflate the contribution."* |
| ORION-16 | *"If real dependency extraction cannot be made authoritative, keep the general theorem and bounded paper; do not manufacture deployed-system claims."* |
| ORION-09 | *"If no invariant predicts the transition better than the existing bounded geometry, stop PRX-Quantum promotion and submit to the strongest defensible specialist venue."* |

**Freeze discipline for any attempt with real outcomes.** The protocol, discriminator, baselines,
metrics and stop rule must land in a commit containing **no results**, and results must land in a
later commit. A single commit holding both is unfalsifiable as a prospective freeze regardless of
what its text asserts — and given #1625's finding that this repository's freeze records are
re-pinned by their own checkers rather than verified, the commit boundary is the only durable
evidence of prospectivity available.

The deductive lanes have no such exposure and may land in one commit, disclosed as such.

---

## 3. Why ORION-05 is deferred rather than attempted

#1649 ranks the global obstruction basis 8th of 10 and gives it a stop rule that fires on either
of two outcomes — a new obstruction class, or no practical compiler consequence. The local
classification is already complete and `kappa_R6M = 2` is already sharp, so the bounded paper is
coherent without it.

Deferred, not returned: if the authorized attempts finish early it may be attempted, and if not
it returns to the bounded lane with no rescue cycle. Recording it as `DEFERRED` rather than
`RETURNED` keeps that distinction honest.

---

## 4. What returning to the bounded lane does and does not mean

For all eight returned papers:

- the bounded submission proceeds **unaffected**; #1609 remains the master and is not closed;
- every adverse, null and `CANNOT_CHECK` result stays exactly as recorded — a return changes
  nothing about the science;
- no further rescue cycle is authorized for them under #1649, which is the point of the rule;
- the existing successor-theory packets from PR #1617's programme stand on their own and are not
  withdrawn.

A return is a **disposition**, not a defeat. Seven of the eight are returned because #1649 did not
identify a credible top-tier path for them, and manufacturing one would be exactly the rescue
behaviour the issue exists to prevent.

---

## Authority

`scientific_authority_delta = NONE`.

No manuscript, ledger, receipt, terminal or claim row is modified by this record. No promotion
package is created, and no promotion budget is spent. The table above is a scheduling and
disposition record only; each authorized attempt must separately earn its own terminal under
#1649's definition of done.

Refs #1649, #1609, #1608, #1617, #1625

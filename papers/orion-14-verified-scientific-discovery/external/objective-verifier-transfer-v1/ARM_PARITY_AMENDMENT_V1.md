# ORION-14 external transfer — arm-parity amendment V1

**Status:** `PROTOCOL_AMENDED_BEFORE_OUTCOMES__STILL_UNRUN`
**Scientific authority delta:** `NONE`. No family has been acquired, no arm has been
run, and no outcome exists. The controlling terminal remains
`OBJECTIVE_VERIFIER_EXTERNAL_TRANSFER_PROTOCOL_FROZEN__OUTCOMES_UNRUN`.

## The discrepancy

Issue #1701's ORION-14 lane specifies **four** arms:

> *Arms: target-aware verifier; strongest generic product; compensatory proxy;
> **information-equivalent ideal control**.*

`PROTOCOL.md` freezes **three**, under the heading "Three policy arms":

| board arm | protocol arm |
|---|---|
| target-aware verifier | `B2 ORION_FULL` |
| strongest generic product | `B1 MATCHED_MULTI_REVIEW` |
| compensatory proxy | `B0 CHECKS_ONLY` |
| **information-equivalent ideal control** | **absent** |

Three of four map cleanly. The fourth has no counterpart.

## Why the missing arm is the one that matters

Without an ideal control, every reportable number is **relative**. `B2` beating `B1` on
21 of 30 families says B2 is better than the registered comparator; it says nothing about
how much of the achievable signal B2 actually captured. If the evidence bytes only
support, say, 70% correct promotion decisions, then a B2 at 68% is close to optimal and a
B2 at 40% is poor — and the B2-vs-B1 comparison cannot distinguish those two worlds.

That is precisely the objection a hostile reviewer raised against this paper — that some
contrasts *"measure interface expressiveness"* rather than verification competence — and
against ORION-19, that *"baselines are weak"*. A strong result against weak baselines and
a weak result against strong ones are indistinguishable without a ceiling.

The ideal control supplies the ceiling. It receives **exactly the same information** as
the policy arms — identical evidence bytes, public metadata and resource ceilings, per
`PROTOCOL.md`'s parity rule — and makes the best decision that information permits. The
gap between `B2` and the ideal control is then the honest statement of how much headroom
remains, and the gap between the ideal control and perfect accuracy is the honest
statement of what the evidence simply cannot decide.

## `B3 INFORMATION_EQUIVALENT_IDEAL_CONTROL`

**Information parity is the whole constraint, and it is what makes this a control rather
than an oracle.** `B3` sees the same bytes as `B0`, `B1` and `B2`. It does **not** receive
protected oracle labels, expected verifier outcomes, or hand-authored hints about which
cases are invalid — the same prohibition `PROTOCOL.md` already places on every policy
arm, whose violation terminates the affected family `CANNOT_CHECK_INFORMATION_PARITY`.

What distinguishes `B3` is decision quality, not information. It selects, per family, the
decision rule that maximises the primary endpoint **over the frozen evidence available to
all arms**, without consulting the protected outcome. It is the best achievable policy
under information parity, not the best achievable policy.

An arm that consults protected labels would be an **oracle**, would exceed parity, and
would make `B3` uninformative about headroom. If parity cannot be preserved for a family,
that family terminates `CANNOT_CHECK_INFORMATION_PARITY` exactly as any other parity
breach does.

## What `B3` does and does not change

It adds a **reference line**, not a gate. Specifically:

- The hard safety gate is unchanged: a confirmatory terminal still requires **zero `B2`
  severe false promotions** across the complete frozen external invalid-object set, and
  any such promotion still yields `ADVERSE_EXTERNAL_FALSE_PROMOTION` regardless of
  accuracy, cost or performance elsewhere.
- The family-level comparator gate is unchanged: still `>= 21/30` `B2`-over-`B1` family
  wins, compared lexicographically as before.
- `B3` **cannot rescue** an adverse terminal. A `B2` that trails `B3` badly is a reported
  weakness, not a failure; a `B2` that matches `B3` is reported as near-ceiling and still
  fails if it breaches the safety gate.

Adding a gate after the fact would be moving the goalposts. Adding a measurement is what
makes the existing gates interpretable.

## Why this amendment is legitimate now, and would not be later

`CLAIM_DISPOSITION.md` records the terminal as `..._PROTOCOL_FROZEN__OUTCOMES_UNRUN`, and
the family acquisition is listed "Still open". **No outcome exists against which this arm
could be tuned.** The amendment is a pre-registration correction, made while the register
is still closed.

The same change made after any family had been scored would be illegitimate and should be
refused, because a fourth arm chosen with knowledge of how the first three performed is
not a control. Recording that boundary here is the point of dating this file.

# ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Governing issue:** #1649 Tier A — **ORION-23's one promotion attempt, now spent**
**Terminal:** `THEOREM_PROVED__EXPLAINS_FROZEN_EXTERNAL_CAMPAIGN`
**Scientific authority delta:** `NONE`

---

## 1. Two corrections to #1649's premise

**The campaign was already executed.** #1649 says *"execute the already-frozen
external lifecycle campaign."* It has been: `campaign_executed: true`,
`results_exist: true`, `outcome_accessed: true`, 31 repositories, 93 cases, all
four pass gates met. **What was missing was the theorem, not the run.**

**I misread the corpus flags on first pass.** The pinning artifact carries
`campaign_executed: false` correctly — it pins repositories and contains no
results. That is not the campaign's status. Corrected here.

## 2. What was proved

**Theorem 1.** Reuse is sound iff every load-bearing premise is `UNCHANGED`;
`CONTRADICTED` forces `REVALIDATE`; `UNKNOWN` forces `CANNOT_CHECK`. The proof
forces the asymmetry that `CONTRADICTED` dominates `UNKNOWN`.

**Theorem 2.** If the observable does not determine a load-bearing premise, **no
observable-measurable policy is both sound and non-vacuous** on that class. The
two horns are unsound reuse and vacuous abstention.

**Theorem 3.** A sound non-vacuous policy's cost is floored by `cost(L)`; the
achievable reduction is bounded by the non-load-bearing remainder. **Anything
cheaper than the floor is unsound or vacuous — not merely worse.**

## 3. The theorems explain every arm, including the failures

| arm | valid | forged FA | stale FA | ops/repo | classification |
|---|---|---|---|---|---|
| `always-raw` | 1.00 | 0 | 0.00 | 10 | sound, non-vacuous |
| `lifecycle-rcs` | 1.00 | 0 | 0.00 | **7** | sound, non-vacuous |
| `provenance-only` | 1.00 | 0 | **1.00** | 5 | **unsound** |
| `confidence-only` | **0.00** | 0 | 0.00 | 3 | **vacuous** |

`provenance-only` cannot see staleness of a load-bearing premise, so Theorem 2
forces it onto a horn — and it takes the accepting one, giving a stale
false-accept rate of exactly `1.00`. `confidence-only` sees nothing load-bearing
and takes the other horn, accepting `0.00` of valid cases. **The theorem predicts
not merely that each fails but which way.**

`lifecycle-rcs` is **behaviourally identical to the exhaustive baseline on all 93
cases** at `7` ops instead of `10`.

**The cost floor is visible in the data.** The cheapest sound non-vacuous arm
costs `7`; every arm cheaper than `7` is unsound or vacuous. So the `30%`
reduction is the **maximum a sound policy can achieve here**, not a tuning
outcome — and the tempting `50%`/`70%` reductions are purchasable only by giving
up soundness or usefulness.

That is what makes this a law rather than a benchmark win: one statement explains
the positive and the adverse regimes together.

## 4. #1649's primary success criterion — met

Exact correctness (identical to `always-raw`), strictly lower cost (`7` vs `10`),
fewer unsafe reuses than provenance-only (`0.00` vs `1.00`) — on 31 externally
sourced repositories across 14 organizations.

## 5. What this packet does not claim

**It is not prospective.** The campaign was frozen on 2026-08-24 and its outcomes
were readable before the theorems were written. This is **explanatory adequacy on
pre-existing frozen evidence**. §6 of `THEORY.md` specifies a genuinely
prospective test — a second organization-disjoint corpus with the cost floor
predicted as a *number* before derivation — and that test is **not executed here**.

**It creates no protected confirmation.** The gold rule's non-bypass boundary
states that an AI session does not create protected confirmation. That binds this
packet, and is acknowledged rather than sidestepped.

**It closes no adjudication gap.** Governance, quality and responsibility
judgments remain `CANNOT_CHECK` without two independent experts plus a
tie-break/custodian. The blinded protocol remains unexecuted.

## 6. Adverse and `CANNOT_CHECK` evidence — preserved and load-bearing

`123` facts decided, **`32` `CANNOT_CHECK`**. Every `TEST_EXIT` fact is
`CANNOT_CHECK`, for the recorded reason that the locked per-repository runtime the
contract requires does not exist and an exit status obtained another way *is not
that fact*. That refusal to substitute a convenient measurement is preserved
verbatim.

**None converted.** No gate re-evaluated, no gold re-derived, no campaign re-run,
no network request made.

## 7. Donor boundary

Provenance systems, proof-carrying actions, certificate reuse, incremental
verification and sufficiency-versus-observable arguments are all **donor-owned**.
**No novelty is claimed for any of them.**

The ORION residual is the **responsibility-relative** criterion — transport
validity is relative to what the claim is *responsible for*, not to provenance or
version identity — plus the cost floor that follows and its confirmation across
four arms. That is the paper's existing thesis; this packet turns it from a
position into a theorem with a measured floor.

## 8. Stop rule and budget

**#1649 stop rule, verbatim:** *"If the external corpus does not support the
broader transport claim, retain the bounded current paper and publish the external
boundary."*

The corpus **does** support it on the objective fact classes the gold rule admits.
The remaining boundary is published as §5 above rather than papered over.

**ORION-23's promotion budget is now SPENT.** No further rescue cycle is
authorized under #1649. If the prospective test in §6 is later run and fails, the
paper returns to its bounded submission lane.

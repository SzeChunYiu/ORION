# ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1 — THEORY

**Paper:** ORION-23 — Responsibility-Carrying State
**Successor id:** `ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1`
**Governing issue:** #1649 Tier A (execution order 4)
**Authorized by:** `WAVE1_TOP_TIER_PROMOTION_TRIAGE_2026-08-28.md` — this is ORION-23's **one** promotion attempt
**Authored:** 2026-08-28
**Status:** `THEOREM_PROVED__EXPLAINS_FROZEN_EXTERNAL_CAMPAIGN`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 0. Two corrections to #1649's premise, stated first

**(a) The campaign was already executed.** #1649 says *"Execute the already-frozen
external lifecycle campaign before redesigning the corpus."* It has been executed.
`P13_P14_POLICY_COMPARISON_V1.json` carries `campaign_executed: true`,
`results_exist: true`, `outcome_accessed: true` over 31 repositories and 93 cases,
and all four pass gates are met. Nothing needed running; what was missing was the
**theorem**.

**(b) The corpus-pinning artifact's `false` flags are not the campaign's.**
`P13_P14_PINNED_REPOSITORY_CORPUS_V1.json` carries `campaign_executed: false` and
`outcome_accessed: false` — correctly, because that artifact pins repositories and
deliberately contains no results. Reading those flags as the campaign's status is
a mistake I made on first pass and correct here.

**(c) Disclosure that bounds this packet's claim.** The campaign outcomes were
frozen on 2026-08-24 and were **readable by me before I wrote these theorems**.
This is therefore **explanatory adequacy on pre-existing frozen evidence, not
prospective validation**. §6 states what a prospective test would be. No claim of
prospectivity is made anywhere in this packet.

---

## 1. Setting

A claim `c` is supported by premises `P(c)`. A distinguished subset
`L(c) ⊆ P(c)` is **load-bearing**: the validity of `c` depends on them. Under
update, each load-bearing premise is in exactly one state:

```
UNCHANGED      still holds, or is entailed by the new state
CONTRADICTED   the new state refutes it
UNKNOWN        its status cannot be resolved from available information
```

A **transport policy** observes some information `I` and emits one of
`ACCEPT` (reuse the certificate), `REVALIDATE` (revoke/recompute), or
`CANNOT_CHECK`.

---

## 2. The theorems

### Theorem 1 (responsibility-relative transport rule)

Reuse is sound **iff** every load-bearing premise is `UNCHANGED`. If any is
`CONTRADICTED`, the correct terminal is `REVALIDATE`. If none is `CONTRADICTED`
but some is `UNKNOWN`, the correct terminal is `CANNOT_CHECK`.

**Proof.** If all load-bearing premises hold, the original support survives and
the certificate transports. If one is contradicted, the support is broken and
reuse asserts a claim whose premises fail. If one is unknown and none is
contradicted, both a sound-reuse world and an unsound-reuse world are consistent
with the observation, so no decision is justified and abstention is the only
correct terminal. ∎

Note the asymmetry that the proof forces: **`CONTRADICTED` dominates `UNKNOWN`**.
A policy that treats unknown as clean is unsound; a policy that treats unknown as
contradicted is merely conservative.

### Theorem 2 (information necessity — why provenance-only fails)

Let `I` be a policy's observable. If `I` does not determine the status of some
load-bearing premise `l`, then there are two update states agreeing on `I` in
which `l` is `UNCHANGED` and `CONTRADICTED` respectively. Hence any
`I`-measurable policy either

- **accepts** on that class, and is **unsound** on the contradicted member, or
- **refuses** on that class, and is **vacuous** on the sound member.

**No `I`-measurable policy is both sound and non-vacuous on that class.** ∎

This is the same fibre object as ORION-09's separator complexity, ORION-13's
semantic separator, ORION-10's explanation gap and ORION-16's dependency closure:
a decision cannot be exact where the observable merges states requiring different
decisions. Here the merged states are *premise statuses*, and the two horns are
**unsound reuse** and **vacuous abstention**.

### Theorem 3 (cost floor)

A sound, non-vacuous policy must resolve every load-bearing premise, so its check
cost is at least `cost(L(c))`. Reuse can skip exactly the non-load-bearing
remainder, so the achievable cost reduction is bounded by
`cost(P(c) \ L(c)) / cost(P(c))`. ∎

**Corollary.** Any policy cheaper than `cost(L(c))` is unsound or vacuous — not
merely worse. Cheapness below the floor is a *diagnosis*, not a tradeoff.

### Corollary 4 (minimal revalidation)

When revalidation is required, the minimal sufficient set is the affected
proof/dependency subgraph under separation witnesses — which is exactly
`ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1`'s `A(Delta)`, applied to the premise
graph. The two results compose: Theorem 1 says *whether* to revalidate,
`A(Delta)` says *what*.

---

## 3. The theorems explain every arm of the frozen external campaign

31 repositories, 14 organizations, 93 cases (`VALID` 31, `FORGED` 31, `STALE` 31).
Measured values are recomputed from the frozen receipt by the checker.

| arm | valid accept | forged FA | stale FA | ops/repo | theorem classification |
|---|---|---|---|---|---|
| `always-raw` | 1.00 | 0 | 0.00 | **10** | `SOUND_AND_NON_VACUOUS` |
| `lifecycle-rcs` | 1.00 | 0 | 0.00 | **7** | `SOUND_AND_NON_VACUOUS` |
| `provenance-only` | 1.00 | 0 | **1.00** | **5** | `UNSOUND` |
| `confidence-only` | **0.00** | 0 | 0.00 | **3** | `VACUOUS` |

Arm by arm, as the theorems predict:

- **`always-raw`** resolves every premise, so it is sound by Theorem 1 — and pays
  the full `10`, because it never exploits the fact that unchanged premises permit
  reuse.
- **`provenance-only`** observes provenance, which does not determine *staleness*
  of a load-bearing premise. Theorem 2 says it must take one of the two horns; it
  takes the accepting horn, so it is unsound — and its stale false-accept rate is
  `1.00`, the maximum. **The theorem predicts not just that it fails but which
  failure it takes.**
- **`confidence-only`** observes a signal that determines no load-bearing premise
  at all. It takes the other horn: it refuses everything, so its valid-accept rate
  is `0.00`. It is sound **only by being vacuous**.
- **`lifecycle-rcs`** observes load-bearing premise support. It is behaviourally
  **identical to `always-raw` on all three case classes** — 31/31 `VALID`
  accepted, 0/31 `FORGED`, 0/31 `STALE` — at `7` ops instead of `10`.

### The cost floor is visible in the data

The cheapest sound, non-vacuous arm costs `7` ops/repo. **Every arm cheaper than
`7` is unsound or vacuous** — `provenance-only` at `5`, `confidence-only` at `3`.
That is Theorem 3's corollary, confirmed on external data: the `30%` reduction
`lifecycle-rcs` achieves is not a tuning outcome but the **maximum a sound policy
can achieve on this corpus**, and the larger `50%`/`70%` reductions are available
only by giving up soundness or usefulness.

This is what makes the result a law rather than a benchmark win: it explains the
**positive and the adverse regimes with the same statement**, and it says why the
losing arms lose.

---

## 4. #1649's primary success criterion

> *"exact/near-exact lifecycle correctness with strictly lower external
> check/recompute cost than always-revalidate and fewer unsafe reuses than
> provenance-only controls."*

| requirement | measured |
|---|---|
| exact lifecycle correctness | `1.00` valid, `0` forged, `0.00` stale — identical to `always-raw` |
| strictly lower cost than always-revalidate | `7` vs `10` ops/repo, `30%` reduction |
| fewer unsafe reuses than provenance-only | `0.00` vs `1.00` stale false-accept |

All three met, on 31 externally sourced repositories across 14 organizations.

---

## 5. Preserved adverse and `CANNOT_CHECK` evidence

Nothing is softened, and the `CANNOT_CHECK` mass is large and load-bearing:

- **`123` facts decided, `32` facts `CANNOT_CHECK`** in the objective gold.
- **Every `TEST_EXIT` fact is `CANNOT_CHECK`**, with the recorded reason: *"the
  locked per-repository runtime the contract requires does not exist, and an exit
  status obtained another way is not that fact."* That is a refusal to substitute
  a convenient measurement for the specified one, and it is preserved verbatim.
- The campaign boundary stands: *"No governance, quality or responsibility
  judgment is made anywhere; those remain `CANNOT_CHECK` without two independent
  experts plus tie-break/custodian."*
- The gold-derivation rule's non-bypass boundaries stand, including *"public
  online data does not create independent adjudication"* and *"an AI session, a
  local hash, same-owner replay or same-owner CI does not create protected
  confirmation."*

The last one applies to this packet: **I am an AI session, so nothing here creates
protected confirmation.** The theorems are independently checkable; the external
adjudication gap is not closed by them and is not claimed to be.

---

## 6. What a prospective test would be, and why this is not one

The outcomes were readable before the theorems were written, so §3 is
**explanatory adequacy**, not prediction.

A genuinely prospective test is available and cheap to specify:

1. freeze a **second** repository corpus, disjoint in organization from the
   current 14;
2. freeze, before any derivation, the theorem's **quantitative** predictions —
   that the cheapest sound arm's ops/repo equals `cost(L)`, that every cheaper arm
   is unsound or vacuous, and that a provenance-style arm takes the accepting horn
   with stale false-accept near `1.00`;
3. derive gold under the same rule, run the same arms, and compare.

Theorem 3 makes that test sharp: it predicts a **specific number** — the sound
cost floor — not merely an ordering. That is what a future campaign should target.

Until then the honest terminal is the one at the top of this file.

---

## 7. Donor boundary

Provenance systems, proof-carrying actions, certificate reuse and incremental
verification own the generic transport machinery. Sufficiency-versus-observable
arguments are donor-owned information theory. **No novelty is claimed for any of
it.**

The ORION residual is narrow and specific: the **responsibility-relative**
criterion — that the premises which matter are the load-bearing ones, so transport
validity is relative to *what the claim is responsible for* rather than to
provenance or version identity — together with the cost floor that follows from it
and its confirmation across the four arms.

That residual is exactly the paper's existing thesis, *"validity/reuse is
responsibility-relative, not provenance-relative."* This packet turns it from a
position into a theorem with a measured floor.

---

## 8. Authority boundary and stop rule

`scientific_authority_delta = NONE`.

- No campaign result, gate, terminal, receipt or gold record is modified,
  re-derived or re-run. The arm table is **recomputed from the frozen receipt and
  compared**, never regenerated.
- No `CANNOT_CHECK` is converted. The 32 `CANNOT_CHECK` facts and the whole
  governance/quality/responsibility judgment layer stay exactly as recorded.
- No external adjudication is claimed; the blinded two-expert protocol remains
  unexecuted and this packet does not substitute for it.
- No manuscript byte is modified.

**Stop rule (#1649, verbatim):** *"If the external corpus does not support the
broader transport claim, retain the bounded current paper and publish the external
boundary."*

The corpus **does** support it, on the objective fact classes the gold rule admits.
The boundary that remains — governance and responsibility judgments, and external
adjudication — is published here as §5 rather than papered over. This is
ORION-23's one promotion attempt under #1649, and it is complete.

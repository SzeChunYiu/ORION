# ORION17.CLOSURE_CHAIN_COMPOSITION.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Governing issue:** #1649 Tier A — **ORION-17's one promotion attempt, now spent**
**Terminal:** `RE_VERIFICATION_PLUS_ONE_LEMMA__TIER_A_EVIDENCE_NOT_EARNED`
**Outcome:** **returned to the bounded submission lane**
**Scientific authority delta:** `NONE`

---

## 1. Retraction, stated first

An earlier draft of this packet framed Theorems 1–2 as a **new arbitrary-chain
theorem**. That was wrong.

`CLAIM_LEDGER_V4.md` row `ORION-17.V4.5` already states, as a **mechanized
theorem** (Z3 over uninterpreted sorts):

> *"Heterogeneous closure-carrying transforms compose scientifically only under
> exact intermediate closure-contract binding or a registered equivalence bridge —
> for chains of any length, over any number of transformations, contracts, closure
> coordinates and obligations, and for every donor-native validity predicate."*

That subsumes both directions I had written up as new — sufficiency, and necessity
via *"only under"*. The Wave-1 closure blueprint (§4.10) flags exactly this, and
it is correct.

## 2. What actually survives

1. **Independent re-verification by a different method.** The ledger's proof is Z3
   over uninterpreted sorts; this one is explicit finite enumeration over concrete
   chains (775 bridging chains to length 5, with exhibited witnesses). A shared
   solver-encoding error could not produce both. That has real value — as
   corroboration, not as a new result.
2. **Classification of the frozen three-domain campaign.** `exact-containment` is
   sound and exact in all three real packages; `donor-coarse` is unsound on numpy
   and scipy (27,348 and 50,282 false retentions) and merely conservative on
   flask, where 19 import edges are too few to separate the coarse test from the
   exact one. The adverse regime appears exactly where dependency structure is
   rich enough to separate them.
3. **One lemma the ledger does not contain.** Searching `CLAIM_LEDGER_V4.md` for
   `affected`, `revalidat`, `slice` and `ancestral` returns **zero** matches. The
   affected-obligation slice lemma — obligations reachable from `Delta` *and*
   ancestral to the closure root `r` form the unique minimal sound revalidation
   set — is new to this paper. Per blueprint §4.11 it is recorded as a
   **revalidation lemma, not a headline**, because it is structurally shared with
   ORION-16.

## 3. The stop rule fires

**#1649, verbatim:** *"If arbitrary-chain behaviour adds no new consequence beyond
pairwise theory, keep the bounded paper and do not inflate the contribution."*

On the corrected reading it adds none: V4.5 already owns it.

Per blueprint §4.12, ORION-17's real Tier-A blocker is a **decisive naturalistic
multi-hop study** — one genuine chain of three distinct operations
(representation/schema migration, responsibility relabel, objective change), all
facts externally sourced, predictions stamped **before** global closure labels are
opened, against five registered baselines.

**That study is not done here.** The Tier-A evidence breakthrough is therefore
**not earned**, and ORION-17 **returns to its bounded submission lane**.

## 4. What the bounded paper keeps

Everything. The bounded paper is unaffected and is explicitly **not inflated**.
V4.5, the pairwise theory, the nonclosure countermodels and the campaign results
are all unchanged. `donor-coarse`'s 77,630 combined false retentions and
`always-reopen`'s up to 382,044 unnecessary reopenings remain reported in full. No
`CANNOT_CHECK` is converted.

## 5. Donor boundary

**No novelty claimed.** Assume-guarantee and contract-based compositional
verification own generic compositional verification; induction over chains is
elementary; and — the point of §1 — the arbitrary-chain result is owned by this
paper's own prior ledger row, not by this packet.

## 6. Budget

**ORION-17's promotion budget is spent**, terminating in a return to the bounded
lane rather than a promotion. No further rescue cycle is authorized under #1649.

This is the correct outcome, not a shortfall: #1649 exists precisely to make one
honest attempt and stop.

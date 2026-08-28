# Wave-1 top-tier promotion pass — closure record

**Governing issue:** #1649. **Additive to** #1609 (closeout master) and #1608 (successor discipline).
**Blueprint:** ORION Wave-1 Top-Tier Closure Blueprint, 2026-08-28.
**Triage this closes out:** `WAVE1_TOP_TIER_PROMOTION_TRIAGE_2026-08-28.md`
**Status:** `PROMOTION_PASS_COMPLETE__ALL_THIRTEEN_DISPOSED`
**Scientific authority delta:** `NONE`

---

## 1. Result in one line

Of thirteen papers, **two earned a materially stronger result**, **one attempt
terminated in a return to the bounded lane**, **one budget was deliberately left
unspent**, **one stays deferred**, and **eight were returned without an attempt**.
No paper received a second rescue cycle.

---

## 2. Disposition of all thirteen

| paper | #1649 tier | attempt | terminal | budget |
|---|---|---|---|---|
| **ORION-23** | A | `EXTERNAL_RESPONSIBILITY_TRANSPORT.v1` | **theorem earned**; explains all four external arms, cost floor measured | spent |
| **ORION-16** | A | `REAL_SYSTEM_MINIMAL_REVALIDATION.v1` | **theory objective earned**; empirical discriminator explicitly not earned | spent |
| **ORION-17** | A | `CLOSURE_CHAIN_COMPOSITION.v1` | **returned to bounded lane** — target already existed | spent |
| **ORION-09** | B | none | derivation material filed | **unspent** |
| **ORION-05** | B | none | deferred, ranked 8th of 10 | unspent |
| ORION-07 | — | none | returned | n/a |
| ORION-08 | C | none | returned | n/a |
| ORION-10 | C | none | returned | n/a |
| ORION-12 | — | none | returned | n/a |
| ORION-13 | — | none | returned | n/a |
| ORION-14 | — | none | returned | n/a |
| ORION-18 | — | none | **returned, forced by theorem** | n/a |
| ORION-19 | C | none | returned | n/a |

---

## 3. What was earned

### ORION-23 — the strongest outcome of the pass

A responsibility-relative transport law that **explains every arm of an already
frozen 31-repository, 14-organization external campaign**, including both
failures:

| arm | valid | forged FA | stale FA | ops/repo | classification |
|---|---|---|---|---|---|
| `always-raw` | 1.00 | 0 | 0.00 | 10 | sound, non-vacuous |
| `lifecycle-rcs` | 1.00 | 0 | 0.00 | **7** | sound, non-vacuous |
| `provenance-only` | 1.00 | 0 | **1.00** | 5 | **unsound** |
| `confidence-only` | **0.00** | 0 | 0.00 | 3 | **vacuous** |

The theorem predicts *which horn* each failing arm takes, and the cost floor is
visible in the data: **every arm cheaper than 7 ops/repo is unsound or vacuous**,
so `lifecycle-rcs`'s 30% saving is the maximum a sound policy can achieve here
rather than a tuning outcome.

This satisfies #1649's criterion 4 — a law explaining positive and adverse regimes
together — and its ORION-23 primary success criterion in full.

### ORION-16 — theory objective, honestly bounded

The two-sided exact accounting for imperfect dependency graphs: over-approximation
costs `w(A_G \ A_{G*})`, under-approximation risks `w(A_{G*} \ A_G)`, exactness is
uniquely optimal, and **the only safe response to detected incompleteness is
`CANNOT_CHECK`**. The frozen real-transition gold matches the taxonomy 4/4.

The empirical discriminator is **not** earned and says so.

---

## 4. What the pass got wrong, and corrected

Three errors, all of the same shape — **a claim asserted wider than the check
behind it** — and all corrected in-branch rather than left standing:

1. **ORION-17 duplicated an existing theorem.** `CLAIM_LEDGER_V4.md` row
   `ORION-17.V4.5` already states the arbitrary-length composition theorem,
   mechanized in Z3, including necessity via *"only under"*. The blueprint §4.10
   caught it. Retracted; the lane now claims only an independent re-verification
   by a different method, a campaign classification, and one lemma the ledger
   genuinely lacks.
2. **ORION-16 asserted a repository-scoped absence from a paper-scoped search.**
   ORION-17's `P7_CLOSURE_RETENTION_V1.json` — three real Python packages, 604,542
   certificate decisions — is adjacent evidence that does not substitute but had
   to be pointed at. Corrected.
3. **A CI report over-generalized.** I reported that all ten earlier Wave-1 PRs
   failed on only two pre-existing jobs; that was generalized from five. PR #1638
   also failed `candidate-theory`, and that failure **was mine**.

The third produced a real repair, below.

---

## 5. The content-binding repair

`check_content_binding_v1.py` enumerates its hashed set from the filesystem, so an
additive file no manifest names turns the gate red **by design** — *"an
unmanifested addition still turns this checker red instead of shrinking the old
binding by convention."* Its `--write` refuses and directs additions to
`CONTENT_MANIFEST_V2.json`.

Three PRs were red for this reason (#1638, #1656, #1658). All three now bind their
additive theory files into V2 via the established three-part pattern — manifest →
`content_binding_v2/SHA256SUMS` → receipt — with **V1 untouched** and each receipt
recording `binds: BYTES ONLY`, `grants_authority: NONE`.

**The binding was built last in every case**, after every content edit it covers,
including the ORION-17 retraction and the packet-contract additions. Building it
earlier would have bound bytes that then changed.

---

## 6. Packet contract

All three #1649 lanes now carry the blueprint §7 nine-file contract. Two files
were missing and were added:

- **`NEGATIVE_HISTORY.jsonl`** — *derived* from each packet's own
  `EXPECTED_TERMINALS` preserved-evidence list, so the two cannot silently
  disagree. Every row carries `converted_by_this_lane: false`.
- **`RESOURCE_ACCOUNTING.json`** — records `0` new experiments and `0` network
  requests for all three lanes, the exact enumeration counts, the measured
  baseline costs, and a statement of why each comparison is information-matched.

---

## 7. Adverse and `CANNOT_CHECK` evidence across the pass

Nothing was converted, softened or dropped. The load-bearing items:

- ORION-23: **32 of 155** objective-gold facts are `CANNOT_CHECK`; **every
  `TEST_EXIT` fact** is, for the recorded reason that the locked per-repository
  runtime does not exist and *an exit status obtained another way is not that
  fact*.
- ORION-16: `RC-ALIAS-MISSING → CANNOT_CHECK` is the lane's **central
  confirmation**, not an inconvenience.
- ORION-17: `donor-coarse`'s 77,630 false retentions and `always-reopen`'s up to
  382,044 unnecessary reopenings, plus the flask domain **retained** rather than
  dropped for being the least favourable.
- ORION-09: the `n=4` forecast failure and the absence of any executed `n=5`
  component stand verbatim.

Three lanes state explicitly that they are **not prospective**: their outcomes
were readable before the theorems were written. Each specifies the prospective
test that would settle the matter, and none of those tests is executed.

---

## 8. Where each returned paper actually stands

Per the blueprint §6, and unchanged by this pass:

- **ORION-18** — returned **by theorem**. Common-mode non-identifiability means no
  volume of same-programme evidence can close it; only an independently governed
  adjudicator can.
- **ORION-13** — the old corpus is confounded, which this programme's own #1632
  measured: every opposite-verdict case in both frozen sets is a polarity flip. A
  successor needs a separately frozen balanced corpus with a same-universe
  comparator. **The bounded mapping submission must not be held open for it.**
- **ORION-14, -12, -07, -06** — closeout and filing work, not science. ORION-14
  needs metadata and upload only.
- **ORION-08, -10, -19** — optional, venue-driven, never blockers.

---

## 9. What remains open, stated plainly

- **ORION-09's one attempt is unspent**, deliberately. The valid path is the
  blueprint's `O_t` obstruction basis validated prospectively at `n=5`, not the
  capacity statistic I began.
- **ORION-05 stays deferred** at rank 8 of 10, with its bounded submission
  unaffected.
- **ORION-23's prospective organization-disjoint confirmation is not run**, and it
  is the paper's remaining blocker per blueprint §3.
- **ORION-16's and ORION-17's empirical discriminators are not run.**
- The repository-wide `ci` workflow remains red on `main` independently of this
  work — 32 failing assertions across 36 test files, reproduced on a pristine
  zero-change worktree.

---

## 10. Authority

`scientific_authority_delta = NONE` for every paper. No manuscript, ledger,
receipt, gate, terminal or claim row was modified anywhere in this pass. Every
lane is an additive directory plus, where the gate required it, a byte-only V2
binding.

#1609 and #1608 remain open and are not closed by this record.

Refs #1649, #1609, #1608, #1617, #1625, #1634

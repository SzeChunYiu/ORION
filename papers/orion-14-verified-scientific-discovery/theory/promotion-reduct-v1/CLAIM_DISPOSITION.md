# ORION14.MINIMAL_PROMOTION_REDUCT.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Terminal:** `PARTIAL__SCOPE_GATED__COMPUTED_ON_THE_COMMITTED_CORPUS`
**Scientific authority delta:** `NONE`
**New blocker raised:** none for submission

---

## 1. The scope gate comes first

Upgrade A — **ranked #2 by expected value** in #1617 — asks for a minimal
promotion reduct over the frozen 400 cases behind
`ORION-14.X.EXACT.400.PROMOTION_RELATION`.

**That table is not committed anywhere in the repository.** The checker searches
repo-wide (excluding `.git`) both by size — every `.jsonl` with 350–450 rows — and
by content — every `.json`/`.jsonl`/`.py` naming the promotion relation. The 11
size hits are ORION-12 SAGE corpora at 385 rows; the one content hit carries no
such table. The claim row records the counts
(400/400, 250/400, 50/400, 400/400) but not the rows.

So the highest-value ORION-14 upgrade is blocked on an **artifact**, not on
science. The remedy is to commit the 400-row coordinate table. Nothing needs to
be re-run.

The deep-upgrade note itself says the reduct should be computed *"if it can be
done entirely from frozen rows."* It cannot, so the bounded submission proceeds
unaffected.

## 2. What was computed instead

The committed 10-case method-authority bench, clearly labelled throughout as a
**different and smaller object**:

```
k* = 3
reducts   { claims_new_primitive, known_composition, prior_art_found }
          { known_composition, prior_art_found, req:NOVELTY }
core      { known_composition, prior_art_found }
```

## 3. The finding worth keeping: `CANNOT_CHECK` is load-bearing

`prior_art_found` is three-valued: `true` (found), `false` (searched, found
nothing), `null` (search could not run).

`closed_world_new_method` and `novelty_unknown` are **identical on every other
recorded field**, including all five required coordinates. They differ in
promotability solely because one has `false` and the other `null`.

**Collapse `null` into `false` and no feature set is sufficient at all** — `k*`
goes from `3` to undefined. The distinction between *checked and clean* and
*could not check* carries the entire relation.

This is a concrete, verifiable instance of the programme's rule that
`CANNOT_CHECK` must never be conflated with a negative. I made exactly that error
on the first pass; the checker's negative control now enforces the distinction so
it cannot recur silently.

## 4. What this does not show

The validity, applicability, transfer and utility coordinates appear in **no**
reduct — because every bench case satisfies them, so none ever separates an
opposite-target pair. **The bench does not test them.** This is a corpus-design
limit, structurally identical to ORION-13's polarity confound, and it is *not*
evidence that those coordinates are unnecessary.

## 5. Adverse and null evidence

`ORION-14.X.EXACT.400.PROMOTION_RELATION` untouched — this packet could not touch
it. The **H3 null** is unchanged, as #1609 requires. `TRANSPORT_CANNOT_CHECK_HTTP_400`
and the other recorded `CANNOT_CHECK` dispositions are unchanged; **none
converted**.

## 6. Independent verification

No ORION-14 module imported. The bench is read as data and the reduct recomputed
from the discernibility definition, exhaustively over all `2^17` subsets. The
absence of the 400-case table is **asserted by search**, not assumed. **3/3**
negative controls fire.

## 7. Donor boundary

**No novelty claimed.** Discernibility, reducts and cores are donor-owned
rough-set mathematics — the same object as ORION-09, ORION-13, ORION-16 and
ORION-10.

## 8. Blocker status

`ORION-14 IS NOT BLOCKED BY THIS LANE.` #1617 recommends *submit rather than
expand* for ORION-14. The absent table blocks an **optional** upgrade, not the
submission.

# ORION-17 — governance adjudication for `ORION17.DENSITY_PROSPECTIVE.v1`

**Date:** 2026-08-29
**Authority:** issue #1701 board, P0 line — *"ORION-17: recover/audit #1692 5/5 prospective
density result; resolve governance; write standalone manuscript."*
**Scientific authority delta:** `NONE`.

Both histories are retained in the tree. Neither is discarded and neither is relabelled.

## 1. The two histories, side by side

**History A — #1649 stop, recorded in `theory/chain-composition-v1/`.**
`ORION17.CLOSURE_CHAIN_COMPOSITION.v1` retracted its own framing of Theorems 1–2 as a
new arbitrary-chain theorem, because `CLAIM_LEDGER_V4.md` row `ORION-17.V4.5` already
owned that result as a Z3-mechanized theorem. #1649's stop rule fired verbatim — *"If
arbitrary-chain behaviour adds no new consequence beyond pairwise theory, keep the
bounded paper and do not inflate the contribution"* — the packet returned ORION-17 to
its bounded submission lane, and recorded `ORION-17's promotion budget is spent`.
Terminal: `RE_VERIFICATION_PLUS_ONE_LEMMA__TIER_A_EVIDENCE_NOT_EARNED`. Its
`NEGATIVE_HISTORY.jsonl` preserves five negatives, including the adverse terminal
`ARBITRARY_CHAIN_THEOREM_ALREADY_EXISTED` and flask as an informative control.

**History B — the later prospective result, recorded in this directory.**
Five of five stamped predictions correct on held-out repositories, including the
registered disambiguator.

## 2. Adjudication

The later result is **admissible and is not a forbidden rescue**, and it **does not earn
Tier A**. Both halves follow from what #1649 actually stopped and what it actually
required.

**Not a rescue.** #1649's stop fired on a specific object: an arbitrary-chain composition
theorem already owned by V4.5. The density lane does not touch that object. It tests a
different one — the mechanism attribution behind `donor-coarse`'s empirical failure
pattern — against outcomes that did not exist when the attribution was written. The
adverse terminal `ARBITRARY_CHAIN_THEOREM_ALREADY_EXISTED` stands unchanged and
unretracted, and no `CANNOT_CHECK` is converted anywhere.

**Does not earn Tier A.** #1649 defined ORION-17's Tier-A blocker by a *study design*:
a decisive naturalistic multi-hop study over one genuine chain of three distinct
operations (representation/schema migration, responsibility relabel, objective change),
all facts externally sourced, predictions stamped before global closure labels are
opened, against five registered baselines. That study was not run. A different study,
however cleanly executed, cannot discharge a blocker defined by design. The density
packet says exactly this in its own `RESULT.md` §4, and this adjudication does not
soften it.

**Consequent terminal:** `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED`. The
bounded paper is strengthened by an admissible prospective mechanism claim; the top-tier
successor as #1649 defined it remains unearned and separately tracked.

## 3. Chronology, verified from git rather than from prose

| fact | how it is checkable |
|---|---|
| the stamping commit's tree contains no result file | `git ls-tree -r --name-only 1db5eaa46 -- <dir>` lists `HELD_OUT_DENSITY.json`, `STAMPED_PREDICTIONS.md`, `o17_density.py` only |
| the result commit descends from it | `git merge-base --is-ancestor 1db5eaa46 9841b15c4` exits 0 |
| `9841b15c4` is the first commit holding the outcome | its tree adds `HELD_OUT_RESULT.json`, `RESULT.md`, `independent_checker/` |
| threshold and predictions never moved | `git diff --quiet 1db5eaa46 9841b15c4 -- <each pre-outcome file>` exits 0 for all three |
| the recovered copy is the stamped copy | `STAMPED_PREDICTIONS.md` sha256 `ee046b2fe9a01123a32906a7002970f3d8fbe66bf4e3cd55b6dffc7c9b9b5e3b` equals `git show 1db5eaa46:<path>` |

The byte-identity fact is the strongest, because it does not rely on commit metadata.
Commit timestamps are author-settable; tree content and ancestry are not. The manuscript
leads with tree content for that reason.

## 4. What was added to the paper

- `submission/density_prospective/main.tex` — standalone venue manuscript, which
  discharges the filing terminal `BLOCKED__NO_STANDALONE_MANUSCRIPT` recorded in
  `RESULT.md` §9. Written under `papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md` using
  `nature-writing` (research playbook, evidence-first drafting order, generic-journal
  fragment, English language fragment).
- `CLAIM_LEDGER_V4.md` row `ORION-17.V4.12`, in the file's existing three-column form,
  carrying all four scope limits in the forbidden-upgrade column.
- `CLAIM_LEDGER_V4.md` boundary addendum dated 2026-08-29, parallel to the V4.11
  addendum. The original boundary sentence is **not** edited: `git diff --numstat` on
  that file reports 14 insertions and 0 deletions.

## 5. Preserved, unsoftened

- The `#1649` stop, the spent promotion budget, and the return to the bounded lane.
- All five entries of `theory/chain-composition-v1/NEGATIVE_HISTORY.jsonl`, including
  `ARBITRARY_CHAIN_THEOREM_ALREADY_EXISTED` and the flask informative control.
- `donor-coarse`'s 77,630 combined false retentions on the calibration campaign and
  `always-reopen`'s up to 382,044 unnecessary reopenings.
- The blueprint §4.12 naturalistic multi-hop blocker, still open.
- The no-naturalistic-corpus boundary on *navigation* claims, unchanged.
- ORION-16's convergent boundary is labelled convergent same-programme evidence in both
  the manuscript and the ledger row, never independent corroboration.

## 6. Not done here

The independent checker was not re-executed (compute). Every number in the manuscript was
instead verified programmatically against `HELD_OUT_RESULT.json` and
`STAMPED_PREDICTIONS.md` in this session: all five per-package rows, the four totals
(2,488 commits / 2,265 changes / 1,671,821 decisions / 512,030 false retentions) and the
calibration figures matched with zero mismatches. `CONTENT_MANIFEST_V2.json` binds a
`subject_commit`/`subject_tree` pair and is deliberately left unmodified; it must be
rebound at freeze time. The root `SHA256SUMS` was extended 73 -> 89 entries with no path
dropped.

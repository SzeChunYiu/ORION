# ORION-07 — submission readiness record

**Terminal: `READY_PENDING_TEMPLATE`** (Wave-1 filing bar, defined in
`WAVE1_UPGRADE_LANE_VENUE_DECISIONS_V1.md` — PR #1692, pending). A complete
standalone manuscript exists and compiles with zero undefined references; it is
not in the venue class and carries no author block. What remains is mechanical,
not authorial.

Supersession note: the earlier label on this record,
`READY_TO_SUBMIT_SECOND_TIER`, named the venue tier reached but hid the
venue-format conversion that this record itself lists below as a remaining
input. That label is superseded by this one.

**Venue tier:** second tier.
Target venue TMLR. The prospectively frozen evidence gate that previously
blocked standalone submission is now closed on its own terms.

## The blocker that was open, and why it is now closed

The paper's earlier readiness record listed standalone evidence sufficiency as
**BLOCKED**: only the V0 instance existed against a prospectively frozen
requirement for additional frontier-question instances.

That requirement has been met by running the work, not by relaxing it:

- `Q3_REPLACEMENT_PROSPECTIVE_PROTOCOL_V2.md` states the content-readiness
  condition: both replacements validly frozen, both independent outcomes
  existing, both scored and mapped, both results replaying, the harness defects
  explicitly disposed, and the original contaminated slots still visible.
- `check_q3_completion.py` returns `Q3_COMPLETION_CHECK=PASS` with
  `VALID_PROSPECTIVE_SERIES=V0,Q3-R1,Q3-R2` and
  `REPLACEMENT_INSTANCES_SCORED=2`, `REPLACEMENT_RESULTS_REPLAYED=2`.
- `CLAIM_LEDGER_PROSPECTIVE_CASE_SERIES_2026-08-23.md` ratifies `n_valid = 3`
  and records the terminal
  `Q3_PROSPECTIVE_CASE_SERIES_COMPLETE__N3_VALID__AGREEMENT_NOT_VALIDATION_COUNTEREXAMPLE_OBSERVED__NO_RELIABILITY_GENERALIZATION`.

No threshold was moved after seeing an outcome. The two withdrawn contaminated
candidate slots remain named in the manuscript and in the series audit.

## What changed in the manuscript

The manuscript was stale against its own ratified ledger and understated its
evidence. Corrected in this pass:

1. **Results.** Replaced the claim that "no V1/V2/V3 benchmark series is present
   on current main" and that the result set is "exactly one scored question"
   with an accurate account of all three units, including the adverse third.
2. **Abstract.** Removed the statement that the evidence gate "remains open";
   added the joint-misdiagnosis finding.
3. **Title.** "First Measurement" became "a First Three-Question Series", which
   is what the paper now reports.
4. **Limitations.** Corrected the sample size from one question to three, and
   framed the joint-misdiagnosis instance as a warning about the construct
   rather than as a rate.
5. **House style.** Removed all internal paper identifiers and sibling-paper
   cross-references from narrative prose, and two machine tokens from Results.

The net effect on the claim ceiling is downward: the paper now carries an
explicit counterexample to the reading that agreement implies correctness.

## Gate table

| Gate | State | Evidence |
|---|---|---|
| Canonical manuscript designated | Closed | `CANONICAL_SOURCE_DECISION.md` |
| Prospective evidence series | Closed | `check_q3_completion.py` PASS, n=3 |
| Result bindings | Closed | `check_q3_result_bindings.py` PASS |
| Compiles to submittable PDF | Closed | 6 pages, no undefined references, no overfull boxes |
| Headline claims match artifacts | Closed | Both instance scores read directly from `FINAL_SCORE.json` |
| Claim ceiling respected | Closed | Ledger's forbidden interpretations all honoured; aggregate reliability still withheld |
| House style | Closed | No machine tokens, internal identifiers, or sibling cross-references in prose |
| Content binding | Unchanged | `BOUND_PARTIAL / PASS` |
| Venue selected | Closed | `VENUE_DECISION.md` |
| Submission manifest | Closed | `SUBMISSION_MANIFEST.md` / `.sha256` |
| Cover letter | Closed | `COVER_LETTER.md` |
| Data/code availability | Closed | `DATA_AND_CODE_AVAILABILITY.md` |

## Venue-format conversion — named explicitly

The manuscript is `\documentclass[11pt]{article}` with `\author{Working framework
draft}`. It is a complete, sectioned, bibliography-resolved manuscript that
compiles cleanly, but it is **not** in TMLR's submission format: no venue
class or style file, no author block, and no anonymisation decision recorded.

Converting it requires tmlr.sty, which is not obtainable from the toolchain used in
this pass, so this is left as an input rather than attempted and half-done.
Treat it as mechanical filing work, not evidence work: the science, the claim
ceiling, and the checks are complete and independent of the template.

## Remaining inputs — human only

1. **Author list** in final order. The title page currently reads "Working
   framework draft".
2. **Affiliations**, **ORCID** identifiers.
3. **Corresponding author** designation and email.
4. **Funding statement** and grant numbers.
5. **Competing-interests declaration.**
6. **TMLR-specific:** whether to opt into public discussion under the author's
   name, and any conflicting-reviewer exclusions.
7. **Public archival deposit** of the instance directories, with the DOI
   substituted into the availability statement.
8. **Licence election** for the deposited artifacts.

Also required before filing: **convert to TMLR's submission template** (tmlr.sty) and record the anonymisation decision.

---

## Addendum 2026-09-03 — identity correction and template-gap closure (tier-B filing-surface pass)

Two items above are resolved or corrected, with receipts:

1. **"What changed" item 3 (title) never landed in the canonical tree.**
   `git log -S'a First Three-Question Series' -- manuscript/main.tex` is empty
   while the control pattern `-S'Receipted Benchmark and First Measurement'`
   resolves; #1957 landed the Wave-1 branch artifacts "keeping main's newer
   prose", so the canonical title has carried the single-benchmark identity
   since 3a1a83178 (2026-08-27). The three-question title exists only in the
   `submission_tmlr/` wrapper (2026-08-29 generation, built from the Q3-cited
   Markdown), which is now marked superseded — see `submission_tmlr/README.md`
   and the banner on `editorial/CANONICAL_SUBMISSION_DESIGNATION.md`. The
   canonical manuscript still reports the three-unit series and the
   joint-misdiagnosis counterexample inside (sections 03/04/06), per
   `submission/CANONICAL_SOURCE_DECISION.md`.
2. **The venue-format conversion is closed.**
   `submission/publication-ready-20260831/journal/source.zip` (bf2a35750,
   2026-09-01) carries the official TMLR assets — `tmlr.sty` (6560 B),
   `tmlr.bst` (26969 B), `fancyhdr.sty` — in double-blind anonymous form built
   on the canonical identity (anonymisation decision: double-blind, as packaged);
   both route zips carry the canonical title. The "tmlr.sty not obtainable from
   the toolchain used in this pass" blocker no longer exists.
3. **Remaining human inputs reduce to portal-side elections**: the TMLR
   public-discussion opt-in and reviewer exclusions, the public archival deposit
   DOI, and the licence election. Name, affiliation, email, funding, and
   competing interests are already recorded (`papers/AUTHOR_IDENTITY_V1.json`;
   no funding, no competing interests). With the template gap closed, this
   record's operative terminal advances from `READY_PENDING_TEMPLATE` to
   `PORTAL_ACTIONS_ONLY`.

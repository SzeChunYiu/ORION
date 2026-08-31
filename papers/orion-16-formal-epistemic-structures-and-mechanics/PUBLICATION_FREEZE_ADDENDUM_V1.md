# ORION-16 publication-freeze addendum V1

**Freeze date:** 2026-08-31  
**Status:** `CURRENT_EARNED_CEILING_FROZEN__REAL_SYSTEM_CAMPAIGN_ACTIVE_ELSEWHERE`

This addendum is part of the frozen ORION-16 paper-content packet. It records the
ceiling the gap ledger and the theory dispositions already establish, and grants no
authority beyond them. It is bound additively through `CONTENT_MANIFEST_V2.json`,
whose subject identity is re-pinned to the commit that introduces this file; the V1
manifest is untouched and its frozen subject is unchanged.

## Earned scientific ceiling

The publication disposition is `BOUNDED_PAPER_READY_TO_FILE` with
`scientific_authority_delta: NONE`. The ledger states the ceiling in one sentence,
reproduced without extension:

> The bounded certificate-lifting semantics and exact graph-quality law are
> supported; broad real-system revalidation authority is not.

Two theory lanes carry it, each closed on its own terms and each recording an
authority delta of `NONE`:

- `theory/dependency-closed-revalidation-v1` — terminal
  `THEORY_PROVED__EXHAUSTIVELY_CHECKED`;
- `theory/graph-quality-revalidation-v1` — terminal
  `THEOREM_PROVED__TAXONOMY_MATCHES_FROZEN_REAL_GOLD`, retaining the #1649 statement
  verbatim that a prior same-programme real audit did not satisfy the external
  empirical discriminator.

The submission surface is `submission/AIJ_MANUSCRIPT.tex`, targeting Artificial
Intelligence, and its front matter is clean: correct title, sole author with the
Stockholm University affiliation, no internal labels.

## Frozen boundary

The graph-quality result is **a terminal-correctness audit over 16 cases on one
system, not a cost claim.** That distinction is load-bearing and is stated in the
disposition rather than left to the reader.

The system's behaviour on missing edges is part of the result rather than a
limitation of it: for `RC-ALIAS-MISSING` it returns `CANNOT_CHECK` instead of a
confident wrong answer. Preserving that is the packet's central confirmation — no
gold terminal is rewritten in this lane, and **no `CANNOT_CHECK` is converted**.

Three things remain explicitly not established: universal minimality of the five
lift coordinates, deployed-agent performance, and donor novelty.
`external_independent_validation` remains `CANNOT_CHECK`, and same-programme work
does not discharge it — this paper cannot validate itself by running more of its own
programme.

**The real-system campaign is active elsewhere and must not be duplicated here.**
The ledger records `protocol_state: ACTIVE_LANE_DO_NOT_DUPLICATE` against PR #1695
and issue #1649 Tier A, with the collision rule that no competing real-system
protocol may be created and #1695's freeze may not be altered. The strongest
remaining gap belongs to that campaign: connecting the exact graph-quality theorem
to authoritative, donor-complete real dependency and change graphs, and measuring
unsafe omissions, conservative excess and revalidation cost. Nothing here
anticipates its outcome.

## Known defect, recorded rather than repaired

`submission/COVER_LETTER.md` names the paper *"Formal Epistemic Structures and
Mechanics: Scientific Admissibility over Repair, Effects, and Authority"*, while
`submission/AIJ_MANUSCRIPT.tex` sets the title to *"Scientific Admissibility Is Not
Computational Correctness: A Contract Theory for Repair, Effects, and Authority"*.
The two disagree. ORION-17 and ORION-18 were checked the same way and match, so this
is a real isolated defect rather than a noisy check.

It is not repaired here because both files are bound by the frozen V1 manifest, and
editing a V1-bound file is refused by design. Correcting it before filing needs a
cover letter regenerated outside the frozen set — a filer's decision, recorded here
so an editor does not find it first.

## Frozen content surface

The content packet is the set bound by `CONTENT_MANIFEST_V1.json` and
`CONTENT_MANIFEST_V2.json`, which together cover every file of this paper, including
`submission/AIJ_MANUSCRIPT.tex`, its two section files, the cover letter and
highlights, both theory lanes with their independent checkers and claim
dispositions, and this addendum. The ORION-16 claim is about scientific
admissibility as a contract over repair, effects and authority; it does not own the
donor mechanisms it absorbs.

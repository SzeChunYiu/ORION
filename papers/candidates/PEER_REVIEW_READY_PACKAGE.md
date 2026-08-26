# ORION-16–ORION-18 peer-review submission package

**Date:** 2026-08-18  
**Scientific base:** theory package merged by #375.  
**Submission gate:** #376.  
**Content terminal:** `SUBMISSION_CONTENT_COMPLETE`.

## Computed peer-review terminal

This file does not hard-code a claim that could become stale after a content edit. For the exact Git commit being evaluated, define

```text
PEER_REVIEW_READY :=
    p6-p8-candidate-ci == success
AND ci == success
AND submission/p6-p8-peer-review-ready-2026-08-18 is the tested PR head
```

The fast candidate workflow must explicitly contain successful steps named:

- `Theory and live-embedding gate`;
- `Peer-review submission gate`;
- `Build and audit submission PDFs`;
- `Archive audited submission PDFs`.

The second step runs `tests/unit/candidates/test_p6_p8_peer_review_ready.py`,
which executes the deterministic submission-source linter. The PDF step builds
all three manuscripts with `latexmk`, rejects overfull boxes and undefined or
multiply-defined references/citations, and archives the exact-head PDFs plus a
hash receipt. The repository-wide `ci` workflow independently runs the full
project `pytest -q` suite.

When those predicates hold on one immutable head, the repository terminal for ORION-16, ORION-17 and ORION-18 is `PEER_REVIEW_READY`. A later content change invalidates the terminal until the new head passes both checks again.

`PEER_REVIEW_READY` means ready for external editorial/referee evaluation. It does not mean `PEER_REVIEWED`, `ACCEPTED`, `FLAGSHIP_PROMOTED`, or `EMPIRICALLY_SUPERIOR`.

## Programme submission artifacts

- `PEER_REVIEW_READY_GATE_2026-08-18.md` — terminal definition and narrowed claims.
- `PRE_SUBMISSION_LITERATURE_DELTA_2026-08-18.md` — two-round current-literature closure.
- `VENUE_REQUIREMENTS_VERIFIED_2026-08-18.md` — live AIJ/JAAMAS author requirements.
- `SUBMISSION_CLAIM_AUTHORITY_V1.md` — journal-headline claim authority and nonclaims.
- `submission/check_peer_review_ready.py` — deterministic structural/citation/venue submission gate.
- `submission/build_and_audit_p6_p8_pdfs.py` — clean PDF build, layout/reference warning gate and hash receipt.
- `tests/unit/candidates/test_p6_p8_peer_review_ready.py` — submission gate test.
- `.github/workflows/p6-p8-candidate-ci.yml` — fast theory + submission gate wiring.

## ORION-16 — Artificial Intelligence

- editable source: `orion-16-formal-epistemic-structures-and-mechanics/submission/AIJ_MANUSCRIPT.tex`
- highlights: `orion-16-formal-epistemic-structures-and-mechanics/submission/HIGHLIGHTS.txt`
- cover letter: `orion-16-formal-epistemic-structures-and-mechanics/submission/COVER_LETTER.md`
- normative theory: `orion-16-formal-epistemic-structures-and-mechanics/manuscript/FORMAL_CORE_V2_1.md`
- claim authority: `orion-16-formal-epistemic-structures-and-mechanics/CLAIM_LEDGER_V2_1.md` plus programme submission ledger;
- reproduce: `orion-16-formal-epistemic-structures-and-mechanics/REPRODUCE_V2_1.md`.

## ORION-17 — Artificial Intelligence

- editable source: `orion-17-epistemic-navigation-open-worlds/submission/AIJ_MANUSCRIPT.tex`
- highlights: `orion-17-epistemic-navigation-open-worlds/submission/HIGHLIGHTS.txt`
- cover letter: `orion-17-epistemic-navigation-open-worlds/submission/COVER_LETTER.md`
- normative theory: `orion-17-epistemic-navigation-open-worlds/manuscript/FORMAL_CORE_V2.md`
- frozen contract manifest: `orion-17-epistemic-navigation-open-worlds/benchmark/instances_v2.jsonl`
- claim authority: `orion-17-epistemic-navigation-open-worlds/CLAIM_LEDGER_V2.md` plus programme submission ledger;
- reproduce: `orion-17-epistemic-navigation-open-worlds/REPRODUCE_V2_1.md`.

## ORION-18 — Autonomous Agents and Multi-Agent Systems

- editable source: `orion-18-epistemic-authority-autonomous-science/submission/JAAMAS_MANUSCRIPT.tex`
- mandatory information sheet: `orion-18-epistemic-authority-autonomous-science/submission/JAAMAS_INFORMATION_SHEET.md`
- cover letter: `orion-18-epistemic-authority-autonomous-science/submission/COVER_LETTER.md`
- normative theory: `orion-18-epistemic-authority-autonomous-science/manuscript/FORMAL_CORE_V2.md`
  plus superseding primitive closure `manuscript/FORMAL_CORE_V2_1.md`
- frozen authority manifest: `orion-18-epistemic-authority-autonomous-science/benchmark/authority_cases_v2.jsonl`
- claim authority: `orion-18-epistemic-authority-autonomous-science/CLAIM_LEDGER_V2.md` plus programme submission ledger;
- reproduce: `orion-18-epistemic-authority-autonomous-science/REPRODUCE_V2_1.md`.

## Author/correspondence metadata used in the package

Public institutional metadata:

- Sze Chun Yiu;
- Department of Physics, Stockholm University, Stockholm, Sweden;
- corresponding e-mail `sze-chun.yiu@fysik.su.se`;
- postal correspondence `SE-106 91 Stockholm, Sweden`.

ORCID, private funding/grant information, and private competing-interest declarations are not inferred. See #377. Those are author attestations at portal submission, not missing scientific claims.

## Archival identity

The exact successful PR head plus its GitHub check runs is the submission archive identity. #379 records the immutable head/check evidence after the computed terminal becomes true, without changing the tested manuscript bytes.

## External boundary

Independent confidential human peer review and editorial acceptance are not repository outputs. See #378. A reviewer-found counterexample legitimately reopens the relevant paper.

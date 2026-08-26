# ORION-P3 Journal Gate Check

**Status:** PREPARATORY (gold study not yet executed)

This document enumerates every gate that must pass before the manuscript is submitted to a peer-reviewed venue. Inspired by the JOURNAL_READINESS.md Step 10 requirements.

## Gate 1: Literature closure

- [ ] Literature closure within 14 days of submission: all mechanism families absorbed (DONE — 13 families in 20-related-work.tex)
- [ ] No material new publication in the absorbed families that changes the novelty boundary (PENDING — re-check before submission)
- [ ] No missed mechanism family that would absorb the claimed residual (PENDING — re-check before submission)

## Gate 2: Gold dataset quality

- [ ] All 32 samples annotated and adjudicated (PENDING)
- [ ] Inter-annotator agreement ≥ threshold on every coordinate (PENDING)
- [ ] Domain-expert review for specialist cases (PENDING)
- [ ] No outcome contamination: adjudication policy frozen before system outputs inspected (DONE — ADJUDICATION_POLICY_V1.md)
- [ ] Data licensing and copyright review complete (PENDING)

## Gate 3: Results

- [ ] H1 (superiority + non-inferiority) testable from frozen artifacts (PENDING)
- [ ] H2 (recoverability), H3 (obstruction value), H4 (ablation necessity) testable (PENDING)
- [ ] All 17 metrics computed across 5 seeds (PENDING)
- [ ] All 7 figures and 3 tables generated (PENDING)
- [ ] Stage-attributed error analysis (extraction vs mapping vs integration) (PENDING)

## Gate 4: Reproducibility

- [ ] Full reproducibility checklist satisfied (see gold/REPRODUCIBILITY.md) (PENDING)
- [ ] One-command evaluation path verified (PENDING)
- [ ] Independent replay of headline mapping/obstruction results (PENDING)
- [ ] Permanent archive/DOI for gold dataset (PENDING)

## Gate 5: Manuscript

- [ ] Formal definitions precise enough for reimplementation (DONE — 30-method.tex)
- [ ] Dataset/annotation Methods written before final labeling (DONE — 40-dataset.tex)
- [ ] Results only from immutable artifacts (PENDING)
- [ ] Limitations section complete (DONE — 07-limitations.tex)
- [ ] Data/code availability and ethics/licensing statements (PENDING)
- [ ] Claim ledger: every headline claim maps to an artifact (PENDING)

## Gate 6: Journal selection

- [ ] Target journal selected after results stabilize (PENDING)
- [ ] Dataset/software contribution framed appropriately for venue (PENDING)
- [ ] Journal formatting, supplement, and cover letter (PENDING)

## Gate 7: Final audit

- [ ] Independent final PDF read (PENDING)
- [ ] Reference checklist: every citation complete and accurate (PENDING)
- [ ] Claim audit: every claim supported by evidence, no overclaiming (PENDING)

## Summary

| Gate | Status |
|------|--------|
| G1: Literature closure | PARTIAL (structurally complete, needs re-check before submission) |
| G2: Gold dataset quality | PENDING (gold study not executed) |
| G3: Results | PENDING (gold study not executed) |
| G4: Reproducibility | PARTIAL (infrastructure ready, artifacts pending) |
| G5: Manuscript | PARTIAL (structure complete, results pending) |
| G6: Journal selection | PENDING |
| G7: Final audit | PENDING |

**Overall:** PEER_REVIEW_READY cannot be declared until the gold study is executed and all gates pass.
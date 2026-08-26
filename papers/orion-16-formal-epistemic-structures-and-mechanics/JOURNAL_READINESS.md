# ORION-16 candidate journal-readiness plan — Formal Epistemic Structures and Mechanics

**Current terminal:** computed per commit, not asserted here. See
`../PEER_REVIEW_READY_PACKAGE.md`, which defines

```text
PEER_REVIEW_READY := p6-p8-candidate-ci == success AND ci == success
                     on one immutable head
```

This line previously read `CANNOT_CHECK / not a promoted paper / not peer-review
ready`. That was written before the submission package existed and had gone
stale: it contradicted `JOURNAL_READINESS_V2_1.md`, which already deferred to the
computed terminal, so the two files in this directory disagreed about ORION-16.

It is deliberately **not** replaced with `PEER_REVIEW_READY`. The package file
states that it does not hard-code a claim that could become stale after a content
edit, and writing a terminal into this file would reintroduce the staleness being
removed. What follows is the last observation, not a standing claim.

**Last observed on `2f701036`** (merge of #402 into `main`):

| predicate | result |
|---|---|
| `p6-p8-candidate-ci` | success |
| `ci` | success |

The candidate workflow's four required steps all passed on that head: *Theory and
live-embedding gate*, *Peer-review submission gate*, *Build and audit submission
PDFs*, *Archive audited submission PDFs*. The PDF step compiled
`submission/AIJ_MANUSCRIPT.tex` with `latexmk` and rejected no overfull box, undefined
reference or undefined citation.

Any commit after `2f701036` — including the one carrying this sentence — has to be
re-evaluated against the same two predicates. That is the point of computing the
terminal rather than storing it.

**Not claimed:** `PEER_REVIEW_READY` means ready for external editorial and
referee evaluation. It does not mean `PEER_REVIEWED`, `ACCEPTED`,
`FLAGSHIP_PROMOTED`, or empirically superior to any baseline.

## 0. Earned local package state — 2026-08-17 wide pass

Present now:

- widened `manuscript/FORMAL_CORE_V1.md` with repaired history-aware commutation boundary;
- widened `manuscript/DRAFT.md`;
- `CLAIM_LEDGER_V1.md` synchronized to the current formal core;
- `P1_P5_OWNERSHIP_MATRIX_V1.md` marking native ORION-11 mechanic/reopening/audit ownership;
- donor/parent pressure maps including DEL/AGM/TMS/separation/effects/authorization/repair/agent architecture;
- exhaustive bounded `formal/check_finite_models.py` plus small theorem-boundary checker;
- `CHECK_RESULTS_V1.md` retained and additive `CHECK_RESULTS_V2.md` recorded;
- `REPRODUCE.md` with deterministic commands/environment/evidence boundaries;
- `PROSPECTIVE_EVALUATION_V1.md` with strong donor baseline slots and negative controls;
- five-role adversarial findings in `EXPERT_REVIEW_LOG_V1.md`.

None of these artifacts closes external novelty, exact donor embedding, clean CI, protected evaluation or independent scholarly review.

## 1. Distinct-object gate
- [ ] #343 proves a non-duplicative residual relative to ORION-11.
- [ ] exact mapping from proposed formal objects to current ORION registry is complete.
- [x] every ORION-11-owned mechanic is marked prior internal ownership, not ORION-16 novelty.

## 2. Nearest-work closure
- [ ] dynamic epistemic logic/action-model families dispositioned with atomic mechanism receipts.
- [ ] AGM/iterated revision/epistemic entrenchment/ranking families dispositioned.
- [ ] truth-maintenance/dependency-directed revision/rollback families dispositioned.
- [ ] incomplete/inconsistent/hyperintensional revision families dispositioned.
- [ ] process/separation/temporal/effect/authorization logic pressure completed.
- [ ] cognitive-architecture/language-agent formalism pressure completed.
- [ ] provenance/audit/incremental-repair parent fields dispositioned.
- [ ] hostile exact-composition search completed.
- [ ] two consecutive no-material-change rounds.
- [ ] #287 novelty certificate current after final absorption.

## 3. Formal contribution
- [ ] canonical definitions frozen.
- [ ] well-formedness rules frozen.
- [x] at least one nontrivial proposition/theorem/property has proof plus bounded mechanical support.
- [x] whole-state commutation overclaim repaired to scientific-projection equality + independent trace equivalence.
- [x] self-authorization/recursive-cycle/stale-reopening countermodels or finite fixtures exist.
- [ ] residual-obligation preservation theorem completed beyond fixture-level support.
- [ ] recursion/fixed-point claims frozen and bounded honestly.
- [ ] at least one high-value theorem independently checked/mechanized where justified.

## 4. Executable correspondence
- [ ] selected ORION mechanics encoded with exact current protocol/registry identities.
- [ ] ORION-11 native decisions reproduced exactly by conservative embedding fixtures.
- [ ] donor-native update/rollback/effect/authorization decisions reproduced by conservative embeddings where feasible.
- [ ] mapping coverage/gaps reported.
- [x] deterministic checker/model enumerator archived in the candidate tree.
- [x] deterministic reproduction command documented.
- [ ] clean-environment/CI replay archived.

## 5. Evaluation
- [x] prospective discriminating protocol draft exists with exact-ground-truth families, strongest-donor baseline slots and negative controls.
- [ ] protocol/generator frozen before result visibility.
- [ ] primary outcome and practical margin frozen.
- [ ] selective reopening compared with strongest dependency-repair donor representation where scientifically relevant.
- [ ] direct test of added authority/residual-obligation/history structure beyond donor-native baselines.
- [ ] at least one non-ORION-11 cross-domain transfer family executed.
- [ ] negative/null cases preserved in immutable raw results.
- [ ] every empirical positive has #283 verification.

## 6. Manuscript
- [x] working markdown draft exists.
- [x] formal core exists and is linked to current claim boundaries.
- [ ] formal notation stabilized after #334/#352 saturation.
- [ ] related work written from full-text verified/atomically dispositioned sources.
- [ ] theorem/evaluation results inserted only from immutable artifacts.
- [ ] claim ledger #346 terminal complete (ledger exists, but several claims remain `CANNOT_CHECK`).
- [x] limitations explicitly separate local formal properties from scientific correctness/novelty.
- [ ] LaTeX journal manuscript created after residual stabilizes.

## 7. Reproducibility
- [x] current proof/checker source and Python-standard-library dependency boundary documented.
- [x] deterministic regeneration command documented in `REPRODUCE.md`.
- [x] V1 and additive V2 result ledgers preserve theorem-boundary history.
- [ ] immutable stdout/hash manifest produced in clean CI.
- [ ] machine-readable donor/ORION-11 embedding fixtures archived.
- [ ] independent replay/attestation.
- [ ] permanent archive after promotion authority stabilizes.

## 8. Submission
- [ ] venue selected under #345.
- [ ] literature refreshed under #344 within 14 days of submission.
- [ ] independent PDF proofread.
- [ ] archive/DOI path frozen.

## Done definition

Promote ORION-16 only if it yields a formal object/property that is distinct from ORION-11 and prior formal systems, with conservative donor embeddings and either a nontrivial surviving theorem or prospective cross-domain evidence showing why the coupled structure matters. Otherwise merge useful material into ORION-11/ORION-15/programme theory or retain it as a technical companion.
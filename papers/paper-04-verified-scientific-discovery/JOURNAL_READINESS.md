# ORION-P4 Journal Readiness — final protected V2

**Terminal:** `ORION-P4 = PEER_REVIEW_READY`  
**Canonical campaign:** `P4.protected-authority.v2` over base protocol `P4.protected-authority.v1`  
**Publication-authorizing subject:** `f6e51b5c8f905382b8e2f5568d9035fc14241aa1`  
**Protected campaign:** GitHub Actions run `31976589735`

## Scientific gate

| Gate | Final result |
|---|---|
| H1 — false scientific-authority promotion | **PASS**: ORION `0/360`; strongest frozen comparator mechanism (ProvenAI-style) `180/360`; effect `-0.50`, paired 95% CI `[-0.553,-0.447]` |
| H2 — clean authority coverage | **PASS**: both `60/60`; clean-FN count `0` for both; coverage effect `0`, CI `[0,0]` |
| H3 — superior correct `CANNOT_CHECK` | **NOT_SUPPORTED**: both `30/30`; effect `0`, CI `[0,0]` |
| Typed authority panel | **PASS**, no blockers |
| Independent reproduction | **PASS**, exact headline counts reproduced |
| Actual scored-process custody telemetry | **PASS**: zero protected-identifier hits and zero external-IP connections for candidate/comparator jobs |
| Eight registered ablations | **PASS as diagnostic evidence**: every ablation increases false promotion while preserving `60/60` clean coverage |

The H3 null is retained as a null result; it is not converted into a positive claim.

## Prospective freeze and custody gate

- [x] repaired subject frozen before hidden-set generation;
- [x] full 420-case public-seed preflight passed before secret split existed;
- [x] harness merged to signed/green `main` before hidden-set generation;
- [x] independent host generated a fresh secret-seeded post-repair split;
- [x] candidate handoff mechanically contained only `case_id` + `candidate_visible`;
- [x] attack labels, gold, custody class, and expected terminal were absent from scored packets;
- [x] signed execution-freeze merge `99bcacc82224089c34019ad82287754388dadbc5` and exact-main CI `31976305223` were verified before launch;
- [x] candidate/comparator jobs completed before the protected evaluator downloaded gold;
- [x] protected and releasable artifacts remain separated.

Frozen identities are recorded in `protocol/PROTECTED_RUN_BINDINGS_V2.json` and `reproducibility/BINDING_MANIFEST_V2.md`.

## Comparator and novelty boundary

- [x] ProvenanceGuard/source-aware factuality and conflation absorbed as prior work;
- [x] AttributionBench/multi-source attribution absorbed;
- [x] claim-level auditability/AAR absorbed;
- [x] ProvenAI citation fidelity/influence separation absorbed;
- [x] FIRE iterative retrieve/verify absorbed;
- [x] CLAIM-BENCH scientific evidence reasoning absorbed;
- [x] RewardHackingAgents evaluator/holdout attack surface absorbed;
- [x] Search-Time Contamination absorbed;
- [x] DeepSciVerify evidence escalation included in the repaired-subject frozen panel;
- [x] residual claim remains the **non-compensatory, non-escalating scientific-authority transition under protected custody**.

Comparator arms are protocol-matched mechanism reimplementations, **not executions of the external authors' original systems**. The empirical claim is restricted to those frozen mechanisms and this battery.

The dated nearest-work audit is `2026-08-16`. Re-run it only if actual submission occurs after `2026-08-30`.

## Exploratory evidence excluded from authorization

The earlier 39-case live-model arm is retained as diagnostic history only. A recursive post-run audit found adjudication/expected-terminal inconsistency, incorrect opportunity denominators, and direct use of candidate-hidden family labels in the live ORION/ablation path. None of its result values are used in the V2 headline, manuscript figures/tables, or claim ledger.

The earlier V1 420-case protected campaign remains valid for its older frozen subject but does not authorize the repaired V2 subject.

## Manuscript and reproducibility gate

- [x] anonymous TMLR-formatted manuscript with immutable protected-V2 Results/Discussion;
- [x] H1/H2 positive and H3 null reported exactly;
- [x] false-negative cost and clean coverage reported;
- [x] five result figures and three tables regenerate only from immutable public V2 aggregates;
- [x] tracked LaTeX tables are byte-checked against deterministic regeneration;
- [x] claim ledger and data/code availability statement are result-bound;
- [x] safe post-run public slice and public verdicts retained in the safe campaign bundle;
- [x] hidden labels/raw traces remain protected;
- [x] clean-room TMLR compile with pinned, unmodified official `tmlr.sty` + `tmlr.bst`;
- [x] undefined-reference and stale-pre-result scans pass;
- [x] exact publication source merge `846a0573fb881c5f9b6caa8e98aede2e51090fca` is GitHub-verified;
- [x] exact-main ordinary CI `31978918884` passed;
- [x] exact-main TMLR audit `31978918885` passed;
- [x] audited 11-page PDF SHA-256 `562af78b7e634159317a002f8ac651ddc0180ea012712a5def555548b267d3db`.

## Permanent archive gate

- [x] permanent GitHub Release tag: `orion-p4-v2-peer-review-ready`;
- [x] release target is the exact publication source commit `846a0573fb881c5f9b6caa8e98aede2e51090fca`;
- [x] release contains audited PDF, safe result bundle, source supplement, and SHA-256 manifest;
- [x] archive workflow run `31979303097` passed after independently re-verifying publication signature/CI/audit and artifact identities;
- [x] archive merge `00c19ecd71071e1ad70a8820df4c198153e4da84` is GitHub-verified;
- [x] archive-merge ordinary CI `31979303114` passed;
- [x] archive-merge clean-room TMLR audit `31979303109` passed.

Protected gold and raw traces are deliberately absent from the public release.

## Submission-time operational step

- [ ] Insert the OpenReview submission ID after an actual TMLR submission is created.

This is an external submission action, not a scientific or reproducibility readiness blocker. If submission is delayed beyond `2026-08-30`, refresh the nearest-work audit first.

## Done definition

All scientific, custody, reproducibility, manuscript, PDF, and permanent-archive gates required for peer review are satisfied. Security-by-total-refusal is ruled out by `60/60` clean promotions. The strongest supported statement is bounded to the protected mechanical-gold benchmark and frozen comparator mechanisms.

**`ORION-P4 = PEER_REVIEW_READY`.**

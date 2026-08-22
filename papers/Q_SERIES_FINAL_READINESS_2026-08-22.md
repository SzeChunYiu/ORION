# ORION-Q paper wave — final internally achievable readiness

**Date:** 2026-08-22  
**Canonical machine spec:** `papers/Q_SERIES_FINAL_SPEC_V1.json`  
**Sync epoch:** `2026-08-22-q-series-final-v1`

This record states what is complete **inside the repository now**. It does not turn skipped external review, journal peer review, future prospective studies, or external novelty adjudication into PASS states.

## Q1 — Sharp Support-Two Normal Forms for Shared-Tag TARE Quantum Compilation

**Canonical manuscript:** `papers/Q-paper-01-tare-expressivity/MANUSCRIPT_SUBMISSION_DRAFT.md`

Internal science package complete:

- sharp theorem `kappa_R6M = 2` under the declared grammar/objective;
- analytic all-`n` proof;
- exact support-one counterexample proving sharpness;
- standalone no-ORION-import sanity checker/result;
- finite-domain regime classifier and prospective benzene confirmation retained as supporting evidence only;
- QG follow-up limitations disclosed;
- split-TARE coefficient lemma given a classical analytic majorization proof;
- bounded hostile novelty research plus final exact-statement refresh;
- claim ledger and figures plan synchronized;
- reproduction and submission-facing editor/significance package included.

**Owner decision:** external quantum-expert pre-review is skipped. This removes that optional internal checklist item; it does not certify the theorem externally.

**Current status:** `COMPLETE_FOR_SCOPED_THEOREM_PAPER__SUBMISSION_FORMATTING_REMAINS`.

The remaining work before an actual journal upload is editorial/venue packaging (journal template, rendered figures, bibliography formatting, author metadata and a same-day literature refresh if submission is materially later). No new Q-era scientific experiment is required by the current claim.

## Q2 — Recursive Recovery of Negative Scientific Results

**Canonical manuscript:** `papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V2.md`

Complete for the scoped claim that ORION-Q is a receipted **single-programme case study** of negative-result recovery. `RECEIPT_INDEX_V2.md` reaches the final R6S/N-lane closure instead of the early manuscript snapshot. A reproduction guide and scoped submission package are included.

The cross-domain protocol remains valuable successor research if a broader productivity/generalization claim is desired, but it is not required to publish the current bounded case-study paper.

**Current status:** `COMPLETE_FOR_SCOPED_CASE_STUDY`.

## Q3 — Dual-Instrument Research Control

**Canonical manuscript:** `papers/Q-paper-03-dual-instrument/MANUSCRIPT_V2.md`

Complete for a systems/benchmark-definition paper with **one** frozen live measurement. Current main repairs the historical malformed-success D2/D3 defects and now exposes a machine-readable Q3 publication contract under `orion_research_harness.publication_contract`. The contract validates deterministic/digest-bound requests and results, create-only persistence, audited failed/invalid-content recovery, campaign authority non-escalation and the declared protected-reference custody surface. A reproduction guide and scoped submission package are included.

The >=20-item deferred-calibration study remains successor research and is required only for a later predictive/calibration claim.

**Current status:** `COMPLETE_FOR_SCOPED_SYSTEMS_PAPER`.

## Q4 — Typed Scientific Epistemic State

**Canonical manuscript:** `papers/Q-paper-04-typed-state/MANUSCRIPT_V2.md`

Complete for the exact-synthetic matched-information mechanism/benchmark claim. The manuscript explicitly gives zero broad novelty credit for typed memory, stale-memory handling or VoI primitives already present in neighboring literature. A reproduction guide and scoped submission package are included.

The >=100 real-decision protocol remains successor research and is required only for a future real-agent transfer claim.

**Current status:** `COMPLETE_FOR_SCOPED_MECHANISM_PAPER`.

## Framework ↔ paper ↔ harness synchronization

The final Q paper set is no longer prose-only synchronized.

- `src/orion/registry.py` fixes the Q-series spec id, sync epoch, paper ids, canonical manuscripts and Q3 harness-contract id.
- `papers/FRAMEWORK_SNAPSHOT.json` mirrors those identities and remains checked by `tests/unit/publication/test_framework_snapshot.py`.
- `src/orion/programme/q_series_sync.py` checks paper/evidence boundaries against committed receipts and exact Q1 theorem/sharpness records.
- `papers/Q_SERIES_CONTENT_BINDING_V1.json` + `q_series_content_binding.py` bind the canonical publication bytes so silent edits fail.
- `src/orion/programme/content_binding_coverage.py` now recognizes Q1-Q4 as watched canonical subsets in the repository-wide binding survey; historical snapshots remain visibly outside that canonical subset and QG remains unbound until its own publication wave is frozen.
- `packages/orion-research-harness/src/orion_research_harness/publication_contract.py` validates every implementation surface explicitly listed by the Q3 paper contract.
- dedicated publication/framework/harness regression tests enforce all of the above.
- `.github/workflows/q-series-publication-sync.yml` runs those Q-specific tests plus the standalone Q1 finite-core sanity checker on relevant pushes/PRs.

These checks are synchronization/integrity instruments. They deliberately grant no scientific, novelty or physical-quantum authority.

## Verification visibility boundary

The repository now contains the executable CI gates required for the final Q-series specification. In this session, GitHub's connector exposes no classic status entries for the direct `main` push commits, and the local execution sandbox cannot clone GitHub due network/DNS restrictions. Therefore this record does **not** claim that the latest Actions run is green without seeing that check result. The publication workflow itself is part of the committed release contract and is triggered by the relevant Q paper/framework/harness paths.

Static review during this synchronization pass found and repaired multiple would-be release failures before finalization, including:

- a skipped-review description that accidentally contained the token used by the non-authority guard for scientific approval;
- an over-broad Q3 harness contract property that belonged to the benchmark protocol rather than harness implementation;
- an assumption that all campaign record types shared the same deserialization API;
- the older global binding survey incorrectly reporting Q1-Q4 as `UNBOUND` despite the new canonical cross-paper binding.

## Release rule

If a canonical Q manuscript, claim ledger, flagship proof, novelty record, final spec, or Q3 harness contract changes:

1. review whether the scientific claim changes;
2. update the corresponding manuscript/ledger/spec together;
3. regenerate the Q-series content binding if canonical bytes changed;
4. advance the sync epoch if the scientific/publication contract changed materially;
5. run the publication + harness regression suites;
6. never let a green software test promote a claim beyond its ledger.

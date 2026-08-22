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
- claim ledger and figures plan synchronized.

**Owner decision:** external quantum-expert pre-review is skipped. This removes that optional internal checklist item; it does not certify the theorem externally.

**Current status:** `COMPLETE_FOR_SCOPED_THEOREM_PAPER__SUBMISSION_FORMATTING_REMAINS`.

The remaining work before an actual journal upload is editorial/venue packaging (journal template, rendered figures, bibliography formatting, author metadata and a same-day literature refresh if submission is materially later). No new Q-era scientific experiment is required by the current claim.

## Q2 — Recursive Recovery of Negative Scientific Results

**Canonical manuscript:** `papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V2.md`

Complete for the scoped claim that ORION-Q is a receipted **single-programme case study** of negative-result recovery. `RECEIPT_INDEX_V2.md` reaches the final R6S/N-lane closure instead of the early manuscript snapshot.

The cross-domain protocol remains valuable successor research if a broader productivity/generalization claim is desired, but it is not required to publish the current bounded case-study paper.

**Current status:** `COMPLETE_FOR_SCOPED_CASE_STUDY`.

## Q3 — Dual-Instrument Research Control

**Canonical manuscript:** `papers/Q-paper-03-dual-instrument/MANUSCRIPT_V2.md`

Complete for a systems/benchmark-definition paper with **one** frozen live measurement. Current main repairs the historical malformed-success D2/D3 defects and now exposes a machine-readable Q3 publication contract under `orion_research_harness.publication_contract`.

The >=20-item deferred-calibration study remains successor research and is required only for a later predictive/calibration claim.

**Current status:** `COMPLETE_FOR_SCOPED_SYSTEMS_PAPER`.

## Q4 — Typed Scientific Epistemic State

**Canonical manuscript:** `papers/Q-paper-04-typed-state/MANUSCRIPT_V2.md`

Complete for the exact-synthetic matched-information mechanism/benchmark claim. The manuscript explicitly gives zero broad novelty credit for typed memory, stale-memory handling or VoI primitives already present in neighboring literature.

The >=100 real-decision protocol remains successor research and is required only for a future real-agent transfer claim.

**Current status:** `COMPLETE_FOR_SCOPED_MECHANISM_PAPER`.

## Framework ↔ paper ↔ harness synchronization

The final Q paper set is no longer prose-only synchronized.

- `src/orion/registry.py` fixes the Q-series spec id, sync epoch, paper ids, canonical manuscripts and Q3 harness-contract id.
- `papers/FRAMEWORK_SNAPSHOT.json` mirrors those identities and remains checked by `tests/unit/publication/test_framework_snapshot.py`.
- `src/orion/programme/q_series_sync.py` checks paper/evidence boundaries against committed receipts and exact Q1 theorem/sharpness records.
- `papers/Q_SERIES_CONTENT_BINDING_V1.json` + `q_series_content_binding.py` bind the canonical publication bytes so silent edits fail.
- `packages/orion-research-harness/src/orion_research_harness/publication_contract.py` validates the implementation surfaces Q3 describes.
- dedicated publication/harness tests enforce all of the above.

These checks are synchronization/integrity instruments. They deliberately grant no scientific, novelty or physical-quantum authority.

## Release rule

If a canonical Q manuscript, claim ledger, flagship proof, novelty record, final spec, or Q3 harness contract changes:

1. review whether the scientific claim changes;
2. update the corresponding manuscript/ledger/spec together;
3. regenerate the Q-series content binding if canonical bytes changed;
4. advance the sync epoch if the scientific/publication contract changed materially;
5. run the publication + harness regression suites;
6. never let a green software test promote a claim beyond its ledger.

# R4 Historical Failure Curriculum — Blind Repair-Responsibility Protocol V1

**Status:** `FROZEN_BEFORE_R4_OUTCOME`  
**Parent:** #964  
**Source corpus:** committed `research/failures/*/README.md` records on the frozen repository base.

## Question

> Can a recovery policy learn from ORION's historical negative/failure records to identify the correct **repair responsibility** for a held-out failure using only its pre-diagnosis failure description, rather than seeing the recorded failure class or repair?

This is a historical-curriculum test. It does not ask the model to reproduce exact patch text or hidden historical reasoning.

## Anti-contamination split inside each record

For every selected README:

- **candidate-visible text:** all Markdown after the top-level title and before the first `## Failure class` heading;
- **evaluator-only:** directory name, top-level title, `## Failure class`, every later section (`Correct response`, `Guard`, `Resolution`, lessons, residuals), and the frozen repair-family label below.

A record without exactly one `## Failure class` delimiter is an instrument failure; it may not be silently skipped.

The candidate-visible text is normalized by:
- removing Markdown code fences only as fence markers (code contents remain);
- replacing 7+ hex-character tokens by `<HEX>`;
- replacing decimal integers by `<NUM>`;
- preserving ordinary technical words and punctuation.

This prevents commit ids and exact counts from serving as record identifiers while keeping the causal symptom language.

## Frozen evaluator action taxonomy

Six broad actions, each with five committed episodes:

### A — `RESTORE_AUTHORITY_GOVERNANCE`
- `2026-08-answer-authority-laundering`
- `2026-08-host-check-authority-laundering`
- `2026-08-recurrence-self-promotion`
- `2026-08-unconditional-terminal-self-issued-authority`
- `2026-08-empty-lineage-false-saturation`

### B — `BIND_IDENTITY_AND_TYPE`
- `2026-08-git-object-ref-identity-mixup`
- `2026-08-digest-representation-boundary-mixup`
- `2026-08-p5-live-artifact-branch-identity-mismatch`
- `2026-08-p5-frozen-packet-unbound-to-execution`
- `2026-08-canonical-cap-excluded-live-projection`

### C — `REPAIR_INSTRUMENT_IDENTIFIABILITY`
- `2026-08-label-recoverable-from-construction-cue`
- `2026-08-unfalsifiable-check-zero-refutation-capacity`
- `2026-08-vacuous-guard-zero-denominator`
- `2026-08-unapplied-treatment-vacuous-null`
- `2026-08-rakl-paper4-instrument-negative`

### D — `WIRE_MECHANISM_INTO_EXECUTION`
- `2026-08-tested-but-unwired`
- `2026-08-graded-but-unapplied-verification`
- `2026-08-unreachable-operator-inert-ablation`
- `2026-08-orion-q-frozen-gate-enforcement-omissions`
- `2026-08-supplied-premise-unbuilt-decision`

### E — `HARDEN_STATE_CUSTODY_AND_FRESHNESS`
- `2026-08-concurrent-ledger-append-race`
- `2026-08-evidence-mixed-occasion-toctou`
- `2026-08-invertible-commitment-vacuous-custody`
- `2026-08-untrusted-source-alias-read-suppression`
- `2026-08-unwatched-paper-content-silent-drift`

### F — `REPAIR_IMPLEMENTATION_OR_NUMERIC_SEMANTICS`
- `2026-08-duplicate-pytest-module-name`
- `2026-08-orion-q-p10-int16-sentinel-overflow`
- `2026-08-orion-q-p10-int32-cumulative-sentinel-overflow`
- `2026-08-orion-research-harness-local-process-false-success`
- `2026-08-chatgpt-main-placeholder-write`

The action assignments are evaluator annotations. They are not visible to the held-out candidate.

## Lane A — learned history policy

For each of the 30 episodes independently:

1. hold out that episode;
2. train a fixed character n-gram TF-IDF + linear SVM on the other 29 visible failure texts and evaluator actions;
3. predict the held-out action.

Frozen model:
- `TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), min_df=1, sublinear_tf=True)`;
- `LinearSVC(C=1.0, class_weight='balanced', random_state=0)`;
- no parameter search;
- no title/directory/class/response text.

This is leave-one-record-out; every score is genuinely out-of-sample with respect to that record.

## Lane B — native responsibility controller

A separately coded rule controller sees the same normalized failure text and no labels from Lane A.

It scores six frozen evidence lexicons:

- authority: `authority, authorize, promotion, self-cert, waiver, readiness, provisional, attestor, verifier lane`;
- identity/type: `identity, digest, hash, ref, branch, commit, tree, representation, bound, binding`;
- instrument: `label, cue, denominator, falsifiable, refutation, treatment, ablation, metric, construction`;
- wiring/execution: `unwired, caller, production path, not called, applied, unreachable, operator, gate, premise, runtime path`;
- custody/freshness: `race, toctou, stale, supersession, alias, custody, concurrent, snapshot, drift, occasion`;
- implementation/numeric: `overflow, int16, int32, dtype, module, import, process, subprocess, placeholder, exception, sentinel`.

Score is matched distinct lexicon entries; ties are resolved by the fixed action order A→F. This controller is intentionally simple and auditable.

## Baselines / hostile controls

- balanced-majority baseline = `1/6` by construction;
- deterministic 64 shuffled-label controls for Lane A, preserving the 5-per-class marginal counts;
- candidate-visible text must not contain its directory slug, the frozen action token, or text after `## Failure class`;
- strip-title control is mandatory;
- exact per-record predictions retained, including errors.

## Primary metrics

- Lane-A leave-one-out accuracy;
- Lane-A macro-F1;
- Lane-B accuracy;
- dual exact-action agreement;
- per-class recall;
- 64-permutation Lane-A accuracy distribution.

## Frozen gates

A bounded historical-curriculum positive requires all:

1. Lane-A accuracy `>= 0.60`;
2. Lane-A macro-F1 `>= 0.55`;
3. Lane-A accuracy exceeds majority baseline by `>= 0.30`;
4. Lane-A accuracy exceeds the **maximum** of the 64 shuffled-label controls;
5. every Lane-A class recall `>= 0.40`;
6. Lane-B accuracy `>= 0.55`;
7. dual exact-action agreement `>= 0.45`;
8. leakage scan is clean on all 30 visible payloads.

No averaging may compensate a leakage failure.

Positive terminal:

`ORION_HISTORICAL_FAILURE_CURRICULUM_REPAIR_RESPONSIBILITY_SUPPORTED`

Honest alternative:

`ORION_HISTORICAL_FAILURE_CURRICULUM_REPAIR_RESPONSIBILITY_NOT_SUPPORTED`

## Claim boundary

A positive means the recorded failure descriptions contain reusable signal for broad repair responsibility and that a fixed learned policy generalizes leave-one-record-out across this 30-episode repository corpus. It does not establish recovery of unseen external scientific failures, exact repair synthesis, or independent historical reconstruction of the original research paths. The prospective QG-20 recovery remains the stronger working-method evidence.
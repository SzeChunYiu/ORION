# ORION-03 top-tier upgrade protocol — prospective multi-frontier agreement study

**Freeze date:** 2026-08-22
**Status:** research protocol only; no new benchmark outcome is claimed by this file.

## 1. Scientific question

Does agreement or disagreement between **architecturally distinct scientific decision instruments**, recorded before a frontier outcome is known, contain calibrated information about the later scientific resolution?

This is not an ensemble-voting study and not an attempt to force consensus.

## 2. Instruments

- **Instrument A — host-driven ORION research loop:** tool-capable host/LLM driving the generic receipt-bound research kernel under the frozen capability contract.
- **Instrument B — typed non-LLM campaign controller:** decisions produced by production typed epistemic-control modules over a frozen manifest and receipt-transcribed observations, with no LLM/free-text reasoning in the decision path.

A benchmark item is admissible only if both instruments can act on materially the same evidence state without one reading the other's answer.

## 3. Prospective item admission

An item must satisfy all conditions **before either instrument is executed**:

1. a concrete research frontier question exists;
2. the relevant scientific resolution is not yet known/committed in the repository or cited external record available to the benchmark operators;
3. a frozen manifest specifies candidate responsible layers/moves and the evidence each instrument may inspect;
4. every primary coordinate has a deferred scoring rule that can be evaluated later without redefining success;
5. no item is admitted because its future outcome is expected to create a desired AGREE/DISAGREE class.

Items whose truth is already known may be used only as **controls**, never as prospective primary data.

## 4. Target sample and domains

Primary target: **at least 20 prospectively admitted frontier decisions**, preferably >=30, spanning at least three materially different research programmes.

Desired domains include, without requiring all:

- quantum compilation/theorem work;
- non-quantum mathematics/formal reasoning;
- computational science/algorithmic research;
- research-infrastructure or epistemic-control questions where later objective evidence can resolve the deferred coordinate.

No single programme should contribute more than half of primary items.

## 5. Frozen outcome vocabulary

For each item, compare diagnosis and move coordinates using a preregistered normalization map:

- `AGREE`
- `PARTIAL`
- `DISAGREE`
- `CANNOT_CHECK_A`
- `CANNOT_CHECK_B`
- `CANNOT_CHECK_BOTH`

No outcome is invalid merely because the instruments disagree.

## 6. Deferred scientific scoring

When the frontier later resolves, bind the result receipt/commit/public artifact and score each instrument separately:

- `ALIGNED`: selected diagnosis/move is supported by the later registered outcome;
- `MISALIGNED`: later outcome explicitly supports a competing frozen diagnosis/move;
- `UNRESOLVED`: later work does not decide the coordinate;
- `INVALIDATED_ITEM`: a pre-outcome protocol defect makes scoring impossible; must be reported, never silently dropped.

Agreement itself never grants authority.

## 7. Primary measurements

After at least 20 resolved/scorable items, report:

1. `P(ALIGNED | AGREE)` with uncertainty interval;
2. `P(ALIGNED | DISAGREE/PARTIAL)` where sufficient counts exist;
3. per-instrument alignment rate;
4. calibration of `CANNOT_CHECK` outcomes — whether withholding occurs on items that remain unsupported or underspecified;
5. disagreement resolution matrix: A-only aligned, B-only aligned, both aligned, neither aligned;
6. evidence/decision cost per instrument, with **manifest-construction cost disclosed separately** rather than silently excluded;
7. time from pre-outcome decision to deferred resolution.

Exploratory, not primary: whether agreement provides incremental predictive value beyond simple covariates such as item difficulty, evidence count or programme identity.

## 8. Strong controls

Include separately labeled controls for:

- known resolved questions to verify scorer implementation;
- deliberately insufficient evidence where `CANNOT_CHECK` is the correct behavior;
- malformed/contradictory evidence receipts;
- stale receipts and evidence-version mismatch;
- shared-bias controls where both instruments receive a misleading but admissible evidence subset;
- manifest ablations to measure dependence of the typed controller on human-authored hypothesis coverage.

Controls do not count toward prospective headline statistics unless their status was frozen before execution.

## 9. Independence threats to disclose

The two instruments are not fully causally independent:

- both may share repository evidence and ontology;
- the typed manifest can be human/LLM-authored;
- the same project can induce shared conceptual priors;
- later scientific work can itself be influenced by the benchmark's selected move.

For each item, record these dependencies. Where feasible, have a third independent scorer/replicator resolve the deferred outcome or bind an external public result.

## 10. Instrument-quality gate before new V1+ items

The original manuscript records D2/D3 malformed-success receipt defects. Main now contains an explicit repair:

- invalid reasoner content is mapped to structured `HOST_CAPABILITY_FAILED` rather than raw traceback;
- `archive_invalid_result(..., reason=...)` preserves malformed successful receipt bytes plus a reason sidecar and frees the deterministic identity;
- regression tests verify recovery and corrected re-ingest.

Before collecting the prospective series, run the relevant harness suite on the chosen benchmark head and bind the exact commit/test result. Do not describe the repaired surface as a security boundary.

## 11. Stop rules

- If fewer than 20 prospective items can be admitted/resolved without leakage, retain ORION-03 as a **benchmark-definition/systems paper**, not a predictive-validity study.
- If agreement is not more informative than simple baselines, publish the negative calibration result.
- If both instruments share frequent correlated errors, treat that as a first-class result and investigate independence rather than adding more agreeable instruments.
- No post-outcome changes to the normalization/scoring map for an executed item.

## 12. Top-tier success criterion

A strong general result would require more than a high agreement rate. Examples of meaningful terminals include:

- prospective inter-instrument agreement is a reproducibly calibrated predictor of later scientific alignment across multiple programmes;
- disagreement has a structured diagnostic value, e.g. typed-controller withholding identifies evidence insufficiency missed by the host lane;
- or a strong negative: apparent agreement is not predictive once shared-evidence bias is controlled, demonstrating a limitation of multi-instrument scientific confidence.

Any of these is scientifically stronger than optimizing for `AGREE` itself.

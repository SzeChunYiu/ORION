# P5 Residual Attribution-Error Revival Receipt V1 (NR-01)

- **schema**: orion.revival-receipt.v1
- **lane**: NR-01 (negative-results backlog)
- **date**: 2026-08-23
- **source negative**: `research/verification/records/P5.glm-5.2-attribution-21-24.json` — GLM-5.2 hidden-cause attribution 21/24 = 0.875, three residual errors (P5-HC-002, P5-HC-012, P5-HC-018), independent standard macro-F1 0.872619.
- **terminal**: `P5_ATTRIBUTION_INSTRUMENT_V2_TREATMENT_24_24__INSTRUMENT_STAGE_POSITIVE`
- **landing**: branch `revive/p5-residuals-nr01` (pushed, no PR — lane transferred to codex by operator directive 2026-08-23, commit `2f247aaa`; this branch is the handoff artifact).

## 1. Root cause (one stage per error, from licensed evidence in the frozen case texts)

All three errors attribute to the **same single stage: the attribution mechanism (the V1 instrument)**, not case ambiguity, not the symptom representation, not the scoring rule. The V1 prompt asks for free-form "best judgment" causal reasoning; it therefore licenses mechanism speculation that can override the evidence the case text actually states. Each lost case is decidable from its licensed evidence; none was relabeled CANNOT_CHECK.

| Case | Gold | V1 attributed | Licensed evidence in the frozen text | Unlicensed override in recorded V1 reasoning |
|------|------|---------------|--------------------------------------|----------------------------------------------|
| P5-HC-002 | RETRIEVAL_MISS | REPRESENTATION_GAP | Failure predicate subject is "the nearest neighbor search"; "fails to find semantically similar documents despite clear content overlap" restates the RETRIEVAL_MISS definition structurally. No representation/encoding/format choice is stated to be wrong. | Inferred embedding quality ("the embedding representation failing to capture semantic similarity") from the mere mention that "document embeddings were generated" — a mechanism the text never states. |
| P5-HC-012 | ENVIRONMENT_DEPENDENCY_TOOL_FAILURE | IMPLEMENTATION_BUG | Conditional failure: "fails when encountering file paths with spaces, despite working on test data with simple names" — a working/failing regime delta whose operative variable (test_data vs production_data path property) is an environment/data property. No code-logic defect is asserted. | Converted the environment-conditional trigger into a code-located defect ("the code fails to correctly handle paths with spaces — a concrete implementation defect"), injecting a defect locus the text does not assert. |
| P5-HC-018 | REPRESENTATION_GAP | METHOD_BASIS_GAP | Explicit stated-cause clause: "because the representation doesn't capture causal structure" names the representation as the failing locus. | Re-derived a "deeper" cause ("its foundational approach lacks causal structure … requires a fundamentally different method"), overriding the stated cause. |

**Common structure**: the three lost cases are exactly those whose designed competitor (per the sealed `competing_cause_set`) is the more "deeply causal" attractor — representation deeper than search, code defect deeper than environment trigger, method deeper than representation. The V1 instrument rewards depth of causal narrative; the suite's discriminative structure lives in what the text *states*.

## 2. Lever (pre-registered before any V2 outcome)

`papers/paper-05-self-orion/protocol/P5_ATTRIBUTION_INSTRUMENT_V2_PROTOCOL.json` — **V2 licensed-evidence staged attribution**:

- **Stage A (model, extraction only)**: structured, verbatim-quote-backed extraction of four fields — `failing_subject`, `stated_cause`, `working_failing_delta`, `stated_code_defect` — over a 9-value locus vocabulary that restates the eight published family definitions. No diagnosis, no family names, no outside knowledge.
- **Stage B (deterministic code)**: priority rules R1–R6 (conflict→CANNOT_DISTINGUISH; stated code defect→IMPLEMENTATION_BUG; stated cause→locus family; environment/data regime delta→ENVIRONMENT_DEPENDENCY_TOOL_FAILURE; failing subject→locus family; else CANNOT_DISTINGUISH).

No case identifiers and no family-pair-specific provisions anywhere in the instrument; rules are stated only over general linguistic structure (stated-cause clause, concessive regime delta, defect-locus assertion, failing subject). The protocol file is deliberately left byte-frozen: its SHA256 is bound into the run's `report.json` (`protocol_sha256`), which is what makes the pre-registration verifiable.

## 3. Re-run design (two arms, identical serving)

`scripts/run_p5_glm_attribution_v2.py` (stdlib-only), frozen suite `PROTECTED_SUITE_V1.json` untouched (SHA256 `1c3650a6…` matches the verification record), temperature 0.0, requested model `glm-5.2` (served `glm-5.3` under the alias, recorded per response, **identical across both arms** — so the instrument is the only varying factor).

- **Control arm**: verbatim V1 `ATTRIBUTION_PROMPT` replay (imported byte-identical from `scripts/run_p5_glm_attribution.py`).
- **Treatment arm**: Stage A extraction + Stage B deterministic mapping.

## 4. Results

| Arm | Accuracy | Standard macro-F1 | CANNOT_DISTINGUISH | Runtime/parse errors |
|-----|----------|-------------------|--------------------|----------------------|
| V1 historical (glm-5.2) | 21/24 = 0.875 | 0.872619 | 0 | 0 |
| Control — V1 replay (served glm-5.3) | **21/24 = 0.875** | **0.872619** | 0 | 0 |
| Treatment — V2 (served glm-5.3) | **24/24 = 1.0** | **1.0** | 0 | 0 |

- The control arm reproduces the historical failure **exactly**: same three errors, same attributed labels (HC-002→REPRESENTATION_GAP, HC-012→IMPLEMENTATION_BUG, HC-018→METHOD_BASIS_GAP). This pins the failure on the instrument, not on the model-version change.
- The treatment arm resolves all three previously-lost cases through the pre-registered rules — HC-002 via R5 (failing subject = search), HC-012 via R4 (environment/data regime delta), HC-018 via R3 (stated cause = representation) — **with zero degradation elsewhere**: all 21 previously-correct cases remain correct (full-matrix result: 24/24, no case-specific rescue).
- Rule usage across the suite: R5×10, R3×10, R2×3, R4×1, R1×0, R6×0.
- Extraction audit (post-run, independent check): 0 out-of-vocabulary loci, 0 extraction flags, and every quote field verified to be a verbatim substring of the case's visible text.

## 5. What remains negative / open

1. **Blind/fresh-transfer capability is NOT certified.** Gold labels are colocated in the in-repo suite (verifier discrepancy `P5.protected-label-colocated-in-suite-json`); this is a re-test of instrument design on a public frozen suite. The fresh-transfer campaign lane is unchanged and still open.
2. **V1 21/24 remains the published unstructured-instrument measurement.** Nothing historical was relabeled, re-scored, or edited; V2 evidence lives in a new directory (`evidence/glm-5.2-attribution-v2/`).
3. **The V1 macro-F1 publication discrepancy** (published 0.875 vs standard 0.872619) remains documented in the verification record, untouched by this revival.
4. **P5-RD-01/02/03** (protected two-factor interventional successors, `P5_RESIDUAL_DISCRIMINATOR_SUCCESSORS_V1.json`) remain `DESIGNED_NOT_EXECUTED`. This revival addresses the diagnostic instrument; it does not execute the causal interventions, which remain the authority for mechanism-level discrimination.
5. **Single-run, single-seed, temperature 0.** No variance estimate across restarts was collected; the control-arm exact reproduction is the replicability evidence available.

## 6. Authority boundary (what this receipt does NOT claim)

- Does **not** claim GLM-5.2/5.3 gained attribution capability — the model's role changed from diagnosing to extracting, and the diagnosis is now deterministic code.
- Does **not** overturn, weaken, or reinterpret the historical negative; the negative was the V1 instrument's measurement and stands immutable.
- Does **not** certify performance outside the 24-case frozen suite, on fresh cases, under other serving conditions, or for other models.
- Does **not** grant scientific authority for the hidden-cause construct; it is an instrument-stage engineering revival within the NR-01 lane, landed for the codex lane (current P1–P5 owner per operator directive 2026-08-23) to combine, supersede, or extend.

## 7. Artifacts

| Artifact | Path (repo-relative) |
|----------|----------------------|
| Pre-registered protocol (byte-frozen, hash-bound) | `papers/paper-05-self-orion/protocol/P5_ATTRIBUTION_INSTRUMENT_V2_PROTOCOL.json` |
| Two-arm driver (stdlib-only) | `scripts/run_p5_glm_attribution_v2.py` |
| Control results (V1 replay) | `papers/paper-05-self-orion/evidence/glm-5.2-attribution-v2/results_control_v1replay.jsonl` |
| Treatment results (V2) | `papers/paper-05-self-orion/evidence/glm-5.2-attribution-v2/results_treatment_v2.jsonl` |
| Run report (hash bindings) | `papers/paper-05-self-orion/evidence/glm-5.2-attribution-v2/report.json` |
| Machine-readable twin of this receipt | `papers/paper-05-self-orion/top_tier/P5_RESIDUAL_ERROR_REVIVAL_RECEIPT_V1.json` |

# ORION paper-contract host protocol

Date: 2026-08-22
Scope: shared `packages/orion-research-harness`
Authority: host/orchestration instructions only; no scientific, novelty, adoption, promotion, merge, or global-stop authority.

## Purpose

The paper-contract runtime closes the distinction between a mechanic being discoverable and being executable. It provides raw-source method reconstruction, evidence-derived multi-axis saturation, Paper-VII navigation, P6 epistemic mechanics, P8 typed authority, P10 obstruction-certified method-language expansion, host-callable P11-P14 decision laws, a V3 paper-aware research director, and a V4 research-resolution lifecycle that distinguishes positive, negative, and unresolved outcomes.

## Install

```bash
python -m pip install -e '.[dev]'
python -m pip install -e 'packages/orion-research-harness[dev]'
```

## Semantic self-checks

Run the paper/harness gates plus the V4 covariance module:

```bash
orion-harness-paper paper-contract-conformance
orion-harness-paper paper-programme-conformance
orion-harness-paper research-v3-conformance
python -m orion_research_harness.research_v4_conformance
```

A release-ready result must report:

```text
ORION_HARNESS_PAPER_CONTRACT_P0_OPERATIONAL
ORION_HARNESS_P1_P15_OPERATIONAL
ORION_HARNESS_RESEARCH_DIRECTOR_CONSENSUS_EXTRACTION_V3_OPERATIONAL
ORION_PAPER_FRAMEWORK_HARNESS_COVARIANCE_V4_OPERATIONAL
```

The P0 gate executes hostile semantic probes; the programme gate executes positive and fail-closed probes for every P1-P15 owner; V3 checks research-director and consensus-extraction control semantics; V4 checks paper ↔ framework ↔ harness outcome-lifecycle covariance. None is a scientific benchmark, an arbitrary-paper extraction-completeness claim, or promotion authority.

## V4 outcome lifecycle: positive, negative, unresolved

The host must keep three outcome classes separate:

- **POSITIVE** — the bounded target contract passes;
- **NEGATIVE** — a verified obstruction, falsification, non-identifiability, donor subsumption, failed frozen transfer, or other scientifically meaningful negative result;
- **UNRESOLVED** — the current contract cannot decide the target judgment (`CANNOT_CHECK`).

### `CANNOT_CHECK` is normally an active resolution obligation

Main harness surfaces now attach `ResearchResolutionObligation.v1` whenever they own an unresolved decision. The object records:

- unresolved class and reason codes;
- required evidence/capability/authority objects;
- admissible next actions;
- prior attempts and blockers;
- an explicit bounded/external stop condition when one applies;
- non-authorizing authority ceilings.

Use the generic host surface directly when needed:

```bash
orion-harness-paper resolution-plan --file unresolved-or-negative.json
```

Example unresolved payload:

```json
{
  "outcome_kind": "UNRESOLVED",
  "subject_id": "claim:x",
  "unresolved_class": "EVIDENCE",
  "reason_codes": ["MISSING_INDEPENDENT_VERIFICATION"],
  "required_object_ids": ["verify:claim:x"]
}
```

The returned obligation will propose admissible actions such as evidence acquisition/verification, capability repair, search expansion, orientation/reframe, responsibility diagnosis, representation repair, OCME, typed authority checking, protocol-authorized resource widening, or protected-evidence request.

A protected/external blocker is not treated as an ordinary local retry. A frozen resource bound does not self-authorize more resources. No resolution obligation can include `TASK_STOP` or grant scientific/novelty/promotion/global-stop authority.

### Negative results are assimilated, not "fixed" into positives

A verified negative result is represented as `ResearchNegativeResult.v1`. Example:

```json
{
  "outcome_kind": "NEGATIVE",
  "result_id": "negative:donor",
  "subject_id": "method:candidate",
  "negative_kind": "DONOR_SUBSUMED",
  "evidence_ids": ["e:donor"],
  "reason_codes": ["STRONG_DONOR_SAME_REACH"]
}
```

Typical assimilation dispositions include registering an obstruction/donor result, closing a hypothesis branch, reopening a dependency, reframing/widening search, revising a paper claim, revising a framework mechanic, or recording a bounded negative terminal. These are research-control consequences, not scientific-authority grants.

## Paper-aware research director

Every completed normal recursive solve carries a derived `research_directive`. Unresolved recursive outcomes also carry `resolution_obligation`. The underlying immutable run receipt is not rewritten; both are control-plane projections over it.

You can also ask the director directly:

```bash
orion-harness-paper research-direct --file solve-state.json
```

The director is deliberately non-compensatory:

- resource exhaustion or ambiguous residual identity -> unresolved + resolution obligation;
- zero/multiple causal responsibilities -> `DIAGNOSE_RESPONSIBILITY`;
- `EXECUTION` -> `RESTORE_CAPABILITY` (P15);
- `EVIDENCE` -> `VERIFY_EVIDENCE` (P4/P8);
- `EVALUATOR` -> `CHECK_EVALUATION_AUTHORITY` (P4/P8/P14);
- `METHOD` -> `ASSESS_OCME` (P10), never an automatic language jump;
- question/representation/search/routing/decomposition/interface/measurement -> `NAVIGATE_OR_REFRAME` (P1/P2/P7);
- verified solution with no material residual -> `ASSESS_SATURATION`, never automatic task stop;
- non-verified solution with no material residual -> `VERIFY_OR_REOPEN`.

When several singular residuals coexist, precedence is `EXECUTION > EVIDENCE > EVALUATOR > METHOD > NAVIGATE_OR_REFRAME`. The director never grants scientific/novelty/promotion/global-stop authority.

## Raw paper -> Paper-I/Paper-III structure

Initialize a normal harness workspace whose `project_root` contains the source:

```bash
orion-harness init .research --project-root .
```

### Preferred V3 consensus path

For research use, prefer the two-lane consensus extractor:

```bash
orion-harness-paper paper-structure-consensus .research path/to/paper.txt method:example \
  --source-id paper:example \
  --source-version v1
```

It is replayable and proceeds through four fail-closed stages:

1. proposer `lane_a` over every deterministic source chunk;
2. proposer `lane_b` over every deterministic source chunk, with a distinct request identity;
3. `INDEPENDENT_REVIEW` coverage check over the merged exact-span ledger;
4. the existing `VERIFY_EVIDENCE` semantic source-support check, which still requires a certificate.

Identical claims retain both proposer lane IDs. Sequence-valued coordinates union source-supported claims. Distinct surviving scalar values produce `CANNOT_CHECK_PROPOSER_DISAGREEMENT` before canonical construction. A valid reviewer-discovered missed claim produces `CANNOT_CHECK_COVERAGE_GAP`; the reviewer claim is not silently promoted into a COMPLETE structure. V4 projects those unresolved states into resolution obligations. Invalid quotes/schema are host capability failures.

The older single-proposer V1 path remains available for backward compatibility:

```bash
orion-harness-paper paper-structure .research path/to/paper.txt method:example \
  --source-id paper:example \
  --source-version v1
```

### Plain text, Markdown, TeX and other UTF-8 text

The harness reads exact local bytes inside `project_root`, computes a SHA-256 source digest, and chunks text deterministically.

### PDF sources

The harness does not pretend to own PDF/OCR semantics. It creates a `DOCUMENT_TEXT_EXTRACT` request containing the project-relative path, exact `sha256:` PDF digest, byte length and an instruction to extract searchable text without semantic summarization. The host result must carry the exact source digest. A digest mismatch fails closed.

### Exact-span proposal rule

Every proposer/reviewer claim uses `coordinate`, `value`, and an exact verbatim `quote`. Every populated scientific coordinate needs exact source support. Unsupported coordinates remain typed `UNKNOWN`. Dependencies are exact `[from_mechanic, to_mechanic]` pairs. The harness checks every quote before canonical P1/P3 construction.

## P6 host commands — epistemic mechanics

```bash
orion-harness-paper mechanic-apply --file mechanic-input.json
orion-harness-paper dependency-repair --file repair-input.json
```

The runtime enforces declared write footprints, hard evidence/authority premises, obligation persistence/discharge, non-escalating authority and recursive audit-rank constraints. `DENIED` and `CANNOT_CHECK` never mutate state. P6 `CANNOT_CHECK` receives an evidence-class resolution obligation.

## P7 host command — open-world navigation

```bash
orion-harness-paper navigation-plan --file navigation-state.json
```

Core invariant:

```text
task_stop -> every mandatory obligation is satisfied, discharged, or certificate-covered
```

Route stop never implies task stop. Budget exhaustion, censored/unavailable route exhaustion, or an unmapped mandatory obligation remains unresolved and carries a coverage-class resolution obligation. An unresolved start yields orientation.

## P8 host command — typed epistemic authority

```bash
orion-harness-paper authority-check --file authority-input.json
```

Authority requires exact typed obligation discharge, blocker refutation, fresh in-scope grant and exact content/epoch binding. Confidence and utility are not authority currency. Cross-domain/type changes require registered protected coercions. Scope widening is denied unless the coercion explicitly declares `allow_scope_widening=true`. P8 `CANNOT_CHECK` carries an authority-class resolution obligation; `DENIED` remains a negative authorization decision rather than being softened to missing evidence.

## Evidence-derived nine-axis research saturation

```bash
orion-harness-paper research-saturation --file rounds.json
```

Each round supplies executed route contracts, observed Self-ORION axes and observed item identities. Novelty counts are derived by set difference. Independent-flat credit is derived structurally and is one-route-per-round; a mixed bundle cannot manufacture a new independent route family. Missing axes, material residuals, dependent routes or resource bounds block bounded saturation and now produce a resolution obligation. Bounded saturation never grants absolute completeness.

### Important telemetry boundary

Core `SearchQuery` records `route_id` and `route_kind`, but it does **not** encode the critical failure/coverage assumptions required by Paper VII to establish structural independence. Therefore the harness must not manufacture structural route contracts from query labels alone. When the director returns `ASSESS_SATURATION` or `NAVIGATE_OR_REFRAME`, the host must supply/execute explicit `RouteContract`s with critical assumption and coverage identities. Missing structural identity is a real unresolved obligation, not a reason to infer independence.

## P10 host command — obstruction-certified method-language expansion

```bash
orion-harness-paper ocme-assess --file ocme-episode.json
```

The runtime enforces O0-O6, including all eight registered lower-level first-right-of-refusal families, independently verified obstruction, candidate edit, independent outside-closure check, held-out transfer/false-expansion guard, donor comparison and independent reproduction. Timeout-only failure is not an obstruction certificate.

Missing O0-O6 proof objects are unresolved and carry method-class resolution obligations. Verified donor subsumption or impossibility boundaries are negative results and receive assimilation objects; they are not rewritten as `CANNOT_CHECK`.

## P11-P14 host-callable paper laws

```bash
orion-harness-paper p11-accessible-rank 20 3
orion-harness-paper p12-allocate 2 0 --budget 2
orion-harness-paper p13-action Z1 VERIFY --recoverable
orion-harness-paper p14-disposition --file governance-facts.json
```

P13/P14 unresolved dispositions carry V4 resolution obligations. The law outputs remain lightweight bounded decision kernels and do not import publication outcomes as policy inputs.

## Authority boundary

Paper extraction/consensus, research directives, resolution obligations, negative-result assimilation, mechanic execution, dependency repair, navigation, authority decisions, bounded saturation, OCME dispositions, P11-P14 law outputs and all conformance terminals are non-authorizing research-control evidence. Scientific conclusions still require normal ORION evidence, protected verification and authority machinery.

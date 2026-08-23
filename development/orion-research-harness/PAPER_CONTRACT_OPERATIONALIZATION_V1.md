# ORION research harness — paper-contract operationalization V1

Date: 2026-08-22
Branch: `codex/paper-contract-operational-harness`
Status: FROZEN BEFORE IMPLEMENTATION
Authority ceiling: engineering/development only. This packet grants no scientific, novelty, adoption, promotion, merge, or global-stop authority.

## Development question

Can the shared `orion-research-harness` execute the scientific mechanics described by the ORION papers as operational research behavior, rather than merely exposing mechanic IDs, typed structures, or authored fixtures?

The required distinction is:

`paper mechanic discoverable != paper mechanic operational`.

V1 closes the highest-risk false-green gaps identified by inspection of the current main branch:

1. Paper-I/Paper-III method structure currently has typed `MethodRealization.v1` / `MethodStructureProjection.v1`, but the published bounded pilot starts from authored structured fixtures rather than raw paper text.
2. Bounded saturation is real, but ordinary route coverage can be represented by route-kind labels without a mechanically checked structural route contract; the richer nine-axis Self-ORION saturation evaluator is not yet bound to evidence-derived route independence in the harness.
3. `orion-harness navigate` is mechanic-catalog discovery, not the Paper-VII open-world epistemic-atlas/navigation state machine.
4. `mechanics-coverage` and `execution-coverage` establish discoverability/owner resolution, not paper-contract behavioral conformance.

## Atomic development fibres

### H1 — raw-source method reconstruction

Input must be source bytes/text, not a pre-populated `MethodRealization`.

The harness must:

- content-bind the raw source;
- extract method coordinates through host reasoning only as proposals;
- require exact source spans for every populated scientific coordinate;
- mechanically reject fabricated/non-occurring quotations;
- preserve unsupported coordinates as typed `UNKNOWN` rather than infer by analogy;
- construct canonical Paper-I `MethodRealization.v1` and Paper-III `MethodStructureProjection.v1` through their production builders;
- perform an independent evidence-verification step before marking an extraction verified;
- keep authority at representation/projection only.

PDF text conversion is a host capability because the harness intentionally does not own OCR/PDF parsing. The conversion request must be digest-bound to the exact local source bytes. Plain text/Markdown/TeX sources are read directly inside the project root.

### H2 — structural route contracts

A search route is not structurally independent because it has a different query string or route-kind label.

The harness must represent a route contract containing at least:

- stable route identity/family;
- obligation scope;
- critical failure/coverage assumptions;
- declared coverage scope;
- censoring/unavailable coordinates.

For V1, structural independence is established only by the conservative sufficient rule from Paper VII: both routes have explicit critical-assumption sets and those sets are disjoint. Missing assumption identity means independence is `CANNOT_CHECK`, not `True`.

### H3 — evidence-derived multi-axis development saturation

The harness must operationalize the Self-ORION axes:

- KNOWLEDGE
- SEARCH_UNIVERSE
- FORMULATION
- OPERATOR
- EXPERIENCE_PATTERN
- OBSTRUCTION
- RELATION
- PATH
- META_METHOD

Novelty counts are derived by set difference against prior observed state. Caller-supplied booleans may not directly certify route independence. Resource exhaustion, missing axis observability, native residuals, or dependent route families prevent bounded-saturation closure.

### H4 — Paper-VII epistemic navigation runtime

The harness must implement typed runtime objects and transitions for:

- charts and chart reachability;
- mandatory obligations;
- registered route contracts;
- visited evidence/location state;
- censored/unavailable routes;
- route-stop versus task-stop;
- orientation when the starting epistemic location is not yet established;
- chart-changing reframes;
- evidence transport distinct from closure transport;
- reopening or `CANNOT_CHECK` when support/objective preservation is not proved.

The invariant is fail closed:

`task_stop -> no mandatory-open or cannot-check obligation`.

### H5 — semantic conformance gate

Add a `paper-contract-conformance` gate that executes hostile known-answer probes. It must not pass merely because modules import or IDs resolve.

The gate must exercise at least:

- fabricated source-span rejection;
- source-insufficient method coordinate -> UNKNOWN;
- same-label/different-contract and different-label/shared-assumption route controls;
- dependent flat routes do not saturate;
- multi-axis residual reopens saturation;
- route-stop does not imply task-stop;
- unmapped/unsupported reframe reopens or yields `CANNOT_CHECK`;
- evidence identity may transport while closure authority does not.

## Incumbent mechanics absorbed rather than duplicated

V1 must call the existing production objects where they own semantics:

- `orion.transfer.v2.p1_method_realization` for Paper-I method realizations;
- `orion.transfer.v2.p3_method_projection` for Paper-III source-local projections;
- `orion.self_orion.saturation_vector` for non-compensatory multi-axis saturation;
- `orion_research_harness.broker` / `workspace` for deterministic host capability receipts;
- existing authority/governance contracts for fail-closed external verification.

The new harness code is orchestration, evidence binding, navigation runtime, and conformance checking. It may not fork a second scientific authority system.

## Bounded saturation assessment before implementation

The current repository already has enough canonical substrate to implement this tranche without inventing new scientific semantics:

- source-bound method structures and projection builders exist;
- evidence/capability request identities are replayable and digest-bound;
- bounded saturation and nine-axis development saturation exist;
- Paper VII supplies explicit formal transition/stopping obligations and finite countermodels;
- the harness already has an external-host architecture for reasoning, retrieval, verification, review, and local tools.

The missing layer is operational wiring and hostile conformance evidence.

This assessment is bounded to the P0 false-green gaps above. It is not a claim that every empirical paper result is reproduced or that arbitrary scientific papers can be extracted perfectly.

## Challenge to the saturation basis

This development plan is wrong or insufficient if any of the following is true:

1. an existing production path already performs raw paper -> Paper-I/Paper-III extraction with exact span binding;
2. ordinary solver route coverage already derives structural independence from explicit critical assumptions rather than route labels;
3. a production Paper-VII atlas/navigation runtime already exists under another vocabulary;
4. nine-axis saturation is already fed by evidence-derived route independence in the shared harness;
5. exact-span support is too weak to prevent semantically incorrect extraction and therefore needs stronger independent annotation before any verified terminal;
6. the host capability boundary cannot safely carry raw paper text within practical context/resource limits.

If these are found, V1 must absorb the incumbent rather than duplicate it.

## Why prior work could have missed the gap

- representation/evaluation pilots can be fully green while starting after the difficult natural-language extraction step;
- a route-kind enum looks like coverage even when the structural failure assumptions were never represented;
- `navigate` is overloaded between catalog lookup and epistemic navigation;
- static execution-owner coverage can turn a distributed implementation into a green row without exercising the paper theorem boundary;
- formal countermodel checkers can be correct while remaining disconnected from the production research harness.

## Frozen implementation hypothesis

Implement the smallest additive tranche:

1. `paper_structure.py` — raw source ingestion, chunked source-bound extraction, exact-span validation, canonical Paper-I/Paper-III construction, independent verification, replayable receipts.
2. `epistemic_navigation.py` — Paper-VII typed charts/routes/obligations/reframes and fail-closed transition rules.
3. `research_saturation.py` — evidence-derived novelty rounds, conservative structural independence, bridge into canonical nine-axis saturation.
4. `paper_conformance.py` — executable hostile semantic probes over the three runtimes.
5. CLI commands `paper-structure` and `paper-contract-conformance`, plus host-handoff documentation.
6. RED->GREEN package tests and CI gate.

Prefer additive files. Modify shared CLI/workflow/README only where required to expose and gate the new behavior.

## Frozen hostile tests

1. Plain text source bytes produce a digest-bound extraction request from raw text, not a prebuilt realization.
2. A proposed coordinate whose quotation is absent from the source is rejected before canonical construction.
3. Missing mandatory source support becomes `UNKNOWN` / partial, never fabricated completeness.
4. A passing structure verification requires at least one certificate id.
5. PDF text extraction request is bound to the exact PDF SHA-256 and cannot silently accept a different digest.
6. Two routes with missing critical assumptions are not independently saturated.
7. Two routes sharing a critical failure assumption are not structurally independent even if their labels/outputs differ.
8. Two explicit disjoint-assumption routes can count as independent only after their route contracts are valid.
9. Novelty/residual on any required saturation axis prevents bounded saturation.
10. Resource-bound rounds never establish closure.
11. Local route exhaustion with an open mandatory obligation cannot produce task-stop.
12. Budget exhaustion with an open mandatory obligation returns `CANNOT_CHECK`, not task-stop.
13. A reframe without support preservation reopens a previously closed mapped obligation.
14. An unmapped mandatory obligation becomes `CANNOT_CHECK` or open; it never silently disappears.
15. Evidence identities transport across an admissible reframe even when old closure authority is reopened.
16. The semantic conformance command fails if any hostile probe fails.
17. All outputs explicitly deny scientific/novelty/promotion/global-stop authority except a task-stop judgment that is mechanically licensed by closed mandatory obligations.

## Reopen triggers

Reopen the design if:

- real paper extraction cannot preserve exact evidence spans under chunking;
- a route-independence case requires a richer causal contract than disjoint critical assumptions;
- the existing nine-axis evaluator cannot represent an observed-but-unknown axis without false flatness;
- navigation requires chart/objective semantics not representable without changing canonical core state;
- a new runtime duplicates an incumbent production owner;
- CI can pass with authored method fixtures while the raw-source test path is broken;
- any new command can claim research completion while a mandatory obligation, unsupported coordinate, censored route, or material residual remains open.

## V1 terminal

`ORION_HARNESS_PAPER_CONTRACT_P0_OPERATIONAL`

Allowed only when the frozen hostile tests pass and the CI semantic gate exercises the raw-source, saturation, and navigation runtimes.

This terminal means the P0 paper-contract mechanics are operationally wired into the shared harness. It does not mean arbitrary-paper extraction accuracy, scientific correctness, novelty, or universal research-space completeness has been established.

# ORION-P3 public-reference gold authority route V1

**Status:** DESIGN_FROZEN, outcome-blind addendum to `P3.cross-domain-atlas.v1`.

## Purpose

Issue #100 originally assumed ORION would commission a new multi-discipline expert annotation campaign. That is not a scientific requirement by itself; the scientific requirement is that headline gold have authority independent of the evaluated systems, preserve source identity, and make uncertainty explicit.

This addendum defines a resource-constrained route that **reuses existing public human/expert annotations and expert-built scientific schemas** instead of duplicating them. It does not weaken the original authority boundary and it does not relabel model-generated guesses as expert gold.

The route is prospective: it changes no existing V1 result and grants no empirical claim until a frozen public-reference atlas passes the gates below.

## Pinned public authorities

1. **MUSE** — `cohentsofia/MUSE@f7a40317db46145d0c90b221311d8324db5da1b9`.
   - 579 expert-annotated full-text paragraphs.
   - Annotation performed by a PhD-level scientific annotator, with an independently annotated held-out quality-control subset by an NLP expert.
   - Carries exact paragraph text, entity spans, problem/solution/rationale labels, conceptual coreference and typed relations.
2. **SciSchema** — `scischema/scischema@55b6197cdb0b66c3123df16d0b0c70b02c4bde8b`.
   - Versioned multidisciplinary expert scientific-process schemas.
   - Public schema families include biology, physics, psychology, materials and imaging.
   - Repository license at the pinned revision is CC BY-SA 4.0.
3. **SciER** — retained as an eligible public human-annotation source when a pinned, redistributable dataset artifact is bound in the source registry. Until that exact artifact and license are bound, SciER-derived coordinates are `UNRESOLVED`, not guessed.

## Gold-authority rule

Every ORION gold coordinate MUST carry a machine-readable authority record. Exactly three authority classes are allowed:

- `EXTERNAL_HUMAN`: copied or losslessly normalized from a human annotation in a pinned public artifact;
- `EXTERNAL_EXPERT`: copied or losslessly normalized from an expert annotation/schema in a pinned public artifact;
- `DETERMINISTIC_DERIVATION`: computed by a documented deterministic rule from one or more `EXTERNAL_HUMAN`/`EXTERNAL_EXPERT` facts.

The following can never create headline gold authority:

- LLM-only annotation;
- self-consistency or agreement between models;
- simulated inter-annotator agreement;
- citation-count, embedding-similarity or lexical heuristics without an externally authoritative premise;
- an ORION system output or baseline output;
- a manual label created after evaluated-system outputs are inspected.

If a requested coordinate lacks admissible authority, its value is `UNRESOLVED`. Missing authority is never converted to a negative label.

## Deterministic derivations

A derivation is admissible only when its rule is fixed before evaluated-system outputs and its premises are cited in the record. Initial allowed rules are deliberately narrow:

- exact source recoverability from pinned `(repository, revision, path, text/span hash)` identity;
- exact alias/coreference transfer where the public annotation explicitly supplies a coreference relation;
- exact unit/schema transformation when the pinned expert schema explicitly specifies the units/constraints needed for the transformation;
- exact provenance linkage from a public annotation span to its source document identity.

Semantic judgments that require new scientific interpretation — e.g. whether two measurements are scientifically equivalent, whether two constructs are the same, or whether two claims truly contradict — remain `UNRESOLVED` unless the public authority directly licenses the judgment.

## Dataset construction

The builder in `orion.study.p3.public_reference_gold` consumes:

1. `gold/PUBLIC_REFERENCE_SOURCE_REGISTRY_V1.json` — pinned external authorities and licenses;
2. normalized case records, each preserving exact source identity and per-coordinate authority;
3. the frozen ORION annotation schema.

It emits:

- `adjudicated/public-reference-gold-v1.json` — scoring-compatible annotation records plus an authority ledger;
- `adjudicated/PUBLIC_REFERENCE_MANIFEST_V1.json` — canonical content hashes, source pins, case/disciplines counts and freeze status.

A publication freeze is fail-closed. It refuses duplicate case IDs, unknown authorities, unpinned sources, model-only authority, missing source locators, or insufficient discipline/case-family coverage.

## Quality model without a new paid annotation team

This route does **not** claim a new ORION inter-annotator agreement statistic when ORION did not commission two ORION annotators. Instead:

- source-dataset quality evidence is reported as source provenance (for example MUSE's independent QC subset);
- agreement is reported only where the imported public artifact actually exposes independent annotations;
- ORION's normalization/derivation layer is validated by deterministic tests and independent replay;
- coordinates without externally grounded authority stay `UNRESOLVED` and reduce coverage rather than inflating agreement.

This changes the paper's interpretation from "new expert-annotated atlas" to "cross-domain public-reference atlas assembled from independently produced human/expert resources." The manuscript must use that wording if this route becomes the headline dataset.

## Gates

`PUBLIC_REFERENCE_GOLD_FROZEN` requires all of:

1. at least three materially different scientific disciplines;
2. every included source pinned by immutable revision/content identity and license/retrieval rule;
3. every scored coordinate bound to an admissible authority record;
4. all eight frozen case families represented, or a new protocol version that prospectively narrows the claim;
5. no evaluated-system output inspected while constructing/finalizing the gold;
6. canonical gold and manifest hashes recorded;
7. deterministic rebuild reproduces the same semantic content hash;
8. an independent replay verifies source locators and derivations.

Failure of any gate is `CANNOT_CHECK`, never `PASS`.

## Relationship to issue #100

This route directly satisfies the resource constraint behind Step 3 by reusing MUSE/SciSchema/SciER where task and license genuinely match. It **does not** by itself complete the real gold dataset, baseline runs, ablations, results, or peer-review-ready terminal. Those boxes become eligible only after the corresponding frozen artifacts exist.

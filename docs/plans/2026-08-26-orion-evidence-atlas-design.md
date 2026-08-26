# ORION P1-P15 evidence atlas design

## Decision

Build a repository-root `visualization/` package that presents ORION as a typed
evidence atlas rather than as a single dashboard score.  Every derived row is
bound to a repository source path and SHA-256 digest.  Static figures are the
deterministic reference objects; notebooks and the self-contained HTML view are
presentation layers and do not add scientific authority.

## Approaches considered

1. **Receipt-derived evidence atlas (selected).** Extract a small normalized
   dataset from registered P1-P15 receipts, render several plot families, and
   keep PASS, FAIL, adverse, UNKNOWN, and CANNOT_CHECK states distinct.  This is
   reproducible and reviewable, but it cannot claim more than the source
   receipts.
2. **Live dashboard over the whole repository.** Discover arbitrary JSON fields
   at runtime and let users chart them.  This is flexible, but schema drift can
   silently change denominators and it is difficult to bind each displayed
   scalar to a declared transformation.
3. **Curated manuscript figures only.** Hand-build a small set of polished
   figures for the strongest papers.  This is visually compact, but it hides
   the cross-paper framework, adverse results, and missing-authority boundaries
   requested for this task.

The selected atlas is the smallest design that exposes the framework, methods,
results, anomalies, and claim boundaries without inventing a portfolio score.

## Scientific figure contract

**Core conclusion:** ORION contains a coherent sequence of state,
discovery/portrait, authority, learning, reasoning, governance, and execution
mechanics that have heterogeneous evidence states.  Some bounded internal
results are positive; several gates fail or remain CANNOT_CHECK.  Repository
integrity is not independent validation.

**Reader questions:**

- What role does each P1-P15 component play, and how do the roles connect?
- Which algorithms or estimands are exercised by real receipts?
- Which comparisons, uncertainty intervals, and failure boundaries are visible?
- Where do denominator drift, identity drift, null results, or absent authority
  prevent a broader claim?

**Evidence units:** topics, cases, family RNG blocks, queries, finite states,
episodes, and workflow receipts remain separate.  Counts are never pooled across
these incompatible units.

**Claim ceiling:** the atlas may demonstrate receipt-bound internal mechanics and
bounded outcomes.  It may not establish external authority, broad generalization,
novelty, superiority, adoption benefit, or journal readiness.

## Architecture and data flow

```text
registered source receipts
  -> source_catalog.json
  -> scripts/build_data.py
  -> data/derived/atlas.json + data/manifests/source_manifest.json
  -> reusable transforms/plots/diagrams
  -> deterministic SVG/PNG + self-contained HTML
  -> notebooks (parameterized views over the same normalized rows)
```

The extractor names each transformation and records the source digest, schema,
byte count, authority tier, and exact fields used.  Missing sources return
`CANNOT_CHECK`; hash or schema drift returns `DRIFT`; a scientific FAIL remains a
scientific FAIL.  `scripts/check.py` rebuilds in a temporary directory and is
read-only with respect to committed outputs.

## Figure sequence

1. Typed P1-P15 framework graph: orientation only; arrows are conceptual
   dependencies, not causal effects or weighted flows.
2. Paper-by-gate status matrix: no scalar completion/readiness score.
3. Flagship evidence: P1 paired-effect forest and observed cost-success grid,
   P2 separate fixed-0-1 Recall@100/nDCG@10 panels with the failed gate printed,
   and a fixed-0-1 P3 Wilson-interval forest. P4/P5 boundaries remain explicit
   in the audit rather than receiving decorative standalone charts.
4. Formal/structured evidence: a log-count P6/P7 event decomposition that
   preserves the separate invalid 738/736 P7 execution. P8-P10 inventory and
   failure boundaries remain available in the formal notebook and anomaly audit.
5. State/governance/harness evidence: P11 ECDF plus all raw sorted deltas, P12
   raw family blocks by registered sigma stratum, P13 three-objective
   cost-correctness-unsafe-reuse trade-off, direction-correct fixed-0-1 P14 rate
   panels, and the full-label P15 workflow gate matrix.
6. Anomaly audit: exact-label counts, paper-by-label map, and explicit
   adverse/null/CANNOT_CHECK table with source bindings.

## Interaction

Five notebooks expose editable paper, metric, arm, and threshold selectors.  A
self-contained HTML atlas supports paper/status filtering and source inspection
without a network connection.  Interactive outputs are presentation-only; the
committed normalized JSON and static figures remain authoritative for replay.

## Verification

- hand-checkable tests for Wilson intervals, Jaccard, ECDF, Pareto dominance, and
  status classification;
- exact source schema/row-count/denominator assertions;
- SHA-256 manifest validation with missing and mutated negative controls;
- two-run byte identity for SVG/PNG and derived JSON;
- notebook JSON validation, code compilation, and offline execution through the
  repository's lightweight runner;
- self-contained HTML audit forbidding external scripts/styles;
- SVG text/axis/legend checks, PNG dimension/nonblank checks, and final visual
  inspection of every panel.

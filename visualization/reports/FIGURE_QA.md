# Figure purpose, estimand, and visual-QA audit

This audit treats every figure as a scientific argument. A plot is retained only
when it helps a reader resolve a defined question using a compatible evidence
unit. None of the figures is a portfolio score, an external-authority judgment,
or a journal-readiness ranking.

## Panel contracts

| Figure | Reader purpose | Evidence unit and estimand | Scale and representation contract | Adverse/authority safeguard |
|---|---|---|---|---|
| `00_framework_map` | Understand which paper conceptually informs which later component. | P1-P15 registry nodes and declared conceptual-dependency edges; no numeric estimand. | Compact three-lane directed graph; arrowheads mean conceptual dependency, not causal effect. | Direction and non-causal edge semantics are printed in the figure. |
| `01_paper_gate_matrix` | See which independent evidence gate is recorded for every paper without scalarization. | One categorical receipt state per paper × gate. | Canonical P1-P15 row order; nominal colors plus full in-cell state names; no ordered colorbar. | `FAIL`, `UNKNOWN`, `CANNOT CHECK`, `NULL`, `ADVERSE`, and `MIXED` remain explicit. |
| `02_p1_hidden_shift_forest` | Estimate the paired hidden-shift success difference between ORION and each comparator. | 480 paired cases per comparator; ORION minus comparator success-rate difference. | Percentage-point x-axis includes zero; receipt-reported 95% paired-bootstrap intervals and values are printed. | Intervals describe numeric uncertainty only; external authority is not encoded. |
| `03_p1_cost_success_pareto` | Inspect the observed budget/success trade-off among registered arms. | One arm-level mean budget and protected-root success rate. | Full success-rate context includes zero; observed points are not joined; black outline marks nondomination only within the displayed grid. | Every coincident arm is named; the figure states that external authority remains `CANNOT CHECK`. |
| `04_p2_retrieval_rates` | Compare Recall@100 and nDCG@10 without treating them as the same quantity. | One 50-topic macro rate per arm and metric. | Two aligned dot panels, each fixed to 0-1; exact values are printed. | Overall `FAIL` and its recall-interval/cost reasons are printed; nDCG cannot rescue the frozen gate. |
| `05_p3_accuracy_forest` | Compare exact 32-case accuracy and interval width across full systems and ablations. | Correct cases out of 32; Wilson 95% interval. | Fixed 0-1 accuracy axis; human labels and `k/32 [CI]` values. | Uniform marks mean one bounded receipt, not external authority or differing authority uncertainty. |
| `06_p6_p7_formal_counts` | Compare event-class counts while retaining the donor-multiplied magnitude range. | Enumerated formula events in the separate P6/P7 finite receipts. | Side-by-side bars on a disclosed log-count axis; counts are printed; categories are neutral event types. | Identical totals are not called replication; P7's separate 738/736 invalid programme execution is printed. |
| `07_p11_delta_ecdf` | Read the cumulative distribution of compiled-minus-universal query deltas. | Thirty registered query-level balanced-accuracy differences. | Percentage-point ECDF with every observation as a rug and a zero reference. | Title retains terminal `GATE_NOT_MET`; positive direction is explicit. |
| `08_p11_delta_strip` | Inspect every raw P11 query delta and the extreme negative tail without smoothing. | Same thirty registered query deltas, sorted only for display. | Raw dot plot in percentage points; no KDE or inferred continuous density. | Negative/non-positive observations are retained and visually distinct; view is descriptive. |
| `09_p12_family_blocks_by_sigma` | Check whether the bounded complementarity gain persists across registered noise strata and family blocks. | Thirty-two independent family RNG blocks, eight per sigma stratum. | All raw block deltas plus stratum means; mean labels occupy a separate top annotation band; y-axis includes zero and registered 0.12/0.15 gates; no interpolating line. | The plot shows finite registered strata, not a continuous response curve or forward-time generalization. |
| `10_p13_three_objective_tradeoff` | Evaluate cost, verified correctness, and unsafe reuse together. | Five arm-level summaries from one bounded randomized finite-world receipt. | Cost × correctness scatter; unsafe-reuse rate is both color-coded and printed; black outline is three-objective nondomination; correctness axis is explicitly 0.90-1.00. | Unsafe reuse cannot disappear behind a favorable 2D projection; population safety and external authority are explicitly disclaimed. |
| `11_p14_governance_rates` | Compare the three common governance rates while preserving their opposite desirable directions. | Five arms on 28 internally authored specification-separated cases; receipt-reported rates. | Three 0-1 dot panels with padded endpoints so markers at exactly 0 or 1 remain whole; each title states higher- or lower-is-better; no shared desirability palette. | False promotion is not visually rewarded; absent intervals and missing external adjudication are stated. |
| `12_p15_workflow_matrix` | Distinguish successful lifecycle/replay checks from scientific-contract and claim-authority checks. | One categorical state per workflow × gate. | Fixed workflow order; concise human row labels; full `PASS`/`CANNOT CHECK` cell text. | Title uses the exact `AUTHORIZED_SCIENCE` receipt disposition and a footer states that it is not publication or external authority; the fourth workflow remains `CANNOT CHECK`. |
| `13_des_execution_coverage` | Separate activity from valid frozen-scope execution across #1332 without comparing heterogeneous absolute denominators. | One planned/observed/valid triple per DES packet in that paper's own registered unit. | Each row normalizes only to its own planned denominator; nested bar thickness and exact `valid/observed/planned` labels distinguish the three quantities. | The title says “not performance”; P4 mechanical execution and P7 invalid generation remain visibly different from valid coverage; all external states remain `CANNOT CHECK`. |
| `14_framework_mechanics_receipts` | Explain why four core computations are internally coherent while retaining information-loss and censoring boundaries. | Separate terminal/action state counts, mutation detection fractions, projection terminal counts, and census classification counts. | Four facets retain separate axes and denominators; heatmap shading is explicitly `log(1+count)`, exact counts are printed, and classification is a 100% composition bar. | Zero law failures does not erase census residuals; exact projection replay does not erase noninjectivity; the title limits all panels to finite internal receipts. |

## Final-size review checklist

For every PNG and SVG, approval requires all of the following:

1. title, axis quantities, units, and direction cues are readable;
2. no tick label, data label, legend, point, interval, or footer overlaps;
3. numeric axes include an honest reference or explicitly disclose a zoom/log
   transform;
4. colors do not reverse desirability or carry meaning without text/shape;
5. adverse, null, failed, not-authority, and `CANNOT CHECK` outcomes remain
   visible; and
6. the SVG retains editable text and the PNG remains legible at intended display
   size.

The interactive atlas is presentation-only. Desktop and narrow-width inspection
must confirm that controls wrap, the source table retains a readable minimum
width with horizontal scrolling, digests remain intact, and exact metrics are
never pooled across units.

## Inspection record — 2026-08-26

- **Static PNGs:** all 15 were opened and inspected individually at original
  resolution after their final render. Titles, labels, axes, notes, marks, and
  adverse-state encodings passed the checklist above. The inspection directly
  triggered repairs to framework arrowheads, P1 annotations, P2/P14 footers,
  P6/P7 labels, misleading frontier legends, and the initial DES-coverage legend
  collision before the final pass.
- **Static SVGs:** the deterministic checker confirms editable text and matching
  file coverage; the PNG inspection is the rasterized final-size visual check.
- **Notebook figures:** all six default notebooks were executed; every default figure was captured,
  and visually inspected. The formal metric matrix was transposed to eliminate
  long-label collisions. The flagship explorer now directly labels methods and
  fixes rate axes to 0-1; the P13 unsafe-reuse explorer uses horizontal labels,
  an explicit lower-is-better direction, and the full 0-1 rate scale. The
  anomaly view now maps each paper to its exact retained label instead of
  drawing fourteen nearly identical count bars. Raw-value/ECDF views replaced
  the density display. The new DES notebook retains planned/observed/valid
  coverage, exact denominators, zero-valid markers, finite collision counts,
  mutation fractions, projection counts, and the censored census residual.
- **Interactive HTML:** the self-contained source and responsive CSS/JavaScript
  contract was inspected in a browser at desktop and 390-pixel mobile widths.
  Controls fit and stack vertically at the narrow width; their mobile position
  is non-sticky so the tall control stack cannot cover plot rows. A review-detected
  overflow from the unbroken authority-boundary token was repaired with explicit
  wrapping; at a 390-pixel viewport the document scroll width is now exactly 390
  pixels. The source-table wrapper is approximately 328 pixels wide while the
  expanded 43-source table retains an approximately 1,913-pixel scroll width;
  SHA cells remained on one line, and horizontal scrolling exposed every
  column. The full mobile page is approximately 9,595 pixels high after adding
  the DES section and expanded source inventory. All 15 DES bars and their
  exact labels remained inside their rows. Humanized labels, signed diverging
  bars, source paths, and digests remained readable. The regenerated P15 matrix
  was also inspected at
  original resolution: its three-line title, exact `AUTHORIZED_SCIENCE`
  disposition, external-authority disclaimer, row labels, and cell text were
  fully visible without overlap or clipping.

## Automated source-preflight interpretation

The generic single-file figure validator was run against
`visualization/scripts/render_all.py`. It parsed the source and passed the
font-size floor, color-map, sampling, exclusion, synthetic-data, uncertainty,
and backend checks. Its remaining export/font findings are cross-file or
delivery-scope findings rather than hidden plot repairs:

- publication-safe sans-serif fallbacks, editable SVG text, PDF type-42 text,
  and 300-dpi PNG previews are configured in the shared style/export module;
- `render_all.py` intentionally delegates saving to that module, so the
  single-file scanner cannot discover the dynamic `.svg`/`.png` paths;
- the atlas currently delivers editable SVG plus 300-dpi PNG, not PDF/TIFF.
  PDF/TIFF packaging and exact physical width remain **unresolved until an
  exact journal, article type, and submission stage are selected**;
- the log-count panel now asserts strictly positive counts before applying the
  logarithmic axis; and
- the only rotation warning was a zero-degree tick setting, which was removed.

These static checks do not replace the individual rendered-image inspection
recorded above and do not add scientific authority.

# ORION P1-P15 evidence atlas

The `visualization/` package turns repository receipts into an inspectable map of
the ORION framework, algorithms, bounded results, anomalies, and claim
boundaries. It is designed for two audiences:

- a human reader who wants diagrams and plots that explain how the P1-P15
  components connect; and
- an auditor who needs every displayed value and adverse outcome to remain
  traceable to committed source bytes.

The atlas is deliberately **not** a portfolio score or an acceptance/readiness
dashboard. P1-P15 use different evidence units and gates. `FAIL`, adverse, null,
`UNKNOWN`, `CANNOT_CHECK`, `GATE_NOT_MET`, `NOT_AUTHORITY`, and not-executed
results are retained rather than averaged away.

## Directory map

```text
visualization/
  README.md                         this guide
  source_catalog.json               declared receipt inputs
  data/
    derived/atlas.json              normalized, receipt-derived rows
    manifests/                      input byte/digest bindings
  src/orion_visualization/          reusable I/O, transforms, plots, styles, diagrams
  scripts/
    build_data.py                   source extraction and normalized-atlas build
    render_all.py                   deterministic, estimand-matched static figures
    build_dashboard.py              self-contained interactive HTML atlas
    build_all.py                    complete build and output-manifest orchestration
    make_notebooks.py               deterministic stdlib notebook generator
    execute_notebooks.py            dependency-light offline notebook execution
    validate_sources.py             CHECKED/DRIFT/CANNOT_CHECK source validation
    check.py                        read-only reproducibility/validation checks
  notebooks/
    00_framework_overview.ipynb
    01_p1_p5_flagships.ipynb
    02_p6_p10_formal_structured.ipynb
    03_p11_p15_state_governance_harness.ipynb
    04_anomaly_audit.ipynb
    05_frozen_des_execution.ipynb
  figures/
    static/                         15 deterministic PNG/SVG reference figures
    interactive/evidence_atlas.html offline filterable presentation artifact
  generated/manifests/             output byte/digest binding
  reports/
    CLAIM_CEILINGS.md               permitted and prohibited interpretation
    ANOMALY_AUDIT.md                anomaly explanations and next discriminators
    FIGURE_QA.md                    purpose, estimand, scale, and visual-QA contract
  tests/                             hand-checkable library and schema tests
```

Generated directories may be absent before the first data/figure build. The
committed source catalog and source receipts—not a notebook's in-memory
objects—define the scientific inputs.

The generated atlas and source manifest identify that input snapshot with a
canonical SHA-256 over source IDs, paths, schemas, byte counts, and exact source
digests. They deliberately do not embed the current Git `HEAD`/tree or local
package versions: those values are self-referential or machine-dependent when
placed in an exactly compared committed output.

## Build from the repository root

Use the repository's configured Python environment. The complete build needs
NumPy and Matplotlib (the repository's `plots` extra); the data and notebook
generators themselves use only the standard library. The data builder reads
only declared local repository sources.

```bash
uv run --extra plots python visualization/scripts/build_all.py
uv run --extra plots python visualization/scripts/check.py
uv run --extra plots pytest -q visualization/tests
```

`make_notebooks.py` uses only the Python standard library and deterministically
writes the six notebook JSON files. Notebook runtime cells expect matplotlib
and add `visualization/src` to `sys.path`. Static-figure tooling may use the
scientific packages already declared by the repository.

To verify that regeneration is stable, run the check script after rebuilding.
The check must not mutate committed outputs; it rebuilds in a temporary area and
compares the normalized data and presentation artifacts.

## Open and interact

Start Jupyter from either the repository root or `visualization/notebooks/`:

```bash
python3 -m pip install -r visualization/requirements-jupyter.txt
python3 -m jupyter lab visualization/notebooks
```

Each notebook locates `visualization/data/derived/atlas.json` from either start
location. Cells tagged `parameters` expose editable paper, exact-metric, status,
row-limit, and display-threshold selectors. Edit a selector and rerun the cells
below it. Display thresholds affect only the visible subset; terminals and the
unfiltered anomaly count remain unchanged.

### Notebook sequence

1. **Framework overview** — typed-state/non-escalation theory, exact status
   membership heatmap, paper-state table, and cross-paper authority discussion.
2. **P1-P5 flagships** — one-metric-at-a-time raw-value and ECDF views, with
   the P2 overall-fail and P5 model-identity anomalies retained.
3. **P6-P10 formal/structured** — finite-certificate and replay methodology,
   binary evidence-presence heatmap, and the P7/P9/P10 failure boundaries.
4. **P11-P15 state/governance/harness** — support, forward-time, corruption-world,
   external-authority, and signature-boundary views.
5. **Anomaly audit** — filterable anomaly inventory with exact counts and the
   mandatory P2, P5, P7, P9-P15 findings.
6. **Frozen DES execution** — the #1332 P1-DES-01 through P15-DES-01 planned,
   observed, and valid-coverage layer, plus finite collision, update-algebra,
   projection, and source-census mechanics. Coverage is normalized only within
   each paper's own unit and is never treated as performance or authority.

Plots intentionally avoid pooling incompatible measurements. An ECDF is created
only for one exact selected metric; categorical heatmaps are labelled as binary
presence/status displays, not performance scales. Read
[`reports/FIGURE_QA.md`](reports/FIGURE_QA.md) for the purpose, estimand, and
scale contract of every static figure.

## Offline operation

No notebook cell, data build, or report requires a web request. After the
repository and its Python environment are present, disconnecting the network
does not change the data source: all inputs come from local paths listed in
`source_catalog.json`. The notebooks do not download data, fonts, JavaScript, or
model outputs. Any HTML artifact must embed its required styling/data and must
not acquire stronger authority merely because it is interactive.

If a declared source is missing or has drifted, the correct response is a
failed integrity check or an explicit unresolved status—not a network fetch or
an imputed value.

The frozen DES layer is intentionally distinct from the paper-specific bounded
studies used elsewhere in the atlas. A DES packet may report mechanical or
preflight activity while its scientific result remains invalid, unscored, or
`CANNOT_CHECK`; the notebook and figure therefore keep `planned`, `observed`,
and `valid` as three separate quantities.

## Evidence and authority boundary

The atlas supports statements of the form:

> The cited repository receipt records this value, status, or finite outcome at
> its registered scope.

It does **not** independently establish:

- correctness of the underlying scientific claim;
- external/independent validation;
- broad generalization or superiority;
- novelty or priority;
- production reliability or secure key custody; or
- specialist, top-tier, or journal submission readiness.

SHA-256 and byte counts have `bytes_only` integrity scope. Passing repository
tests, a clean replay, GPU visibility, a finite certificate, or a valid
signature must never be promoted into scientific or external authority. Read
[`reports/CLAIM_CEILINGS.md`](reports/CLAIM_CEILINGS.md) before quoting a figure
and [`reports/ANOMALY_AUDIT.md`](reports/ANOMALY_AUDIT.md) before interpreting a
favorable-looking metric.

## Adding a visualization safely

1. Add the source receipt to `source_catalog.json` with an exact path and scoped
   extraction declaration.
2. Extract only explicit receipt fields; preserve JSON `null` and exact status
   strings.
3. Put reusable scientific transforms in `src/orion_visualization/`, with tests.
   Do not hide a scientific transform only inside a notebook.
4. Bind the source bytes/digest and label the evidence unit and denominator.
5. Choose a plot whose geometry matches the estimand; do not mix units merely
   to obtain a denser dashboard.
6. Add adverse and missing-authority interpretations to the anomaly report.
7. Regenerate and run the complete check before treating the figure as current.

When a stronger conclusion is desired, the remedy is a newly frozen,
identity-bound experiment or external review—not a different color scale.

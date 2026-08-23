# Q/QG rendered-artifact visual audit V1

Date initialized: 2026-08-21
Status: `PENDING_ARTIFACT_INSPECTION`

A successful LaTeX/figure build is not a visual audit. This ledger remains fail-closed until the exact workflow artifacts are inspected. No package may use `TECHNICALLY_GREEN` merely because its build completed.

## Audit rules

For each PDF, inspect **every rendered page** from the workflow artifact, not a local re-render with different dependencies.

For every page record:
- page index;
- clipping: pass/fail;
- overlap: pass/fail;
- missing/broken glyphs: pass/fail;
- table width/readability: pass/fail;
- equation/code readability: pass/fail;
- citation/reference rendering: pass/fail;
- pathological heading/page break: pass/fail;
- identity/anonymity where applicable;
- notes.

For figures, inspect each authoritative V2 PNG/SVG:
- label readability at intended width;
- clipping/overlap;
- axis direction/scale meaning;
- exact numeric agreement with `source_data.json`;
- caption evidence class/denominator agreement;
- no color-only semantics;
- no visually implied stronger claim than the manuscript.

A repair that changes scientific prose/data invalidates the prior scientific/package checks and must re-run them. A layout-only target-wrapper repair does not change scientific authority but requires a new exact rendered audit.

## Required artifact identities

### Q1 / Quantum preflight
Workflow: `q1-qg2-quantum-preprint`
Artifact: `q1-qg2-quantum-preprint-packages`
Subtree: `Q1/`

Current audit terminal: `PENDING_ARTIFACT_INSPECTION`

### Q2 / AIJ preflight
Workflow: `q2-aij-package`
Artifact: `q2-aij-preflight-package`

Current audit terminal: `PENDING_ARTIFACT_INSPECTION`

### Q4 / TMLR review package
Workflow: `q4-tmlr-package`
Artifact: `q4-tmlr-review-package`

Mandatory additional check: anonymous source/PDF must expose no author identity.

Current audit terminal: `PENDING_ARTIFACT_INSPECTION`

### QG1 / PRX Quantum preflight V2
Workflow: `qg1-prx-preflight-v2`
Artifact: `qg1-prx-preflight-v2-package`

The older `qg1-prx-preflight` two-column assertion is development history only and carries no visual/package authority.

Current audit terminal: `PENDING_ARTIFACT_INSPECTION`

### QG2 / Quantum preflight
Workflow: `q1-qg2-quantum-preprint`
Artifact: `q1-qg2-quantum-preprint-packages`
Subtree: `QG2/`

Current audit terminal: `PENDING_ARTIFACT_INSPECTION`

### Publication figures V2
Workflow: `q-qg-figures-v2`
Artifact: `q-qg-publication-figures-v2`
Required: 12 standalone PNG + 12 SVG.

Current audit terminal: `PENDING_ARTIFACT_INSPECTION`

## Completion record template

Fill one block per artifact only after exact inspection:

```text
workflow_run_id:
workflow_job_id:
artifact_id/name:
source_head_sha:
pdf_or_bundle_sha256:
rendered_pages_total:
pages_inspected_total:
figure_files_inspected:
visual_defects:
identity/anonymity_result:
reference_rendering_result:
final_visual_terminal: PASS | FAIL | CANNOT_CHECK
inspector_notes:
```

## Final package rule

A content-ready paper can become:

`PACKAGE_TECHNICALLY_GREEN__AUTHOR_INPUT_PENDING`

only if:
1. current-head publication/science/reference/package routing checks pass;
2. exact target/preflight source and PDF build pass;
3. exact rendered PDF pages pass this audit;
4. any included V2 publication figures pass this audit;
5. no unresolved citation or author-identity leak exists.

`SUBMISSION_PACKAGE_READY` additionally requires the author-controlled fields in `Q_QG_AUTHOR_INPUT_REQUIRED_V1.md` and a final rebuild/re-audit after those values are inserted.

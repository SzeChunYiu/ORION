# ORION-14 independent claim / PDF audit

Audit subject: `b7cfaecfb55d9ad6c12fb59374935769ed8d8787`. Not a #283 verification record.

| ID | Claim | Artifact | Status |
|---|---|---|---|
| ORION-14.H1 | 0/360 vs 180/360 false promotions; effect -0.50, CI [-0.553,-0.447] | `evidence/protected_v2/PUBLICATION_METRICS_V2.json` | SUPPORTED |
| ORION-14.H2 | 60/60 clean promotions both systems | same | SUPPORTED |
| ORION-14.H3 | Superior correct `CANNOT_CHECK` | same (`hypotheses.H3.status`) | **NOT_SUPPORTED** |
| ORION-14.PDF | Independent final proofread of the current in-tree PDF | no independent proofread artifact | **OPEN** |

H3 remains a retained null. The paper-declared terminal `PEER_REVIEW_READY` is recorded but this package stays `SCAFFOLDING` until an in-tree or DOI-bound PDF is present. Release SHA `f2ede371…3ccf` is identity evidence for a remote artifact, not a tracked file this checker can hash.

## Addendum, 2026-08-22 — ORION-14.H3 moved off a saturated axis

The table above is the audit as it stood at `b7cfaec…`, and its rows are not
restated. Two things about the `ORION-14.H3` row have since been established, and the
manifest now reads differently from it.

**The row's null was not a finding.**
`evidence/audit/P4_PANEL_RESOLUTION_2026-08-22.json` reports, for the V2 panel,
`decided_on: correct_cannot_check_rate`, `metric_resolution: SATURATED`,
`declared_ci95: [0.0, 0.0]`, `verdict_could_have_differed: false`, and lists H3
under `hypotheses_settled_before_any_system_ran`. All eleven systems scored 1.0.
The verdict records the benchmark, not the systems. It is retained in the
manifest as `ORION-14.H3.V2`, still `NOT_SUPPORTED`, because that is what the V2
construction produced.

**A measurement that could have come out either way now exists.**
`evidence/protected_v3/` holds it: `FREEZE.md` written before the construction
was repaired and before any panel outcome was seen, `IDENTIFIABILITY_V3.json`
written before the panel ran, then `PANEL_V3.json`. On that battery H3 is
`SUPPORTED` at 1.0, CI95 [1.0, 1.0] — ORION 30/30 correct `CANNOT_CHECK`, 0/360
false promotions, against 0/30 for the H1-selected comparator
`provenai-citation-fidelity-influence`. **`deepsciverify-abstract-to-full-escalation`
scores 15/30, so against it the margin is 0.5**, and both numbers belong in any
sentence about H3.

What that measures was fixed in `FREEZE.md` §5 before the panel ran: terminal
expressiveness under a non-compensatory gate lattice — the ability to report an
inability — and not a finer-grained scientific judgement. Nine of the ten
comparators score 0 because they cannot emit `CANNOT_CHECK` at all. The score is
quotable because the exact V3/`CANNOT_CHECK` claim axis clears at informedness
0.0 over fourteen probes and thirteen seeds; the same register reports 1.0 on
the V1 and V2 constructions. Four digest-prefix noise-control residuals on the
off-claim `BLOCK`/`PROMOTE` axes remain disclosed; this is not a whole-register
pass.

This addendum is not a new independent audit. `audit_subject_revision` and
`audit_date` in `MANIFEST.json` are unchanged, and `ORION-14.PDF` remains **OPEN**.

The V2-scoped documents around this package are left as they are, on purpose.
`JOURNAL_READINESS.md` is a frozen V2 integrity input — `tests/unit/p4/test_partial_evidence_acquisition_v2.py`
pins its digest — so its gate table still reads `H3 … NOT_SUPPORTED`, which is
the correct record of the V2 campaign it certifies, and it is not annotated here
or anywhere. The same applies to `evidence/protected_v2/` and
`protocol/PROTECTED_RUN_BINDINGS_V2.json`.

## Addendum, 2026-08-24 — an in-tree PDF exists

`manuscript/main.pdf` is now a tracked, hash-bound compiled PDF:

| Field | Value |
|---|---|
| Source revision | `d4cf8c09c128c0b0331b96b45385c35a96b9427e` (main.tex and all `\input` sections unmodified from HEAD at render time) |
| SHA-256 | `7a6b5182480a6bd89eca05c6ace33501db22ee049119bfd1cd5da56a1ea3be6c` |
| Pages | 26 |
| Engine | tectonic (XeTeX; PDF producer xdvipdfmx 0.1) |

**Engine honesty.** This is a local tectonic/XeTeX render, not the CI artifact:
`.github/workflows/p4_tmlr_submission_audit.yml` compiles clean-room with
latexmk/pdflatex against upstream-pinned `tmlr.sty`/`tmlr.bst`. The tracked PDF
therefore establishes that the committed sources compile end-to-end and what
they render to under one engine; it does not establish bit-identity with the CI
PDF (TeX engines are not bit-reproducible across engines), and it is not a
substitute for a green clean-room compile. The `tmlr.sty`/`tmlr.bst` files are
vendored in `manuscript/` (tracked), which is what made the local render
possible; `COMPILE.md` is corrected accordingly.

**Content audit (programmatic, 2026-08-24).** `pdftotext` extraction of the
rendered PDF confirms: TMLR under-review front matter and title; abstract and
keywords; all eleven section sources render (introduction through ablation
interpretation); the `submission/P4_X_PROMOTION_AUTHORITY_SECTION.tex` successor
section ("Post-saturation successor: donor-complete scientific-promotion
authority") is included; headline figures `0/360` vs `180/360` false promotions
and the `30/30` correct-`CANNOT_CHECK` contrast appear in abstract, findings and
results. The string "SciFact" does not appear in the manuscript — correct, since
`protocol/SCIFACT_LABEL_STATE_MAP_V1.json` is a frozen pre-scoring protocol
artifact, not a manuscript claim; its absence is recorded here so nobody reads
the PDF as covering it.

**What this does not establish.** This is a render and a mechanical content
audit by the same session that packaged it — not an independent proofread. The
`ORION-14.PDF` claim above stays **OPEN** until an independent final proofread of this
exact file (by hash) is recorded. `audit_subject_revision` and `audit_date` in
`MANIFEST.json` are unchanged; the render binding lives in
`MANIFEST.json` under `pdf_render_binding`.

## Addendum, 2026-08-24 (second) — abstract-carrier restoration re-render

Integration commit `6474c521` rewrote the abstract to the identifiability
framing and compressed the H3-v3 result to a qualitative clause, dropping the
`$[1.0,1.0]$` carrier paragraph that
`tests/unit/p4/test_p4_h3_v3_promotion.py::test_the_manuscript_never_reports_the_margin_without_the_other_one`
binds (the abstract must state the repaired-battery interval together with the
15/30 and the $0.5$ margin, as the introduction findings list and the results
section already did). The commit touched no test files; the drop was collateral
damage of the abstract rewrite, not a reconciled removal. This re-render
restores the pre-`6474c521` abstract sentence (both margins, pre-registered
terminal-expressiveness reading) inside the new abstract.

| Field | Value |
|---|---|
| Source revision | `abfc846a61a1596309a7ebc0ac38e579aa0f333f` (manuscript/main.tex carries the restored carrier; all other `\input` sections unmodified from `93cf5f41`; commit rebased without content change from the pre-rebase render revision, `main.tex` sha256 unchanged at `df0010d0afe449dd980524776ca8154b52eded6c3970469baf93c1fd1451ed20`) |
| SHA-256 | `2d3841da6c0a70b169dcaf162fb126fc0e1b0c9c54d0a15fd897744239644f71` |
| Pages | 26 |
| Engine | tectonic (XeTeX; PDF producer xdvipdfmx 0.1) |

**Content audit (programmatic).** `pdftotext` extraction of this render
confirms the abstract now carries "paired difference 1.0, 95% CI [1.0, 1.0]"
together with "selects it on 15/30, so the margin against that mechanism is
0.5" in the same paragraph. Page count is unchanged at 26. The engine-honesty
and independence caveats of the first addendum apply unchanged: local tectonic
render, same-session mechanical audit, `ORION-14.PDF` stays OPEN pending an
independent proofread of this exact file (by hash).

The local 26-page render and same-session mechanical audit are recorded separately as `ORION-14.LOCAL_RENDER` = **BOUNDED**. They do not satisfy `ORION-14.PDF` or create a submission package.

## Addendum, 2026-09-01 — pinned clean-CI render reconciliation

The repository's clipping gate rebuilt every working manuscript from the same
source under its pinned Ubuntu 24.04 / TeX Live 2023 environment. The resulting
ORION-14 PDF is the current tracked working render:

| Field | Value |
|---|---|
| Source revision | `ae693283365d6b7c0129e7122ce9c6f5a7ac03d3` |
| Workflow run | `33463297400` |
| Artifact ID | `9783994917` |
| SHA-256 | `76c9a0c43d2e53bceff04f1397fbe2cceb1427b16240bb5c0a6c6b3478445ea1` |
| Pages | 28 |
| Engine | pdfTeX-1.40.25 via latexmk 4.83; pinned Ubuntu 24.04 TeX Live 2023 |

The two-page layout difference from the retained 26-page tectonic render is an
engine/layout effect. The historical manifest named the tectonic render SHA
`2d3841da...`, while the tracked PDF immediately before this reconciliation and
its checksum record named `216d2d5a...`; that pre-existing mismatch is retained
explicitly in the manifest history rather than normalized away. No manuscript
source, claim, table, evidence artifact, negative result, or authority record
changed in this reconciliation. The prior manifest and checksum records remain
under `journal_package/history/`. This is still a programmatic same-project
render audit, not an independent proofread: `ORION-14.PDF` remains **OPEN**.

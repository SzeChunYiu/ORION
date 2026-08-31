# Readiness, re-derived from executable gates

The earlier green/amber/red table in this session was built by reading manuscripts. This one is built from what the repository's own checkers return, plus binding state and rendered-PDF facts. Where the two disagree, this one is correct.

## What the checkers return on `main`

| paper | checker | result | qualifier |
|---|---|---|---|
| ORION-06 | `check_transition_graph.py` | runs | `SCIENTIFIC_CAUSALITY_AUTHORITY=NOT_GRANTED_BY_VALIDATOR` |
| ORION-07 | `check_q3_completion.py` | `PASS` | `AGGREGATE_RELIABILITY_AUTHORITY=FALSE` |
| ORION-07 | `check_q3_result_bindings.py` | `PASS` | both replacement results sha-bound |
| ORION-21 | `check_p11_adverse_integration_v2.py` | `PASS` | `scientific_authority_delta: BOUNDARY_NARROWING_ONLY` |
| ORION-22 | `check_p12_lifecycle_integration_v4.py` | `PASS` | **`top_tier_submission_allowed: false`** |
| ORION-22 | `check_p12_stopgo_integration_v1.py` | `PASS` | `scientific_authority_delta: NONE` |
| ORION-23 | `check_p13_p14_pinned_corpus_v1.py` | freeze intact | 45 repos / 22 orgs, no ORION subject |
| ORION-23 | `check_lifecycle_consolidation_binding_v1.py` | `PASS` | `population_inference: false` |

Every checker passes. **Passing is not readiness.** Each carries a qualifier that bounds what the paper may claim, and two of them bound it hard: ORION-22 may not be submitted to a top-tier venue at all, and ORION-23 supports an internal panel with no population inference.

## Blockers, by kind

Grouping by what would actually unblock each paper matters more than a colour.

**Locked by their own protocol (needs new science, not packaging)**
- ORION-22 --- `top_tier_submission_allowed` is asserted false; the checker fails if flipped. Needs a bound public-data benchmark result.

**Blocked by the V1 freeze (needs a policy decision)**
- ORION-16, -20, -21, -22, -23 --- `manuscript/main.tex` bound in a frozen `BOUND` manifest. Carries unfixable first-page defects: three of them name themselves by catalogue number in the abstract.

**Blocked by a render constraint (needs diagnosis)**
- ORION-17, -18 --- re-rendering degrades a reproducibility target from `BOUND` to `PARTIAL`. Source fix is available and unmerged; neither route is an implementer's call.

**No LaTeX source at all (needs authoring)**
- ORION-01, -02, -04 --- cannot be built or edited.
- ORION-25 --- has `main.tex` but zero section files.

**Curated artifact (do not re-render)**
- ORION-05 --- committed PDF is deliberately de-identified and differs from source by design. Guarded by `test_render_path_respects_curated_pdfs.py`.

**Open on packaging only**
- ORION-06, -07, -08, -09, -10, -11, -12, -13, -14, -15 --- rendered front matter is clean, no internal codes, no anonymity conflicts. Remaining work is bibliographic depth and venue metadata.

## The correction this table makes

The earlier table put ORION-22 in the packaging queue. It cannot be packaged into readiness --- the flag is enforced, and editing it breaks the checker that guards it. It also treated ORION-07 as blocked on evidence when its gate had already passed.

Both errors have the same cause: readiness was inferred from prose. Prose is the right instrument for finding a leaked code or a placeholder author, and the wrong one for an evidence gate. Where a paper states its status in code, that statement is authoritative.

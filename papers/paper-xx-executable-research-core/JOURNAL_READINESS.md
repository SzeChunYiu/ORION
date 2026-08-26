# ORION-19 merged-evidence readiness — 2026-08-18

ORION-19 is **peer-review ready as a merged ORION-18/programme evidence object**, not as a
standalone paper.

| Gate | Receipt | Status |
|---|---|---|
| Exact public source | ASlib commit, six immutable source files and SHA-256 protocol | `PASS` |
| Outcome-blind protocol | Protocol commit precedes public outcome run | `PASS` |
| Leakage control | Scenario outer folds; inner-only threshold selection; training-only imputation | `PASS` |
| Public result | JSON/Markdown generated from one in-memory result | `PASS` |
| Determinism | Two complete runs; JSON SHA-256 `8246d007260be1bc5df437002c1de004bc98868edd114b29c3ffb22046532f06` both times | `PASS` |
| Hostile tests | Digest substitution, source shape and numerical-gate assertions | `PASS` (3/3) |
| Framework tests | Capability/authority, donor, ledger, planner and content-binding suite | `PASS` (33/33 on closure branch) |
| Constructive saturation | Eight primary donors, each with extraction plus adoption/defer receipt | `PASS_BOUNDED` |
| Strong configured selector | AutoFolio-class comparison | `NOT_RUN`; blocks standalone superiority only |
| Independent standalone residual | Routing/abstention absorbed; authority separation owned by ORION-18 | `NO_RESIDUAL` |
| Terminal artifact | Claim ledger, merge disposition and ORION-18 companion | `PASS` |

## Reviewer-facing limit

The single ASlib scenario is a discriminator for a mechanism, not a general
benchmark claim. The failure-aware method pays higher mean PAR10 and lower solve
rate than the non-abstaining RF router because abstentions count as PAR10. Its
supported result is a bounded attempt/retention trade-off. It does not establish
algorithm-selector superiority, transfer, correctness or authority.

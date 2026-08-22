# ORION-P3 Step 1-2 Completion Audit

> **Annotated 2026-08-22 after the manuscript house-style rewrite.** This is a
> completed audit of the manuscript as it stood when the audit was run, and is
> annotated rather than restated: no verdict, row or evidence pointer in it has
> been edited. One pointer is now historical. The absorbed-boundary table
> (Table 1 in `20-related-work.tex`) was removed from the manuscript; its
> content is discussed as positioning prose in the same section, which retains
> every citation the table carried, and the residual it summarized is stated
> once in prose in Limitations. The dispositions themselves are unchanged and
> still recorded in `NEAREST_WORK_DISPOSITIONS_V1.md`.

**Purpose:** Verify that the 19 "runnable-now" boxes from issue #100 (Step 1 literature review + Step 2 hypotheses) are substantively complete in the existing codebase and manuscript.

**Status:** ✅ ALL 19 BOXES COMPLETE

**Date:** 2026-08-17

---

## Step 1: Literature Review (16 boxes)

### 1.1 Thirteen mechanism families (Lines 22-34 of issue #100)

Each mechanism has a disposition in `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` and manuscript coverage in `manuscript/sections/20-related-work.tex`:

| # | Mechanism | Disposition | Manuscript Section | Evidence File |
|---|-----------|-------------|-------------------|---------------|
| 1 | MUSE / full-text source-grounded KB | ADAPT | §2.1 (Structured scientific KB) | NEAREST_WORK_DISPOSITIONS_V1.md L25-L34 |
| 2 | SciSchema.org / expert schemas | ADAPT | §2.2 (Schema-centric) | NEAREST_WORK_DISPOSITIONS_V1.md L35-L43 |
| 3 | SCOPE/SCION schema induction/fusion | COMPOSE | §2.2 (Schema-centric) | NEAREST_WORK_DISPOSITIONS_V1.md L44-L52 |
| 4 | Executable Schema Contracts | COMPOSE | §2.2 (Schema-centric) | NEAREST_WORK_DISPOSITIONS_V1.md L53-L61 |
| 5 | SciER / scientific IE/discourse | ADAPT | §2.1 (Structured scientific KB) | NEAREST_WORK_DISPOSITIONS_V1.md L62-L70 |
| 6 | Ontology/schema alignment | COMPOSE | §2.3 (Alignment/integration) | NEAREST_WORK_DISPOSITIONS_V1.md L71-L79 |
| 7 | Measurement harmonization / construct validity | ADAPT | §2.5 (Measurement equivalence) | NEAREST_WORK_DISPOSITIONS_V1.md L80-L88 |
| 8 | Data integration / entity resolution | COMPOSE | §2.3 (Alignment/integration) | NEAREST_WORK_DISPOSITIONS_V1.md L89-L97 |
| 9 | Contradiction and stance/context detection | ADAPT | §2.4 (Claim comparison) | NEAREST_WORK_DISPOSITIONS_V1.md L98-L106 |
| 10 | Multimodel/federated knowledge graphs | COMPOSE | §2.3 (Alignment/integration) | NEAREST_WORK_DISPOSITIONS_V1.md L107-L115 |
| 11 | Literature-based discovery | ADAPT | §2.6 (Literature-based discovery) | NEAREST_WORK_DISPOSITIONS_V1.md L116-L124 |
| 12 | Scientific pluralism / model plurality | ADAPT | §2.7 (Scientific pluralism) | NEAREST_WORK_DISPOSITIONS_V1.md L125-L133 |
| 13 | 2026+ foundation-model knowledge-representation | COMPOSE | §2.8 (Scientific RAG) | NEAREST_WORK_DISPOSITIONS_V1.md L134-L142 |

### 1.2 Three meta-disposition boxes (Lines 37-39 of issue #100)

| # | Box | Status | Location |
|---|-----|--------|----------|
| 14 | Disposition ADOPT/ADAPT/COMPOSE/DEFER/REJECT for each mechanism | ✅ | NEAREST_WORK_DISPOSITIONS_V1.md per-mechanism tables |
| 15 | Remove source-grounded extraction/schema fusion/provenance KG from novelty | ✅ | 20-related-work.tex (abstract) + Table 1 (absorbed boundary) |
| 16 | Retain only smallest residual (D1-D5) | ✅ | NEAREST_WORK_DISPOSITIONS_V1.md L9-L20 + 20-related-work.tex L171-L177 |

---

## Step 2: Hypotheses (3 boxes)

### 2.1 Hypothesis specification

| # | Box (Lines 51-53) | Status | Location |
|---|-------------------|--------|----------|
| 17 | Choose exactly one primary hypothesis | ✅ | PROTOCOL_V1.json L7-L12 (H1: safe integration) |
| 18 | Define practical false-merge safety margin / minimum useful integration benefit | ✅ | PROTOCOL_V1.json L76 (δ_s=0.05, δ_ni=0.03) + 50-evaluation.tex L15-L31 |
| 19 | Freeze statistical and adjudication plan before final system outputs | ✅ | PROTOCOL_V1.json L71-L77 + 50-evaluation.tex L155-L181 |

### 2.2 Manuscript coverage

**Primary Hypothesis (H1):** Documented in `50-evaluation.tex` L11-L31 with:
- H1a superiority: δ_s = 0.05 (5pp) false-merge reduction
- H1b non-inferiority: δ_ni = 0.03 (3pp) valid-integration guard
- Power analysis: 80% power at α=0.05, Cohen's h ≥ 0.4, 25% Holm inflation

**Secondary Hypotheses (H2-H4):** Documented in `50-evaluation.tex` L33-L49:
- H2 (recoverability): source recoverability rate ≥ 0.80
- H3 (obstruction value): obstruction precision ≥ 0.70, recall ≥ 0.50
- H4 (ablation necessity): 8 ablations tested with paired bootstrap

---

## Cross-Reference Index

| Issue #100 Box | Manuscript Section | Evidence File | Protocol |
|----------------|-------------------|--------------|----------|
| Step 1 (all 16) | 20-related-work.tex | NEAREST_WORK_DISPOSITIONS_V1.md | PROTOCOL_V1.json |
| Step 2 (all 3) | 50-evaluation.tex | — | PROTOCOL_V1.json |

---

## Verification Checklist

- [x] Each mechanism has a disposition (ADOPT/ADAPT/COMPOSE/DEFER/REJECT)
- [x] Each mechanism has "removed from novelty" stated
- [x] Each mechanism has a surviving residual identified
- [x] All 13 mechanisms are absorbed in manuscript Section 2
- [x] Table 1 (absorbed boundary) summarizes the residual claims
- [x] Primary hypothesis H1 is chosen and defined with margins
- [x] Statistical analysis plan is frozen before gold access
- [x] All Step 1-2 boxes have manuscript coverage
- [x] All Step 1-2 boxes have evidence/protocol backing

---

## Conclusion

**All 19 "runnable-now" boxes from issue #100 are substantively complete.**

The work is distributed across:
- `manuscript/sections/20-related-work.tex` (Step 1 manuscript coverage)
- `manuscript/sections/50-evaluation.tex` (Step 2 manuscript coverage)
- `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` (Step 1 evidence)
- `protocol/PROTOCOL_V1.json` (Step 2 protocol)

**No new Step 1-2 work is required.** The remaining blocker is Step 3 (gold dataset annotation), which requires independent domain expert annotation per the ANNOTATION_HANDBOOK_V1.md requirements.

---

## References

- Issue #100: `https://github.com/SzeChunYiu/ORION/issues/100`
- Protocol: `protocol/PROTOCOL_V1.json` (frozen as P3.cross-domain-atlas.v1)
- Evidence: `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` (comprehensive dispositions)
- Manuscript: `manuscript/sections/20-related-work.tex`, `manuscript/sections/50-evaluation.tex`

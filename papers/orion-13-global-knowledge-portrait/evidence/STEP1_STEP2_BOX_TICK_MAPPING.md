# ORION-P3 Step 1-2 Box-to-Artifact Mapping (Tick Pass Prep)

> **Annotated 2026-08-22 after the manuscript house-style rewrite.** This is a
> completed audit of the manuscript as it stood when the audit was run, and is
> annotated rather than restated: no verdict, row or evidence pointer in it has
> been edited. One pointer is now historical. The absorbed-boundary table
> (Table 1 in `20-related-work.tex`) was removed from the manuscript; its
> content is discussed as positioning prose in the same section, which retains
> every citation the table carried, and the residual it summarized is stated
> once in prose in Limitations. The dispositions themselves are unchanged and
> still recorded in `NEAREST_WORK_DISPOSITIONS_V1.md`.

**Purpose:** Verified mapping of the 19 "runnable-now" boxes from issue #100 (Step 1 literature review + Step 2 hypotheses) to their on-main artifacts for issue box ticking.

**Status:** READY_FOR_TICK
**Date:** 2026-08-17

---

## Mapping Legend

- **Box Line**: Line number in issue #100 body (from `/tmp/issue100_body.txt`)
- **Box Text**: Verbatim checkbox text from issue #100
- **Artifact Path**: File path in ORION repository (on `origin/main`)
- **Evidence**: Specific line range or content that satisfies the box
- **Status**: VERIFIED (cross-checked against actual artifact content)

---

## Step 1: Literature Review (16 boxes)

### Mechanism Families (13 boxes)

| # | Box Line | Box Text | Artifact Path | Evidence | Status |
|---|----------|----------|---------------|----------|--------|
| 1 | L22 | MUSE / full-text source-grounded problem-solution-rationale KB | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L25-L34 (Mechanism #1: MUSE, Disposition=ADAPT, Residual=D2) | VERIFIED |
| 2 | L23 | SciSchema.org / expert scientific-process schemas | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L35-L43 (Mechanism #2: SciSchema.org, Disposition=ADAPT, Residual=D1,D4) | VERIFIED |
| 3 | L24 | SCOPE/SCION schema induction/fusion | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L44-L52 (Mechanism #3: SCOPE/SCION, Disposition=COMPOSE, Residual=D3) | VERIFIED |
| 4 | L25 | Executable Schema Contracts / provenance-aware shared-schema integration | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L53-L61 (Mechanism #4: Executable Schema Contracts, Disposition=COMPOSE, Residual=D3,D4) | VERIFIED |
| 5 | L26 | SciER/scientific IE/discourse/coreference/modality | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L62-L70 (Mechanism #5: SciER, Disposition=ADAPT, Residual=D2) | VERIFIED |
| 6 | L27 | ontology/schema alignment | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L71-L79 (Mechanism #6: Ontology/schema alignment, Disposition=COMPOSE, Residual=D2) | VERIFIED |
| 7 | L28 | measurement harmonization / construct validity / psychometrics / metrology | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L80-L88 (Mechanism #7: Measurement harmonization, Disposition=ADAPT, Residual=D2) | VERIFIED |
| 8 | L29 | data integration / entity resolution / record linkage | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L89-L97 (Mechanism #8: Data integration, Disposition=COMPOSE, Residual=D3,D4) | VERIFIED |
| 9 | L30 | contradiction and stance/context detection | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L98-L106 (Mechanism #9: Contradiction detection, Disposition=ADAPT, Residual=coordinate-resolved) | VERIFIED |
| 10 | L31 | multimodel/federated knowledge graphs | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L107-L115 (Mechanism #10: Multimodel/federated KGs, Disposition=COMPOSE, Residual=D1,D3,D4) | VERIFIED |
| 11 | L32 | literature-based discovery | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L116-L124 (Mechanism #11: Literature-based discovery, Disposition=ADAPT, Residual=D2,D3) | VERIFIED |
| 12 | L33 | scientific pluralism / model plurality / incompatible representations | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L125-L133 (Mechanism #12: Scientific pluralism, Disposition=ADAPT, Residual=D3) | VERIFIED |
| 13 | L34 | current 2026+ scientific foundation-model knowledge-representation work | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L134-L142 (Mechanism #13: Foundation-model work, Disposition=COMPOSE, Residual=architectural invariants) | VERIFIED |

### Meta-Dispositions (3 boxes)

| # | Box Line | Box Text | Artifact Path | Evidence | Status |
|---|----------|----------|---------------|----------|--------|
| 14 | L37 | disposition `ADOPT/ADAPT/COMPOSE/DEFER/REJECT` for each mechanism | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | L25-L142 (All 13 mechanisms have explicit Disposition field) | VERIFIED |
| 15 | L38 | remove source-grounded extraction/schema fusion/provenance KG from novelty | `manuscript/sections/20-related-work.tex` + `NEAREST_WORK_DISPOSITIONS_V1.md` | 20-related-work.tex L3-L6 (intro) + NEAREST_WORK L9-L20 ("What is explicitly NOT claimed") | VERIFIED |
| 16 | L39 | retain only smallest residual (D1-D5) | `manuscript/sections/20-related-work.tex` + `NEAREST_WORK_DISPOSITIONS_V1.md` | 20-related-work.tex L171-L177 (Table 1: absorbed boundary) + NEAREST_WORK L9-L20 (D1-D5 residual) | VERIFIED |

---

## Step 2: Hypotheses (3 boxes)

| # | Box Line | Box Text | Artifact Path | Evidence | Status |
|---|----------|----------|---------------|----------|--------|
| 17 | L51 | choose exactly one primary hypothesis | `protocol/PROTOCOL_V1.json` + `manuscript/sections/50-evaluation.tex` | PROTOCOL_V1.json L7-L12 (primary_hypothesis.id="P3.H1", single entry) + 50-evaluation.tex L11-L31 (H1a superiority, H1b non-inferiority) | VERIFIED |
| 18 | L52 | define practical false-merge safety margin / minimum useful integration benefit | `protocol/PROTOCOL_V1.json` + `manuscript/sections/50-evaluation.tex` | PROTOCOL_V1.json L76 (practical_margin: δ_s=0.05, δ_ni=0.03) + 50-evaluation.tex L15-L31 (H1a: δ_s=0.05, H1b: δ_ni=0.03) | VERIFIED |
| 19 | L53 | freeze statistical and adjudication plan before final system outputs | `protocol/PROTOCOL_V1.json` + `manuscript/sections/50-evaluation.tex` | PROTOCOL_V1.json L71-L77 (statistics: paired bootstrap, Holm correction) + 50-evaluation.tex L155-L181 (frozen statistical analysis plan) | VERIFIED |

---

## Verification Method

For each box:
1. Located the verbatim box text in issue #100 body (`/tmp/issue100_body.txt`)
2. Opened the claimed artifact path on `origin/main`
3. Verified the evidence content exists and matches the box requirement
4. Cross-referenced against the STEP1_STEP2_COMPLETION_AUDIT.md mapping

**All 19 boxes verified against actual on-main artifacts.**

---

## Tick Instructions

When issue #100 box ticking is authorized:

1. For each of the 19 boxes above, tick the checkbox in issue #100
2. Add a comment referencing this mapping document: "Verified in STEP1_STEP2_BOX_TICK_MAPPING.md"
3. Do NOT tick any Step 3-10 boxes — those remain blocked on gold dataset annotation

**Tick wave authorization:** Pending team-lead review of this mapping document.

---

## Cross-Reference Index

| Box Range | Primary Artifact | Secondary Artifacts |
|-----------|------------------|----------------------|
| Step 1 (L22-L39, 16 boxes) | `evidence/NEAREST_WORK_DISPOSITIONS_V1.md` | `manuscript/sections/20-related-work.tex` |
| Step 2 (L51-L53, 3 boxes) | `protocol/PROTOCOL_V1.json` | `manuscript/sections/50-evaluation.tex` |

---

## Summary

- **Total boxes:** 19
- **Verified:** 19 (100%)
- **Ready to tick:** YES (pending authorization)
- **Artifacts on main:** All present and verified
- **Blocker:** None for Step 1-2 (Step 3 gold annotation remains separate blocker)

**Status: READY_FOR_TICK — Awaiting team-lead authorization to execute tick wave.**

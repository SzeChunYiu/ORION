# ORION-14 Wave-1 recursive review — Reviewer 3: reproducibility / reporting / clarity / boundaries

**Review type:** simulated independent pre-submission lens; not external peer review.  
**Frozen manuscript reviewed:** `6665ee4ea34553a5020e5f1c29ffa95d59c48cd4`.  
**Target under review:** TMLR.  
**Reviewer packet rule:** this report was prepared against the frozen manuscript and rendered-package state without using another simulated reviewer report.

## Overall posture

The repository contains unusually detailed custody and replay records, and the current clean-room TMLR audit is green. The problem is the opposite of missing documentation: too much developer/audit history has leaked into the manuscript-facing surface. This makes the paper harder to evaluate and creates double-blind and final-release risks.

## Major concerns

### R3-C01 — repository-to-manuscript leakage and revision accretion

**Severity:** blocking-repairable.  
**Locations:** Methods, Results, Threat model/limitations, Data and code availability, Conclusion, and the long prospective source-expansion appendix.  
**Examples:** hosted-job and default-branch language, workflow/API details, run IDs, commit hashes, script/file paths, internal terminal identifiers, V4--V12 transport chronology, JAR/build debugging.  
**Resolution test:** translate inference-critical mechanics into scientific abstractions; move operational provenance to one artifact manifest or supplementary record; the main paper remains intelligible with no repository tree open.

### R3-C02 — current anonymous artifact path is unresolved

**Severity:** blocking for TMLR filing.  
**Concern:** the current availability prose names the public `SzeChunYiu/ORION` repository and many identifying paths while the target is double blind.  
**Resolution test:** prepare an anonymous review artifact/supplement or another TMLR-compliant blinded access route, and ensure the submitted PDF does not reveal author identity through repository ownership or metadata. Exact public archive can be revealed when the review policy permits.

### R3-C03 — TMLR LLM-assistance disclosure requires factual author verification

**Severity:** compliance blocker at filing, not a scientific blocker.  
**Concern:** current TMLR guidance requires a first-page disclosure when LLMs assisted manuscript preparation. The exact statement must reflect the real use and cannot be inferred by this review.  
**Resolution test:** author verifies the factual scope of AI/LLM assistance; the required first-page disclosure is inserted before filing; all scientific ideas, claims and results remain author-responsibility statements rather than AI-attributed evidence.

### R3-C04 — exact current rendered artifact must be re-audited after revision

**Severity:** blocking-repairable.  
**Concern:** green historical/current-source workflows are necessary but not sufficient after manuscript surgery.  
**Resolution test:** clean rebuild on exact final revision; record PDF SHA-256; inspect every page, final page, references, figures/tables, metadata and spill/clipping; bind the exact audited PDF to the submission manifest.

## Reporting/clarity concerns

- The abstract is information-dense enough that the primary paper question can be lost among three evidence layers and source-programme status. It should retain V2/V3/P4-X boundaries but remove transport-detail status unless essential to the main decision.
- The Data and code availability section should identify one authoritative review package and its contents, not enumerate the repository.
- The conclusion should end on the established scientific boundary, not a development log.
- The V2 H3 negative and excluded live-model arm are valuable adverse evidence and should remain visible after compression.

## Recommendation to editor

`major_revision_before_simulated_closure`.

The required repairs are mostly manuscript allocation, anonymity/compliance packaging and exact-current rendering. They do not require fabricating or adding a scientific result.

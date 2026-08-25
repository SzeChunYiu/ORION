# Five-paper submission V3 development packet

Date: 2026-08-25
Branch: `shadow/five-paper-submission-v3-20260825`
Base: `main@8470d3cdcf5219aac906e6f37e65d7499aa13e66`
Academic-paper workflow: `SzeChunYiu/academic-paper-skills@188e83e639571c435344630ae68fdc66072650d2`

## Objective

Convert Papers A, B, C, D and the non-quantum `C_5^3` manuscript from hardened Markdown candidates into complete, organized, buildable submission packages. Each paper must have a standalone LaTeX master, section-level TeX sources, bibliography, claim-driven figures with source data and scripts, reproducibility instructions, review and claim-boundary records, and a compiled PDF that has been visually preflighted. The scientific text will be expanded only where explanation, evidence, comparison, proof readability, or boundary reporting materially improves the paper.

## Recursive academic-paper-skills route

The lane applies the current skill repository recursively rather than as a one-time style pass:

1. `nature-writing`: evidence-first rhetorical architecture, explanatory sufficiency, analogue-paper calibration, content placement, main-text discipline and consistency sweep.
2. `nature-citation`: atomic claim segmentation, best-evidence retrieval, support grading, structured metadata and bibliography validation.
3. `nature-figure`: claim -> reader question -> estimand/data structure -> uncertainty/boundary -> plot; Python backend because the ORION scientific workflow and committed verifiers are Python-based.
4. `nature-reviewer`: editorial triage followed by three independent reviewer lenses (validity; prior work/significance; reproducibility/boundaries), then post-review editor synthesis and minimum-sufficient repair.
5. `nature-polishing`: sentence-dependency repair, terminology consistency, author-voice preservation, LaTeX layout repair and rendered-page inspection.
6. Data/reference/reproducibility skills are used for availability statements, source-data packaging and final reference audit.

After any blocking reviewer finding, the paper returns to the earliest relevant stage and is re-run through the downstream stages. Venue style does not upgrade scientific authority.

## Expert group

- Quantum compilation algebra lead: Papers A/B theorem semantics, compiler interpretation, objective cones and transfer.
- Proof-complexity and zero-sum lead: Paper B certificate-language exactness and Paper A/B Davenport donor subtraction.
- Algebraic-statistics / decision-theory lead: Paper C fibers, minimax statements, Markov-basis donors and information-query boundaries.
- Formal-methods / provenance lead: Paper D fixed-point semantics, authority typing, evaluator semantics and donor subtraction.
- Additive-combinatorics lead: non-quantum corridor, saturation, multiplicity/rank phase, atom budget and computational-authority boundary.
- Literature and reference auditor: primary-source metadata, negative/limiting evidence, claim-to-source map.
- Figure/reproducibility editor: plot contracts, source data, scripts, build determinism and PDF visual QA.
- Hostile journal referee/editor: target-specific decision proof, overclaim checks and top-tier stop/go gate.

These are distinct review lenses in one AI execution context, not represented as independent human peer reviewers.

## Scientific nonpromotion rules

- The current V2 theorem and evidence boundaries remain controlling unless a new all-size proof or exact parent result is added.
- In elementary binary generated subgroups, the alphabet zero-sum-free ceiling is not claimed below generated rank; a spanning alphabet contains a basis and has `zsf = rank`.
- Paper B lower bounds remain scoped to the named deletion/certificate language.
- Paper C generic Markov/fiber/Mobius mathematics remains donor-owned; compiler-specific query hierarchy is the residual claim.
- Paper D generic TMS/Datalog/provenance/fixed-point mathematics remains donor-owned.
- The non-quantum paper does not claim exact `D_4(C_5^3)`, `31 in C_0(C_5^3)`, support-23 theorem authority, or external replication unless separately established.

## Submission-package layout

Each paper receives `submission/` with:

- `main.tex`
- `sections/*.tex` (one file per reader-facing chapter/appendix)
- `references.bib`
- `figures/` with generated PDF/PNG assets and `source-data/*.csv`
- `scripts/make_figures.py` and `scripts/verify_submission.py`
- `Makefile`
- `README.md`
- `CLAIM_LEDGER.md`
- `REVIEW_MEMO.md`
- compiled `<paper-id>.pdf`

A portfolio-level index, skill-recursion manifest, citation audit and build report will be added under `papers/`.

## Merge rule

Work enters through a PR. The user has authorized merge to main and previously authorized not waiting for unrelated CI. Before merge, the lane must nevertheless pass its own five-paper LaTeX builds, focused submission verifiers, bibliography checks, PDF preflight and visual inspection. Scientific top-tier status is recorded per paper rather than forced to PASS as an umbrella condition.
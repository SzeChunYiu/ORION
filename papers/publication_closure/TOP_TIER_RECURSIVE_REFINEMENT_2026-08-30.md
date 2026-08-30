# Recursive top-tier manuscript refinement — 2026-08-30

**Branch:** `academic-top-tier-refinement-20260830`  
**Pipeline:** `academic-paper-skills` / `academic-paper-pipeline` v1.9.0  
**Scientific authority delta:** none unless explicitly backed by an already-landed evidence object  
**Release rule:** additive manuscripts only; current upload-facing release masters are not replaced by this pass.

## Scope

This pass covers the portfolio papers whose bounded science is already either **READY TO SUBMIT** or **VENUE/RELEASE READYING** under `ORION-paper/v1-papers/README.md`:

- ORION-03 — JAR → TOCL
- ORION-05 — Quantum → TCS
- ORION-06 — AIJ → TMLR
- ORION-07 — TMLR → AIJ Research Note
- ORION-08 — TMLR → AIJ
- ORION-10 — Quantum → TCS
- ORION-12 — Information Processing & Management → IR/information-science specialist
- ORION-13 scoped — Semantic Web Journal → Journal of Web Semantics
- ORION-14 — TMLR → AIJ
- ORION-16 — AIJ → TCS
- ORION-19 — TMLR → AIJ Research Note
- ORION-24 bounded — JAAMAS → agent-governance / empirical-SE specialist

Papers whose intended top-tier claim still requires new scientific or external authority remain outside this finish-now set. In particular, this pass does not convert structural evidence gaps into prose solutions.

## Recursive expert roles

The manuscript loop is run from four independent review roles before synthesis.

1. **Theory and novelty editor** — formal methods / AI reasoning / theoretical CS. Checks theorem assumptions, proof-vs-finite authority, sharpness, donor subtraction, and whether the claimed residual survives strongest prior mechanisms.
2. **Evidence and reproducibility reviewer** — empirical AI / scientific software / provenance. Checks prospective vs retrospective status, independent unit, custody, replay, finite-vs-general evidence, same-programme replication, and release statements.
3. **Claims and statistics reviewer** — benchmark and statistical inference. Checks denominators, paired units, clustering, uncertainty semantics, non-inferiority/equivalence logic, exact counts, pseudo-replication, and whether a comparator contrast is definitional.
4. **Journal and manuscript editor** — venue triage / scholarly writing. Checks title/abstract/first-page decisionability, target fit, main-vs-support allocation, repository-to-manuscript leakage, limitations, anonymity, and reader-facing terminology.

The roles are lenses over the same evidence, not votes. A single technically valid blocker remains a blocker.

## Skill rules applied recursively

Each manuscript goes through:

`evidence freeze → atomic claim ceiling → donor/novelty subtraction → target contract → manuscript rewrite → hostile reviewer pass → statistics/authority correction → editor synthesis → second rewrite → release-surface handoff`.

The main constraints carried from the skill are:

- every atomic claim keeps its quantifier, comparator, domain and uncertainty;
- finite zero-error checks never substitute for an all-size proof;
- prospective, retrospective, post-outcome and same-programme evidence remain distinct;
- strong donor absorption narrows the novelty claim rather than disappearing from the paper;
- null, adverse and `CANNOT_CHECK` outcomes stay visible;
- repository paths, CI names, branch names and development chronology are translated into scientific abstractions in the manuscript body;
- title, abstract, Results, Discussion and Conclusion cannot silently strengthen the same claim;
- target-specific packaging and availability statements are release claims and must be verified separately from manuscript prose.

## Live target contracts used

### Quantum
Current author guidance requires the arXiv submission to be posted/cross-listed to `quant-ph`, asks authors to state main results and assumptions clearly within the first couple of pages, and evaluates significant technical/conceptual advance, clarity, scope and reproducibility. ORION-05 and ORION-10 therefore lead with theorem-backed results, assumptions and authority hierarchy rather than benchmark accuracy.

### TMLR
Current TMLR guidance requires a double-blind anonymized submission in the mandatory TMLR style, permits a separate named arXiv preprint, and emphasizes technical correctness. ORION-07/08/14/19 keep identity-bearing release material outside the anonymous manuscript and foreground bounded claims, adverse results and exact evidence limits.

### AIJ
The current AIJ scope includes reasoning, knowledge representation, learning and other principled AI methods; Research Notes are supported. ORION-06 and ORION-16 are framed as reasoning/governance and formal-state contributions rather than as generic software-process papers.

### JAR
Current JAR scope is the theory, implementation and application of logical reasoning by computer, including automated theorem proving, proof systems, formal methods and AI guidance of reasoning. ORION-03 therefore leads with its typed least-fixed-point semantics and proof-tree theorems; the X.509 material is an instantiation, not the theorem authority.

### IP&M
Current IP&M scope includes original research, methods and critical system-design work at the intersection of computing and information science. ORION-12 is therefore framed as an open-world discovery/stopping methods paper and explicitly declines retrieval-superiority language after its preregistered external gate fails.

### Semantic Web Journal
Current SWJ guidance accepts full original research papers and strongly encourages public evaluation data. ORION-13 is kept scoped to structured scientific identity/compatibility; raw-text and downstream-portrait claims remain outside the paper.

### JAAMAS
Current JAAMAS scope covers foundational, theoretical and practical aspects of autonomous agents and multi-agent systems, including agent decision-making and learning. ORION-24 is therefore framed as a bounded research-agent governance decision contract, not as evidence that an autonomous scientist improves real science.

## Reviewer findings that changed manuscript content

### ORION-07
The older rewrite described one primary prospective item. The authoritative prospective case-series ledger contains **three valid prospectively frozen frontier questions**. Both instruments agree on all three; both are responsibility-aligned on two, and both are responsibility-misaligned on QG-20 while still selecting the aligned next move. This supplies an explicit prospective counterexample to `agreement = correctness` and must replace the single-item story. No reliability estimate is authorized at `n=3`.

### ORION-12
The controlled premature-closure comparison is partly **definition-driven** because only the governed rule exposes an explicit unresolved terminal. That controlled contrast is therefore mechanism/conformance evidence, not a performance estimate. The external 50-topic TREC-COVID study remains the decisive empirical test and is adverse on the registered recall-and-cost gate.

### ORION-13
On the two 32-case public-reference holdouts, every case is predicate-equal, so the flat predicate baseline is an always-merge classifier on those corpora. Six confirmatory cases carry the reported 0.1875 false-merge contrast; exact paired discordance is `b=6,c=0`, two-sided McNemar `p=0.03125`. The initial holdout alone is `b=4,c=0`, `p=0.125`; pooled evidence is reported separately. Nine of ten registered coordinates decide no case on those holdouts; the observed discriminator collapses to polarity (with predicate/modality context). This is a coverage limitation, not evidence that the other coordinates are globally dispensable.

### ORION-14
The original H1 interval treated cases too independently. A landed family-cluster reanalysis over 12 attack families reproduces the -0.5 contrast, gives a family-bootstrap 95% interval `[-0.75,-0.25]`, and an exact two-sided cluster test `p=0.03125` over six discordant families, all favoring the target-sufficient rule. The top-tier rewrite uses the cluster-respecting uncertainty.

### ORION-19
The five-family diagnostic is too small for a population-style superiority claim. The registered protected table has four paired task-family discordances favoring the intervention diagnostic and none favoring the generic compute-escalation heuristic; an exact two-sided McNemar calculation is `p=0.125`. Moreover, the generic heuristic escalates compute by construction. The refined paper treats the result as bounded mechanism evidence and reports the false-escalation contrast as a design consequence, not an estimated effect.

### ORION-24
The specification-separated benchmark contains 28 deterministic specification variants, not 28 independent population draws. Full governance is 28/28 and `MULTI_REVIEW` 24/28: four discordant rows, all favoring the full contract. A case-level exact McNemar calculation is `p=0.125`, but inferential sampling language is not licensed because the rows are authored specification cases. The paper reports exact conformance and the four-row discordance, not a general agent-performance effect.

## Per-paper editorial disposition

| Paper | Manuscript action | Top-tier manuscript status after this pass |
|---|---|---|
| 03 | formal-first JAR refinement; theorem assumptions and donor boundary moved forward | manuscript-refined; release package remains separate |
| 05 | Quantum first-page theorem/assumption/significance refinement | manuscript-refined; replay/literature/render gates remain release work |
| 06 | AIJ reasoning/governance refinement; single-programme evidence ceiling made explicit | manuscript-refined; named arXiv build remains release work |
| 07 | rewrite around the actual three-frontier prospective series and agreement counterexample | manuscript-refined; existing green release remains authoritative until adoption |
| 08 | TMLR mechanism paper tightened around matched-information design, uncertainty and donor absorption | manuscript-refined; existing green release remains authoritative until adoption |
| 10 | Quantum authority-hierarchy story tightened; explanation refutation made central | manuscript-refined; existing green release remains authoritative until adoption |
| 12 | IP&M methods framing; definitional controlled contrast demoted; adverse external gate remains central | manuscript-refined; blind/named release audit still required |
| 13 | scoped identity paper corrected for baseline degeneracy, discordance count and coordinate coverage | manuscript-refined; exact-subject CI/package audit still required |
| 14 | TMLR refinement integrates cluster-respecting uncertainty | manuscript-refined; existing green release remains authoritative until adoption |
| 16 | AIJ formal-state refinement; distinct configurations separated from repeated donor loops | manuscript-refined; existing green release remains authoritative until adoption |
| 19 | TMLR refinement removes population-style reading of five-family contrast | manuscript-refined; named arXiv release remains required |
| 24 | JAAMAS conformance framing; exact four-row discordance and no pseudo-inference | manuscript-refined; named arXiv/final venue package remain required |

## Adoption rule

These rewrites are **candidate higher manuscript surfaces**, not automatic replacements for current submission masters. A release master may adopt one only after its own bibliography, figure, anonymity/named-release, availability, PDF/render, metadata and target-format checks are rerun on the adopted text. Existing green packages stay green and authoritative until such an adoption is explicitly made.

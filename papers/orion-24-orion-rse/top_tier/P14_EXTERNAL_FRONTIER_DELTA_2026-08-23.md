# P14 external frontier delta — 2026-08-23

**Programme:** #977  
**Status:** promotion-wave nearest-work pressure; submission-day refresh still required.

## Donor-owned evaluation capabilities

### PaperBench — replication engineering

PaperBench evaluates agents replicating 20 ICML 2024 Spotlight/Oral papers from scratch using 8,316 author-co-developed rubric items and separate judge evaluation.

**Disposition:** ADOPT. P14 does not claim novelty for hierarchical paper-replication rubrics or judging research engineering outputs.

https://arxiv.org/abs/2504.01848

### ReplicatorBench — replicable and non-replicable scientific claims

ReplicatorBench includes human-verified replicable and non-replicable social/behavioral-science claims and evaluates extraction/retrieval, experiment design/execution, and interpretation.

**Disposition:** ADOPT. P14 does not claim novelty for including negative/non-replicable science in agent evaluation or for process-level replication benchmarking.

https://arxiv.org/abs/2602.11354

### AutoResearchBench — scientific literature discovery

AutoResearchBench evaluates deep and wide scientific literature discovery and shows that even strong browsing agents remain weak on difficult research-oriented retrieval.

**Disposition:** ADOPT. P14's donor-subtraction component must be evaluated with strong research-oriented retrieval rather than weak generic search.

https://arxiv.org/abs/2604.25256

### AstaBench / ResearcherBench / Scientist-Bench — scientific research suites

Current 2025–2026 suites evaluate research-oriented agents across scientific tasks, frontier research questions, data-driven discovery and comparison with expert work.

**Disposition:** ADOPT. P14 cannot claim general scientific-agent benchmarking.

- https://openreview.net/pdf?id=M7TNf5J26u
- https://openreview.net/forum?id=oj6A9hrNdL

### Shadow evaluations — original-author judgment on unpublished research questions

Kirgis et al. (2026) give frontier agents the central research questions of unpublished NeurIPS 2026 submissions and have the original authors grade research progress. They report recurrent failures in publishability judgment, research-design repair/backtracking, resource awareness and instruction following.

**Disposition:** ADOPT / strongest external-authority pattern. Original-author/expert blinded grading is a direct donor for the external P14 adjudication design.

https://arxiv.org/abs/2607.27191

## Donor-owned research-system capability

Recent systems such as Robin, Co-Scientist and The AI Scientist demonstrate that literature search, hypothesis generation, analysis, experiment planning/execution and report generation can be increasingly automated and evaluated in real scientific settings.

**Disposition:** ADOPT. P14 must not confuse ability to generate/execute research with the governance question.

- Robin: https://www.nature.com/articles/s41586-026-10652-y
- Co-Scientist: https://www.nature.com/articles/s41586-026-10644-y
- The AI Scientist: https://www.nature.com/articles/s41586-026-10265-5

## Upward P14 residual

The stronger scientific question is now:

> Given the **same evidence-generation capability, model/tool access and budget**, does an explicit fail-closed scientific-promotion contract improve the quality of final research decisions—novelty ownership, claim width, protected endpoint fidelity, negative retention, `CANNOT_CHECK`, split/subsume/reopen/stop—without reducing independently judged useful discovery?

P14 therefore studies a **governance intervention over research trajectories**, not generic research-agent capability.

## Required paired design consequence

The strongest experiment should reuse identical frozen research packets and, wherever feasible, identical evidence-generation traces in two modes:

1. donor research workflow makes its ordinary final research judgment;
2. the same available evidence is passed through the P14 governance contract before promotion.

This isolates governance from raw model/retrieval/engineering capability. A second end-to-end arm may let governance affect experiment selection/backtracking, but must be reported separately because it changes the evidence trajectory.

## No first-of-kind language

This refresh authorizes no claim that P14 is the first system to evaluate research quality, preserve negatives, use expert adjudication, benchmark research agents, or employ multi-agent/reflection/preregistration mechanisms.

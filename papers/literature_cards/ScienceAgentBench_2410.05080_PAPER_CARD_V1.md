# Paper Card — ScienceAgentBench

**Source mode:** primary ICLR 2025 proceedings + arXiv/GitHub record.  
**Context mode:** externally verified benchmark-parent check.  
**Checked:** 2026-08-21.

## 01. Bibliographic position
Ziru Chen et al. **ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery.** International Conference on Learning Representations (ICLR), 2025. arXiv:2410.05080.

## 02. Research question
Can language agents reliably carry out individual real scientific data-analysis tasks, and how should such capability be evaluated before claiming end-to-end scientific automation?

## 03. Background route
The work responds to broad end-to-end AI-scientist claims by decomposing scientific workflows into concrete tasks sourced from peer-reviewed research.

## 04. Prior-work / field context
ScienceAgentBench is an early rigorous benchmark for scientific language-agent code generation and execution. It is distinct from later AstaBench and SciAgentArena.

## 05. Pain point
End-to-end demos can hide failure on essential scientific subtasks; benchmark construction also faces contamination, annotation-quality and scientific-plausibility risks.

## 06. Core insight
Evaluate agents on 102 tasks extracted from 44 peer-reviewed publications, validated by nine subject-matter experts, with target outputs normalized to self-contained programs and metrics that inspect generated code, execution results and costs.

## 07. Method / module logic
The benchmark uses real data-driven discovery tasks in multiple disciplines, expert validation, program execution/evaluation, repeated attempts/frameworks and contamination-mitigation strategies.

## 08. Essential formulas
Not central to Q2/Q3 positioning.

## 09. Experiment-to-claim evidence
The primary record reports that the strongest evaluated agent solved only a minority of tasks even with repeated attempts/expert knowledge, motivating caution about end-to-end automation claims.

## 10. Main conclusions
Rigorous scientific-agent evaluation should decompose research into authentic tasks, validate annotations/outputs and evaluate executable results/cost rather than rely on plausible generated prose.

## 11. Conclusion boundaries
ScienceAgentBench already owns substantial territory in:
- authentic scientific-task benchmark construction;
- expert validation;
- executable program-level evaluation;
- data-contamination mitigation;
- cautious inference from task-level capability to end-to-end automation.

## 12. Author-stated limitations
The repository/benchmark has continued to evolve, including a 2026 verified benchmark split. Submission-date related-work text should cite the archival ICLR paper and mention later benchmark repairs only if scientifically relevant.

## 13. Critical analysis
Q2 is not a benchmark paper and must not claim that decomposed/executable scientific-agent evaluation is new. Q3's residual is likewise not “rigorous scientific-agent evaluation”: it is the different measurement object of pre-outcome agreement/diagnosis between research instruments on an unresolved frontier question, scored only later.

## 14. Learned knowledge
ScienceAgentBench, AstaBench and SciAgentArena form related but distinct evaluation lineages; citations should not use their names interchangeably.

## 15. Knowledge connections
AstaBench; SciAgentArena; MLGym; Q2 negative-successor discipline; Q3 dual-instrument benchmark.

## 16. Testable research ideas
- Add a frontier-diagnosis extension to task-level science benchmarks once Q3 has enough prospective cases.
- Compare task-level competence with ability to choose the right next research question after a negative result.

## ORION claim effect
**Removed from Q2/Q3 novelty:** rigorous authentic scientific-task evaluation, expert-validated benchmark construction, executable result scoring and contamination-aware evaluation.  
**Q2 residual:** successor authority after negative disposition.  
**Q3 residual:** pre-outcome inter-instrument frontier diagnosis/agreement with deferred scoring.

# Paper Card — ScientistOne / Chain-of-Evidence

**Source mode:** primary arXiv record/abstract.  
**Context mode:** targeted external novelty check.  
**Checked:** 2026-08-21.

## 01. Bibliographic position
Rui Meng et al. **ScientistOne: Towards Human-Level Autonomous Research via Chain-of-Evidence.** arXiv:2605.26340 (2026), DOI `10.48550/arXiv.2605.26340`.

## 02. Research question
How can autonomous research systems produce research outputs whose claims, reported scores, references and method descriptions are verifiably tied to underlying evidence/implementation?

## 03. Background route
The work starts from end-to-end research agents that can produce plausible papers while still fabricating citations, reporting unreproducible scores or describing methods inconsistently with code.

## 04. Prior-work / field context
ScientistOne sits in the autonomous-research/AI-scientist literature and directly attacks verification rather than only task performance.

## 05. Pain point
Surface-quality evaluation does not expose whether research claims are actually supported by sources/results/code.

## 06. Core insight
Maintain a **Chain-of-Evidence (CoE)** by construction and audit research artifacts post hoc using score verification, specification checks, reference verification and method-code alignment.

## 07. Method / module logic
Three reported contributions:
1. Chain-of-Evidence framework;
2. ScientistOne end-to-end autonomous research system maintaining CoE;
3. CoE Audit with four integrity checks applied to systems.

## 08. Essential formulas
Not assessable/needed from source-limited record. The paper's novelty is procedural/evaluative rather than a formula ORION-02 must reproduce.

## 09. Experiment-to-claim evidence
The abstract reports evaluation across 75 papers, five systems and five frontier research tasks, with additional transfer to six tasks. Reported failure modes include hallucinated references, failed score verification and method-code mismatch; ScientistOne improves these integrity metrics while remaining competitive on task outcomes.

## 10. Main conclusions
Research-agent outputs need claim-to-evidence traceability and implementation-aware audits; maintaining evidence chains throughout the workflow improves verifiability.

## 11. Conclusion boundaries
ScientistOne directly owns broad claims about:
- claim-to-source evidence chains;
- reference verification;
- score verification;
- method-code alignment;
- end-to-end evidence-preserving autonomous research.

## 12. Author-stated limitations
Not fully assessable from the abstract record. Full paper must be read before ORION-02 makes detailed comparisons about autonomy, human involvement or failure modes not named in the primary abstract.

## 13. Critical analysis
This is a direct novelty threat to any ORION-02 framing such as “scientific claims should carry receipts/provenance.” ORION-02 must move one step later in the research lifecycle: **after evidence is correctly bound and a frozen claim receives a negative/donor/CANNOT_CHECK disposition, which successor scientific question is legally opened without rewriting the predecessor?**

## 14. Learned knowledge
Evidence traceability and successor authority are distinct. A perfectly traceable negative result still leaves the question of how a research programme should change its hypothesis/method space.

## 15. Knowledge connections
Preregistration; truth maintenance; counterexample-guided refinement; scientific-agent benchmarking; ORION-02 typed transition graph; ORION-03 instrument agreement.

## 16. Testable research ideas
- Apply ORION-02 successor rules on top of CoE-traced research agents and measure invalid post-negative transitions.
- Compare retained-negative transition policies against “restart/new idea” policies on controlled research programmes.
- Use CoE audit as a prerequisite evidence gate before ORION-02 responsibility attribution.

## ORION claim effect
**Removed from ORION-02 novelty:** evidence-chain construction, claim/source traceability, score/reference/method-code audit.  
**ORION-02 residual:** typed negative disposition → responsibility/donor analysis → prospectively frozen successor, with append-only predecessor authority.  
**Full-text gate:** required before detailed comparative statements beyond the abstract-record contributions.

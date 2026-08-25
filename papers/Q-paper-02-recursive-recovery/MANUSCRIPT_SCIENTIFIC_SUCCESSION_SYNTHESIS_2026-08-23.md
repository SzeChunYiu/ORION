# Recursive Recovery of Negative Quantum Results: A Receipted Longitudinal Study of Scientific Succession

**ORION-Q2 Manuscript V2 — publication-synthesis draft**  
Publication cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Foundation: `PUBLICATION_FOUNDATION_V2.md`

## Abstract

Autonomous and computational research systems increasingly preserve evidence, code and execution traces, but reproducibility alone does not specify what a research programme should do when a prospectively frozen hypothesis fails. We present a longitudinal case study of an executable **negative-result recovery** discipline used in the ORION-Q quantum-compilation programme. The discipline treats negative, null, donor-subsumed and `CANNOT_CHECK` outcomes as persistent scientific state. A result can license a successor only after its failure responsibility is localized, the strongest located donor receives first right of refusal, and the successor hypothesis/protocol is frozen before its own outcome. Later success never rewrites the earlier disposition. Across the programme, this transition rule produces qualitatively different legitimate endpoints: donor absorption, exact counterexample, bounded finite positive, prospective confirmation, all-`n` theorem, further refutation, or unresolved open state. We reconstruct representative chains rather than claiming the quantum mathematics as methodology novelty. One chain moves from weight-one donor closure to exact split and borrow counterexamples, then to finite support-two closure and an all-`n` support theorem. A separately frozen fresh-subject predictor is confirmed on its registered subject but a later broader closed-form extrapolation is refuted, illustrating that a bounded prospective positive and a later negative can both remain scientifically valid. We compare this discipline to 2026 evidence-chain and scientific-agent benchmarking work, which already owns broad claim-to-evidence traceability and controlled evaluation. Our narrower claim is that **the transition from a retained negative disposition to the next licensed scientific question can itself be made executable and auditable**. This is one-programme evidence of feasibility and research hygiene, not a statistical demonstration that the method improves scientific productivity.

## 1. Introduction

AI-assisted research has moved quickly from literature and coding assistants toward end-to-end systems that generate hypotheses, implement experiments and draft papers. With that progress, verification has become a central concern. Recent surveys of autonomous research agents describe a gap between code availability and claim-level verifiability. AstaBench provides controlled, reproducible scientific-agent evaluation across thousands of tasks. ScientistOne develops a Chain-of-Evidence framework in which claims are traceable to underlying sources and checks. The AI Scientist demonstrates end-to-end research generation and automated review. These systems and studies establish substantial prior art for evidence provenance, reproducibility, benchmark control and automated scientific workflows.

A different methodological problem appears after those controls are in place. Suppose a hypothesis is frozen prospectively and then fails. What happens next?

The easiest response is to discard the run and search for a new positive. A subtler failure is to reinterpret the old claim until the observed outcome becomes a success. Both practices destroy the information carried by the negative. At the other extreme, simply archiving a failed run is scientifically passive: it records what happened but does not specify which next question is licensed by that failure.

This paper studies an intermediate object: **negative-result recovery as a typed scientific transition**. A retained disposition says not only that a claim failed, but what kind of failure was observed, which alternative explanation or donor remains viable, and what successor question may be frozen next. The transition is constrained by chronology. The successor cannot be backdated to make the predecessor look correct, and its outcome cannot be used to redefine the predecessor.

We developed and repeatedly applied this discipline in the ORION-Q programme, which studies exact/synthetic quantum-compilation questions with heavy use of frozen protocols, exact referees, donor first-right-of-refusal and receipt-bound results. The programme is useful as a case study because many hypotheses are cheap enough to attack aggressively and exact counterexamples can often be serialized. It contains genuine negatives, donor absorptions, bounded positives and theorems, rather than a sequence of only successful experiments.

The contribution is methodological and deliberately bounded. We do **not** claim that ORION-Q invented evidence chains, preregistration, reproducibility or autonomous science. We do not claim that the recovery discipline increases discovery speed or quality across fields. We show instead that one research programme can represent the transition

`frozen claim -> outcome -> disposition -> responsibility/donor analysis -> frozen successor`

as an auditable scientific object whose earlier states remain immutable even when later work succeeds.

## 2. Related work and donor boundary

### 2.1 Evidence chains and verifiability

ScientistOne (Meng et al., 2026; arXiv:2605.26340) directly addresses verifiability failures in autonomous research through Chain-of-Evidence, score verification, reference verification and method-code alignment. Q2 therefore cannot claim general claim-to-evidence traceability as its novelty.

The 2026 survey *Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap* documents weak availability of seeds/traces and novelty verification across existing systems. This motivates verification but does not make verification itself novel here.

### 2.2 Scientific-agent benchmarks

AstaBench (ICLR 2026) provides a large controlled scientific-research evaluation suite with standardized tools, strong baselines and cost-aware comparisons. ScienceAgentBench similarly evaluates real scientific tasks against validated target outputs. Q2 does not claim rigorous agent benchmarking.

### 2.3 End-to-end automated research

The AI Scientist and related systems already span ideation, experimentation, analysis and manuscript production. Q2 is not an autonomy paper. Its case study can be executed with human/model assistance; the methodological object is the **authority transition between research states**.

### 2.4 Preregistration, provenance and negative results

Prospective hypothesis/protocol freezing and provenance are mature scientific practices. The residual investigated here is their composition with a typed **successor relation**: which failure class opens which next question, after prior work receives first right of refusal, while the old result remains an active constraint.

## 3. The negative-recovery state machine

### 3.1 Research state

A research atom contains:

- a claim/hypothesis identifier;
- exact scope/model/objective;
- protocol and outcome-space frozen before the result;
- result receipt and authority class;
- disposition (`SUPPORTED`, `NEGATIVE`, `DONOR_ABSORBED`, `CANNOT_CHECK`, `OPEN`, etc.);
- responsibility explanation, to the extent justified;
- nearest-work/donor disposition;
- successor pointer, if one is later frozen.

A receipt establishes attribution/replay properties. It does not self-certify novelty or scientific interpretation.

### 3.2 Allowed terminal classes

A frozen research question may legitimately end in several ways:

**Bounded positive.** The registered gate passes in the stated domain.

**Exact counterexample / negative.** A claim is false in its own domain.

**Donor absorption.** A located prior mechanism subsumes the candidate; scientific understanding may increase while novelty credit decreases.

**CANNOT_CHECK.** Required evidence/authority is unavailable under the declared model; absence is not converted to failure or success.

**Theorem.** A stronger proof replaces finite evidence for a strictly defined claim without rewriting the finite predecessor.

**Open residual.** The current instrument cannot close the remaining claim and no admissible stronger inference exists.

### 3.3 Responsibility localization

A negative result does not automatically imply “invent a new method.” The programme first asks whether the failure is attributable to:

- representation/family restriction;
- search/exactness limitation;
- objective mismatch;
- implementation or environment;
- evaluator/measurement;
- donor domination;
- model non-identifiability;
- unavailable evidence.

Only a responsibility supported by the evidence can license a successor targeted at that layer.

### 3.4 Donor first right of refusal

Before a candidate mechanism receives novelty credit, the strongest located donor is given the opportunity to close the same residual. If it does, the result is donor absorption rather than “ORION improvement.” This rule is central to the case study because several early candidate ideas disappear under donor pressure.

### 3.5 Successor freeze

A successor becomes scientifically admissible only after the predecessor disposition exists and before the successor outcome is accessed. The successor names:

- what changed relative to the predecessor;
- what did not change;
- the new hypothesis/gates;
- what evidence would refute it;
- which old negative remains immutable.

This prevents an outcome-aware “repair” from masquerading as a prospective experiment.

## 4. Case chain I: donor closure to exact counterexample

The TARE programme begins with a natural restricted donor family for a shared-Tag compilation grammar. Large finite/chemistry checks make weight-one structure look plausible, and local support-dominance evidence suggests that extra support is expensive.

Crucially, the local analysis explicitly records a gap: removing support can change the shared Tag syndrome. The programme therefore does not promote the local check to a global closure theorem.

A frozen hostile panel then finds an exact counterexample: split frame anchors with a spread Tag achieve cost 8 where the common-anchor donor family costs 9. The correct disposition is not “TARE failed.” It is:

`NEGATIVE: common-anchor closure false`  
`RESPONSIBILITY: Tag/anchor coupling`  
`SUCCESSOR QUESTION: does D+ (arbitrary anchors + exact minimum Tag) close the gap?`

D+ is frozen only after the counterexample and succeeds on the registered first-regime panels.

This is a minimal example of negative recovery: the failed statement is retained and a more precise family is created from the witnessed mechanism.

## 5. Case chain II: the successor also fails

The D+ successor is then attacked on a structured `n=2` domain. It fails on hundreds of exact instances. The minimal witness has exact cost 5 versus D+ cost 6.

The witness localizes a different mechanism: a support-two frame can be placed on a cheap central branch and thereby purchase a cheaper Tag. The negative is therefore not another instance of split anchors; it identifies **frame-for-Tag borrowing**.

Again the discipline forbids a post-hoc threshold change. The outcome is preserved as a refutation of D+ closure. The successor question becomes whether the full support-two family `D++` contains the exact optimum.

A finite D++ campaign closes every then-critical frozen instance, but the programme still does not call that an all-`n` theorem. The scientific responsibility has moved from “find a missing configuration” to “prove whether larger support can ever help.”

## 6. Case chain III: finite positive to all-`n` theorem

The next step illustrates a different transition. Finite support-two closure is a positive but not enough to justify universal extrapolation. A theorem programme therefore freezes the missing proof obligation.

R6S proves an all-`n` exchange theorem for the frozen R6M/raw-support objective: support at least three can always be reduced at non-increasing cost while preserving the required structural relations. Hence `C_DP=C_D++` for every `n`/instance in scope.

The theorem does not delete the finite predecessor. Instead the evidence hierarchy becomes:

- R6P: finite support-two closure and exact witnesses;
- R6S: all-`n` proof that authorizes the stronger claim.

The upgrade is explicit and claim-specific. Other grammar/objective variants remain outside the theorem.

## 7. Case chain IV: a prospective positive and a later refutation can both be valid

The programme also contains a useful chronology test. A finite regime predicate is derived from earlier TARE panels. A fresh public Benzene DUCC subject is then deterministically selected, and its regime/cost prediction is digest-stamped **before** the unrestricted DP referee is opened. All 15 matchings agree with the frozen prediction.

The correct disposition is a prospective bounded confirmation. It is not a theorem.

Later QG work generates a different fresh `n=3` instance that refutes the broader closed-form extrapolation: exact truth is 10 while the simple forecaster returns 11. The earlier 15/15 result remains true on its frozen subject. The later result says only that the extrapolation was too broad.

This sequence is important methodologically because it resists a common narrative temptation. A later counterexample does not make the earlier prospective test “invalid”; an earlier prospective success does not protect a universal claim from later refutation. Both receipts remain active with different scopes.

## 8. Case chain V: repair does not grant universal completeness

The QG5 counterexample identifies an omitted borrow home. A separately frozen B′ successor repairs that instance and its registered panels. If negative recovery were merely an iterative heuristic-fitting loop, the story could stop with “fixed the bug.”

Instead the repaired family is attacked again. QG7 finds 64 exact fourth-regime witnesses outside B′. A separately frozen B″ family closes the registered successor panels, but the current all-`n` smallest-family classification remains open at one lemma link.

The succession record therefore contains:

`closed form -> refutation -> targeted successor -> finite closure -> new refutation -> new successor -> partial theorem/open link`.

At no point does a finite zero-error panel erase the earlier counterexample or automatically grant universality.

## 9. Donor absorption as a successful outcome

Negative recovery is not only about counterexamples. In other ORION-Q lanes, candidate mechanisms are given first right of refusal against stronger existing methods. When the donor matches or subsumes the candidate, the correct terminal is **donor absorption**.

This is scientifically useful for two reasons. First, it prevents novelty inflation. Second, it changes where the next question should be asked. If a donor already closes a proposed mechanism, subsequent effort moves to a residual the donor does not explain rather than repeatedly renaming the same idea.

Q2 therefore treats “candidate disappears into prior work” as a successful research disposition, even though it is a negative publication result for that candidate.

## 10. What is executable about the method?

The methodology is not a prose philosophy. For each selected chain, the repository records:

- pre-outcome protocol identity;
- exact result receipt;
- authority/claim boundary;
- negative or positive disposition;
- successor protocol identity and chronology;
- independent verifier/replay where available.

The final Q2 package should expose a compact transition ledger with columns:

`predecessor | frozen claim | outcome | responsibility | donor disposition | successor | freeze-after-predecessor? | successor outcome | authority`.

A validator can check simple but consequential invariants:

1. successor protocol commit/time follows predecessor disposition;
2. successor result follows successor protocol;
3. old result/claim boundary remains byte-stable;
4. no negative is relabeled positive in the successor ledger;
5. donor-owned mechanisms receive no candidate novelty credit;
6. `CANNOT_CHECK` is not converted into numeric failure/success without new evidence.

This is the sense in which Q2's recovery discipline is executable.

## 11. Comparison with evidence-chain and benchmarking methods

ScientistOne's Chain-of-Evidence addresses whether claims can be traced to evidence and whether scores/references/method descriptions align. Q2 needs that kind of traceability, but it asks a later question: **once a claim has been correctly traced and found false or unsupported, what successor research transition is licensed?**

AstaBench and ScienceAgentBench improve rigor by controlling tools, tasks, costs and ground truth. Q2 does not replace such benchmarks. Its case study is about a single evolving research programme where the hypothesis space itself changes after exact counterexamples.

Preregistration prevents some forms of outcome-aware hypothesis editing. Q2 adds a typed successor relation and donor-first-refusal rule so that a preregistered failure becomes an active constraint on what may be tried next.

These distinctions are conceptual claims and require a fresh submission-date literature review. We therefore avoid claiming that no prior workflow has ever combined similar ideas.

## 12. Reproducibility / receipt index

A submission-ready Q2 should provide a reviewer-facing receipt index rather than expect readers to browse the full ORION history. Each representative chain should include:

- source protocol;
- source result;
- exact claim/disposition;
- successor protocol;
- successor result;
- replay/independent verification;
- companion paper owning the detailed scientific claim.

Quantum result numbers should be cited minimally in Q2. Q1 owns TARE expressivity mathematics; QG1 owns cross-family regime geometry; QG2 owns certified forecasting. Q2 uses those results only to show the transition discipline.

## 13. Limitations

**Single programme.** The evidence demonstrates that the methodology can be applied consistently in ORION-Q. It does not show that it improves discovery across laboratories, domains or agent architectures.

**Selection of case chains.** The final paper should state the full eligible transition inventory and the rule used to choose representative chains, so the narrative cannot cherry-pick only clean recoveries.

**Exact/synthetic bias.** Many ORION-Q problems have exact referees or exhaustive finite structure. Negative responsibility is harder to localize in noisy empirical sciences.

**Human/agent involvement.** The process may involve humans and multiple AI systems. Q2 does not claim autonomous methodological governance.

**Novelty search.** Internal donor searches are bounded and cannot self-certify external novelty. Submission requires a fresh primary-source search over autonomous research methodology, provenance, adaptive/preregistered experimentation and negative-result handling.

**Receipts are not truth.** Content-addressed replay proves identity/reproduction properties. A flawed scientific model can be perfectly receipted.

## 14. Discussion

The most important property of the case study is that the “best” scientific outcome changes form over time.

At one stage the useful result is an exact negative: common-anchor closure is false. At another it is a bounded positive: D++ closes the registered panels. Later it is a theorem: support two suffices all `n`. A prospective predictor then succeeds on a new subject but a broader extrapolation later fails. Each outcome is useful because the programme does not require every rung to be positive.

This alters the role of negative results. A negative is not merely something to archive for transparency. It can become a **constraint on the next scientific state**. The split counterexample says the next family must allow anchor separation. The borrow counterexample says a weight-one-only theory is insufficient. The QG5 mismatch says the support theorem is fine but the named borrow family is missing a feasible shape. The QG7 mismatch says that repair is still not a universal closed form.

The donor rule plays the same role for novelty. If prior work already provides the missing mechanism, the correct successor is not a renamed candidate—it is a narrower unresolved question.

The discipline therefore aims at **monotone scientific history rather than monotone positive scores**. Later research may overturn an extrapolation, but it should not make the record less truthful about what was known when each decision was made.

## 15. Conclusion

Evidence chains and reproducible execution are necessary for trustworthy automated research, but they do not determine how a research programme should evolve after a claim fails. ORION-Q provides a longitudinal case study of one executable answer: preserve the negative as typed state, localize its responsibility, give prior work first right of refusal, freeze the successor before its outcome, and keep every later disposition alongside rather than over the predecessor.

The result is not a guarantee of better science. It is a verifiable research-history invariant: **a later theorem, repair or positive result cannot erase the negative evidence that licensed it.**

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
# Recursive Recovery of Negative Scientific Results: A Fully Receipted Quantum-Computing Case Study

**Manuscript V2 — 2026-08-22.** This version updates the paper through the final closed ORION-Q programme, including R6Q/R6R/R6S and the completed N-lane receipts. `MANUSCRIPT_DRAFT_V1.md` is preserved as the earlier research snapshot. This paper claims a methodology/case study, not the quantum-mathematical novelty owned by Q1.

---

## Abstract

Autonomous research systems are increasingly able to propose hypotheses, implement experiments and produce papers, while provenance and reproducibility are becoming recognized prerequisites for trusting their output. A separate problem remains underdeveloped: **what should an auditable research programme do after a strong hypothesis fails?** Naive research loops can hide negatives, weaken gates after seeing outcomes, repeatedly rediscover donor methods, or narrow claims until something publishable survives. We present a receipt-first recovery discipline in which negative, absorbed, mixed, saturated and cannot-check outcomes are first-class terminals; strong existing methods receive first right of refusal; successor questions are frozen before their outcomes; and every result can be replayed from committed evidence.

We study the discipline through the complete ORION-Q quantum-computing programme. Early candidate mechanisms repeatedly collapse to generic or donor-composed baselines. A native R6 campaign then terminates at a frozen negative with a protected discriminator subject never opened. Exact successor grammars R6I/R6K/R6M again add zero value over donor envelopes. Rather than treating this saturation as a dead end, the programme reopens the explanatory question under frozen protocols. A 688,041,472-case local support-dominance audit explains the collapse but refutes the proposed global donor closure at a pre-declared Tag-coupling gap. A repaired family is refuted again by the converse frame-for-Tag trade. Support-two closure then succeeds on every registered finite domain; a structural regime predictor is fixed and prospectively confirmed on a previously unread public Hamiltonian; and the programme terminates with an all-`n` theorem showing that support three or larger can never strictly improve the frozen R6M grammar. Separately, four N-lanes show that some earlier full-knowledge negatives survive donor comparison while others reopen under partial knowledge or higher-order synthesis.

The contribution is not provenance alone and not a claim of autonomous scientific superiority. It is an executable pattern for **productive backtracking after negative results**: donor subtraction, prospectively frozen successors, explicit refutation branches, saturation/lower-bound terminals, and immutable replay. The single-programme scope prevents a general causal claim about scientific productivity; the case study instead demonstrates that the discipline can both suppress false novelty and preserve enough structure for a chain of negatives to end in a sharper theorem.

---

## 1. Why negative-result recovery is a separate research problem

Modern autonomous-science work increasingly emphasizes complete provenance. That emphasis is well justified: without a reopenable record of what was proposed, executed and measured, an agentic research result is difficult to audit or correct. Provenance, however, answers primarily **what happened**. It does not by itself specify **what research move is licensed after the result is negative**.

This distinction matters because scientific failure has several meanings that require different successors:

- a candidate may fail because a stronger known method already expresses it;
- an optimizer may fail because the benchmark class has a structural ceiling;
- an apparent negative may disappear under partial knowledge or a broader representation;
- a method may work on a proxy while fail under implementation-aware accounting;
- a closure conjecture may be false only at a sharply localized coupling gap;
- an experiment may be uncheckable because the available evidence is insufficient.

Treating all of these as “try another idea” encourages uncontrolled post-hoc search. Treating all of them as terminal failure loses scientific information.

ORION-Q therefore separates **evidence provenance** from a **recovery policy**. Every registered question is evaluated under a protocol frozen before its result. Its outcome receives a typed terminal. Only then may a successor be registered, with the previous terminal retained as an immutable premise rather than rewritten as an unsuccessful draft.

The complete programme closure packet is `development/orion-q-max-r0/PROGRAMME_CLOSURE_PACKET_2026-08-21.md`.

---

## 2. Recovery contract

### 2.1 Prospective freezing

Before a result-bearing run, each lane freezes:

- the scientific question;
- admissible subject/data access;
- candidate and donor families;
- resource/accounting definition;
- acceptance and refutation gates;
- stop rules;
- permitted terminal vocabulary.

If a world or implementation defect is found, it is handled by a separately recorded amendment/repair. A result does not license weakening the scientific gate that judged it.

### 2.2 Donor first right of refusal

A candidate earns incremental value only after comparison with the strongest faithfully composed known mechanism available under the same information and resource contract. A donor tie or win is not an experimental failure; it is the terminal **ABSORBED**.

This rule was load-bearing throughout ORION-Q. Several apparently specialized quantum-research mechanisms matched generic symbolic synthesis, canonical transforms, library learning, value-of-information planning, or existing TARE/Pauli constructions once the donor received the same facts.

### 2.3 Typed terminals

The programme distinguishes at least:

- **POSITIVE:** the prospectively frozen gates pass against the registered donor;
- **NEGATIVE:** the candidate fails while validity/hostile controls pass;
- **ABSORBED:** a known donor owns the observed value;
- **MIXED:** value survives only in a restricted regime and the restriction is part of the result;
- **SATURATED:** all registered successors in a declared class fail to leave residual value;
- **LOWER_BOUND_CLOSED:** a structural lower bound explains why no policy in the closed class can improve the target quantity;
- **CANNOT_CHECK:** the available evidence/instrument contract is insufficient for an honest verdict.

Negative and cannot-check outcomes remain in the record and can constrain later work.

### 2.4 Recovery is successor registration, not claim mutation

A negative result may motivate a new question, but the new question receives its own frozen protocol. The previous claim is never retroactively broadened/narrowed to fit the successor outcome.

This produces a research DAG rather than a sequence of overwritten hypotheses.

### 2.5 Exactness and replay

Where the scientific object is finite, the programme uses exact dynamic programs, independent brute-force controls, serialized witnesses and deterministic reruns. The shared research harness stores content-addressed capability receipts, supports deterministic replay, and keeps failed orchestration receipts separate from scientific evidence.

This paper uses that infrastructure as a measurement instrument but does not claim that provenance/receipt systems are unique to ORION; contemporary autonomous-science literature increasingly identifies provenance-complete experimentation as a core requirement.

---

## 3. The completed ORION-Q recovery arc

### 3.1 Early MAX ladder: useful state, repeated donor subtraction

R0–R3 established that typed/scoped research state can carry decision information while repeatedly showing that policy-level value disappears when a strong donor receives the same state.

- R0: scoped failure state improves success/cost relative to raw history in synthetic research worlds.
- R1: typed scoped state perfectly separates the registered operator-arbitration cases.
- R2: once the same complete typed state is given to a generic learner, transfer is perfect; no ORION-specific policy advantage survives.
- R3B: local independent receipts have an exact 1/2 ceiling on balanced hostile pairs while joint obligation binding reaches 1.0, but the mechanism is owned by existing ORION P7/P4 binding and is absorbed rather than rebranded as a new method.
- R3E: protected skill admission leaves a bounded positive in exact-synthetic scope, without establishing real quantum-algorithm invention.

The methodological point is that a positive-looking mechanism can be scientifically useful while still yielding zero novelty after donor subtraction.

### 3.2 R4–R5: implementation-aware positives and honest projection dependence

R4 supplies both positive and negative endpoints:

- grouped sparse-QSVT produces favorable low-overhead proxy results, but realistic grouped-unitary synthesis can erase the gain;
- split-TARE coefficient majorization yields a theorem for one normalization coordinate;
- fresh H2 falsifies one registered heterogeneous-pair hypothesis;
- public H2O gives a strong structural Pareto point on a real Hamiltonian.

R5 then demonstrates why representation quality cannot be summarized by a single proxy. On N2, internal representation cost improves substantially, but outer-resource projections disagree: one projection is worse, another better. The honest terminal is `FULL_R5_NOT_SUPPORTED` rather than a scalarized victory.

### 3.3 Native R6 campaign: a frozen negative remains negative

The R6 native campaign was driven end-to-end through the research harness. Its prospective gate returned

`R6_EARNED = NO`

and the protected stretched-N2 discriminator subject remained unopened.

This is an important control for the recovery methodology. The system had the technical ability to continue searching, but the registered promotion gate did not permit a stronger scientific claim.

### 3.4 Exact successor grammars: saturation onto donor envelopes

The programme then executed exact successor optimizations under prospectively frozen grammars.

- **R6I:** unrestricted rank-2 shared-Tag DP ties the donor on all open subject partitions.
- **R6K:** adding Restore factoring again collapses onto the corresponding donor.
- **R6M:** three-block exact joint optimization ties the R6L donor on all 30 open chemistry matchings.

At this point the registered open subjects provide no residual exact optimization value beyond the absorbed donor stack. A weaker research process could stop with “nothing works.” ORION-Q instead changes the question from **optimization** to **explanation**.

---

## 4. Explanatory recovery: from saturation to theorem

### 4.1 R6N: explanation succeeds locally, global closure is refuted

R6N freezes a support-dominance conjecture together with an explicit declared analytic gap: changing frame support can alter the minimum compatible shared Tag.

The local theorem side is extremely strong. Across complete R6M and R6I local domains, support-dominance inequalities have zero violations over **688,041,472 configurations**. This explains why the exact DPs repeatedly collapse onto simple low-support donors.

But the global closure conjecture fails exactly at the declared Tag-repair gap. A synthetic R6M instance has

`C_DP = 8 < 9 = C_R6L`,

using weight-one frames on different anchors and a weight-two shared Tag.

The lane therefore closes as a **refutation with a new regime**, not as the desired closure theorem.

### 4.2 R6O: repair the first gap, discover the converse gap

The next protocol enlarges the donor to `D+`: weight-one frames may choose arbitrary anchors and the minimum compatible shared Tag is allowed.

This repairs the R6N counterexample, but exact search finds a second regime. On hundreds of structured/random instances the unrestricted optimum spends support two on a cheap central frame branch to compress the Tag and improve Restore alignment. The smallest witness has

`C_DP = 5 < 6 = C_D+`.

The first trade pays Tag support for anchor freedom; the second pays frame support for Tag/Restore savings.

Again, the right terminal is refutation rather than post-hoc adjustment.

### 4.3 R6P: support-two finite closure

A new family `D++` permits frame support at most two. It matches the unrestricted optimum on every registered finite domain: exhaustive `n=1`, full structured `n=2`, seeded random panels, hostile panels, and all recorded chemistry matchings.

All 559 previously violating R6O instances are re-derived and closed with exact witnesses.

This is a strong finite-domain result, but its protocol explicitly leaves the all-`n` composition theorem open.

### 4.4 R6Q: finite-domain structural prediction

R6Q asks whether the first two discovered trades can predict donor exactness without calling the unrestricted DP. The selected split/borrow predicate has zero error on 9,771 registered instances, including two seeded held-out panels and the chemistry matchings.

The programme records this as finite-domain evidence. It does not elevate the taxonomy to all `n`.

### 4.5 R6R: prospective confirmation

A subject-selection rule is frozen before coefficient access and selects a previously unread public benzene DUCC2 Hamiltonian. The regime prediction is printed/digest-bound before the exact R6M referee runs.

All 15 matchings are predicted donor-exact and all 15 are confirmed.

This does not prove universal transfer, but it upgrades the evidence from retrospective fitting to a prospectively staged structural forecast.

### 4.6 R6S: all-`n` theorem

The final recovery step asks the precise unresolved question left by R6P: can support `>=3` ever be necessary?

R6S proves no. An `F_2^2` zero-sum subset exchange removes support-three-or-larger frame coordinates while preserving both anticommutation and Tag syndrome. The finite local cost obligation is an exhaustive 18,432-case inequality with zero violations. For every `n` and every admitted R6M instance,

`C_DP = C_D++`.

Together with R6O's exact support-one counterexample, the final Q1 analysis gives the sharp intrinsic support threshold `kappa_R6M = 2`.

The recovery sequence therefore ends not in “we eventually found something positive,” but in a substantially different object from the original candidate methods: a **normal-form theorem explaining the exact design-space boundary**.

---

## 5. N-lanes: when old negatives do and do not reopen

The N1–N4 lanes test a complementary question: whether negatives established under full knowledge remain meaningful when representation, access or epistemic state changes.

### 5.1 N1: several method-invention positives collapse to known parents

Parameterized schema induction, failure-conditioned grammar growth, costly verification and generated representation edits all look useful against weak finite baselines. Strong parents close the policy-level residuals:

- symbolic synthesis matches the parameterized schema;
- library learning reproduces the learned macro;
- ideal VOI matches the typed allocation policy exactly;
- canonical eigendecomposition reproduces the generated frame.

A machine-checked lower bound additionally closes the finite complete-edit-set benchmark class: if the candidate set is finite, verification exact, and the budget permits full enumeration, no ordering policy can improve solve rate over exhaustive search.

### 5.2 N2: one residual survives only under misspecification

Most registered route/resource successors produce no residual. A prospective crossover predictor initially beats frozen baselines, but a stronger model-selection donor absorbs the well-specified-world advantage. The candidate remains better only in the deliberately misspecified world.

The surviving claim is therefore **robustness to functional-form misspecification**, not a general predictive advantage.

### 5.3 N3: higher-order synthesis leaves bounded residuals

Four exact-synthetic families show residual value when the supplied donor grammar itself is too concrete or lacks the needed operator/representation language. Exact verifiers catch planted overgeneralization and donors correctly win the worlds in which supplied parametric structure suffices.

These are bounded mechanism signals, not real-quantum synthesis claims.

### 5.4 N4: partial knowledge changes the value of research state

Six frozen studies find value in typed/scoped partial-knowledge mechanisms: type-conditioned VOI, scoped reopening, Pareto-targeted verification, full-chain receipt transport, decision-coupled probing and typed remint/transport.

Q4 owns these mechanism claims. For Q2, their methodological role is narrower: they demonstrate that a negative established in a full-information benchmark does not automatically authorize closure after the epistemic contract changes.

---

## 6. What the case study demonstrates

### 6.1 Avoiding false novelty is an observable output

Several proposed mechanisms return exact negatives or donor absorptions despite initially favorable behavior. The programme preserves these outcomes rather than weakening comparison classes. This is valuable because current autonomous-research systems are known to struggle with scientific judgment and can produce polished but unsound or poorly calibrated claims.

### 6.2 Backtracking can be productive when the failure state is structured

R6 is the central example. The sequence

negative -> saturation -> explanatory lemma -> refutation -> repair -> second refutation -> finite closure -> prospective prediction -> all-`n` theorem

is not a generic property of retrying. Each transition depends on the previous terminal identifying a specific unresolved obligation.

### 6.3 Provenance is necessary but not the claimed novelty

The broader autonomous-science community now explicitly identifies provenance-complete experimentation as foundational. Q2 therefore treats immutable receipts as infrastructure. The research contribution under study is the **recovery layer above provenance**: typed terminals, donor-first subtraction, pre-frozen successors and saturation/lower-bound stop rules.

### 6.4 A negative can be more informative than a weak positive

The grouped-QSVT and R5 results illustrate why the programme does not maximize the number of positive terminals. A proxy win that disappears after implementation cost is less useful than a negative that identifies the missing resource coordinate. Likewise, a donor absorption can remove an entire false novelty direction.

---

## 7. Related autonomous-science context

End-to-end AI research automation is already established as a research direction, including systems that generate ideas, execute experiments, analyze results and write papers. Other 2026 work focuses specifically on AI-driven replication. Self-driving-laboratory reviews increasingly identify provenance completeness as a prerequisite for scalable autonomous science.

At the same time, recent evaluations show that current agents can automate substantial research engineering while still failing at open-ended scientific judgment, productive backtracking, evidence revision and research integrity. Work on publication bias in AI-scientist pipelines also emphasizes the danger of systematically losing null results.

Against this landscape, Q2 makes a deliberately narrower contribution. It does not ask whether ORION can conduct all science autonomously. It asks whether a research programme can make **negative-result transitions explicit, prospectively testable and replayable**, and presents one complete programme in which that discipline both suppresses false novelty and yields a later theorem.

A fresh bounded literature map is in `NOVELTY_RESEARCH_2026-08-22.md`.

---

## 8. Limitations

1. **One principal programme.** ORION-Q is a detailed case study, not a randomized or cross-domain evaluation of recovery methodology.
2. **Substantial synthetic evidence.** Several N-lane and early MAX results use exact synthetic worlds designed for mechanism isolation.
3. **Programme-designed successor space.** The framework controls how successors are frozen but does not prove that the initial set of possible successors is complete.
4. **No causal comparison to human research teams.** The paper does not show that this process is faster or more creative than expert science.
5. **Provenance is not truth.** Receipts preserve what happened; exact verifiers/independent evidence are still needed to establish scientific correctness.
6. **Later QG work continues the science.** The Q programme is closed under its own charter, but subsequent QG work refines the finite trade taxonomy. Closure means the registered Q questions reached terminals, not that quantum compilation is solved.

---

## 9. What would be required for a general top-tier methods claim

A broader successor study should apply the same recovery contract prospectively in multiple independent domains and compare against matched workflows such as naive agent iteration, strongest-donor-only stopping, and ordinary retry-with-review.

Pre-registered measurements should include:

- number of false novelty claims avoided;
- productive recoveries per negative terminal;
- evidence/time cost to terminal;
- frequency of theorem/validated-positive outcomes after recovery;
- calibration of SATURATED/CANNOT_CHECK decisions;
- whether the method generalizes outside the programme in which it was designed.

Until such a study exists, the current paper should be read as a **complete executable case study and methodology definition**.

---

## 10. Reproducibility

The closure packet binds the final programme status and receipt locations. Q2's `RECEIPT_INDEX_V2.md` lists the result artifacts used by this manuscript, including the final R6O–R6S and N-lane successors absent from the original index.

The programme's strongest claims are cross-owned rather than duplicated:

- Q1: TARE/R6 mathematical theorem and quantum-compilation interpretation;
- Q2: negative-result recovery methodology and programme arc;
- Q3: receipt/harness and dual-instrument benchmark;
- Q4: typed partial-knowledge mechanism studies.

This division prevents a methodological paper from taking scientific novelty credit for results whose mathematical statement belongs elsewhere.

---

## Related-work anchors

- MacKnight et al., *Provenance grounds trust in autonomous science*, Nature Computational Science (2026).
- *Towards end-to-end automation of AI research*, Nature (2026).
- Falck et al., *Training AI Scientists to Replicate Research*, arXiv:2608.13331 (2026).
- Canty and Abolhasani, *The past, present and future of self-driving laboratories*, Nature Reviews Chemistry (2026).
- Chauhan, *Dead Science Walking: Publication Bias and the AI Scientist Pipeline*, arXiv:2606.04220 (2026).

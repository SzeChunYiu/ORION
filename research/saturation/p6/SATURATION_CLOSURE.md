# P6 submission saturation closure

Date: 2026-08-19  
Normative paper: V2.1 / AIJ submission object.  
Successor #463/T1–T8 work remains excluded unless it falsifies this paper.

## One-sentence contribution

> P6 formalizes the extra scientific-admissibility semantics needed when familiar repair, dependency, effect, authorization and provenance mechanisms operate on scientifically certified state, and proves that computational/support preservation alone need not preserve scientific admissibility.

## Primary-source foundation verification

The historical parent records that were only `UNVERIFIED_SECONDARY` in stale PR #401 were independently verified from primary publisher records during saturation:

- Jon Doyle, *A Truth Maintenance System*, Artificial Intelligence 12(3):231–272 (1979), DOI 10.1016/0004-3702(79)90008-0.
- Johan de Kleer, *An Assumption-Based TMS*, Artificial Intelligence 28(2):127–162 (1986), DOI 10.1016/0004-3702(86)90080-9.
- de Kleer's companion *Extending the ATMS* and *Problem Solving with the ATMS* were likewise verified from the same 1986 Artificial Intelligence issue.
- Acar, Blelloch and Harper's *Adaptive Functional Programming* is bound to POPL 2002, pp.247–259, DOI 10.1145/503272.503296.
- Park and Sandhu's UCONABC is verified as ACM TISSEC 7(1):128–174 (2004), DOI 10.1145/984334.984339.

These are donor ownership, not P6 novelty evidence.

## Literature round B — formal systems / agent verification

Fresh primary-source pressure was tested against the theorem residual rather than keyword similarity.

- ETAS (arXiv:2607.17780) already gives typed effects, requested/handled/denied/committed event semantics, residual obligations, policy monitors and soundness for agent systems. P6 therefore owns none of effect typing or residual-obligation visibility.
- *Formal Verification of Agentic Systems over Operational Data* (arXiv:2608.03609) formalizes stateful tool-enabled agent deployments over relational data, FO-CTL requirements, preservation under finite-domain restriction and a canonical wrapper. This is strong current verification precedent, but its property is system/workflow specification preservation rather than scientific-certificate admissibility after epistemic repair.
- *Proof of Execution: Runtime Verification for Governed AI Agent Actions* (arXiv:2607.05397) provides runtime guarantees for authorization, path compliance, null effect on deny, history integrity and replayability. These are donor/context pressure on execution governance; they do not collapse the P6 typed-erasure separation.
- 2025 AAAI sound/complete generalized-planning abstraction work and situation-calculus temporally lifted abstractions are direct precedent for abstraction/refinement preservation. P6 therefore makes no generic abstraction novelty claim.

Round B terminal: `NO_MATERIAL_THEOREM_OR_CLAIM_CHANGE`.

## Literature round C — planning abstraction / authorization / incremental semantics

An alternate search across abstraction-refinement, planning verification, usage control, self-adjusting computation and authorization again returned parent mechanisms rather than a P6 replacement:

- sound and complete abstraction in generalized planning provides formal refinement guarantees for plans/goals;
- UCON provides authorization/obligation/condition continuity and mutability;
- self-adjusting computation proves consistency with from-scratch semantics under dynamic change propagation;
- current agent authorization papers narrow tool authority and bind policy/intent/request identities.

None decides whether an unchanged computational/support result may retain a **scientific certification** whose admissibility additionally depends on evidence, provenance, obligations and commit authority.

Round C terminal: `NO_MATERIAL_THEOREM_OR_CLAIM_CHANGE`.

Two consecutive fresh rounds therefore close literature saturation for V2.1. Reopen only if a donor-complete formalism proves the same scientific-admissibility separation under equivalent semantics or a new countermodel falsifies a V2.1 theorem.

## Theorem-by-theorem nearest-parent audit

| P6 object | Strongest parent pressure | Residual / nonclaim |
|---|---|---|
| root-inclusive reopening | TMS/ATMS, dependency repair | changed certified root must be included; no novelty for selective invalidation |
| safety vs minimality | dependency abstractions, abstraction/refinement | sound over-approximation does not imply graph-descendant minimality; minimax theorem needs affected-realizability |
| preservation/revalidation | incremental computation, repair, authorization | scientific certificate continuity distinguished from recomputation/support reuse |
| footprint-faithful commutation | effect/process/separation traditions | hidden semantic reads defeat declared separation; current-state equality only under faithful full scientific separation |
| obligation persistence | ETAS/effect systems/UCON | donor-owned residual obligations; P6 only carries them into scientific admissibility |
| authority non-escalation | authorization/UCON/FAVA | donor-owned authorization; P6 does not claim generic permission logic |
| recursive audit | P1/internal + termination methods | boundary only; no P6 novelty claim |
| typed-erasure separation | integrated donor product | main residual: identical bare computation/dependency semantics can differ in scientific admissibility |

## Hostile theorem review — round 1

### R1 formal novelty reviewer
Attack: P6 is a relabelled product of TMS + effects + authorization.
Resolution: component novelty is rejected. The publishable object is the separation/admissibility law over their composition, with explicit conservative donor embeddings and ideal donor-product baseline.
Verdict: no unresolved major/blocking concern.

### R2 proof/premise reviewer
Attack: root-descendant minimality was previously over-strong; declared footprints can hide ambient reads.
Resolution: V2.1 already contains the spurious-edge countermodel, affected-realizability premise, direct-root treatment and footprint-fidelity counterexample. These are normative, not footnotes.
Verdict: no unresolved major/blocking concern.

### R3 AI relevance/reproducibility reviewer
Attack: finite checkers do not prove usefulness for real agents.
Resolution: manuscript labels them bounded consistency/countermodel support; empirical superiority is not claimed. The paper motivates the semantics via current agent effects/repair/authorization systems and supplies deterministic reproduction.
Verdict: no unresolved major/blocking concern.

## Hostile theorem review — round 2

- **Reduction attack:** if scientific obligations/authority/provenance are inert, P6 must reduce to donor-native transition/dependency semantics. The manuscript explicitly states those conservative special cases.
- **Ideal-product attack:** an information-equivalent ideal donor product may tie P6. The paper accepts that; no universal superiority claim remains.
- **Successor contamination attack:** T1–T8 higher-order revision/control work is not needed to state or prove V2.1 and is excluded from this submission.

Second round: no new unresolved major/blocking concern.

## Venue/style closure

Primary: **Artificial Intelligence (AIJ)**. Fallback: **JAIR**.

Core presentation rules:

1. definition/theorem order follows the failure it repairs;
2. every theorem states assumptions before consequence;
3. countermodels sit adjacent to the over-strong statement they defeat;
4. donor ownership appears before the residual, not as an afterthought;
5. finite checkers are labelled bounded formal support, not empirical agent results;
6. programme-internal P1/P5/P8 ownership remains explicit;
7. no successor formalism is imported merely to make the paper look larger.

JAIR requires no scientific broadening; it is a packaging/style fallback over the same V2.1 object.

## Citation/reference audit

The current AIJ submission already cites the main donor families and has 0 undefined citations/references in the candidate PDF gate. Historical TMS/ATMS identities above are now primary-source verified. Current preprints should be replaced by archival versions at actual submission if one exists; that is a final metadata refresh, not a claim change.

## Formal/checker/reproduction audit

Normative checker set remains:

- `check_theory_closure_v2.py`;
- `check_theory_closure_v2_1.py`;
- hostile assumption regressions and merged candidate tests;
- content binding / SHA256 package checks;
- candidate PDF build/audit.

No new statistical inference is manufactured for theorem enumerations. Counts from finite checkers are exact bounded enumeration facts only.

## Whole-paper invariant

Forbidden drift:

- `dependency repair` -> P6 novelty;
- `effect typing` -> P6 novelty;
- `authorization/provenance` -> P6 novelty;
- graph soundness -> minimality without affected-realizability;
- declared R/W names -> commutation without semantic footprint fidelity;
- successful recomputation -> scientific certificate preservation;
- P6 successor T1–T8 -> current-paper evidence.

Terminal: `P6_SATURATION_CONVERGED__NO_MANUSCRIPT_CLAIM_CHANGE_REQUIRED`.

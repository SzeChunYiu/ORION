# #463 formal saturation and scientific closure review V1

**Subject base:** `main@b7abcc6ad76d2a985ea938fcbd070a6097b0fe99`  
**Closure protocol frozen:** `development/p6-successor-formal-closure/README.md` before the new checker.  
**Status in this document:** recommendation only until exact-head CI, merge, and host issue disposition.

## Question

Does the implemented T1–T8 successor stack support a scientifically distinct *unified* calculus, or are its load-bearing mathematical ingredients products of mature formalisms joined by a useful ORION-specific typed/non-authorizing interface?

## Round 1 — direct ingredient parents

The search/read pass targeted each proposed mathematical primitive rather than terminology matching.

### Responsibility / minimal diagnosis

Reiter (1987) already defines first-principles diagnosis from a system description plus observations. de Kleer & Williams (1987) explicitly compute minimal fault candidates and select measurements to localize faults. Grastien, Haslum & Thiébaux (`arXiv:2309.16180`) generalize diagnosis to arbitrary hypothesis spaces equipped with a preference relation.

**Disposition:** competing responsibility hypotheses, preference/minimality, and discriminating observations are parent-owned. Keep only the ORION scientific-coordinate/authority interface.

### Minimal / iterated revision

AGM (1985), Dalal (1988), Katsuno–Mendelzon (1991), Darwiche–Pearl (1997), and later semantic generalizations already supply minimal-change and richer-epistemic-state foundations for revision.

**Disposition:** generic minimal change and iterated epistemic state are parent-owned. The T1 write/preservation/authority preorder remains a bounded design contract, not a universal theorem of scientific rationality.

### Interface sufficiency

Blackwell comparison of experiments and the state-abstraction/sufficient-statistic literature already own generic task-relevant information sufficiency.

**Disposition:** #459/T3 can register and route explicit sufficiency checks, but cannot claim sufficiency theory.

### Computation allocation

Horvitz, Russell–Wefald, and Hay et al. already formalize computation as a decision/metareasoning action with cost/value.

**Disposition:** #458/T4 adopts rational metareasoning. ORION's narrower design rule is that external scientific obligations/authority are not scalar utility and therefore cannot be compensated by value of computation.

### Containment

Viability/control-invariance and control-barrier-function theory already formalize admissible safe regions separately from performance optimization.

**Disposition:** T5 adopts safe-set/viability structure. The useful ORION interface explicitly prevents a containment receipt from becoming a truth certificate.

### Social evidence

Aumann establishes common-knowledge structure; Bayesian information-aggregation work such as Clemen (1987) explicitly treats overlapping/dependent information.

**Disposition:** T6 does not own common knowledge, testimony dependence, or evidence fusion. Its bounded provenance check is an interface into scientific evidence authority.

### Minimal repair / persistent information

Database-repair theory already uses minimally changed repairs and identifies information that persists across repairs.

**Disposition:** preservation across alternative minimal repairs is parent-owned in broad form. P6/P7 retain their typed scientific dependency/reopen interface.

## Round 1 consequence

`MATERIAL_CHANGE = YES`: the proposed headline **one unified higher-order epistemic calculus** loses novelty ownership. The implementation remains useful, but its mathematical ingredients must be cited/adopted as separate mature components.

## Round 2 — hostile subsumption / adjacent-formalism search

The second round searched for either:

1. a **single existing formalism** that already subsumes the complete ORION product, which would force `EXISTING_FORMALISM_SUFFICIENT`; or
2. a genuinely new cross-component mathematical primitive that survives the Round-1 attribution and would justify a stronger #463 terminal.

Pressure routes included:

- generalized model-based diagnosis and preferred hypotheses;
- semantic/general AGM and iterated revision;
- decision/information ordering and abstraction;
- metalevel MDP/value-of-computation formulations;
- viability/safe-set control;
- dependent-information fusion and epistemic logic;
- minimal database repairs/persistent truths;
- ORION's already-existing P6 typed mechanics and P8 non-compensatory authority.

### Round-2 result

No additional primitive is required to state the surviving ORION design contracts. Conversely, no one parent found in the round supplies the entire cross-domain product *including ORION's existing scientific authority/preservation interfaces* as a single formal object.

`MATERIAL_CHANGE = NO` relative to the Round-1 narrowed conclusion.

A follow-up search over adjacent repair/epistemic/fusion formalisms again changed attribution detail but did not change the closure disposition: separate mature formalisms + typed composition interface.

## Scientific result

The evidence supports a **negative unification result**:

> T1–T8 should not be presented as a newly discovered universal calculus of scientific revision. Their useful residual is a versioned, typed, non-authorizing composition discipline that connects mature diagnosis, belief-change, sufficiency, metareasoning, safe-set and social-evidence formalisms to ORION's P6/P8 preservation/authority boundaries.

This is scientifically useful because it removes an over-broad theory claim while preserving executable interfaces that make cross-component authority mistakes testable.

## What survives

- claim-relative typed read/write footprints;
- explicit hard evidence and authority obligations;
- explicit preservation/reopen obligations;
- fail-closed unresolved states;
- no arbitrary escalation past narrower unresolved candidates;
- computation value separated from scientific authority;
- containment separated from correctness;
- provenance dependence separated from independent evidence;
- read-only T7 composition into the framework.

These are **ORION design/interface commitments**, not claimed as independently novel mathematical primitives.

## What is struck

- generic minimal diagnosis as ORION novelty;
- generic minimal revision as ORION novelty;
- generic information sufficiency as ORION novelty;
- value-of-computation/metareasoning as ORION novelty;
- generic safe-set/containment mathematics as ORION novelty;
- common-knowledge/dependent-testimony theory as ORION novelty;
- minimal-repair persistence as ORION novelty;
- the headline claim that these components constitute a new universal higher-order calculus.

## Finite falsification layer

`HigherOrderFormalFiniteClosure.v1` uses the actual merged T1–T7 implementations. The pre-frozen finite contract contains 32 revision signatures and exact expected counts:

- preorder reflexivity: 32/32;
- transitivity witness triples: 1,024;
- strict-minimality ordered pairs: 211;
- narrower unresolved blocks broader escalation;
- incomparable minima remain plural;
- missing authority blocks regardless of cost;
- hard computation obligations outrank optional high-value computation;
- local compute stop does not close the scientific task;
- containment cannot promote truth;
- shared social provenance cannot count as independent;
- incomplete social provenance remains unresolved;
- T7 controller remains non-authorizing.

These expectations were frozen before the exact-head CI outcome. A checker failure reopens implementation; it does not get repaired by changing the expected scientific terminal.

## Closure recommendation

If and only if the exact-head checker and repository CI are green:

`FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS`

This closes **#463 only**.

It does not close:

- #500/#501 scientific Jump/regime invention;
- #507 recursive atom studies;
- #452 global responsibility taxonomy;
- #454 structural assimilation process;
- #455/T8 protected empirical Self-ORION efficacy;
- P5 readiness.

## Paper disposition

The current P6 V2.1 paper stays unchanged. Its saturation lane correctly classifies T1–T8/#463 as successor-additive.

The successor manuscript should state the negative result directly: the framework adopts mature component theories and retains a typed scientific-admissibility integration layer. Future papers may consume that interface, but cannot cite #463 as evidence that ORION invented diagnosis, minimal change, metareasoning, containment, social epistemics, or a universal calculus.

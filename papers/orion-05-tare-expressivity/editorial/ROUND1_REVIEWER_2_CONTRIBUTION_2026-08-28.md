# Frozen simulated Reviewer 2 report

Date: 2026-08-28  
Status: mutually blind simulated review, not external peer review  
Frozen object: commit `6a639e13b5fa162da3405a219e6ae83de2abf525`  
Lens: contribution, nearest prior work, target-specific significance and utility

No live literature search, working-tree files, other reviewer reports, or later revisions were used. Journal-policy and literature currency were not independently refreshed by this reviewer.

## Overall assessment

The paper establishes a clean but narrow result for one fixed six-target, three-block, shared-label grammar and one support-count objective. Every optimum has a support-two representative, support one fails on an exact two-qubit witness, and support-two enumeration gives a direct $O(n^9)$ word-RAM upper bound. The paper appropriately preserves the adverse runtime result and disclaims hardware, fault-tolerant-resource, general-compiler, and performance implications.

The exact combination may be original, but the frozen material does not establish external novelty authority. More importantly for venue selection, it does not yet explain why this bespoke objective and fixed grammar matter beyond their formalization, nor whether the $O(n^9)$ algorithm improves the prior worst-case state of the art. These are significance and positioning objections, not objections to the theorem's stated correctness.

- **Contribution/originality:** plausible narrow residual; priority not established.
- **Target-specific significance:** insufficient for PRX Quantum and below the frozen record's threshold for *Quantum*.
- **Utility:** formal and diagnostic in the current manuscript.
- **Recommended posture:** specialist formal/theory retarget unless substantial generalization or an independently meaningful consequence is added.

## Strengths

1. The claim boundaries distinguish exact normal form from speed, resources, and hardware.
2. The upper theorem and explicit $5<6$ obstruction make the threshold clear.
3. All six direct-solver full-subject timeouts remain visible.
4. The paper subtracts the base Tag-and-Restore method, anticommuting partitioning, phase-gadget and parity-sharing ideas, Pauli compiler optimization, universality, stabilizer foundations, and Hamiltonian weight reduction.
5. The review archive is usable as bounded evidence, not external validation.

## Major concerns

### OR05-R2-M01 — The residual contribution is not demarcated precisely enough from the donor method and nearest compiler literature

**Severity:** Major  
**Blocking:** Yes for originality evaluation and both requested targets; not a theorem-correctness objection

The frozen related-work section is a defensible disclaimer, but not a decision-grade comparison. It does not map which grammar elements and objective terms are inherited, specialized, modified, or introduced, nor compare optimized objects and guarantees against the closest Pauli compilers and synthesis approaches.

**Resolution test:** Supply a source-verifiable contribution crosswalk. Map the donor primitive, frames, shared-label constraint, target pairing, factorization, objective coefficients, and optimization domain. Mark each component as inherited, specialized, modified, or new. Compare neighboring work by scientific object, exactness or approximation, ancillary degrees of freedom, preserved quantity, support restriction, and theorem guarantee. Retain no priority language.

### OR05-R2-M02 — The scientific motivation for this exact grammar and objective is too weak for the requested venues

**Severity:** Major  
**Blocking:** Yes as a target-significance and utility blocker

The theorem depends on a fixed grammar, a two-unit sharing discount, and frame-support coefficients two and four. The paper honestly calls this a logical coordinate rather than a physical model. It does not show that optimizing this coordinate answers a broad compilation question, characterize representative workload frequency, or derive a downstream resource consequence.

**Resolution test:** Complete one of three routes: derive and demonstrate an operational consequence; generalize to a nontrivial parameterized family; or contract the venue and present the work explicitly as a fixed-model formal note. Exposition alone does not resolve this concern for PRX Quantum or *Quantum*.

### OR05-R2-M03 — The $O(n^9)$ result lacks a same-problem complexity baseline

**Severity:** Major  
**Blocking:** Yes for presenting the bound as a state-of-the-art advance

The paper does not prove a worst-case time or memory bound for the unrestricted comparator or closest exact method on the identical grammar. The adverse finite runtime removes practical performance as a substitute.

**Resolution test:** Define input representation and word size; give a same-model comparator bound; state whether any asymptotic axis improves. If none is proved, label the result a constructive exact-solvability corollary rather than algorithmic advancement. Preserve the adverse runtime outcome.

## Minor concerns

- **OR05-R2-m01:** Identify the exact donor version and precise source locations for inherited machinery.
- **OR05-R2-m02:** Replace the single-basket compiler comparison with a structured comparison by scientific object and guarantee.
- **OR05-R2-m03:** Make the search cutoff and query families reviewer-visible.
- **OR05-R2-m04:** Explain how $n$ grows while the grammar retains six targets and relate $n$ to input length.

## Venue judgments

### PRX Quantum

Not a defensible fit in the frozen form. The fixed grammar and nonphysical objective provide neither a broadly reusable principle nor a compiler/resource benefit. The minimum credible route is substantial theorem generalization or an independently validated resource consequence.

### Quantum

Closer than PRX Quantum, but still a significance mismatch. Correctness and exactness do not by themselves establish a significant state-of-the-art advance for a fragile, fixed objective with adverse practical performance.

### Strong specialist formal/theory venue

Potentially suitable after contribution cross-mapping, objective motivation, and complexity-claim narrowing.

This is a simulated Reviewer 2 assessment, not a journal decision, external peer review, novelty certificate, or acceptance prediction.

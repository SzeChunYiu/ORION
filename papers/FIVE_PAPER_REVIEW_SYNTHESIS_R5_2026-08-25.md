# Five-Paper Hostile Review Synthesis R5

Date: 2026-08-25

Review target: recovered V3 manuscripts plus the five R4 mathematical addenda on branch `research/five-paper-math-r3-20260825`.

Review standard: a selective mathematical journal should be able to separate theorem, donor result, model assumption, executable evidence, application implication, and unresolved claim. Reviewers were instructed to search for counterexamples before improving prose.

## 1. Council discussion protocol

The internal expert council used five independent lenses.

1. **Additive combinatorics:** zero-sum definitions, inverse theorems, multiplicity arithmetic, rank reductions.
2. **Compiler realization:** abstract-to-production maps, semantic deletion soundness, objective ownership.
3. **Information theory:** minimax quantifiers, randomized estimators, query-specific representation sufficiency.
4. **Logic and complexity:** least-fixed-point semantics, finite proof supports, intervention reductions.
5. **Skeptical editor:** novelty boundaries, application overreach, reproducibility, title/abstract eligibility.

A finding was closed only after the relevant mathematical reviewer and the skeptical editor agreed on one of four dispositions:

- `ACCEPTED`: proved and appropriately scoped;
- `ACCEPTED_WITH_BOUNDARY`: correct only with an explicit assumption or donor boundary;
- `OPEN_GATE`: plausible or desirable but not proved;
- `REJECTED_CLAIM`: false, unsupported, or owned by a different model.

## 2. Portfolio-level findings

### Finding P0 — historical state mattered more than surface polish

**Concern.** The V2 surfaces were not a safe base. Paper D's least/greatest-fixed-point equivalence and the non-quantum absent-point saturation step were invalid.

**Response.** Recover the complete formally audited V3 state before adding mathematics.

**Disposition.** `ACCEPTED`. All R4 work is based on V3, not the defective V2 surfaces.

### Finding P1 — “top-tier ready” is not a proof status

**Concern.** A manuscript may be correct yet lack standalone novelty, production realization, broad significance, or a complete exact theorem.

**Response.** Maintain separate ledgers for correctness, novelty, reproducibility, and editorial readiness.

**Disposition.** `ACCEPTED`. No paper is promoted solely by stronger rhetoric or an application paragraph.

### Finding P2 — application language can silently expand theorem scope

**Concern.** Quantum, AI, regulatory, and coding applications are attractive but can make a formal structural theorem sound empirically validated.

**Response.** Every application now states theorem bridge, artifact, validation requirement, and prohibited overclaim.

**Disposition.** `ACCEPTED_WITH_BOUNDARY`.

## 3. Paper A review

### A-M1 — direct-sum equality requires axis separation

**Concern.** For an arbitrary alphabet in `H_1 direct_sum H_2`, cross-coordinate letters can couple the components, so simple additivity need not hold.

**Author response.** State the alphabet exactly as

`(A_1 x {0}) union ({0} x A_2)`

and prove both directions by splitting a word into coordinate-axis subwords.

**Disposition.** `ACCEPTED`.

### A-M2 — the quotient theorem has only one safe direction

**Concern.** A quotient can collapse nonzero sums and therefore cannot generally provide an upper bound on the source invariant.

**Author response.** State only

`zsf(H;A)>=zsf(K;phi(A))`

and interpret it as a lower obstruction to an aggressive support claim.

**Disposition.** `ACCEPTED`.

### A-M3 — the multiplicity program is finite but not automatically efficient

**Concern.** Calling the formulation “computable” could be read as polynomial-time tractability.

**Author response.** Bound every multiplicity by the order of its letter, formulate exact submultiset constraints, and explicitly decline a polynomial-time claim.

**Disposition.** `ACCEPTED_WITH_BOUNDARY`.

### A-M4 — approximate normalization may destroy optimality

**Concern.** When deletions increase the objective, the final state is not another optimum.

**Author response.** Report a feasible support-normalized state with additive defect relative to `OPT`; do not call it optimal.

**Disposition.** `ACCEPTED`.

### A-E1 — production significance remains unproved

**Concern.** The abstract grammar is motivated by a compiler, but a high-selectivity compiler journal will ask whether the support cap changes a production-relevant workload or resource.

**Author response.** Preserve the abstraction boundary and identify a production-realization study as an editorial gate.

**Disposition.** `OPEN_GATE`.

### Paper A decision

**Decision:** mathematically strengthened selective-specialist candidate; not yet a top-tier compiler submission.

**Reason:** the theorem package is coherent and new at the level of the declared model, but the production significance argument is incomplete.

## 4. Paper B review

### B-M1 — abstract terminal exactness does not imply intrinsic compiler exactness

**Concern.** The V3 abstract standard-basis word proves a terminal lower bound only in the abstract deletion language.

**Author response.** Add a four-part production-realization criterion: normalization, production preimage, move representation, and nonreducibility under every named production rule.

**Disposition.** `ACCEPTED` for the criterion; factor-five production interpretation remains `OPEN_GATE`.

### B-M2 — product lower bounds require product lower witnesses

**Concern.** Component upper normalizations compose automatically, but intrinsic lower bounds can fail when objectives or transformations couple components.

**Author response.** Require Cartesian-product feasibility, additive objective, no cross-component moves, and one lower-witness instance per component.

**Disposition.** `ACCEPTED_WITH_BOUNDARY`.

### B-M3 — enumeration exponents are architecture-specific

**Concern.** `Theta(n^B)` for support enumeration is not an algorithm-independent lower bound.

**Author response.** Define the exact enumerator volume

`V_B(n)=sum_{j=0}^B binom(n,j)q^j`

for fixed `B,q`, prove its leading degree, and restrict all consequences to that architecture.

**Disposition.** `ACCEPTED`.

### B-N1 — is the realization criterion itself enough for a standalone paper?

**Concern.** The framework is rigorous, but a selective journal may regard it as methodology without a flagship realized separation.

**Council discussion.** The compiler reviewer favored merging it with Paper A unless several production systems instantiate the criterion. The skeptical editor agreed: a framework paper needs either multiple exact case studies or one striking strict separation.

**Disposition.** `OPEN_GATE`.

### Paper B decision

**Decision:** hold as standalone top-tier submission; retain as a rigorous companion or merge candidate.

**Reason:** the central reporting distinction is valuable, but the strongest numerical production example remains unrealized.

## 5. Paper C review

### C-M1 — deterministic minimax quantifiers

**Concern.** The estimator chooses one value per representation fiber; the adversary then chooses the hidden instance. The theorem must not swap these quantifiers.

**Author response.** Prove fiberwise

`inf_z max_{x in F_y}|z-T(x)|=d_y/2`

and then take the maximum over fibers.

**Disposition.** `ACCEPTED`.

### C-M2 — randomization might help

**Concern.** A randomized estimator could potentially distribute error between the two endpoints.

**Author response.** Use pointwise triangle inequality for absolute loss and the endpoint-average identity for squared loss. Both show a deterministic midpoint is minimax.

**Disposition.** `ACCEPTED`.

### C-M3 — optimizer-property labels must handle nonunique optima

**Concern.** “The optimum has a triple” is ambiguous when several optima exist.

**Author response.** Freeze predicates such as “every optimum contains a triple” or “some optimum contains a triple,” and prove the classifier lower bound only for a well-defined Boolean instance property.

**Disposition.** `ACCEPTED_WITH_BOUNDARY`.

### C-N1 — the midpoint theorem is classical

**Concern.** A general fiber-radius theorem alone is not sufficient novelty.

**Author response.** Explicitly assign two-point minimax and midpoint logic to donor mathematics. Claim novelty in the exact compiler constructions: identical complete low-order representations, solved values, scalable additive and high-order gaps, and separation between value, optimizer structure, and unary-optimality decision.

**Disposition.** `ACCEPTED_WITH_BOUNDARY`; final literature comparison remains required.

### C-R1 — exact family proofs are load-bearing

**Concern.** Every broad information conclusion depends on exact equality of the frozen features and exact solution of the target optimum in both family members.

**Author response.** Keep the V3 family proofs in the main theorem chain and require an independent hostile replay before submission.

**Disposition.** `OPEN_GATE` for external replay, not for the abstract minimax corollaries.

### Paper C decision

**Decision:** top-tier theory candidate after independent proof replay and primary-source overlap audit.

**Reason:** it has the best combination of exact theorem, scalable construction, broad interpretive reach, and honest donor boundary.

## 6. Paper D review

### D-M1 — least and greatest fixed points are not interchangeable

**Concern.** Unsupported positive cycles can carry arbitrary authority at a greatest fixed point but none at the least fixed point.

**Author response.** Use the least fixed point exclusively; retain a visible two-node unsupported-cycle counterexample.

**Disposition.** `ACCEPTED`.

### D-M2 — coordinatewise decomposition

**Concern.** Rule caps and body intersections could couple licenses.

**Author response.** Project onto one Boolean coordinate `lambda`. Membership in a cap and membership in every body authority are Boolean conditions; each license therefore follows an independent positive Horn closure.

**Disposition.** `ACCEPTED`.

### D-M3 — recursive rules may generate infinitely many proof trees

**Concern.** The hitting-set theorem refers to minimal proof footprints; their family must be finite.

**Author response.** Claims are finite, so footprints are subsets of a finite claim set. Although syntactic proof trees may repeat nodes, only finitely many distinct footprints exist; take inclusion-minimal realized footprints.

**Disposition.** `ACCEPTED`.

### D-M4 — intervention hardness reduction

**Concern.** The target might survive under a different proof path not represented by the hitting-set instance.

**Author response.** In the reduction, the only target rules are `{p_j}->q`; each `p_j` has exactly one conjunctive support `E_j`. The target survives exactly when one set `E_j` is completely unhit.

**Disposition.** `ACCEPTED`.

### D-N1 — overlap with provenance and resilience

**Concern.** Minimal witnesses, hitting sets, query resilience, and abduction have established literatures.

**Author response.** Do not claim generic novelty for hitting-set provenance. Claim the paper-specific least-fixed-point license semantics, caps, direct-refutation behavior, proof-footprint theorem, and evaluation/intervention boundary. Require a primary-source comparison before submission.

**Disposition.** `OPEN_GATE` for novelty calibration.

### D-A1 — applications need one faithful encoding

**Concern.** Evidence, regulation, and agent provenance are currently theorem-backed possibilities, not validated case studies.

**Author response.** Add exact application contracts and require one fully worked graph with domain-reviewed semantics.

**Disposition.** `OPEN_GATE`.

### Paper D decision

**Decision:** strong specialist or broad-theory candidate after overlap audit and one worked application.

**Reason:** the NP-complete intervention theorem gives a genuine spine, but editorial distinctiveness depends on how the semantics differs from existing provenance frameworks.

## 7. Non-quantum review

### NQ-M1 — applicability of Property C at `n=5`

**Concern.** The boundary proof depends on a rank-two inverse theorem, not merely `eta(C_5^2)=13`.

**Author response.** State Property C as an external donor theorem and use only its exact consequence: every length-12 5-short-free sequence in `C_5^2` is `T^4` with `|T|=3`. Add the original/modern donor citation in the final bibliography.

**Disposition.** `ACCEPTED_WITH_BOUNDARY`.

### NQ-M2 — repeated terms in `T`

**Concern.** Property C permits a length-three sequence notation; the three terms must be shown distinct before reading off `c_4=3`.

**Author response.** If two terms coincide, that group element occurs at least eight times in `T^4`, contradicting the established multiplicity cap four and, independently, producing five equal copies.

**Disposition.** `ACCEPTED`.

### NQ-M3 — rank-one boundary

**Concern.** Property C is rank two; a low-rank sequence could lie in a cyclic subgroup.

**Author response.** Exclude rank one first using `D(C_5)=5`: any five terms in the cyclic subgroup contain a nonempty zero sum of length at most five.

**Disposition.** `ACCEPTED`.

### NQ-M4 — the boundary conclusion

**Concern.** Does `H=T^4` really force support 22?

**Author response.** `H` contains only multiplicity-two and multiplicity-four support points. Three distinct fourfold terms imply `c_4=3,c_2=0`; then `c_2=31-s-3c_4` gives `s=22` and `c_1=19`.

**Disposition.** `ACCEPTED`.

### NQ-E1 — exact threshold remains open

**Concern.** Closing one rank diagonal does not prove `C_0(31)` or the exact generalized Davenport constant.

**Author response.** Keep the manuscript conditional and state the residual atom-overlap, support-classification, and next-diagonal gates explicitly.

**Disposition.** `OPEN_GATE`.

### Non-quantum decision

**Decision:** publishable specialist structural advance; not an exact-value top-tier submission.

**Reason:** the new inverse argument is genuine and useful, but the central obstruction is not eliminated.

## 8. Cross-paper consistency review

### 8.1 Terminology

- `intrinsic support` is reserved for all-instance upper normalization plus a matching optimum lower witness.
- `certificate complexity` is tied to a named proof language.
- `terminal complexity` is used for the abstract shortening system.
- `representation fiber` is the inverse image of a frozen feature map.
- `authority` is a least-fixed-point license set, not truth.
- `rank forcing` concerns the span of the repeated stratum, not the whole support.

**Disposition:** `ACCEPTED`.

### 8.2 Donor boundaries

- finite-group and Property-C donor theorems are cited as external;
- generic minimax midpoint logic is not claimed as new;
- generic hitting-set hardness is not claimed as new;
- the papers claim the model-specific constructions, reductions, or realization criteria.

**Disposition:** `ACCEPTED_WITH_BOUNDARY` pending final bibliography verification.

### 8.3 Reproducibility

The superseding verifier checks small zero-sum invariants, product arithmetic, minimax radii, the intervention reduction on every subset of a finite example, and the new non-quantum diagonal. It passes. Full theorem verification still requires human replay and the external Property-C source.

**Disposition:** `ACCEPTED` as a finite sanity layer.

## 9. Final editorial ranking

1. **Paper C:** advance to top-tier theory pre-submission audit.
2. **Paper D:** advance to overlap audit and worked-application integration.
3. **Paper A:** advance to selective-specialist draft; production relevance determines higher tier.
4. **Non-quantum:** advance as a specialist structural note; continue exact-threshold research separately.
5. **Paper B:** retain as a rigorous companion/merge candidate until production realization is closed.

This ranking is not a judgment of long-term potential. It reflects the current ratio of proved theorem strength to unresolved flagship interpretation.
# QG-13 V2 / QG-9 — combined R6I deletion theorem protocol

Date frozen: 2026-08-21.
Parent programme: ORION-QG #740. Theorem-miner parent: #767 / QG-13 V1.
Scientific target owner: QG-9 #762.
Parent theorem: canonical QG-1 rank-2 all-n generator-support <=5 theorem.

Status: **FROZEN BEFORE REPOSITORY V2 OUTCOME**. Exploratory scratch algebra found the candidate below; the repository checker must independently recover every stated finite count and may refute any of them. No repository result was read when choosing the V2 edit grammar or gates.

Authority ceiling: bounded machine-checked theorem attempt over the frozen R6I grammar. No novelty authority, no R6 authority, no physical quantum-advantage claim.

## 1. Scientific question

Canonical QG-1 proves that every optimum in the frozen R6I rank-2 shared-2-bit-Tag grammar admits each independent generator with support <=5. The proof treats non-coincidence SOLO moves and coincidence PAIR moves separately, yielding `5 = 3 + 2`.

V2 asks whether a richer but still local production edit grammar eliminates the support-five boundary:

> Does every QG-1-irreducible support-five generator pattern admit a semantics-preserving combined local deletion with non-increasing objective, implying an all-n support <=4 normal form?

## 2. Frozen edit grammar

At one block and one qubit, with local independent generator letters `(r0,r1)` and dependent `r2=r0*r1`, the only V2 actions are:

- `d0`: set `r0 -> I`, leave `r1`, recompute `r2`;
- `d1`: set `r1 -> I`, leave `r0`, recompute `r2`;
- `db`: set both `r0,r1 -> I`, recompute `r2=I`.

`d0` exists only when `r0 != I`; `d1` only when `r1 != I`; `db` only when both are nonidentity. No target, Tag, permutation, central choice or other qubit is changed.

No rewrite synthesis is performed. Quartz/QSymb/superoptimization/equality-saturation rule discovery is donor territory and receives zero novelty credit.

## 3. Exact semantic change coordinate

For one block use five conserved bits

`v = (<R0,R1>, <S0,R0>, <S1,R0>, <S0,R1>, <S1,R1>) in F_2^5`.

For every realizable local `(r0,r1,s0,s1)` and action, compute the exact `before XOR after` five-bit signature from production Pauli symplectic algebra. A multi-column action is semantics-preserving iff the XOR of its local signatures is zero.

Zero total signature preserves block anticommutation and both Tag syndromes of both independent generators. Because anticommutation remains one, both generators remain nonzero/rank two. Dependent `R2` and its label are recomputed, not assumed independent.

## 4. Exact local objective domain

The frozen R6I objective is qubit-additive and has no Restore factor coupling. For each local `(r0,r1)` pair, meaningful action, central branch in `{0,1,2}`, and target triple `(p0,p1,p2) in {I,X,Y,Z}^3`, compute exact

`Delta C = C_after - C_before`

including all three frame multipliers and all three Restore supports with dependent `r2` recomputed.

Unique cost domain target: **6,336** cases. Semantic signature domain target: **528** realizable local action rows over all Tag-letter pairs. The checker must derive these counts, not skip them.

For each semantic descriptor/action record the worst local delta separately for each common central choice. For a multi-column move, the proof uses `sum_q max_local_delta(q, central)` and then the worst of the three common central choices. This is a valid adversarial upper bound for every target configuration because the R6I objective is additive over qubits.

## 5. Descriptor quotient and QG-1 irreducibility

A local semantic descriptor is

`(active0, active1, coincidence, alpha, beta00, beta10, beta01, beta11)`

with
- `alpha=<r0,r1>`;
- `beta i0=<Si,r0>`;
- `beta i1=<Si,r1>`.

The checker enumerates all local Pauli/Tag letters and quotients by this descriptor. Exploratory expected count: **28 realizable descriptor types**. The official run must recover this independently.

For a selected generator `R0` whose support is exactly `w`, enumerate multisets of `w` descriptors with `active0=1`. Keep only patterns that can occur in a QG-1 support-minimal optimum:

1. XOR alpha over the selected support is one;
2. the selected generator's two-bit Tag label is nonzero;
3. the coincidence-class multiset has no nonempty zero-sum subset in F2^2;
4. the selected generator's non-coincidence classes have no nonempty zero-sum subset in F2^3;
5. the partner generator's non-coincidence classes **within these columns** have no nonempty zero-sum subset (otherwise canonical QG-1 already has a SOLO move).

No condition is imposed on partner-only qubits outside the selected support; this makes the theorem robust to arbitrary completion of the other generator and its final label.

Exploratory expected irreducible counts:
- support five: **324** descriptor multisets;
- support four: **432** descriptor multisets.

## 6. Combined-move search

For each irreducible pattern, enumerate the Cartesian product of `{none,d0,d1,db}` restricted by action availability. A candidate move must:

- be nonempty;
- XOR to zero in the five semantic coordinates;
- delete at least one selected-generator letter;
- have worst total local-cost upper bound <=0 for **every** common central choice.

Deterministic selection order minimizes `(worst_cost, -selected_support_drop, -total_support_drop, action_word)`.

### V2 theorem gate

Every support-five irreducible pattern must have such a move.

Exploratory target:
- 324 / 324 reducible;
- 288 strictly cost-decreasing;
- 36 cost ties with strict support descent.

### Boundary / anti-overclaim gate

Run the identical grammar on support-four irreducibles. Exploratory target:
- 432 irreducible support-four patterns;
- exactly 36 have **no** certified combined move under this grammar.

This is a hard anti-overclaim boundary. A positive V2 may claim support <=4 only; it may not claim support <=3 or tightness of four.

## 7. All-n theorem composition

Use canonical QG-1 as a parent theorem, opened only after the V2 local theorem packet is built.

Choose, among globally optimal configurations, one minimizing total independent-generator support. QG-1 guarantees all four generators have support <=5.

If some generator has support five:

- if canonical QG-1 SOLO/PAIR applies, support-minimality is already contradicted;
- otherwise its local descriptor multiset is one of the V2 support-five irreducibles;
- the V2 zero-signature combined move preserves semantics and has non-increasing cost, while strictly reducing total support;
- ties still contradict lexicographic support minimality.

Thus no support-five generator occurs in a support-minimal optimum, and every optimum admits all four generators with support <=4.

Symmetry under swapping `R0/R1` and blocks `A/B` is machine-checked.

## 8. Parent and donor checks

The official run binds:
- production R6I Pauli algebra / DP identity;
- canonical QG-1 authority and support-five theorem;
- QG-13 V1 protected recovery receipt as permission to open V2;
- no chemistry/protected-subject access.

Hostile prior-art scan credits Symphony/PHOENIX++ global BSF simplification, stabilizer/Clifford normal forms, Pauli-based compilation, and generic finite-group support arguments. No novelty authority is granted by this run.

## 9. Dual harness

Generic ORION verifier independently regenerates the 28 descriptors, action signatures, 6,336 local-cost cases, support-five/support-four irreducible multisets and combined-action search from primitive Pauli algebra. It must not import the V2 checker module.

Native ORION-Q sees only serialized checker/generic artifacts and may `ACCEPT_SUPPORT4 / REJECT / CANNOT_CHECK`. It must retain:
- `support3_authority=false`;
- `tightness4_authority=false`;
- `novelty_authority=false`.

## 10. Honest terminals

- `QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED`
- `QG13_V2_SUPPORT5_PATTERN_REFUTATION_FOUND`
- `QG13_V2_LOCAL_COST_BOUND_REFUTED`
- `QG13_V2_PARENT_COMPOSITION_GAP`
- `QG13_V2_NATIVE_GENERIC_DISAGREEMENT`
- `QG13_V2_CANNOT_CHECK`

A finite pattern search is theorem-relevant here only because QG-1 already reduces all-n support to <=5 and V2 exhausts the complete semantic descriptor quotient of the remaining support-five case.

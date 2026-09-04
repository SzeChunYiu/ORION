# Paper 2 top-specialist theorem spine — V3

Status: **reconciled dependency and authority map for a top-specialist manuscript development track**. This file is intentionally shorter than the reader-facing draft. It records what is proved, how the results depend on one another, and what remains open.

The package does **not** prove `D_3(C_7^3)=36`, does not classify all length-37 obstructions, and does not certify novelty, priority, or venue acceptance.

## Proposed title

**Representation-depth rigidity and support growth in the first multiwise Davenport corridors of elementary rank-three groups**

## Reader-facing draft

`PAPER2_MANUSCRIPT_DRAFT_V1.md`

## Central method

For a maximal zero-sum atom `U`, define

`rho_U(z)=min{|T|:T|U, sigma(T)=z}`.

A companion subsequence `W` violates inherited short-zero-freeness exactly when

`|W|+rho_U(-sigma(W))`

is below the corridor threshold. Exact formulas for `rho_U` convert a global packing problem into modular residue inequalities.

A canonical support-four maximal atom has

`U_a=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-a^(-1)(e1+e2)`,

and length

`boxed{|U_a|=3p-2}`.

At `p=7`, this is the length-19 atom in the maximal corridors `(8,10,19)` and `(9,9,19)`. The first-corridor companion length is `(3p-1)/2=3H+1`, not the maximal-atom length.

## Main theorem suite

### A. Exact type-`a=2` overlap and radial staircase

For `p=2H+1`,

`c_light=2 floor(H/2)`

and

`lambda_{2,c}(D)=D+2 ceil(max(D-c-2,0)/2)`.

**Authority:** analytic integration-lane theorem.

**Files:**

- `A2_EXACT_OVERLAP_AND_RADIAL_STAIRCASE_V1.md`
- `check_a2_exact_overlap_and_radial_staircase_v1.py`
- `A2_RADIAL_STAIRCASE_HOSTILE_AUDIT_V1.md`
- `verify_a2_radial_staircase_independent_v1.py`

The latter pair is independent audit evidence, not duplicate theorem authority.

### B. Exact type-`a=2` depth-fiber envelope

For `w=[P+Q]_p`, the maximum

`M_p(w,C)=max rho_U(P,Q,C)`

over the fiber `[P+Q]_p=w` has a complete four-region piecewise formula with explicit sharp witnesses.

**Authority:** analytic.

**Files:**

- `A2_EXACT_DEPTH_FIBER_ENVELOPE_V1.md`
- `check_a2_exact_depth_fiber_envelope_v1.py`

### C. Exact arbitrary-type overlap-plane lifting cost

For targets `C s+D g`, the exact cost is the two-variable minimum `nu_a(C,D)` in

`SUPPORT4_EXACT_OVERLAP_PLANE_LIFTING_COST_V1.md`.

**Authority:** analytic.

**Files:**

- `SUPPORT4_EXACT_OVERLAP_PLANE_LIFTING_COST_V1.md`
- `check_support4_overlap_plane_rank3_scalar_v1.py`

### D. Complete type-`a=3` support-three rank-two closure

For every prime `p>=7`, the type-three rank-two equality face is empty. Exact inverse-three radial depth, a donor-owned cyclic length-four index-one theorem, and explicit right- and left-half multipliers close every boundary row.

**Authority:** analytic, donor-dependent at the index-one step.

**Principal files:**

- `A3_EXACT_RADIAL_EXCESS_V1.md`
- `A3_BOUNDARY_INDEX_ONE_DONOR_REDUCTION_V1.md`
- `A3_RIGHT_HALF_BOUNDARY_ELIMINATION_V1.md`
- `A3_LEFT_HALF_BOUNDARY_ELIMINATION_V1.md`
- corresponding replay checkers

### E. Generic rank-three reductions for `a>=4`

The reconciled V8 chain proves:

1. `c_light+c_heavy<=a-2`;
2. doubling eliminates every box with smaller new-value multiplicity greater than `H`;
3. every survivor lies on a thin boundary;
4. scalar three removes the central part and leaves four explicit edge regimes.

**Authority:** analytic reductions, not full closure.

**Files:**

- `SUPPORT4_SIMULTANEOUS_OVERLAP_SUM_BOUND_V1.md`
- `SUPPORT4_RANK3_A_GE4_DOUBLING_BOUNDARY_REDUCTION_V1.md`
- `SUPPORT4_RANK3_A_GE4_TRIPLE_CENTRAL_BOUNDARY_V1.md`
- their three replay checkers

### F. Type-`a=2` top-overlap standard families

For prime `p>=13`, `p==1 (mod 4)`, no top-overlap companion survives when the high-multiplicity value has form

`(A,-A,1)` or `(A,-A,2)`.

The upper half is closed by a half-step, quarter-step, or complemented quarter-step according to `floor(p/b)` and `b mod 4`.

**Authority:** analytic conditional-family theorem.

**Files:**

- `A2_MAXIMAL_OVERLAP_STANDARD_FAMILIES_EMPTY_V1.md`
- `check_a2_maximal_overlap_standard_familIES_v1.py`

**Open interface:** classify every power-compatible high-multiplicity value into these standard fibers, apart from the bounded central exceptions.

### G. Exact `p=7` rank-three equality-face closure

For the type-two length-19 atom in corridor `(8,10,19)`, exact overlap leaves six multiplicity rows. Occurrence-level depth leaves fourteen ordered parameter pairs after separate power tests. Every pair has an explicit mixed zero-sum certificate of length at most eight.

**Authority:** exact finite theorem with direct certificates.

**Files:**

- `P7_A2_RANK3_SUPPORT4_EQUALITY_EMPTY_V1.md`
- `check_p7_a2_rank3_support4_exception_table_v1.py`

### H. Two-corridor `C_7^3` support-six exclusion

If a hypothetical length-37 obstruction over `C_7^3` contains a support-four length-19 atom, then it cannot remain in the support-six maximal-pair face in either maximal corridor.

- `(8,10,19)`: pair support six is empty already at the `19+10` stage.
- `(9,9,19)`: 26 support-six maximal pairs have 1634 short-free completions, and both structurally independent exact verifiers four-pack all 1634.

**Authority:** composite analytic/explicit-certificate and dual-verifier finite theorem.

**Principal files:**

- `P7_A2_RANK3_SUPPORT4_EQUALITY_EMPTY_V1.md`
- support-three layer eliminations for types `a=1,2,3`
- `SUPPORT6_9919_CLOSURE_V1.md`
- `search_support6_9919_closure_v1.cpp`
- `verify_support6_9919_independent_v1.cpp`

## Proof dependency graph

1. First-failure reduction isolates a length-`3p-2` support-four maximal atom and inherited short-zero thresholds.
2. Canonical normalization reduces the maximal atom to `U_a`.
3. Exact radial, fiber, and overlap-plane formulas provide certificate costs.
4. Support-six normal forms split rank-two support-three from rank-three support-four companions.
5. Prime-uniform rank-two theorems close heavy sharing, all interiors, type three, and bounded exceptional layers.
6. Prime-uniform rank-three theorems reduce `a>=4` to four edge regimes.
7. The inverse-quarter theorem closes the standard type-two top-overlap families.
8. The fourteen-entry table closes the remaining `p=7` first-corridor rank-three face.
9. Two independent executables close the `p=7` second-corridor support-six completion face.
10. The combined support-growth theorem follows.

## Reproducibility surfaces

- `PAPER2_REPRODUCIBILITY_MANIFEST_V1.json`
- `run_paper2_reproduction_v1.py`
- `PAPER2_ATOMIC_CLAIM_LEDGER_V1.json`
- `check_paper2_atomic_claim_ledger_v1.py`
- `.github/workflows/shadow-davenport-paper2-a2-breakthrough.yml`

The C++ builds must retain assertions; `-DNDEBUG` is forbidden.

## Atomic open gaps

1. Type-`a=1` light-share rank-two layers `c>=5`.
2. Type-`a=2` light-share rank-two layers `c>=5`, including the standard-family classification interface.
3. The four `a>=4` rank-three edge regimes.
4. Exceptional rank-three types `a=2,3` for general prime.
5. A support-seven augmentation theorem spanning both `C_7^3` corridors.
6. Maximal atoms of support at least five.
7. The support-eight one-projective-collision Type-A face.
8. The exact value `D_3(C_7^3)=36`.

## Claim ceiling

The strongest current claim is:

> exact representation-depth formulas and support-growth theorems exclude the support-six maximal-pair face in both maximal `C_7^3` corridors, while the all-prime support-six equality problem is reduced to explicit high-overlap and rank-three edge regimes.

The package must not state or imply:

- `D_3(C_7^3)=36`;
- all-prime first-corridor support seven;
- a complete length-37 obstruction classification;
- novelty or priority certification;
- top-generalist submission authority.

## Readiness verdict

There is enough mathematical substance for a **top-specialist manuscript development track**: exact analytic calculus, multiple prime-uniform reductions, a nontrivial two-corridor `C_7^3` theorem, explicit terminal certificates, dual independent verification, a one-command reproduction path, and a fail-closed claim ledger.

External mathematical review, database/thesis prior-art subtraction, independent reimplementation or formal replay of the fourteen-entry classifier, and manuscript polishing remain required before submission.

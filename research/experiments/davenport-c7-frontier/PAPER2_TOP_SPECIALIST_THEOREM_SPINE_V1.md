# Paper 2 top-specialist theorem spine — V2

Status: **reconciled theorem-dense specialist-paper spine ready for full manuscript development**. This version incorporates the Paper-2 V8 rank-three reductions, removes duplicate `a=2` radial authority, and separates analytic theorems, donor-dependent reductions, exact finite closures, and independent audits.

The package supports a strong structural/computer-assisted zero-sum paper. It does not support an exact-value announcement for `D_3(C_7^3)`, a top-generalist venue claim, or a novelty certificate.

## Proposed title

**Representation-depth rigidity and support growth in the first multiwise Davenport corridors of elementary rank-three groups**

A more `C_7^3`-forward alternative is:

**Exact representation depth and support-six exclusion in the maximal corridors of `C_7^3`**

## Provisional abstract

We study the first nontrivial multiwise Davenport corridors in elementary abelian groups of rank three through the geometry of a maximal zero-sum atom and the representation depth it induces on a companion atom. For the canonical support-four maximal type with light multiplicity two, we determine the exact light-overlap ceiling, radial lifting cost, and a complete piecewise-linear maximum depth envelope on every affine coordinate-sum fiber. For arbitrary canonical type, we derive an exact two-dimensional overlap-plane lifting cost. This yields prime-uniform support-sharing reductions: the light multiplicity-three rank-two face is empty for every prime `p>=7`; simultaneous overlap for types `a>=4` is sharply bounded; doubling and scalar three collapse the generic rank-three face to four explicit edge regimes; and an inverse-quarter rotation selector eliminates both standard high-multiplicity families on the maximal type-two overlap face. At `p=7`, the remaining type-two rank-three support-four equality face reduces to fourteen ordered parameter pairs, each admitting an explicit mixed zero-sum certificate of length at most eight. Combined with two structurally independent exhaustive verifiers for the second maximal corridor, these results show that in both maximal `C_7^3` corridors a hypothetical packing obstruction containing a support-four maximal atom cannot remain in the support-six maximal-pair face. The result is a support-growth theorem and a reproducible proof architecture, not a determination of `D_3(C_7^3)`.

## 1. Central thesis

The unifying object is the **representation-depth function**

`rho_U(z)=min{|T|: T|U, sigma(T)=z}`

of a fixed maximal atom `U`.

A companion subsequence `W` is forbidden exactly when

`|W|+rho_U(-sigma(W))`

falls below the inherited short-zero threshold. Once `rho_U` is explicit, support sharing becomes a finite family of residue inequalities rather than an unconstrained search in `C_p^3`.

The manuscript should present every finite computation as a terminal reduction after analytic normalization, not as the source of the mathematical statement.

## 2. Main theorem suite

### Theorem A — exact type-`a=2` overlap and radial calculus

For `p=2H+1>=7`, the exact reusable light multiplicity is

`c_light=2 floor(H/2)=2 floor((p-1)/4)`,

and for every allowed overlap `c` and target `1<=D<=p-1`,

`lambda_{2,c}(D)=D+2 ceil(max(D-c-2,0)/2)`.

The proof excludes wrapped representations and splits the inverse-of-two residue into even and odd classes.

**Authority:** analytic integration-lane theorem.

**Canonical files:**

- `A2_EXACT_OVERLAP_AND_RADIAL_STAIRCASE_V1.md`
- `check_a2_exact_overlap_and_radial_staircase_v1.py`

**Independent audit:**

- `A2_RADIAL_STAIRCASE_HOSTILE_AUDIT_V1.md`
- `verify_a2_radial_staircase_independent_v1.py`

The audit extends the replay to the full formal capacity range, freezes the first optimizer, and rejects a floor-rounding mutation; it does not create a second theorem-authority surface.

### Theorem B — exact type-`a=2` depth-fiber envelope

For `p=2H+1`, the maximum of `rho_U(P,Q,C)` over every fiber `[P+Q]_p=w` has a complete four-region piecewise formula. Every maximum has an explicit sharp witness.

This is the paper’s strongest reusable method theorem. It compresses three coordinates to the pair `(w,C)` and exposes the singular middle fiber `w=H` and endpoint fiber `w=p-1`.

**Authority:** analytic with explicit witnesses.

**Files:**

- `A2_EXACT_DEPTH_FIBER_ENVELOPE_V1.md`
- `check_a2_exact_depth_fiber_envelope_v1.py`

### Theorem C — exact overlap-plane lifting in rank three

For the canonical maximal atom

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

with `g=s-a^(-1)(e1+e2)`, the exact `U`-cost of an overlap-plane target `C s+D g` is

`nu_a(C,D)=min (z+q+2[a^(-1)(q-D)]_p)`

over

`0<=z<=a`, `0<=q<=p-a`, `z+q==C+D (mod p)`.

This removes the free geometry of the two new values from the first scalar attack on a rank-three support-four companion.

**Authority:** analytic integration-lane theorem.

**Files:**

- `SUPPORT4_EXACT_OVERLAP_PLANE_LIFTING_COST_V1.md`
- `check_support4_overlap_plane_rank3_scalar_v1.py`

### Theorem D — complete type-`a=3` rank-two face elimination

For every prime `p>=7`, no exact-support-six first-corridor support-three rank-two companion survives in the canonical type-`a=3` light-share face.

The proof combines:

- exact inverse-three radial depth;
- a capacity-aware length-four index-one donor reduction;
- explicit elimination of the right half `e<=f`;
- explicit elimination of the complementary left half `e>f`.

**Authority:** analytic. The cyclic length-four index-one theorem is donor-owned and must remain explicitly attributed.

**Principal files:**

- `A3_EXACT_RADIAL_EXCESS_V1.md`
- `A3_BOUNDARY_INDEX_ONE_DONOR_REDUCTION_V1.md`
- `A3_RIGHT_HALF_BOUNDARY_ELIMINATION_V1.md`
- the committed left-half closure and its independent replay

### Theorem E — generic rank-three reductions for `a>=4`

For canonical types `a>=4` with both overlap directions available:

1. the exact reuse ceilings satisfy
   
   `c_light+c_heavy<=a-2`;
2. if the smaller new-value multiplicity exceeds `H`, doubling produces a zero-sum of length exactly `p-1`;
3. every survivor lies on the thin boundary
   
   `r=H-k`, `t=p-(c+d)+k`, `0<=k<=c+d-1`;
4. scalar three eliminates every boundary box satisfying the four central capacity inequalities, leaving only four explicit edge regimes.

**Authority:** analytic integration-lane theorem chain.

**Files:**

- `SUPPORT4_SIMULTANEOUS_OVERLAP_SUM_BOUND_V1.md`
- `check_support4_simultaneous_overlap_sum_bound_v1.py`
- `SUPPORT4_RANK3_A_GE4_DOUBLING_BOUNDARY_REDUCTION_V1.md`
- `check_support4_rank3_a_ge4_doubling_boundary_reduction_v1.py`
- `SUPPORT4_RANK3_A_GE4_TRIPLE_CENTRAL_BOUNDARY_V1.md`
- `check_support4_rank3_a_ge4_triple_central_boundary_v1.py`

This chain is a major all-prime reduction, not a complete elimination of the `a>=4` rank-three face.

### Theorem F — maximal-overlap standard-family exclusion for type `a=2`

For prime `p>=13`, `p==1 (mod 4)`, the top light-overlap face cannot have its high-multiplicity value in either standard family

`y=(A,-A,1)` or `y=(A,-A,2)`.

The upper noncentral half is closed by a three-case selector:

1. a half-step when `floor(p/b)=2`, `b==1 (mod 4)`;
2. a quarter-step when `floor(p/b)=2`, `b==3 (mod 4)`;
3. a complemented quarter-step when `floor(p/b)>=3`.

The selected power has a uniform positive depth margin.

**Authority:** analytic conditional-family theorem.

**Files:**

- `A2_MAXIMAL_OVERLAP_STANDARD_FAMILIES_EMPTY_V1.md`
- `check_a2_maximal_overlap_standard_families_v1.py`

The remaining gap is the prime-uniform classification that forces a power-compatible high-multiplicity value into these standard fibers, apart from bounded central exceptions.

### Theorem G — explicit `p=7` rank-three equality-face closure

For the canonical type-`a=2` length-19 atom over `C_7^3`, the rank-three support-four length-10 companion face has six multiplicity rows. Separate power tests leave exactly fourteen ordered parameter pairs. Every one has an explicit mixed zero-sum certificate of length `4`, `6`, `7`, or `8`.

**Authority:** exact finite theorem with occurrence-level depth and direct vector certificates.

**Files:**

- `P7_A2_RANK3_SUPPORT4_EQUALITY_EMPTY_V1.md`
- `check_p7_a2_rank3_support4_exception_table_v1.py`

### Theorem H — two-corridor `C_7^3` support-six exclusion

Let a hypothetical length-37 packing obstruction over `C_7^3` contain a support-four length-19 maximal atom.

- In corridor `(8,10,19)`, every maximal pair of total support six is impossible already at the `19+10` stage.
- In corridor `(9,9,19)`, the exact support-six maximal-pair universe has 26 pair candidates; all 1634 short-free completions by the second length-9 atom admit four disjoint zero-sums, independently confirmed by two different verifiers.

Therefore, in either maximal corridor, a surviving obstruction with a support-four maximal atom must escape the support-six maximal-pair face.

**Authority:** composite theorem: analytic/explicit-certificate first-corridor closure plus dual-verifier exact finite second-corridor closure.

**Principal files:**

- `P7_A2_RANK3_SUPPORT4_EQUALITY_EMPTY_V1.md`
- the support-three elimination files for canonical types `a=1,2,3`
- `SUPPORT6_9919_CLOSURE_V1.md`
- `search_support6_9919_closure_v1.cpp`
- `verify_support6_9919_independent_v1.cpp`

## 3. Proof dependency graph

The reader-facing proof should follow this order:

1. **First-failure reduction.** Convert a hypothetical `D_3` counterexample into three atoms and the two maximal length corridors.
2. **Maximal-atom normal form.** Reduce a support-four length-`(3p-1)/2` atom to canonical type `a`.
3. **Representation depth.** Define `rho_U`, derive the bounded resource formula, then specialize to exact radial, fiber, and overlap-plane costs.
4. **Support-sharing normal forms.** Separate rank-two support-three and rank-three support-four companions.
5. **Prime-uniform rank-two eliminations.** Present heavy-share closure, all light types `a>=3`, and the residual `a=1,2` high-overlap interface.
6. **Prime-uniform rank-three reductions.** Present simultaneous overlap, doubling, and scalar-three boundary collapse.
7. **Inverse-quarter rotation.** Eliminate the type-two standard high-multiplicity fibers.
8. **`C_7^3` terminal face.** Give the six rows and fourteen explicit mixed certificates.
9. **Second corridor.** State the 26-pair/1634-completion theorem and explain verifier independence.
10. **Support-growth conclusion.** Combine both corridors and state the exact remaining frontier.

The manuscript should avoid interleaving discovery chronology with the proof.

## 4. Computational-proof architecture

The finite `C_7^3` statements meet a credible computer-assisted-proof standard because the decisive predicates are replayed independently.

### First corridor

- Depth is computed from the actual 19 occurrences of the maximal atom.
- The closed support-four depth formula is used only as an independent cross-check.
- Every terminal survivor has a human-readable count-vector certificate whose vector sum and capacity are checked directly.
- Removing any one certificate leaves exactly one unresolved ordered case.

### Second corridor

The two implementations disagree structurally at every decisive layer:

- depth oracle versus direct bounded count enumeration;
- cardinality-indexed subset sums versus occurrence-mask minimum depth;
- small-block search versus pair-union/complement matching.

The manuscript should include pseudocode, exact census tables, hashes, compiler versions, and a one-command replay appendix.

## 5. Recommended paper structure

1. Introduction and statement of results
2. Multiwise Davenport first-failure framework
3. Canonical support-four maximal atoms
4. Representation-depth calculus
5. Exact radial, fiber, and overlap-plane theorems
6. Prime-uniform rank-two eliminations
7. Prime-uniform rank-three boundary reductions
8. Inverse-quarter rotation on the top-overlap face
9. The explicit `C_7^3` rank-three exception table
10. The `(9,9,19)` dual-verifier closure
11. Combined support-growth theorem
12. Reproducibility and hostile verification
13. Remaining frontier and limitations

Appendices:

- cyclic index-one donor statement and attribution;
- full piecewise fiber table and sharp witnesses;
- fourteen `C_7^3` certificates;
- complete machine-readable census receipts.

## 6. Figures and tables that materially help

1. The two maximal corridors `(8,10,19)` and `(9,9,19)`.
2. A support-sharing diagram separating support-three/rank-two and support-four/rank-three faces.
3. A heat map of the exact `M_p(w,C)` envelope, emphasizing `w=H` and `w=p-1`.
4. The four-regime V8 rank-three boundary after doubling and scalar three.
5. The inverse-quarter selector on the cyclic rotation orbit.
6. The six-row/fourteen-certificate `C_7^3` terminal table.
7. A verifier-independence matrix for the second corridor.

## 7. Atomic open gaps

The bounded paper does not require these gaps to be closed, but they determine whether a stronger all-prime sequel or exact-value paper is possible.

1. Prove the high-multiplicity classification forcing the type-`a=2` top-overlap value into `(A,-A,1)` or `(A,-A,2)`, with the bounded central exceptions explicitly handled.
2. Eliminate the rank-two light type `a=1`, overlap `c>=5`.
3. Eliminate the remaining rank-two light type `a=2`, overlap `c>=5`, including lower-than-top overlap layers.
4. Close the four `a>=4` rank-three edge regimes after the V8 reductions.
5. Close the exceptional rank-three types `a=2,3` prime-uniformly.
6. Establish a support-seven/rank-three augmentation theorem covering both `C_7^3` corridors without finite enumeration.
7. Close maximal atoms of support at least five.
8. Resolve the support-eight one-projective-collision Type-A packing face.
9. Only after those steps reconsider `D_3(C_7^3)=36`.

## 8. Claim ceiling

The strongest current reader-facing claim is:

> exact representation-depth formulas and support-growth theorems exclude the smallest support-four maximal-pair face in both maximal `C_7^3` corridors, while all-prime support-six equality is reduced to explicit high-overlap and rank-three edge regimes.

The manuscript must not state or imply:

- `D_3(C_7^3)=36`;
- a complete classification of all length-37 obstructions;
- all-prime closure of the type-`a=1` or type-`a=2` high-overlap faces;
- complete elimination of the V8 rank-three edge regimes;
- independent novelty or priority;
- top-journal acceptance authority.

## 9. Readiness assessment

### Ready

- one coherent analytic method based on representation depth;
- exact radial, fiber, and overlap-plane calculus;
- multiple prime-uniform eliminations and boundary reductions;
- a nontrivial two-corridor `C_7^3` headline;
- explicit terminal certificates;
- dual independent verification in the larger finite closure;
- branch-scoped CI replay;
- an honest claim boundary and nearest-work audit.

### Required before submission

- external mathematical audit of the exact type-two fiber envelope and inverse-quarter selector;
- external prior-art subtraction through MathSciNet, zbMATH, theses, and citation networks;
- independent reimplementation of the fourteen-entry `C_7^3` classifier or a formal proof-assistant replay;
- conversion to a concise LaTeX manuscript;
- a referee-facing data and code availability statement;
- author-level decision on venue and novelty language.

### Verdict

There is enough mathematical substance for a **top specialist-paper development track**. The result is not yet an exact generalized-Davenport paper and should not be marketed as one. Its strength is the exact depth calculus, all-prime support-sharing rigidity, and independently reproducible finite closure.

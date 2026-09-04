# Paper 2 top-specialist theorem spine — V1

Status: **theorem-dense specialist-paper spine ready for full manuscript development**. The package supports a strong structural/computer-assisted zero-sum paper. It does not support an exact-value announcement for `D_3(C_7^3)`, a top-generalist venue claim, or a novelty certificate.

## Proposed title

**Representation-depth rigidity and support growth in the first multiwise Davenport corridors of elementary rank-three groups**

A more C7-forward alternative is:

**Exact representation depth and support-six exclusion in the maximal corridors of `C_7^3`**

## Provisional abstract

We study the first nontrivial multiwise Davenport corridors in elementary abelian groups of rank three through the geometry of a maximal zero-sum atom and the representation depth it induces on a companion atom. For the canonical support-four maximal type with light multiplicity two, we determine the exact radial lifting cost and a complete piecewise-linear maximum depth envelope on every affine coordinate-sum fiber. For the light multiplicity-three type, explicit scalar constructions eliminate the entire rank-two support-three companion face for every prime `p>=7`. On the top-overlap multiplicity-two face for primes `p==1 (mod 4)`, an inverse-quarter rotation selector eliminates both standard high-multiplicity families. At `p=7`, the remaining rank-three support-four equality face reduces to fourteen ordered parameter pairs; each admits an explicit mixed zero-sum certificate of length at most eight. Combining these analytic reductions with two structurally independent exhaustive verifiers for the second maximal corridor shows that, in both maximal `C_7^3` corridors, a hypothetical packing obstruction with a support-four maximal atom cannot have a maximal pair of total support six. The result is a support-growth theorem and a reproducible proof architecture, not a determination of `D_3(C_7^3)`.

## 1. Central thesis

The paper’s unifying object is not a raw search over sequences. It is the **representation-depth function**

`rho_U(z)=min{|T|: T|U, sigma(T)=z}`

of a fixed maximal atom `U`.

A companion subsequence `W` is forbidden exactly when

`|W|+rho_U(-sigma(W))`

falls below the inherited short-zero threshold. Once `rho_U` is explicit, support sharing becomes a finite family of residue inequalities rather than an unconstrained search in `C_p^3`.

The manuscript should present every finite computation as a terminal reduction after analytic normalization, not as the source of the mathematical statement.

## 2. Main theorem suite

### Theorem A — exact type-`a=2` radial calculus

For every odd prime `p>=5`, every `0<=c<=p-3`, and every `0<=D<=p-1`,

`lambda_{2,c}(D)=D+2 ceil(max(D-c-2,0)/2)`.

This is proved by excluding wrapped representations and splitting the inverse-of-two residue into even and odd classes.

**Authority:** analytic.

**Files:**

- `A2_EXACT_RADIAL_EXCESS_V1.md`
- `check_a2_exact_radial_excess_v1.py`

### Theorem B — exact type-`a=2` depth-fiber envelope

For `p=2H+1`, the maximum of `rho_U(P,Q,C)` over every fiber `[P+Q]_p=w` has a complete four-region piecewise formula. Every maximum has an explicit sharp witness.

This is the paper’s strongest reusable method theorem. It compresses three coordinates to the pair `(w,C)` and exposes the singular middle fiber `w=H` and endpoint fiber `w=p-1`.

**Authority:** analytic with explicit witnesses.

**Files:**

- `A2_EXACT_DEPTH_FIBER_ENVELOPE_V1.md`
- `check_a2_exact_depth_fiber_envelope_v1.py`

### Theorem C — complete type-`a=3` rank-two face elimination

For every prime `p>=7`, no exact-support-six first-corridor support-three rank-two companion survives in the canonical type-`a=3` light-share face.

The proof combines:

- exact inverse-three radial depth;
- boundary index-one reduction;
- explicit elimination of the right half `e<=f`;
- explicit elimination of the complementary left half `e>f`.

**Authority:** analytic; the length-four index-one ingredient is donor-owned and clearly attributed.

**Principal files:**

- `A3_EXACT_RADIAL_EXCESS_V1.md`
- `A3_BOUNDARY_INDEX_ONE_DONOR_REDUCTION_V1.md`
- `A3_RIGHT_HALF_BOUNDARY_ELIMINATION_V1.md`
- the committed left-half closure on the integration branch
- corresponding replay checkers

### Theorem D — maximal-overlap standard-family exclusion for type `a=2`

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

### Theorem E — explicit `p=7` rank-three equality-face closure

For the canonical type-`a=2` length-19 atom over `C_7^3`, the rank-three support-four length-10 companion face has six multiplicity rows. Separate power tests leave exactly fourteen ordered parameter pairs. Every one has an explicit mixed zero-sum certificate of length `4`, `6`, `7`, or `8`.

**Authority:** exact finite theorem with occurrence-level depth and direct vector certificates.

**Files:**

- `P7_A2_RANK3_SUPPORT4_EQUALITY_EMPTY_V1.md`
- `check_p7_a2_rank3_support4_exception_table_v1.py`

### Theorem F — two-corridor C7 support-six exclusion

Let a hypothetical length-37 packing obstruction over `C_7^3` contain a support-four length-19 maximal atom.

- In corridor `(8,10,19)`, every maximal pair of total support six is impossible already at the `19+10` stage.
- In corridor `(9,9,19)`, the exact support-six maximal-pair universe has 26 pair candidates; all 1634 short-free completions by the second length-9 atom admit four disjoint zero-sums, independently confirmed by two different verifiers.

Therefore, in either maximal corridor, a surviving obstruction with a support-four maximal atom must escape the support-six maximal-pair face.

**Authority:** composite theorem: analytic first-corridor closure plus dual-verifier finite second-corridor closure.

**Principal files:**

- `P7_A2_RANK3_SUPPORT4_EQUALITY_EMPTY_V1.md`
- the support-three elimination files for types `a=1,2,3`
- `SUPPORT6_9919_CLOSURE_V1.md`
- `search_support6_9919_closure_v1.cpp`
- `verify_support6_9919_independent_v1.cpp`

## 3. Proof dependency graph

The reader-facing proof should follow this order:

1. **First-failure reduction.** Convert a hypothetical `D_3` counterexample into three atoms and two maximal length corridors.
2. **Maximal-atom normal form.** Reduce a support-four length-`(3p-1)/2` atom to canonical type `a`.
3. **Representation depth.** Define `rho_U`, derive the general bounded resource formula, then specialize to exact type-`a=2` and `a=3` envelopes.
4. **Support-sharing normal forms.** Separate rank-two support-three and rank-three support-four companions.
5. **Prime-uniform eliminations.** Present `a=3` closure and the type-`a=2` standard-family theorem.
6. **C7 terminal face.** Give the six rows and fourteen explicit mixed certificates.
7. **Second corridor.** State the 26-pair/1634-completion theorem and explain verifier independence.
8. **Support-growth conclusion.** Combine both corridors and state the exact remaining frontier.

The manuscript should avoid interleaving discovery chronology with the proof.

## 4. Computational-proof architecture

The finite C7 statements meet a credible computer-assisted-proof standard because the decisive predicates are replayed independently.

### First corridor

- Depth is computed from actual occurrences of the 19-term atom.
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
5. Exact type-`a=2` radial and fiber theorems
6. Prime-uniform rank-two eliminations
7. Inverse-quarter rotation on the top-overlap face
8. The explicit C7 rank-three exception table
9. The `(9,9,19)` dual-verifier closure
10. Combined support-growth theorem
11. Reproducibility and hostile verification
12. Remaining frontier and limitations

Appendices:

- cyclic index-one donor statement and attribution;
- full piecewise fiber table and sharp witnesses;
- fourteen C7 certificates;
- complete machine-readable census receipts.

## 6. Figures and tables that materially help

1. A diagram of the two maximal corridors `(8,10,19)` and `(9,9,19)`.
2. A support-sharing diagram separating support-three/rank-two and support-four/rank-three faces.
3. A heat map of the exact `M_p(w,C)` envelope, emphasizing `w=H` and `w=p-1`.
4. The inverse-quarter selector on the cyclic rotation orbit.
5. The six-row/fourteen-certificate C7 terminal table.
6. A verifier-independence matrix for the second corridor.

## 7. Atomic open gaps

The paper does **not** need these gaps closed to support its bounded theorem, but they determine whether a stronger all-prime sequel or exact-value paper is possible.

1. Prove the high-multiplicity classification forcing the type-`a=2` top-overlap value into `(A,-A,1)` or `(A,-A,2)`, with three central exceptions.
2. Eliminate lower-overlap type-`a=2` layers `c>=5` prime-uniformly.
3. Establish a support-seven/rank-three augmentation theorem covering both C7 corridors without finite enumeration.
4. Close maximal atoms of support at least five.
5. Resolve the support-eight one-projective-collision Type-A packing face.
6. Only after those steps reconsider `D_3(C_7^3)=36`.

## 8. Claim ceiling

The strongest current reader-facing claim is:

> exact representation-depth formulas and support-growth theorems exclude the smallest support-four maximal-pair face in both maximal `C_7^3` corridors.

The manuscript must not state or imply:

- `D_3(C_7^3)=36`;
- a complete classification of all length-37 obstructions;
- all-prime closure of the type-`a=2` face;
- independent novelty or priority;
- top-journal acceptance authority.

## 9. Readiness assessment

### Ready

- coherent analytic method;
- multiple prime-uniform theorems;
- a nontrivial bounded C7 headline;
- explicit terminal certificates;
- dual independent verification in the larger finite closure;
- branch-scoped CI replay;
- honest claim boundary.

### Required before submission

- external mathematical audit of the two new exact type-`a=2` formulas;
- external prior-art subtraction;
- independent reimplementation of the 14-entry C7 classifier or a formal proof-assistant replay;
- conversion to a concise LaTeX manuscript;
- a referee-facing data and code availability statement;
- author-level decision on venue and novelty language.

### Verdict

There is now enough mathematical substance for a **top specialist-paper development track**. The result is not yet an exact generalized-Davenport paper and should not be marketed as one. Its strength is the exact depth calculus, support rigidity, and independently reproducible finite closure.

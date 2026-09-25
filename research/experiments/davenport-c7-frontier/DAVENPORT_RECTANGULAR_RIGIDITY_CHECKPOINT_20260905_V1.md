# Davenport research: rectangular rigidity checkpoint — 2026-09-05

Status: **a complete prime-uniform rank-two type-two submaximal-overlap theorem and general cyclic rigidity theorems are proved**. The remaining top overlap, mixed rank-three faces, type-one geometry, and separate global gates remain open. Neither the full first corridor nor `D_3(C_7^3)` nor the generalized Davenport numerical formula is claimed.

## 1. Continuity and branch audit

This continuation began from the published live head `c66be6545384ee79b5bade07844b51c1e3df8f68`, tree `e4c4f04c6ce90c4e9b813bdd70eb8a875c1dcf08`, rather than the older user-supplied `86f089ab`. The earlier continuation had already incorporated the intervening stronger work, including the exceptional rank-three `a=3` negative-even/odd J-selector closure and the full saturated type-two boundaries.

Before new research, both Git remote heads and the complete paginated GitHub branch search were inspected. All 27 Davenport heads were unchanged from the preceding checkpoint. A fresh prepublication inspection again found the live head at `c66be654` and no newer Davenport branch. Work was isolated on `shadow/davenport-unsaturated-20260905`; other sessions' branches and files were not edited.

The prior quotient-budget packet received independent proof scrutiny. The only statement corrections were adding the explicit zero-sum hypothesis to the type-two exact-budget and H-minus-two theorem statements. Under that intended hypothesis, the auditor found no mathematical blocker in the budgets, elementary rigid-power bound, one-missing-g inverse, saturated boundary, H-minus-two/three proofs, or the type-one quarter layer.

## 2. The structural jump and complete application

Write `p=2H+1`, `a=H-c+1`, and project a hypothetical rank-two type-two companion modulo its shared light direction. Its two-value quotient has length `p+a-1`, and each total multiplicity is below `p`.

The number of zero-sum count vectors in its capacity rectangle is at least `a+1`, by intersecting two cyclic arithmetic intervals of sizes `r+1` and `t+1`. The exact proper-part defect window allows at most one vector for each level `1,...,a-1`, plus the empty and full vectors. Equality follows, so **every level is realized by an actual occurrence divisor**.

The level-one divisor is an atom. The vectors at all other levels are its scalar multiples modulo `p`. Their forced parity prevents either coordinate from wrapping alone. A first simultaneous wrap would produce an actual proper zero-sum divisor of the level-one atom. Thus no wrap is possible: the whole quotient is an exact rigid power. Its endpoint has a new multiplicity `p-1`, which the established saturated donor theorem excludes.

Consequently, for every prime `p>=7`, **all rank-two type-two light-share companions with `1<=c<H` are impossible**. The proof is in `A2_RANK2_ALL_SUBMAXIMAL_OVERLAPS_ELIMINATED_V1.md`, using `CYCLIC_RECTANGULAR_CHARGE_RIGIDITY_V1.md`.

The abstract charge theorem is an iff classification throughout the full feasible parameter range `2<=a<=p-1`. Its conclusions force `(r,t)=(a,p-1)`, `y=a x`, and `2a|(p-1)`, up to interchanging the values. It quantifies over all proper zero-sum divisors, not just atoms.

## 3. Generalized theorems proved in this continuation

| Theorem | Exact advance | Proof file |
|---|---|---|
| Consecutive lattice atoms | Consecutive nonnegative atoms of any full-rank sublattice of `Z^2` have determinant equal to the lattice index; a capacity rectangle inherits the corresponding atomic-length gcd bound. | `TWO_VALUE_LATTICE_ATOMS_AND_LENGTH_GCD_DICHOTOMY_V1.md` |
| Weighted cyclic rectangle | For a two-value prime-cyclic zero-sum `S`, each multiplicity below `p`, `N=|S|>p`, and an integer linear functional positive on every atomic divisor, `f(S)>=N-p+1`. Odd coefficients give the exact rigid equality case and nonrigid gap `f(S)>=N-p+3`. | `CYCLIC_WEIGHTED_RECTANGLE_EXTREMAL_THEOREM_V1.md` |
| Full integer-weight equality | With two nonzero coefficients, equality forces rigidity without a parity assumption; a zero coefficient gives an exact coordinate-projection exception. Every equality case has a saturated multiplicity. | `CYCLIC_INTEGER_FUNCTIONAL_EQUALITY_CLASSIFICATION_V1.md` |
| Long rigid powers | A two-value atomic power longer than `p`, with both total multiplicities below `p`, is rigid iff one atom multiplicity is one. | `CYCLIC_TWO_VALUE_LONG_RIGID_POWER_SINGLETON_V1.md` |
| Saturated cyclic donor | For every finite abelian group, `sigma(R)=-dg`, `0<=d<ord(g)`, and `m=|R|+d>ord(g)`, absence of zero-sums shorter than `m` in `R g^(ord(g)-1)` is equivalent to atomicity of the quotient of `R`. The threshold is sharp. | `SATURATED_CYCLIC_DONOR_ATOM_EQUIVALENCE_V1.md` |

These are fully proved structural statements. They are not assertions of a generalized Davenport numerical formula or of literature priority.

## 4. Additional local advances and the exact remaining frontier

| Face | Current proved state | Remaining gate |
|---|---|---|
| Exceptional rank-three `a=3` | Already completely closed before this packet. | None within that canonical face. |
| Rank-two type-two `1<=c<H` | Completely closed by the new counting/parity theorem. The intermediate H-minus-four/five and positive-congruence proofs remain committed. | None within that range. |
| Rank-two type-two `c=H` | Odd `H` is impossible. For even `H`, an actual equal-length exchange produces an explicit support-six maximal atom and support-four companion. | The exchanged support-six atom needs a valid structural theorem; the exchange alone is not a contradiction. |
| Rank-three type-two `c=1` | Completely closed. The new unsaturated certificate is `s^3 g^3 x^(H-1) y^(p-6)`, of length `m-1`. | None in this overlap layer. |
| Rank-three type-two `t=p-b` | Every unsaturated face has exact second-quotient label budget `sum q_i=b`, unique possible counts per label, and an ordinary-proportion rigidity criterion. | Original donor geometry still has to eliminate the permitted quotient models. |
| Rank-three first unsaturated face `b=2` | Atomic branch gives `c|H` or `r|H`; the alternative has even `c,r` and a rigid square. Its exact classification leaves `min(c,r)=2` or `4`, plus five explicit primitive doubled pairs. | These are necessary inverse forms, not proved full-companion realizations or eliminations. |
| Rank-three second unsaturated face `b=3` | The quotient is necessarily atomic and gives `c|H-1` or `r|H-1`. | The resulting mixed geometry remains open. |
| Rank-two type one, `1<=c<H` | Every rigid quotient is excluded, so any surviving quotient must have at least two atom types and atomic-length gcd one. Prior low-share, quarter-layer and other established bands remain valid. | General nonrigid mixed geometry. |
| Rank-two type one, upper overlap | The proper-part budget extends through the light-share ceiling; at `c=floor(3H/2)` the quotient is atomic and one new multiplicity divides `floor(H/2)`. | These necessary forms still need elimination. |

The top-exchange and upper-overlap proofs are in `A2_RANK2_TOP_OVERLAP_MAXIMAL_ATOM_EXCHANGE_V1.md` and `A1_RANK2_UPPER_OVERLAP_QUOTIENT_REDUCTION_V1.md`. The rank-three proofs are in `A2_RANK3_ONE_LIGHT_SHARE_FULL_ELIMINATION_V1.md`, `A2_RANK3_UNSATURATED_QUOTIENT_BUDGET_V1.md`, and `CYCLIC_QUARTER_LENGTH_RIGID_SQUARE_CLASSIFICATION_V1.md`.

The separate global first-corridor gates are not silently reduced to this table of local canonical faces.

## 5. Preserved proof routes and failed shortcuts

The longer affine-potential argument is preserved in `A2_AFFINE_DEFECT_ROUTE_PRESERVED_V1.md`. Its formerly conjectural weighted endpoint is now proved by the general weighted theorem. The direct rectangular charge proof gives a shorter route to the complete submaximal closure.

The following limitations remain explicit:

- The least-residue formula for an atom's length cannot be applied to arbitrary proper projected-zero parts. The successful count proof uses actual count coordinates throughout.
- The saturated-value inverse theorem cannot be applied to `p-b` copies of a value. The rank-three quotient budget uses separate projection and carry arguments.
- The `c=1` multiplier-three certificate does not extend directly to `c=2`. For `p>=11`, that particular extension gives `e1 e2 s^4 g^5 x^(H-4) y^(p-6)`, which fits but has length `m+1`, not a strict-short certificate. No claim is made that all other selectors fail.
- The top `c=H` quotient is one atom of length `p`. It has no proper projected-zero divisor, so the successful submaximal count-saturation hypotheses are absent.
- Weighted equality need not imply rigidity if a coefficient is zero. The exact analytic `p=7` counterexample and its atoms are preserved in the integer-functional equality proof.
- A maximal-atom exchange from support four to support six cannot reuse a support-four classification without a new argument.

## 6. Verification and proof authority

Three mathematical researchers worked on bounded independent tasks: quotient structure, mixed rank-three geometry, and hostile proof audit. The coordinating researcher read and checked every integrated proof. The main complete submaximal closure received independent hostile scrutiny and a further fixed-commit integration review. The full charge-range and nonzero-coefficient strengthenings were independently checked by the coordinating and quotient-structure researchers.

Primary long-atom and two-value splitting statements were reopened to verify their precise hypotheses. Those inputs remain confined to the explicitly attributed inverse/exchange reductions; the complete rectangular counting theorem and its new prime-uniform closure need neither a long-atom index theorem nor a prime sweep. The saturated-boundary dependency retains its separately attributed Bernoulli-pairing theorem.

No enumeration of primes, vectors, supports, or subsequences supplied new theorem authority. Exact bounded algebraic case distinctions in the quarter-length square classification are proved with displayed formulas and converse arguments.

Every genuine advance and the preserved intermediate routes have separate commits. Publication uses tree-identity checks for every commit and nonforced, precondition-checked ref updates. The companion publication receipt records the resulting remote identities.

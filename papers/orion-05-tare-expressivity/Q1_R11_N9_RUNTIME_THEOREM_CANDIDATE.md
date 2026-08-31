# Q1 R11 theorem candidate: exact support-two pair count and O(n^9) direct search

Date: 2026-08-27
Status: THEOREM CANDIDATE / NOT SCIENTIFIC AUTHORITY
Owner: #1518 under #1511

This note records a new derivation to be independently attacked before any claim-ledger or manuscript promotion. It does not alter the established support-two theorem, the current resource results, or any production/hardware claim.

## 1. Established inputs used

The current Q1 authority already proves that every optimum of the frozen R6M six-slot grammar has an equally good representative in which each of the six frame Paulis has support at most two. The six frame slots form three ordered anticommuting pairs.

The frozen objective/feasibility implementation also makes the shared Tag contribution explicit: Tag affects the six frame-label symplectic constraints and contributes `2 wt(S)` to cost. Restore-factor cost depends on target/frame products, not directly on Tag.

## 2. Exact count and direct generator for one ordered anticommuting support-two pair

Let `A_n` be the set of nonidentity phase-ignored n-qubit Pauli strings of support one or two. Its size is

`M(n) = 3n + 9 C(n,2)`.

For a fixed first frame `R` of weight one, the number of support<=2 partners `R'` that anticommute with `R` is

- 2 weight-one partners on the same coordinate;
- `6(n-1)` weight-two partners sharing that coordinate.

Thus a weight-one `R` has `6n-4` partners.

For a fixed first frame `R` of weight two, the number of support<=2 anticommuting partners is

- 4 weight-one partners supported on one of `R`'s two coordinates;
- 4 weight-two partners on the same two-coordinate support, with exactly one local anticommutation;
- `12(n-2)` weight-two partners overlapping `R` in exactly one coordinate.

Thus a weight-two `R` has `12n-16` partners.

There are `3n` weight-one first frames and `9 C(n,2)` weight-two first frames. Therefore the exact number of ordered anticommuting pairs is

`B(n) = 3n(6n-4) + 9 C(n,2)(12n-16)`

`     = 54 n^3 - 108 n^2 + 60 n`.

This is `Theta(n^3)`, not the `Theta(n^4)` obtained by treating the two support-two frames as independent.

The counting proof is constructive and gives an `O(B(n))=O(n^3)` generator rather than requiring an `O(M(n)^2)=O(n^4)` all-pairs scan:

1. enumerate every weight-one first frame by its coordinate and one of three local nonidentity letters; emit its two same-coordinate anticommuting partners, then for each other coordinate emit the six weight-two partners obtained by choosing one of the two anticommuting letters on the shared coordinate and one of three nonidentity letters on the new coordinate;
2. enumerate every weight-two first frame by its unordered coordinate pair and two nonidentity local letters; emit its four weight-one partners, its four same-support weight-two partners with exactly one local anticommutation, then for each outside coordinate emit the twelve weight-two partners formed by choosing which of the first frame's two coordinates is shared, one of two anticommuting local letters there, and one of three nonidentity letters on the outside coordinate.

Every emitted partner anticommutes by construction. Conversely any support<=2 anticommuting partner must overlap the first frame and falls into exactly one listed support-overlap case, so the generator is complete and duplicate-free for a fixed first frame.

The independent no-ORION-import checker on the candidate branch reproduces `B(n)` for `n=1,...,6`, including the per-weight partner degrees.

## 3. Three frame branches and the sharper active-union bound

Before cross-branch, Tag, target, matching, permutation and objective filtering, the three ordered frame pairs have exactly

`B(n)^3 = Theta(n^9)`

pair-local choices.

Moreover, an anticommuting Pauli pair must overlap on at least one coordinate. Since each member has support at most two, the union of one pair has size at most three. Therefore the union `U` of all six frame supports satisfies

`|U| <= 3 + 3 + 3 = 9`.

This sharpens the previous crude `<=12` union bound.

## 4. Tag confinement and a support-six Tag bound

Fix any support-two frame triple. Let `U` be the union of its six frame supports.

If a feasible Tag `S` contains a nonidentity letter outside `U`, deleting that letter changes none of the six symplectic products `<S,R_jk>` because every frame is identity there. It also leaves every target/Restore term unchanged, while weakly decreasing the Tag cost `2 wt(S)`. Repeating gives an equally good or better feasible Tag supported entirely on `U`.

Thus a minimum compatible Tag may be chosen with support inside at most nine qubits.

There is also a rank bound. For a fixed frame triple and a fixed common-label orientation, Tag feasibility is a binary linear system with six symplectic equations in the `2|U| <=18` binary `(x,z)` variables. Let its rank be `r<=6`. In row-echelon form, setting free variables to zero yields a solution with at most `r` nonzero binary pivot variables whenever the system is feasible. A nonzero Pauli coordinate consumes at least one nonzero binary variable, so a compatible Tag exists with

`wt(S) <= r <= 6`.

This is a support upper bound, not a claim that every optimum needs six Tag coordinates.

An exact minimum-weight Tag can therefore be found in constant time with respect to `n`, e.g. by a 64-state syndrome DP over at most nine active coordinates and four local Pauli letters per coordinate.

## 5. Constant-size candidate scoring after O(n) preprocessing

The frozen local objective is coordinate-separable before summation:

- direct frame cost depends only on the six frame letters and the three central bits;
- Tag contributes only local symplectic parity and `2 wt(S)`;
- each of the two Restore branches uses the local three-way factor cost `F3` on the three target/frame products.

For each constant matching/permutation choice, preprocess in `O(n)` the baseline Restore-factor sum obtained with identity frame letters on every coordinate.

For a support-two frame candidate, every frame differs from identity only on `U`, with `|U|<=9`. Therefore its exact Restore-factor score is

`baseline - baseline_contribution(U) + candidate_contribution(U)`,

which requires only a bounded number of local `F3` evaluations. Direct frame cost and all pair anticommutation checks are also bounded-size. Tag feasibility/minimum weight is solved on `U` as above.

Consequently candidate feasibility and candidate cost can be evaluated in `O(1)` arithmetic operations with respect to `n` after `O(n)` preprocessing. The constant is grammar-dependent but finite.

The current historical D++ implementation does **not** realize this bound: it materializes a `4^(2n)` pattern table and sweeps all nonzero n-qubit Tags. Those are implementation choices, not requirements of the frozen grammar; the argument above is for a new direct exact algorithm.

## 6. Candidate exact-runtime theorem

For one admitted frozen R6M six-slot instance of length `n`, under a word-RAM model in which a qubit index and a target local letter are `O(1)` objects:

1. preprocess target-local baseline data in `O(n)` time;
2. directly generate the `B(n)=Theta(n^3)` legal ordered support-two anticommuting frame pairs in `O(n^3)` time using the support-overlap construction above;
3. enumerate three such pairs, `B(n)^3=Theta(n^9)` frame triples;
4. for each triple, evaluate the constant number of matching/permutation/central/label choices, solve the bounded Tag problem on `|U|<=9`, and compute the exact objective in `O(1)` time with respect to `n`.

This yields the candidate bound

`T(n) = O(n + B(n)^3) = O(n^9)`

for exact direct optimization of the frozen R6M six-slot grammar.

The pair list can be generated/stored in `O(n^3)` space or streamed directly into the three nested loops. The time bound therefore does not rely on materializing an `O(n^4)` candidate cross-product.

Under bit-complexity accounting, index manipulation adds at most polylogarithmic factors; no stronger bit bound is claimed here.

## 7. Required hostile review before promotion

Independent review must either prove or break every item below:

- the exact pair-count formula and duplicate-free `O(n^3)` pair generator;
- the claim that the six frame variables are exhausted by exactly three ordered anticommuting pairs;
- the `|U|<=9` active-union bound;
- the Tag-deletion argument outside `U`;
- the support-`<=6` linear-system Tag corollary;
- the baseline-minus-`U` preprocessing identity for every objective term;
- `O(1)` candidate feasibility/cost evaluation after preprocessing;
- constancy in `n` of matching, permutation, central-choice and label multiplicities in the frozen six-slot grammar;
- absence of any hidden n-dependent solver, oracle, table materialization, or verification call in the *new* direct algorithm.

If only the counting corollary survives, the honest terminal is `Q1_R11_PAIR_COUNT_ONLY__RUNTIME_HIDDEN_DEPENDENCY`. If all obligations survive, the candidate terminal is `Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM`.

## 8. Authority boundary

Even a proved `O(n^9)` result would be:

- an exact algorithm for the frozen R6M six-slot grammar and frozen objective only;
- not a generic TARE/block-encoding complexity theorem;
- not a statement about the runtime of the existing production DP or historical D++ implementation;
- not a physical quantum-resource or hardware-advantage result;
- not a novelty certificate without current primary-source subtraction.

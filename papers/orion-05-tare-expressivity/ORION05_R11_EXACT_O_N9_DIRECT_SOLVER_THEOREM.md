# ORION-05 R11: exact `O(n^9)` direct solver for the frozen R6M grammar

Date: 2026-08-27
Status: **THEOREM-GRADE ON THE FROZEN GRAMMAR**
Terminal:
`ORION05_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM__FROZEN_R6M_ONLY`
Parent: #1518 under the three-round programme #1511
Supersedes: the theorem-candidate status in draft #1524, after this packet is
merged on a clean current-main lineage

This is a research theorem/algorithm record, not a manuscript rewrite. It does
not change the existing production DP, the support-one refutation, the current
resource evidence, or any protected Task-3 lane.

## 1. Exact statement

Consider one admitted instance of the frozen R6M three-block shared-one-bit-Tag
TARE-M2 grammar under its frozen support-count objective. There are six target
Paulis, three ordered anticommuting auxiliary-frame pairs, one common Tag, 15
canonical target matchings, two relative target permutations for each of
blocks B and C, two common-label orientations, and one binary central choice
per block.

Using the established R6S support-two theorem, an exact optimum and an exact
phase-reconstructible witness can be found in

\[
T(n)=O\!\left(n+B(n)^3\right)=O(n^9),
\qquad
B(n)=54n^3-108n^2+60n,
\]

on a word RAM where a qubit index and a target local letter are constant-size
words. The direct implementation uses `O(n+B(n))=O(n^3)` working memory. If
index and accumulated-cost bit operations are charged explicitly, the bound
acquires polylogarithmic factors; no tighter bit-complexity claim is made.

This is an upper bound for a new direct algorithm. It is neither a lower bound
nor a runtime claim for the historical 512-state production DP or D++ code.

## 2. Exact constructive pair count

Let `A_n` contain the nonidentity phase-ignored `n`-qubit Paulis of support one
or two. There are

\[
|A_n|=3n+9\binom n2.
\]

Fix the first member `R` of an ordered pair.

### Weight-one first frame

There are two weight-one anticommuting partners on the same coordinate. A
weight-two partner must include that coordinate, choose one of its two
anticommuting letters there, and choose one of three nonidentity letters at one
of the `n-1` other coordinates. Hence the degree is

\[
2+2\cdot3(n-1)=6n-4.
\]

### Weight-two first frame

An anticommuting partner is in exactly one of three disjoint cases:

1. weight one on either active coordinate: `2*2=4` choices;
2. weight two on the same support, anticommuting at exactly one coordinate:
   `2*1+1*2=4` choices;
3. weight two with exactly one shared coordinate: choose the shared coordinate,
   its anticommuting letter, the outside coordinate, and its nonidentity letter,
   giving `2*2*(n-2)*3=12(n-2)` choices.

Thus the degree is `12n-16`. Multiplication by the numbers of possible first
frames gives

\[
\begin{aligned}
B(n)
 &=3n(6n-4)+9\binom n2(12n-16)\\
 &=54n^3-108n^2+60n.
\end{aligned}
\]

The three case lists are also a duplicate-free generator. They produce each
partner directly from its support-overlap type rather than scanning the
`Theta(n^2)`-by-`Theta(n^2)` Pauli cross-product. Generation therefore costs
`Theta(B(n))=Theta(n^3)` time.

## 3. Active union and Tag confinement

Anticommutation requires two support-two Paulis to overlap. One pair therefore
uses at most three coordinates. Three pairs use an active union `U` satisfying

\[
|U|\le 3+3+3=9.
\]

Fix the six frames. All Tag constraints are the six symplectic equations
against those frames. A Tag letter outside `U` contributes zero to every
equation and contributes two positive support units when nonidentity. Deleting
all such letters preserves feasibility and Restore terms while weakly lowering
the objective. A minimum Tag is therefore supported entirely inside `U`.

For either common-label orientation the Tag problem is a binary linear system
of six equations in `2|U|` variables. If its rank is `r`, row reduction with
all free variables set to zero gives a feasible solution with at most `r`
nonzero binary variables whenever the system is consistent. Its Pauli support
is at most that number, so

\[
w(S)\le r\le6.
\]

An exact minimum-weight Tag is obtained by a 64-syndrome dynamic program over
at most nine coordinates and four local letters. This is constant work with
respect to `n`; it is not the production 512-state optimizer.

## 4. Linear preprocessing and constant candidate scoring

For one matching and relative target order, preprocess at every coordinate the
Restore cost obtained when all six frame letters are identity:

\[
b_q=F_3(P_{A0,q},P_{B0,q},P_{C0,q})
   +F_3(P_{A1,q},P_{B1,q},P_{C1,q}).
\]

The sum of the `b_q` costs `O(n)` time. For a frame triple, every nonidentity
frame letter lies in `U`, so its exact Restore cost is

\[
\sum_q b_q-sum_{q\in U}b_q+
\sum_{q\in U}b_q^{\mathrm{candidate}}.
\]

At most nine coordinates are read. Frame cost uses the six constant-size
supports. Tag feasibility and minimum weight use at most nine coordinates and
64 syndromes. Anticommutation is guaranteed by the pair generator.

The remaining families are constants of the frozen grammar:

- 15 target matchings;
- four relative B/C target orders;
- eight central choices (or, equivalently, place multiplier two on the heavier
  member of each pair, choosing branch zero on a tie);
- two common-label orientations.

There is no other feasibility condition in the frozen source. Hence candidate
evaluation after preprocessing is `O(1)` in `n`.

## 5. Exact algorithm and witness gate

1. Preprocess the constant matching/permutation family in `O(n)` total time.
2. Generate or store the `B(n)` ordered anticommuting support-two pairs in
   `O(n^3)` time.
3. Enumerate three pair choices: `B(n)^3=Theta(n^9)` triples.
4. For every triple, solve the bounded Tag problem and evaluate the constant
   central/permutation/matching choices using active-coordinate corrections.
5. Retain one minimum-cost sparse witness.
6. Once, in `O(n)` time, reconstruct all six signed Restore Paulis, both common
   factors, their three residuals per branch, and the exact Hermitian `i`-phase
   identities.

The implementation in `orion05_r11_sparse_direct_solver.py` follows this
algorithm. Its imports are limited to Python standard-library modules and its
abstract syntax tree contains no production-DP symbols.

## 6. Separate finite cross-check against the frozen DP

`ORION05_R11_SPARSE_EQUIVALENCE_RESULTS.json` is regenerated by
`orion05_r11_sparse_equivalence_verify.py` and binds the exact current-main
R6M protocol, production DP, R6S proof/receipt, R6O adverse receipt, R6P
support-two receipt, and current QG-21 resource receipt.

The frozen production DP is a separate exact optimum oracle. The finite
verifier deliberately reuses some sparse-solver Pauli, Restore, and phase
primitives, so it is not a structurally independent implementation of every
witness identity. Two same-owner hostile proof/code reviews separately checked
the all-`n` reduction and found no theorem blocker; they do not establish
external independence.

The registered checks are:

- constructive generator equals a naive all-pairs set, duplicate-free, for
  every `n=1,...,6`; observed counts are
  `6, 120, 666, 1968, 4350, 8136`;
- union-three for one pair and union-nine for three pairs are both attained;
- 640 full-Tag-versus-active-Tag cases, with 412 feasible and 228 infeasible;
- every feasible checked Tag satisfies confinement and `w(S)<=rank<=6`;
- 961 full-scan-versus-baseline/correction Restore comparisons, including an
  `n=257` hostile with nine far-apart active coordinates;
- the complete `n=1` domain: all 4,096 ordered six-target tuples, all eight
  central choices, and both label orientations, totalling 65,536 slices;
- on all 65,536 slices, exact sparse and production-DP costs agree and both
  optimum witnesses separately pass feasibility, cost, Restore, factor, and
  exact phase reconstruction;
- exact optimum/witness equivalence on both registered R6M hostile `n=2`
  panels; and
- the adverse sharpness instance is reproduced exactly:
  support two and the production DP give cost `5`, while the complete
  support-one family gives cost `6`; the sparse optimum contains an actual
  support-two frame.

Witness equivalence means that both separately checked feasible witnesses
recompute the same exact optimum. Equality of historical serialized tie-break
bytes is not a mathematical requirement and is not claimed. The complete
finite coverage exercises ordered slices at `n=1` and registered matching
panels at `n=2`; it is corroboration of the source-level all-`n` proof, not an
empirical all-`n` proof or an end-to-end production benchmark.

## 7. Adverse-resource and authority preservation

This theorem changes only the direct normal-form classical upper bound. It
does not change the current resource record:

- under the QG-21 primary `theta_FT` objective, all 90/90 chemistry rows remain
  donor-exact;
- under defensible sensitivity S1, only 18/90 rows improve, by two logical
  two-qubit Clifford gates, against the invariant nine-rotation backdrop;
- T count, T depth, logical depth, qubits, physical spacetime, hardware
  performance, and measured compiler performance remain unestablished;
- convergence V1 already preserves #1449's exact `PARTIAL_RESOURCE_MAP` donor
  record on current main at its bounded ceiling; this theorem does not change
  that adverse resource status.

For any later clean rematerialization of #1449's report/checker layer, this
theorem supersedes only the `O(n^12)` raw six-independent-frame
candidate-count row. It does not supersede the partial-resource terminal, the
adverse QG-21 observations, or any `CANNOT_CHECK` field.

## 8. Exact boundary and next round

Authorized conclusion:

> The frozen R6M six-slot grammar under its frozen support-count objective has
> an exact direct `O(n^9)` word-RAM optimizer induced by the established
> support-two normal form.

Not authorized:

- generic TARE or block-encoding complexity;
- an acceleration measurement for the existing production DP;
- an asymptotic lower bound or optimality of exponent nine;
- physical, hardware, or fault-tolerant resource advantage;
- novelty, venue, journal, or submission authority.

This closes **Round 1 theorem-to-algorithm conversion only**. Under #1511,
Round 2 remains the separately frozen production-faithful comparison of the
new support-two search against the unrestricted referee, including nodes,
states, CPU/wall time, RSS, and proof-verification cost. No Round-2 result may
be inferred from the theorem or from the finite equivalence receipt.

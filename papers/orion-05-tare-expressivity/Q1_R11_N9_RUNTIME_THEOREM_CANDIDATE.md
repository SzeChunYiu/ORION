# Q1 R11 theorem candidate: exact support-two pair count and O(n^9) direct search

Date: 2026-08-27
Status: THEOREM CANDIDATE / NOT SCIENTIFIC AUTHORITY
Owner: #1518 under #1511

This note records a new derivation to be independently attacked before any claim-ledger or manuscript promotion. It does not alter the established support-two theorem, the current resource results, or any production/hardware claim.

## 1. Established inputs used

The current Q1 authority already provides two ingredients for the frozen R6M six-slot grammar:

1. every optimum has an equally good representative in which each of the six frame Paulis has support at most two;
2. a minimum compatible shared Tag need not act outside the union of those six frame supports, hence outside at most 12 qubits.

The frozen grammar groups the six frame slots into three ordered anticommuting frame pairs.

## 2. Exact count for one ordered anticommuting support-two pair

Let A_n be the set of nonidentity phase-ignored n-qubit Pauli strings of support one or two. Its size is

M(n) = 3n + 9 C(n,2).

For a fixed first frame R of weight one, the number of support<=2 partners R' that anticommute with R is

- 2 weight-one partners on the same coordinate;
- 6(n-1) weight-two partners sharing that coordinate.

Thus a weight-one R has 6n-4 partners.

For a fixed first frame R of weight two, the number of support<=2 anticommuting partners is

- 4 weight-one partners supported on one of R's two coordinates;
- 4 weight-two partners on the same two-coordinate support, with exactly one local anticommutation;
- 12(n-2) weight-two partners overlapping R in exactly one coordinate.

Thus a weight-two R has 12n-16 partners.

There are 3n weight-one first frames and 9 C(n,2) weight-two first frames. Therefore the exact number of ordered anticommuting pairs is

B(n) = 3n(6n-4) + 9 C(n,2)(12n-16)
     = 54 n^3 - 108 n^2 + 60 n.

This is Theta(n^3), not the Theta(n^4) obtained by treating the two support-two frames as independent.

## 3. Three frame branches

Before cross-branch, Tag, target, matching, permutation and objective filtering, the three ordered frame pairs therefore have exactly

B(n)^3 = Theta(n^9)

raw legal pair-local choices.

This strictly sharpens the current single-frame raw count [3n+9C(n,2)]^6 = Theta(n^12) by using the mandatory anticommutation structure.

## 4. Candidate exact-runtime corollary

The following is a candidate theorem, not yet authorized.

For a fixed admitted R6M target six-tuple of length n:

1. preprocess the coordinatewise Restore contribution for identity frame/Tag letters for each constant grammar choice in O(n) time;
2. enumerate the three ordered anticommuting support-two frame pairs, B(n)^3 possibilities;
3. for each frame triple let U be the union of the six frame supports, so |U|<=12;
4. enumerate the compatible Tag only on U; a crude upper bound is 4^12 assignments, independent of n;
5. evaluate all candidate-dependent support, Tag, symplectic and Restore contributions only on U, replacing the precomputed baseline contribution on those <=12 coordinates.

If every other matching/permutation/central-choice factor of the frozen six-slot grammar is constant and no candidate evaluation invokes an n-dependent oracle or unrestricted DP, this gives deterministic exact direct optimization in

O(n + B(n)^3) = O(n^9)

time for the frozen grammar, with a large n-independent constant from Tag and grammar enumeration.

## 5. Required hostile review before promotion

Independent review must either prove or break every item below:

- the exact pair-count formula;
- the claim that the six frames are exhausted by exactly three ordered anticommuting pairs;
- the <=12-qubit Tag-union confinement under the identical frozen grammar/objective;
- the baseline-minus-U preprocessing argument for every objective term;
- O(1) candidate feasibility/cost evaluation after preprocessing;
- constancy in n of matching, permutation and central-choice multiplicities;
- absence of any hidden n-dependent solver, oracle, table materialization, or verification call.

If only the pair count survives, the honest terminal is `Q1_R11_PAIR_COUNT_ONLY__RUNTIME_HIDDEN_DEPENDENCY`. If all obligations survive, the candidate terminal is `Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM`.

## 6. Authority boundary

Even a proved O(n^9) result would be:

- an exact algorithm for the frozen R6M six-slot grammar and frozen objective only;
- not a generic TARE/block-encoding complexity theorem;
- not a statement about the runtime of the existing production DP;
- not a physical quantum-resource or hardware-advantage result;
- not a novelty certificate without current primary-source subtraction.

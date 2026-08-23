# N3-D Frozen Protocol: Representation Variable Synthesis

- Lane: ORION-Q N3 (issue #676), successor family D.
- Status at freeze: FROZEN BEFORE ANY OUTCOME. Runner:
  `research/extensions/orion-q/nlanes/n3_d_representation_variables.py`.
- Scope/authority: exact-synthetic bounded diagnostic only. No real-quantum,
  no novelty, no P10 authority. Honest negatives are valid terminals.
- Donor first right of refusal: induction in the SUPPLIED (raw/concrete)
  representation is attempted first at matched budget; if it already yields a
  verified family, transport cost must be 0 and the arm is parent-sufficient.

## Exact synthetic world

Programs: sequences of `CNOT(c,t)` on n wires; exact semantics = GF(2) linear
map (matrix equality). Wire counts are PRIMES so modular-multiplicative
re-indexings are bijections: train n in {5,7}; held-out n in {11,13}.

Arms (each supplies concrete train artifacts for n = 5 and n = 7; the world
spec at any n is the exact semantics of the ground-truth concrete program):

- D1 residual: ground truth concrete program
  `P(n) = [C(3t mod n, 3(t+1) mod n) for t = 0..n-2]` — a logical chain hidden
  under the fixed re-indexing `i -> 3i mod n`. Raw-representation affine
  induction cannot fit (index sequences wrap non-affinely).
- D2 donor-sufficient: ground truth is the plain chain
  `P(n) = [C(t,t+1)]` — identity representation already fits; the candidate
  must select identity, charge transport cost 0, and record
  parent_sufficient = true (no residual claim).
- D3 hostile: concrete indexing by keyed pseudorandom permutations sigma_n
  (random.Random(20260821), fresh shuffle per n):
  `P(n) = [C(sigma_n(t), sigma_n(t+1))]`. No library representation fits BOTH
  train sizes; the candidate must report NO_VALID_REPRESENTATION and emit no
  family claim (a mechanism willing to pick a partially-fitting representation
  would leak here and be caught).

## Candidate mechanism (prespecified)

Representation library R, in fixed order, each entry a bijection family
parametric in n (entries inapplicable at some n, e.g. non-invertible
multipliers, are skipped for that n and cannot be selected):
1. identity (transport cost 0)
2. reversal `i -> n-1-i` (cost 1)
3. mul2 `i -> 2i mod n` (cost 1)
4. mul3 `i -> 3i mod n` (cost 1)
5. mul5 `i -> 5i mod n` (cost 1)

Affine schema class (same as N3-A, integer arithmetic, NO modular wrap):
`[CNOT(p*t+q, r*t+s) for t = 0..L(n)-1]`, p,q,r,s in {-3..3},
L(n) = alpha*n + beta, alpha in {0,1}, beta in {-3..3}.

Procedure: for each r in R (in order), transform every train artifact's gate
indices by r^{-1} (for that n); if the transformed artifacts admit an exact
token-level schema fit valid at BOTH train sizes, select r (first hit wins;
identity therefore always has first refusal). Prediction at held-out n:
generate the schema program, map indices through r for that n, and
EXACT-verify semantics against the world spec. Transport cost of the selected
representation is charged and reported. If no r fits both train sizes:
NO_VALID_REPRESENTATION, no family claim.

## Donor baselines (strongest, matched budget)

- D-raw donor: the identical affine schema induction applied in the supplied
  raw representation (this IS the r = identity branch; it gets first refusal).
- D-search donor: BFS over concrete CNOT sequences toward the held-out spec at
  budget B = 200,000 expanded nodes per held-out n (residual arm).
- Trivial-generalization baseline: replay the n = 7 train artifact embedded on
  n wires; exact-verify (must fail in D1 for the candidate to claim value).
- Budget matching: candidate constructed-program count <= 200,000 (recorded).

## Prespecified gates

- GD0 (budget sanity): candidate constructed-program count <= 200,000.
- GD1 (residual value, D1): raw induction fails both train fits; candidate
  selects a non-identity representation at transport cost 1, family
  exact-verifies at BOTH held-out n in {11,13}; BFS donor fails both at
  budget B; trivial replay fails both. If raw induction or any donor matches,
  GD1 is false and the terminal is PARENT_SUFFICIENT_NEGATIVE.
- GD2 (donor first-refusal honored, D2): identity selected, transport cost 0,
  parent_sufficient = true, no residual claim.
- GD3 (hostile catch, D3): no library representation fits both train sizes;
  candidate reports NO_VALID_REPRESENTATION and emits no family claim.
- GD4 (determinism): study run twice in-process; canonical sorted JSON
  byte-identical (SHA-256 digests equal).

## Terminal vocabulary

- `N3D_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`: GD0-GD4 all true.
- `N3D_PARENT_SUFFICIENT_NEGATIVE`: GD1 false because raw/donor matched.
- `N3D_MECHANISM_FAILED_NEGATIVE`: any other gate failure.

## Determinism and receipts

SEED = 20260821 (used only for the fixed hostile permutations; identical
across runs). Stdout receipt line
`ORIONQ_N3_D_REPRESENTATION_VARIABLES=<canonical sorted compact JSON>` plus
pretty JSON, also written to
`research/extensions/orion-q/nlanes/N3_D_REPRESENTATION_VARIABLES_RESULTS.json`.
Schema id: `ORIONQ.N3D.RepresentationVariableSynthesis.v1`. Authority string:
`exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority`.

## Claim boundary

Any positive result claims ONLY: in this exact-synthetic world class, paying
an explicit transport cost to synthesize a representation variable recovered a
verified symbolic family that induction in the supplied representation and
matched-budget concrete search did not, with identity-representation first
refusal and an out-of-library hostile world dispositioned honestly. No claim
about compiler/IR transformation tooling, real qubit routing, or novelty.

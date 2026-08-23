# N3-A Frozen Protocol: Finite Optimum -> Symbolic Family Induction

- Lane: ORION-Q N3 (issue #676), successor family A.
- Status at freeze: FROZEN BEFORE ANY OUTCOME. This document prespecifies worlds,
  mechanisms, baselines, budgets, gates, and terminal vocabulary. The runner
  (`research/extensions/orion-q/nlanes/n3_a_symbolic_induction.py`) implements
  exactly this protocol; outcomes are written only after this freeze.
- Scope/authority: exact-synthetic bounded diagnostic only. No real-quantum,
  no novelty, no P10 authority. Honest negatives are valid terminals.
- Donor first right of refusal: if a donor using only the supplied grammar
  (concrete or supplied-parametric, at matched budget) matches the candidate on
  the residual arm, the family terminal is PARENT_SUFFICIENT_NEGATIVE.

## Exact synthetic world

Programs are finite sequences of `CNOT(c,t)` gates on `n` wires, `c != t`.
Exact semantics: the induced invertible linear map on GF(2)^n (n x n binary
matrix; `CNOT(c,t)` adds row `c` into row `t` of the accumulated map). Ground
truth is enumerable: two programs are equal iff their matrices are equal, and
minimal program length for a target matrix is proved by breadth-first search
(BFS) over gate applications with deduplication (first hit = minimal depth).

Target family (world A1, residual arm): prefix-parity transform `M_n` with
rows `y_i = x_0 xor ... xor x_i`. Known ground truth: the chain
`CNOT(t,t+1), t = 0..n-2`, length `n-1`.

- Train sizes: n in {2,3,4,5}. Donor BFS supplies proved-optimal artifacts
  (program + minimality certificate = BFS depth of first hit).
- Held-out sizes A1: n in {8,10,12}.

World A2 (donor-sufficient arm): identical targets `M_n`, but the supplied
grammar is PARAMETRIC: macros {CHAIN(n), FAN(n), REV_CHAIN(n)} with exact
expansions. Donor enumerates the 3 macros per held-out n and verifies exactly.

World A3 (hostile arm, overgeneralization trap): targets `T'_n = M_n` for
n <= 5 but for n >= 6 `T'_n` = `M_n` composed with a swap of the last two
wires. Train optima (n=2..5) fit the same symbolic family as A1; the induced
family is WRONG for n >= 6 and MUST be rejected by the exact verifier.
Held-out sizes A3: n in {6,8,10}.

## Candidate mechanism (prespecified)

Symbolic schema class S: programs `[CNOT(a*t+b, c*t+d) for t = 0..L(n)-1]`
with integer coefficients a,b,c,d in {-2..2}, and L(n) = alpha*n + beta with
alpha in {0,1,2}, beta in {-2..2}. Induction procedure:

1. Consume train artifacts: proved minimal lengths and gate lists.
2. Enumerate the full schema grid (5^4 * 3 * 5 = 9375 parameter tuples) in
   lexicographic order; a tuple FITS iff for every train n its generated
   program is well-formed (indices in range, c != t), has length equal to the
   proved minimal length, and its exact matrix equals the train target.
3. The induced family = first fitting tuple (deterministic). If none fits,
   report induction failure (honest negative).
4. Family claim requires EXACT verification at every held-out n
   (matrix equality against the world target). Any held-out mismatch =>
   family_claim = false.

## Donor baselines (strongest, matched budget)

- D1 concrete-grammar donor: BFS over concrete CNOT sequences at each held-out
  n with budget B = 200,000 expanded nodes per n (prespecified). Candidate
  total constructed-program count must be <= B (recorded; else GA0 fails).
- D2 supplied-parametric donor (world A2): enumerate the 3 macros per n,
  exact-verify. If this donor verifies all held-out n, the arm is
  parent-sufficient and the candidate MUST NOT claim residual value.
- D3 trivial-generalization baseline: replay the largest train artifact
  (n=5 program embedded on n wires); must be exactly verified or fail.

## Prespecified gates

- GA0 (budget sanity): candidate constructed-program count <= 200,000.
- GA1 (residual value, world A1): induced family exact-verifies at ALL
  held-out n in {8,10,12}; concrete donor FAILS all three at budget B; trivial
  baseline fails all three. If the concrete donor matches the candidate at any
  held-out n, GA1 is false and the terminal is PARENT_SUFFICIENT_NEGATIVE.
- GA2 (donor first-refusal honored, world A2): parametric donor verifies all
  held-out n AND candidate records parent_sufficient = true AND emits no
  residual claim for A2.
- GA3 (hostile catch, world A3): schema fits train, exact verifier rejects at
  least one held-out n, and family_claim = false for A3 (no leak).
- GA4 (determinism): full study executed twice in-process; canonical sorted
  JSON of both runs is byte-identical (SHA-256 digests equal).

## Terminal vocabulary

- `N3A_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`: GA0-GA4 all true.
- `N3A_PARENT_SUFFICIENT_NEGATIVE`: GA1 false because a donor matched.
- `N3A_MECHANISM_FAILED_NEGATIVE`: any other gate failure.

## Determinism and receipts

No randomness anywhere in family A; fixed constant SEED = 20260821 recorded
for schema id purposes. Single stdout receipt line
`ORIONQ_N3_A_SYMBOLIC_INDUCTION=<canonical sorted compact JSON>` followed by
pretty JSON; pretty JSON also written to
`research/extensions/orion-q/nlanes/N3_A_SYMBOLIC_INDUCTION_RESULTS.json`.
Schema id: `ORIONQ.N3A.SymbolicFamilyInduction.v1`. Authority string:
`exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority`.

## Claim boundary

Any positive result claims ONLY: within this exact-synthetic world class, a
symbolic-family induction step above a supplied concrete grammar recovered a
verified family that matched-budget donor search did not, while the supplied
parametric donor retained first right of refusal and hostile
overgeneralization was caught by the exact verifier. No claim about real
quantum synthesis, QSynth-class tools, or novelty is made or implied.

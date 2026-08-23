# N3-C Frozen Protocol: Cross-Family Operator Induction

- Lane: ORION-Q N3 (issue #676), successor family C.
- Status at freeze: FROZEN BEFORE ANY OUTCOME. Runner:
  `research/extensions/orion-q/nlanes/n3_c_operator_induction.py`.
- Scope/authority: exact-synthetic bounded diagnostic only. No real-quantum,
  no novelty, no P10 authority. Honest negatives are valid terminals.
- Donor first right of refusal: donor-produced atoms plus supplied-grammar
  search (and the trivial replay baseline) are consulted FIRST on every
  held-out size; if they match, the arm is parent-sufficient and the candidate
  must claim no operator value.

## Exact synthetic world

Programs: sequences of `CNOT(c,t)` on n wires; exact semantics = GF(2) linear
map (matrix equality is the exact verifier). Each algorithm family f is
defined by a ground-truth generator `P_f(n)`; the spec for (f, n) is the exact
semantics of `P_f(n)`.

Donor-produced atoms (given artifacts):
- Train families (full atoms at n = 2..5):
  - F1 chain: `P(n) = [C(t,t+1) for t=0..n-2]`
  - F2 fan: `P(n) = [C(0,t+1) for t=0..n-2]`
  - F3 chain+fan double layer: `P(n) = concat_t [C(t,t+1), C(0,t+1)]`
- Held-out families (atoms ONLY at n = 2,3,4; evaluated at n = 8,10):
  - F4 (residual arm C1): reverse fan with base:
    `P(2) = [C(1,0)]`, `P(n) = P(n-1) ++ [C(n-1,0)]` (i.e. Delta(m) = [C(m+1,0)]).
  - F5 (donor-sufficient arm C2): constant family `P(n) = [C(0,1)]` for all n.
  - F6 (hostile arm C3): chain for n <= 4; for n >= 5 ground truth is
    chain ++ [C(0, n-1)] (a correction gate invisible in the supplied atoms).

## Candidate mechanism (prespecified)

Second-order operator induction from train families F1-F3:
1. For each train family check the structural law
   `P(n) = P(n-1) ++ Delta(m)` with `m = n-2`, constant block size k_f, and
   every Delta gate's indices affine in m: `(a*m+b, c*m+d)`,
   coefficients in {-2..2}, fitted exactly across all train deltas.
2. The induced cross-family operator L = "prefix-incremental affine fold"
   exists only if ALL THREE train families satisfy it exactly (else honest
   induction failure).
3. Transfer to a held-out family: given atoms n = 2,3,4 only, fit the
   family-local parameters of L (base = P(2); Delta blocks from n=2->3 and
   n=3->4; affine coefficients through the two points, verified integral),
   then unroll to held-out n in {8,10} and EXACT-verify semantics against the
   world spec. Any mismatch => transfer_claim = false for that family.

## Donor baselines (strongest, matched budget)

- D1 concrete-grammar donor: BFS over CNOT sequences toward the held-out spec
  at budget B = 200,000 expanded nodes per (family, held-out n).
- D2 trivial-generalization baseline: replay the largest supplied atom
  (n = 4 program, embedded on n wires), exact-verify.
- First-refusal rule: donor/trivial run FIRST; if either exactly matches ALL
  held-out sizes of a family, that family is parent-sufficient and the
  candidate must set operator_value_claim = false there.
- Budget matching: candidate constructed-program count <= 200,000 (recorded).

## Prespecified gates

- GC0 (budget sanity): candidate constructed-program count <= 200,000.
- GC1 (residual transfer, F4): induced operator L fits F1-F3 exactly;
  F4 transfer exact-verifies at both n = 8 and n = 10; concrete donor fails
  both at budget B; trivial replay fails both. If donor or trivial matches,
  GC1 is false and the terminal is PARENT_SUFFICIENT_NEGATIVE.
- GC2 (donor first-refusal honored, F5): trivial replay (or donor) matches all
  held-out sizes; candidate records parent_sufficient = true and makes no
  operator value claim for F5.
- GC3 (hostile catch, F6): the fold law fits the supplied F6 atoms, but the
  unrolled prediction FAILS exact verification at n = 8 and n = 10, and
  transfer_claim = false for F6 (no leak).
- GC4 (determinism): study run twice in-process; canonical sorted JSON
  byte-identical (SHA-256 digests equal).

## Terminal vocabulary

- `N3C_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`: GC0-GC4 all true.
- `N3C_PARENT_SUFFICIENT_NEGATIVE`: GC1 false because donor/trivial matched.
- `N3C_MECHANISM_FAILED_NEGATIVE`: any other gate failure.

## Determinism and receipts

No randomness; SEED = 20260821 recorded. Stdout receipt line
`ORIONQ_N3_C_OPERATOR_INDUCTION=<canonical sorted compact JSON>` plus pretty
JSON, also written to
`research/extensions/orion-q/nlanes/N3_C_OPERATOR_INDUCTION_RESULTS.json`.
Schema id: `ORIONQ.N3C.CrossFamilyOperatorInduction.v1`. Authority string:
`exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority`.

## Claim boundary

Any positive result claims ONLY: in this exact-synthetic world class, a
higher-order composition law induced across donor-produced program families
transferred to a held-out family beyond matched-budget donor search, with
parent-sufficient and hostile held-out families dispositioned honestly by the
exact verifier. No claim about DreamCoder-class library learning, real
quantum program families, or novelty.

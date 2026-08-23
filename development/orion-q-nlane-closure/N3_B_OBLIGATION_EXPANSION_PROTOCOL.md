# N3-B Frozen Protocol: Proof-Obligation-Driven Grammar Expansion

- Lane: ORION-Q N3 (issue #676), successor family B.
- Status at freeze: FROZEN BEFORE ANY OUTCOME. Runner:
  `research/extensions/orion-q/nlanes/n3_b_obligation_expansion.py`.
- Scope/authority: exact-synthetic bounded diagnostic only. No real-quantum,
  no novelty, no P10 authority. Honest negatives are valid terminals.
- Donor first right of refusal: if the supplied grammar G0 alone (donor
  enumeration at matched budget) synthesizes the spec, the candidate MUST
  propose no expansion; a residual-arm match by G0 alone makes the terminal
  PARENT_SUFFICIENT_NEGATIVE.

## Exact synthetic world

Specs are total functions f: Z16 -> Z16, represented as 16-tuples (fully
enumerable ground truth; exact full-domain verification).

Supplied grammar G0 (expression ASTs):
- leaves: variable `x`, constants 0,1,2,3 (size 1 each);
- binary ops (size 1 + left + right): ADD16 (mod 16), MUL16 (mod 16),
  MAX, MIN.

Semantic enumeration is bottom-up by AST size with value-table deduplication,
so "spec not expressible in G up to size bound s" is an EXACT bounded
inexpressibility proof (a proof obligation), not a timeout.

Extension library E (each cost 1, prespecified):
- XOR (binary, bitwise xor), SHR1 (unary, x >> 1), NOT16 (unary, 15 - x),
  MOD2 (unary, x & 1).

Arms:
- B1 residual: spec = Gray code g(x) = x xor (x >> 1)
  (table (0,1,3,2,6,7,5,4,12,13,15,14,10,11,9,8)).
- B2 donor-sufficient: spec = (2*x + 3) mod 16, expressible in G0.
- B3 hostile: spec = fixed pseudorandom permutation table
  (7,12,1,14,9,0,5,11,3,15,6,2,13,8,10,4). The runner asserts it is NOT
  expressible even in G0 + all of E at the candidate bound; if that assertion
  ever failed the arm reports HOSTILE_MISCONFIGURED and GB3 fails honestly.
  The trap: a mechanism that fit only observed counterexamples could emit a
  spurious expansion; the candidate must instead report
  OBLIGATION_UNRESOLVED_AT_BOUND and emit NO expansion claim.

## Candidate mechanism (prespecified)

1. Enumerate G0 bottom-up to size bound S_CAND = 7. If spec present: donor
   grammar sufficient; propose NO expansion (empty extension set).
2. Otherwise the failure is materialized as a proof obligation:
   {spec table} minus {exact expressible set of G0 up to the exhausted bound}.
3. Search extension subsets of E in increasing (total cost, lexicographic
   name) order; for each subset, enumerate G0 + subset bottom-up to S_CAND.
   First subset whose language contains the spec table (exact full-domain
   match) is the proposed MINIMAL expansion; by exhaustive order, all strictly
   cheaper subsets are proved insufficient at the bound.
4. If no subset (including all of E) suffices: report
   OBLIGATION_UNRESOLVED_AT_BOUND; no expansion claim.

## Donor baselines (strongest, matched budget)

- D1 supplied-grammar donor: enumerate G0 ONLY, bottom-up, increasing size,
  under a combination-evaluation budget B = 2,000,000 (prespecified); record
  the largest size bound fully exhausted and whether the spec was found. This
  is a bounded inexpressibility PROOF for B1/B3 if the spec is absent.
- Budget matching: candidate total combination evaluations across all its
  enumerations must be <= B (recorded; else GB0 fails).
- D2 trivial-bloat baseline: add ALL of E at once (cost 4) and synthesize at
  S_CAND. The candidate's proposal must have strictly smaller cost than the
  bloat baseline in B1 (else no value above trivial generalization).

## Prespecified gates

- GB0 (budget sanity): candidate evaluations <= 2,000,000.
- GB1 (residual value, B1): donor G0 proves bounded inexpressibility of Gray
  code (spec absent from every fully exhausted size <= its bound); candidate
  proposes an expansion of cost 2 whose language synthesizes the spec exactly
  at S_CAND; every cost-1 subset proved insufficient at S_CAND; proposal cost
  < bloat-baseline cost 4. If donor G0 finds the spec, GB1 is false and the
  terminal is PARENT_SUFFICIENT_NEGATIVE.
- GB2 (donor first-refusal honored, B2): donor G0 synthesizes the spec;
  candidate proposes the EMPTY expansion and records parent_sufficient = true.
- GB3 (hostile catch, B3): hostile spec absent from G0 + every subset of E at
  S_CAND; candidate reports OBLIGATION_UNRESOLVED_AT_BOUND and emits no
  expansion claim (no spurious minimal-extension claim).
- GB4 (determinism): full study run twice in-process; canonical sorted JSON
  byte-identical (SHA-256 digests equal).

## Terminal vocabulary

- `N3B_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`: GB0-GB4 all true.
- `N3B_PARENT_SUFFICIENT_NEGATIVE`: GB1 false because G0 alone matched.
- `N3B_MECHANISM_FAILED_NEGATIVE`: any other gate failure.

## Determinism and receipts

No randomness; SEED = 20260821 recorded. Stdout receipt line
`ORIONQ_N3_B_OBLIGATION_EXPANSION=<canonical sorted compact JSON>` plus pretty
JSON, also written to
`research/extensions/orion-q/nlanes/N3_B_OBLIGATION_EXPANSION_RESULTS.json`.
Schema id: `ORIONQ.N3B.ObligationGrammarExpansion.v1`. Authority string:
`exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority`.

## Claim boundary

Any positive result claims ONLY: in this finite exact world, converting a
bounded-exhaustive synthesis failure into a proof obligation and proposing the
provably minimal grammar extension at the bound outperformed both the supplied
grammar alone and trivial grammar bloat, with the hostile unresolvable case
reported honestly. Inexpressibility statements are bounded (size-limited), not
absolute. No claim about CEGIS/abstraction-refinement tooling or novelty.

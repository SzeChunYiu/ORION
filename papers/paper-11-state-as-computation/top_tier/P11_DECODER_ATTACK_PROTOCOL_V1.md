# P11 decoder-attack frontier protocol V1

**Programme:** #977  
**State:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** extend the T11.2 relative no-answer-laundering witness into a
mapped decoder-capacity frontier: which downstream decoder families can realize
the protected target, at what exact minimal size, so the compositional-decoder
boundary becomes a frontier statement rather than a two-family example.

## Protected target (identical to the frozen T11.2 witness)

For k ∈ {2, 3, 4}: states = {±1}^k in lexicographic order, labels =
`prod(z)` (parity_k). The witness object is not modified.

## Decoder families under attack (frozen)

- **F1 constants** — the 2 constant functions.
- **F2 signed single coordinates** — the 2k functions ±z_j.
- **F3 characters** — ±prod_{j∈S} z_j over all S ⊆ [k] (2^(k+1) functions).
  These are exactly the GF(2)-affine decoders: XOR composition is
  multiplicative in the ±1 representation, so this family closes both the
  "signed monomial" and "affine over GF(2)" readings in one enumeration.
- **F4 odd-majority thresholds** — sign(sum_{j∈J} z_j) over subsets J of odd
  cardinality.
- **F5 axis decision lists** — nodes (coordinate, branch value ±1, leaf label
  ±1) with a terminal default label; all lists of length ≤ 3 enumerated
  exhaustively, plus a registered analytic claim for all lengths.
- **F6 decision trees** — binary trees testing single coordinates;
  construction at 2^k leaves; minimality registered analytically.

## Frozen claims

- **C1** (T11.2 re-verification): no constant realizes parity_k. Exhaustive.
- **C2** (T11.2 re-verification): no signed single coordinate realizes
  parity_k. Exhaustive.
- **C3 character frontier**: the unique realizing character is
  prod_{j∈P} z_j; minimal character degree equals k. Exhaustive over F3.
- **C4**: no odd-majority threshold realizes parity_k. Exhaustive.
- **C5 list impossibility**: no axis decision list of ANY length realizes
  parity_k for k ≥ 2. Verified exhaustively for lengths ≤ 3 on k ∈ {2,3,4};
  the general claim is the prefix-fixing argument: a list node whose matched
  domain is nonempty and leaves a parity coordinate free mislabels some state
  in that domain, and the first node of any list always has such a domain.
- **C6 tree frontier**: parity_k is realized by the depth-k testing tree with
  exactly 2^k leaves, and no tree with fewer leaves realizes it — every leaf
  subcube must fix all k parity coordinates (else labels vary within a leaf),
  and Kraft's inequality in exact rational arithmetic then forces at least 2^k
  leaves.
- **C7 boundary statement**: no-answer-laundering is decoder-family-relative.
  Composition realizes the target with exact minimal sizes (character degree
  k; decision tree 2^k leaves) and every non-compositional family tested
  (F1, F2, F4, F5 at any length) fails.

## Dual verification

- **Runner** (`run_decoder_attacks_v1.py`, stdlib only): exhaustive
  enumeration with direct truth-table comparison, plus explicit constructions
  and the C5 invariant check on every enumerated list.
- **Independent checker** (`check_decoder_attacks_independent_v1.py`, stdlib
  only): exact Fourier/Möbius spectra in `Fraction` arithmetic (two functions
  are equal iff their spectra are equal) instead of truth-table comparison;
  explicit witness-pair extraction (two states on which the decoder agrees but
  the labels differ) for F1/F2/F4/F5; the C5 reduction implemented
  independently; the C6 Kraft check in exact Fractions with an independent
  recursive tree evaluator. The two implementations share no comparison code
  path.

## Terminals

- `P11_DECODER_ATTACK_V1_GREEN` (runner) — every enumerated disposition and
  construction check holds.
- `P11_DECODER_ATTACK_V1_INDEPENDENT_GREEN` (checker) — every claim
  re-derived by the second mathematics.
- Byte-replay determinism for both programs, asserted in CI before any
  receipt is bound.
# MAX-R6O enlarged-Tag donor closure protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Predecessor: MAX_R6N_SUPPORT_DOMINANCE_PROTOCOL.md (outcome: REFUTED at the
declared Tag-repair gap; frame support dominance itself machine-verified with
0 violations over 688,041,472 local configurations).
Status: FROZEN BEFORE R6O OUTCOME.
Authority ceiling: explanatory family-closure audit over the frozen R6M
grammar; not R6, no novelty credit, no donor credit, no new subject data.

## Scientific question

R6N refuted the full weight-one donor-family closure of the R6M grammar at
exactly its declared gap: on the synthetic instance `n2_b` the unrestricted
exact DP optimum is 8 while the R6L weight-one donor family optimum is 9, and
the DP witness uses weight-one frames anchored at *different* qubits (block A
at qubit 0, blocks B and C at qubit 1) with a weight-2 shared Tag (Y(x)Y) —
inexpressible in the R6L grammar, whose shared Tag key forces a common
weight-one Tag (hence a common anchor qubit). R6N's post-gate diagnostic
showed that "weight-one frames + unrestricted minimal shared Tag" already
reaches 8 on that instance.

R6O freezes and tests the natural repair hypothesis:

> **Enlarged-Tag donor closure.** Define the enlarged donor family
> `D+` = { three weight-one TARE-M2 frames with arbitrary per-block anchor
> qubits, one shared Tag `S` of unrestricted support minimized subject to the
> common label constraints, donor-owned all-three Restore factoring }. On
> every instance of the frozen R6M grammar, the unrestricted exact DP optimum
> equals the `D+` optimum: `C_DP == C_D+`. Support dominance (verified in
> R6N) handles the frames; the unrestricted minimal Tag handles the
> Tag-anchor coupling that broke R6N.

`D+` is still donor-owned machinery: weight-one frames and minimum-weight
shared Tags are donor concepts (R6L); the enlargement is bookkeeping over
anchor combinations. No novelty credit attaches to a positive outcome.

## Frozen `D+` definition

Local Pauli letters `0=I, 1=X, 2=Y, 3=Z` with the frozen `local_mul` /
`local_symp` / `local_wt` algebra of the R6 stack. An instance is six targets
grouped by a matching into ordered blocks A, B, C with target pairs
`(P_j0, P_j1)`.

A `D+` member is determined by the choice tuple

- per block `j in {A,B,C}`: an anchor qubit `q_j in {0..n-1}`, an ordered
  letter pair `(a_j, b_j)` of two *distinct non-identity* local letters
  (6 ordered pairs), giving weight-one frames `R_j0 = a_j` at `q_j`,
  `R_j1 = b_j` at `q_j` (automatically anticommuting), and a target
  permutation `p_j in {0,1}` (identity / swap of the block's target pair);
- a common label orientation `(l0, l1) in {(0,1), (1,0)}` shared by all
  three blocks (`<S, R_j0> = l0`, `<S, R_j1> = l1` for all `j`), matching the
  R6M DP acceptance constraints (equal labels across blocks, distinct labels
  across branches);
- the shared Tag `S`: the *unique minimum-weight* Pauli satisfying the six
  label constraints.

**Exact minimal Tag (frozen closed form).** Because every frame Pauli is
weight-one at its anchor, the constraints act only on the local letters of
`S` at the anchor qubits. For a block with pair `(a, b)`: with labels
`(0,1)`, the local letter of `S` at its anchor must commute with `a` and
anticommute with `b`; among the 4 letters the unique solution is `a` itself
(`I` and the third letter fail the anticommute/commute split, `b`
anticommutes with `a`). With labels `(1,0)` the unique solution is `b`.
Hence each anchor qubit carries a *forced* letter per block anchored there; a
choice tuple is **feasible** iff all blocks sharing an anchor qubit force the
same letter, and then the minimal Tag is that forced letter at each distinct
anchor qubit and identity elsewhere, so

`w(S) = number of distinct anchor qubits among (q_A, q_B, q_C) in {1,2,3}`.

Any feasible Tag must carry every forced letter, so this is the unique
minimum; the Tag term `2 w(S)` is additive and independent of the Restore
term, so restricting to minimal Tags loses no `D+` optimum. This closed form
is machine-verified in-run: (i) the local uniqueness claim exhaustively over
all 6 ordered pairs x 2 label orientations x 4 candidate letters, and (ii) a
full global brute at n=2 over all `8 anchor-triples x 216 letter-pair
triples x 2 labels = 3456` combinations against all 256 two-qubit Paulis
(minimum feasible weight == #distinct anchors; infeasible exactly when
forced letters clash at a shared anchor).

**Frozen `D+` cost** (identical objective to the frozen R6M grammar):

`C_D+ = 2 w(S) + sum_{k in {0,1}} F3support(T_Ak, T_Bk, T_Ck)`

with `T_jk = P_{j, pi_j(k)} * R_jk` (`pi_j` = the block's target
permutation), `F3support` = the frozen donor-owned all-three Restore
common-factor support (per qubit: 1 if all three local letters are equal and
non-identity, else the sum of the three local weights). Uanti support is 0
for every weight-one frame under either central choice (both multipliers act
on `w-1 = 0`), so the central bits are cost-irrelevant inside `D+` and are
not enumerated.

**Enumeration and completeness.** The enumerator sweeps all
`2 labels x 2^3 permutations x n^3 anchor triples x 6^3 letter-pair triples`
choice tuples, skips infeasible ones, and attaches the unique minimal Tag to
each feasible one. Every `D+` member corresponds to exactly one choice tuple
(the Tag is determined), so the sweep is complete. (Enumerating all three
per-block permutations plus both label orientations double-covers the
grammar's branch-swap symmetry; this is redundancy, not omission.)

**Containments (hard integrity assertions wherever both sides are
computed).** Every `D+` member is a member of the full R6M grammar (weight-
one frames are frames; `S` satisfies the acceptance constraints), so
`C_DP <= C_D+` always. The R6L donor family is the `D+` sub-family with a
common anchor qubit and agreeing forced letters (shared weight-one Tag), so
`C_D+ <= C_R6L` always. Hence `C_DP <= C_D+ <= C_R6L` on every instance.

## Equality gate

On every instance of every verification domain below:

`C_DP == C_D+` (unrestricted exact R6M DP optimum equals the `D+` optimum).

## Structural independence

The unrestricted optimum is obtained from the frozen R6M module
(`max_r6m_exact_three_tare2_shared_factor_dp`) unmodified. The `D+`
enumerator is written independently of the DP code paths: it uses only the
frozen local algebra primitives (`p10.mul/wt/symp`, `h.BITS_CODE` /
`h.CODE_BITS`) and its own F3 table, and never touches `_local_table`,
`_solve_config`, `_DELTA` or the DP backtracking. Binding checks: the
independent F3 table must equal `r6m._F3` exactly, and sampled `D+` witnesses
are re-verified through the frozen `factor_restore_triple` (exact phases)
with recomputed cost equality.

## Verification domains (all prespecified)

- **(a) R6N synthetic R6M-grammar panels** (5 instances): the three frozen
  n=1 panels and both frozen n=2 panels (`n2_a` and the refuting `n2_b`),
  built by the frozen `_synthetic_terms` on the frozen target pairs with the
  frozen matching `((0,1),(2,3),(4,5))`. DP side: frozen
  `exact_r6m_matching` (full witness). The R6N *R6I-grammar* panels are out
  of scope: they belong to a different frozen family whose weight-one closure
  was verified, not refuted, in R6N.
- **(b1) Exhaustive n=1** (4096 instances): ALL ordered 6-tuples
  `(PA0,PA1,PB0,PB1,PC0,PC1) in {I,X,Y,Z}^6` of local targets at n=1,
  matching `((0,1),(2,3),(4,5))`. This exhausts the entire R6M grammar
  instance space at n=1. DP side: at n=1 the frozen DP state after the single
  qubit equals the frozen `_local_table` cost vector, so
  `C_DP = min over the two frozen accepting states, 4 relative-permutation
  configs and 8 central configs of the table entry, minus 18`; this reader
  is bound to the frozen `_dp_config_cost` on every 32nd instance (128
  instances) and to `exact_r6m_matching` on 8 instances, requiring exact
  equality.
- **(b2) Exhaustive structured n=2** (9261 instances): ALL `21^3` instances
  in which each block's target pair is an unordered pair (repetition
  allowed) of the six weight-one two-qubit Paulis
  `{X0,Y0,Z0,X1,Y1,Z1}` (frozen order: qubit-0 X,Y,Z then qubit-1 X,Y,Z;
  canonical within-block order = nondecreasing frozen index), matching
  `((0,1),(2,3),(4,5))`. Within-block order is canonical WLOG: swapping a
  block's pair maps both families onto themselves cost-preservingly (D+ by
  its per-block permutation; the DP by its relative permutations for B/C and
  by the global branch swap for A, which exchanges the two accepting states
  and is enumerated); this invariance is additionally machine-checked by
  recomputing the DP cost with block A's pair swapped on 32 deterministic
  instances (every 290th) and requiring equality. This slice is exactly the
  regime that produced the R6N refutation (weight-one targets spread over
  two qubits). DP side: the frozen two-qubit DP identity
  `C = min over accepting s of min_d (c0[d] + c1[d xor s]) - 18` evaluated
  directly on the frozen `_local_table` vectors `c0, c1`; bound to the frozen
  `_dp_config_cost` on every 97th instance (96 instances), requiring exact
  equality.
- **(c) Seeded random panel** (240 instances): 120 at n=2 then 120 at n=3,
  generated by `numpy.random.default_rng(20260821)` in frozen order; each
  instance is six iid uniform non-identity Paulis (draw `x, z` uniform in
  `[0, 2^n)`, redraw while `(x,z) == (0,0)`), matching
  `((0,1),(2,3),(4,5))`. DP side: frozen `_dp_config_cost` minimized over
  all 4 x 8 relative-permutation/central configs.
- **(d) Frozen chemistry subjects** (30 matchings): H4 (n=8) and
  equilibrium N2 (n=12), loaded ONLY via the frozen `r6f._frozen_batch`
  path with source-blob verification; all 15 frozen perfect matchings per
  subject. DP side: the recorded `C_R6M` per matching from the frozen
  receipt `MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json` (the
  heavy chemistry DP is not re-run; the receipt's equality with a fresh
  donor recomputation was already machine-verified by R6N). R6L side:
  recomputed fresh via the frozen `donor_r6l_matching` and required to equal
  the recorded `C_R6L_same_matching`. Prediction: `D+` ties the old donor on
  all 30 matchings (`C_D+ == C_R6L`), which is forced whenever the gate
  `C_D+ == C_R6M` holds, since `C_R6M == C_R6L` on all 30 recorded rows.
  The protected stretched-N2 discriminator is never read.

Witness re-verification (frozen `factor_restore_triple` with exact phases,
syndrome and anticommutation checks, cost recomputation): on every instance
of domain (a), every chemistry matching of domain (d), and deterministic
samples of the large domains (every 64th instance of (b1), every 97th of
(b2), every 10th of (c)).

## Prespecified gates

- G1 `dp_dplus_equal_r6n_panels`: `C_DP == C_D+` on all 5 panel instances
  (including the R6N-refuting `n2_b`).
- G2 `dp_dplus_equal_exhaustive_n1`: equality on all 4096 n=1 instances.
- G3 `dp_dplus_equal_structured_n2`: equality on all 9261 instances.
- G4 `dp_dplus_equal_random_panel`: equality on all 240 instances.
- G5 `chemistry_dplus_equals_receipt_dp`: `C_D+ == C_R6M(receipt)` on all 30
  matchings.
- G6 `chemistry_dplus_ties_r6l`: `C_D+ == C_R6L(recomputed) ==
  C_R6L(receipt)` on all 30 matchings (predicted consequence of G5).
- G7 `dp_reader_binding_exact`: the fast n=1 / n=2 DP readers agree exactly
  with `_dp_config_cost` / `exact_r6m_matching` on all binding samples, the
  independent F3 table equals `r6m._F3`, and the block-A-swap invariance
  check passes.
- G8 `tag_minimality_verified`: local forced-letter uniqueness (24 cases,
  each over 4 candidate letters) and the full n=2 global Tag brute (3456
  combos x 256 Paulis) both confirm the frozen closed form.
- G9 `witness_reverification_pass`: every sampled/full `D+` witness and every
  domain-(a) DP witness passes the frozen checks with recomputed cost
  equality.
- G10 `no_new_subject_data`: chemistry only via the frozen `r6f._frozen_batch`
  path with blob verification; stretched-N2 unread.

Hard integrity assertions (abort nonzero, no authority emitted, on failure):
`C_DP <= C_D+` on every instance where both are computed; `C_D+ <= C_R6L` on
every instance where R6L is computed (all of (a), (c), (d)); receipt /
recomputation mismatches; binding failures; blob mismatches.

## Honest outcome space

- All of G1-G10 pass: authority
  `MAX_R6O_ENLARGED_TAG_DONOR_CLOSURE_VERIFIED__FAMILY_CLOSURE_RESTORED_ON_VERIFIED_DOMAINS__NOT_R6`.
  `D+` restores exact family closure on the stated finite domains:
  exhaustively at n=1, exhaustively on the weight-one structured n=2 slice
  (the refuting regime), and on every panel, random and recorded chemistry
  instance. This is bounded machine evidence, not an unconditional theorem
  for all n, and carries no novelty credit.
- Any instance with `C_DP < C_D+` in G1-G5: the hypothesis is FALSE; that is
  a SECOND NEW REGIME beyond the R6N Tag-anchor coupling (weight-one frames
  plus unrestricted minimal shared Tag still insufficient). Authority
  `MAX_R6O_ENLARGED_TAG_DONOR_CLOSURE_REFUTED__SECOND_NEW_REGIME_FOUND__NOT_R6`;
  every violating instance is serialized verbatim (targets, matching, both
  costs, DP witness where computed) and reported prominently. Refutation is
  a fully acceptable outcome.
- Any integrity failure: abort nonzero with the failing assertion; no
  authority string.

## Claim boundary (must be restated in the receipt)

The claim covers exactly the frozen R6L/R6M three-block TARE-M2
shared-one-bit-Tag grammar with the donor-owned all-three Restore
common-factor rule under the frozen raw support-count objective. Equality is
machine-evidenced only on the stated finite domains (exhaustive at n=1 and on
the structured weight-one n=2 slice; sampled/recorded elsewhere); it is NOT a
theorem for all n or all instances, and the Tag-repair coupling term remains
analytically unbounded (the R6N declared gap is repaired empirically by
enlarging the family, not closed by a proof). `D+` is donor-owned
machinery — weight-one frames and minimal shared Tags are R6L donor
concepts; the enlargement over per-block anchors is bookkeeping and earns no
novelty credit and no donor credit. Other objectives, rotation-count
trade-offs, larger Tag ranks, grammars outside the frozen family, and all
fresh subject data (including the protected stretched-N2 discriminator)
are out of scope. Not R6.

## Receipt

Single stdout line
`ORIONQ_MAX_R6O_ENLARGED_TAG_DONOR=<canonical sorted json>` plus pretty
`MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`, containing: the frozen `D+`
definition summary, per-domain instance counts and equality counts, every
violating instance verbatim, the 30-matching chemistry table with the
receipt DP / recomputed R6L / `D+` sandwich, all gates, binding and Tag-brute
results, the runtime, the authority string (containing `NOT_R6`), and the
claim-boundary text above.

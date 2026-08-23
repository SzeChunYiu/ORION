# MAX-R6P weight-2 frame donor closure protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Predecessor: MAX_R6O_ENLARGED_TAG_DONOR_PROTOCOL.md (outcome: REFUTED — on
486/9261 exhaustive structured-n2 instances and 73/240 seeded random
instances the unrestricted R6M DP is strictly below the enlarged weight-one
family `D+`; every observed gap is 1 or 2 support units; the DP witnesses
spend a weight-2 frame Pauli at the central multiplier to compress the shared
Tag to weight one and improve Restore-factor alignment; smallest
counterexample: structured-n2 instance_index 16, targets
A=((1,0),(1,0)), B=((1,0),(1,0)), C=((2,0),(2,2)), DP 5 < D+ 6).
Status: FROZEN BEFORE R6P OUTCOME.
Authority ceiling: explanatory family-closure audit over the frozen R6M
grammar; not R6, no novelty credit, no donor credit, no new subject data.
Weight-2 admission is bookkeeping over the already-characterized trade
(the R6O refutation mechanism); a positive outcome earns no novelty.

## Scientific question

R6O refuted the enlarged weight-one donor family `D+` (weight-one frames,
arbitrary per-block anchors, minimal unrestricted shared Tag) exactly at the
newly observed trade: the unrestricted DP buys a Tag/factor saving by paying
for one weight-2 frame Pauli placed on the cheap central multiplier. R6N's
support-dominance audit (0 violations over 688,041,472 local configurations)
machine-verified that each unit of frame support can only tie or purchase
Tag/Restore-factor savings bounded by its own cost, so support beyond weight
2 should never *strictly* pay once weight-2 frame letters — the observed
trade currency — are admitted into the donor family. R6P freezes and tests
the resulting repair hypothesis:

> **Weight-2 frame donor closure.** Define the further-enlarged donor family
> `D++` = { three TARE-M2 frames whose six frame Paulis each have global
> support <= 2 (arbitrary support sets / anchors), one shared Tag `S` of
> unrestricted support minimized subject to the common label constraints,
> per-block central-branch choice, donor-owned all-three Restore factoring }.
> On every instance of the frozen R6M grammar, the unrestricted exact DP
> optimum equals the `D++` optimum: `C_DP == C_D++`.

The support-dominance reasoning above is stated as *motivation only*; the
gate is empirical equality on the frozen domains. A refutation — an instance
whose DP optimum needs a frame Pauli of support >= 3 — would be a THIRD
regime beyond the R6N Tag-anchor coupling and the R6O weight-2 trade, and is
a valid, fully reportable discovery.

## Frozen `D++` definition

Local Pauli letters `0=I, 1=X, 2=Y, 3=Z` with the frozen
`local_mul`/`local_symp`/`local_wt` algebra of the R6 stack. An instance is
six targets grouped by a matching into ordered blocks A, B, C with target
pairs `(P_j0, P_j1)`.

A `D++` member is determined by the choice tuple

- per block `j in {A,B,C}`: an ordered pair of *nonzero* frame Paulis
  `(R_j0, R_j1)` with `symp(R_j0, R_j1) = 1` (anticommuting) and global
  support `wt(R_jk) <= 2` for both `k` (arbitrary support sets; weight-one
  frames are the special case), a target permutation `p_j in {0,1}`, and a
  central-branch bit `c_j in {0,1}` (now cost-relevant: weight-2 letters make
  the M2 Uanti term nonzero);
- a common label orientation `(l0, l1) in {(0,1), (1,0)}` shared by all
  three blocks (`<S, R_j0> = l0`, `<S, R_j1> = l1` for all `j`), matching the
  R6M DP acceptance constraints;
- the shared Tag `S`: a *minimum-weight* Pauli satisfying the six label
  constraints (the GF(2) symplectic solution set may carry several
  minimum-weight members once frames spread over several qubits; any one
  minimum realizes the family cost, and the frozen enumerator's
  deterministic tie-break below fixes the recorded witness).

**Frozen `D++` cost** (identical objective to the frozen R6M grammar):

`C_D++ = sum_j Uanti_j + 2 w(S) + sum_{k in {0,1}} F3support(T_Ak, T_Bk, T_Ck)`

with `T_jk = P_{j, pi_j(k)} * R_jk`, `F3support` = the frozen donor-owned
all-three Restore common-factor support (per qubit: 1 if all three local
letters are equal and non-identity, else the sum of the three local
weights), and the frozen M2 raw-frame rule
`Uanti_j = 4 (w(R_{j,nc}) - 1) + 2 (w(R_{j,c}) - 1)` (central multiplier 2,
non-central 4). Centrals affect only `Uanti`, so each block's central bit is
minimized independently; frozen tie-break: central on the heavier frame
Pauli, `c_j = 0` on equal weights.

**Tag relaxation identity (frozen, with proof).** `S` enters the cost only
through the additive term `2 w(S)` and the feasibility constraints; hence

`min over D++ members = min over (frames, perms, labels) and ALL feasible S
of [frame terms + 2 w(S)]`,

because for each feasible (frames, labels) the inner minimum over `S` is
attained exactly by a minimum-weight feasible Tag, and non-minimal Tags can
only increase the cost. The enumerator therefore sweeps `S` over all
`4^n - 1` nonzero Paulis (identity is never feasible: distinct labels force
`S` to anticommute with some frame Pauli); this realizes the minimal-Tag
family definition exactly, extending R6O's exact Tag-minimality machinery
from the anchored closed form to arbitrary support-<=2 frames. Witness-level
check: for every re-verified witness, the recorded `S` is confirmed to be a
minimum-weight feasible Tag by exhaustive brute force over all `4^n` Paulis
(n <= 3 on every domain where the direct search runs).

**Enumeration and completeness.** Per block the enumerator sweeps ALL
ordered pairs of nonzero support-<=2 Paulis with symplectic product 1
(`P(n)` pairs: 6 at n=1, 120 at n=2, and the full anticommuting pair count
over the 36 support-<=2 Paulis at n=3; the realized counts are asserted
in-run) times both target permutations; globally it sweeps both label
orientations and all nonzero Tags `S`. Every `D++` member corresponds to a
swept tuple (frames, perms, labels are enumerated outright; the minimal Tag
is covered by the relaxation identity; centrals are covered by the per-block
minimum, which is exact because centrals enter no other term), so the sweep
is complete.

**Exact joint minimization (frozen pattern transform).** For fixed
`(S, labels)` the blocks are filtered independently by the label
constraints; the residual coupling is the F3 bonus (−2 per (branch, qubit)
position where all three T letters are equal and non-identity). Per block
the enumerator scatter-minimizes `base_j = Uanti_j + w(T_j0) + w(T_j1)` over
the base-4 letter code of `(T_j0, T_j1)` on the `2n` positions, then applies
the exact don't-care min-transform: `g_j[pattern]` = minimum `base_j` over
codes whose letters agree with every non-`*` pattern digit. The joint
optimum for this `(S, labels)` is
`min over patterns of g_A + g_B + g_C + 2 w(S) - 2 #(non-* digits)`.
Exactness: any choice triple is reproduced with its exact cost by the
pattern equal to its all-three-match letter set, and every pattern value is
an upper bound realized by some triple whose actual match set contains the
pattern; hence the pattern minimum equals the true triple minimum. A safe
lower-bound prune (`2 w(S) + sum_j min base_j − 4n >= incumbent`) may skip
`(S, labels)` iterations; it never affects the returned minimum.
Deterministic tie-breaks: labels in order ((0,1),(1,0)), `S` ascending by
(weight, key), first-minimum pattern, lowest choice index per block.

**Containments (hard integrity assertions wherever both sides are
computed).** Every `D+` member is a `D++` member (weight-one frames have
support <= 2, Uanti = 0, same minimal Tag), and every `D++` member is a
member of the full R6M grammar, so `C_DP <= C_D++ <= C_D+ <= C_R6L` on every
instance (R6L computed on panels, random and chemistry domains as in R6O).

## Equality gate

On every instance of every verification domain below:

`C_DP == C_D++` (unrestricted exact R6M DP optimum equals the `D++` optimum).

## Structural independence

The unrestricted optimum is obtained from the frozen R6M module
(`max_r6m_exact_three_tare2_shared_factor_dp`) unmodified — the DP is the
referee. The `D++` enumerator is written independently of the DP code paths:
it uses only the frozen local algebra primitives (`p10.mul/wt/symp`,
`h.BITS_CODE`/`h.CODE_BITS`) and its own F3/weight tables, and never touches
`_local_table`, `_solve_config`, `_DELTA` or the DP backtracking. The `D+`
reference values are recomputed via the frozen, already-machine-verified R6O
enumerator (`max_r6o_enlarged_tag_donor_closure.dplus_pairs`), imported
unmodified. Binding checks: the independent F3 table must equal `r6m._F3`
exactly; the new enumerator restricted to weight-one frames must reproduce
`C_D+` exactly on binding samples; witness `Uanti` values must equal the
frozen `r6m._uanti_m2`; sampled `D++` witnesses are re-verified through the
frozen `factor_restore_triple` (exact phases) with recomputed cost equality.

## Verification domains (all prespecified; full panels, no subsampling)

- **(a) The R6O critical set** — ALL 486 structured-n2 violations and ALL 73
  random violations recorded by the frozen R6O receipt
  `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`. These are the instances where
  `C_DP < C_D+`, i.e. exactly where `D++` must do new work. Realization:
  both R6O panels are re-derived IN FULL below (so no violation can be
  sampled away); the receipt is read and cross-checked as follows. The
  receipt's 240 random rows identify all 73 violating (n, index) pairs
  explicitly: the run's own gap set must equal that set exactly, and every
  one of the 240 rows must match the receipt's recorded
  `C_unrestricted_dp` / `C_Dplus` / `C_R6L_weight_one_donor` values. The
  receipt caps structured-n2 verbatim rows at 20: the run's structured-n2
  gap set must have size exactly 486 (= 9261 − the receipt's equal_count
  8775) and must contain all 20 verbatim receipt rows with exactly matching
  costs. Every critical instance receives a full `D++` witness
  re-verification (frozen factor machinery, exact phases, Tag-minimality
  brute, cost recomputation).
- **(b) Exhaustive structured n=2** (9261 instances): the identical frozen
  panel construction as R6O (`21^3` unordered pairs over the six weight-one
  two-qubit Paulis, frozen order, matching `((0,1),(2,3),(4,5))`), for
  direct comparability. DP side: the frozen two-qubit DP identity on
  `r6m._local_table`, bound to `_dp_config_cost` on every 97th instance and
  to `exact_r6m_matching` on every 1153rd instance; block-A swap invariance
  re-checked on every 290th instance.
- **(c) Exhaustive n=1** (4096 instances): ALL ordered 6-tuples of local
  targets, as in R6O. At n=1 every Pauli has weight one, so `D++ == D+`
  structurally; the run still executes the new enumerator on all 4096
  instances and the sandwich forces the check. DP side: frozen
  `_local_table` reader bound to `_dp_config_cost` on every 32nd instance
  and to `exact_r6m_matching` on every 512th.
- **(d) Seeded random panel** (240 instances): the identical frozen
  generator as R6O — `numpy.random.default_rng(20260821)`, 120 at n=2 then
  120 at n=3, six iid uniform nonzero Paulis each, matching
  `((0,1),(2,3),(4,5))`. DP side: frozen `_dp_config_cost` over all 32
  configs. R6L recomputed per instance for the sandwich and receipt
  cross-check.
- **(e) R6N synthetic R6M-grammar panels** (5 instances, including the
  R6N-refuting `n2_b`): DP via frozen `exact_r6m_matching` (full witness),
  full `D++` witness verification.
- **(f) Frozen chemistry subjects** (30 matchings): H4 (n=8) and equilibrium
  N2 (n=12), loaded ONLY via the frozen `r6f._frozen_batch` path with
  source-blob verification; all 15 frozen matchings per subject. DP side:
  the recorded `C_R6M` from the frozen R6M receipt (heavy chemistry DP not
  re-run; its receipt equality was machine-verified by R6N). `C_D+`
  recomputed fresh via the frozen R6O enumerator and required to equal the
  R6O receipt's recorded `C_Dplus`; `C_R6L` recomputed fresh and required to
  equal both receipts. `C_D++` at n=8/n=12 is obtained by the **pinch**: the
  hard containment `C_DP <= C_D++ <= C_D+` plus recorded/recomputed
  `C_D+ == C_R6M(receipt)` on all 30 rows forces `C_D++` equal to both; the
  direct `D++` sweep (Tag space `4^n − 1`) is infeasible and prespecified as
  not run at chemistry scale — the pinch is exact, not an approximation.
  Expected outcome: quadruple tie `C_DP == C_D++ == C_D+ == C_R6L` on all 30
  matchings. The protected stretched-N2 discriminator is never read.

Witness re-verification (frozen `factor_restore_triple` with exact phases,
anticommutation, label, support-<=2 and Tag-minimality-brute checks, cost
recomputation): on every instance of domain (e), every critical instance of
domain (a), every 97th instance of (b), every 64th of (c), every 10th of
(d). Weight-one-restricted binding runs of the new enumerator against the
frozen R6O `dplus_pairs`: all 5 panels, every 210th of (b), every 128th of
(c), every 15th of (d).

## Prespecified gates

- G1 `dp_dxx_equal_r6n_panels`: `C_DP == C_D++` on all 5 panel instances.
- G2 `dp_dxx_equal_exhaustive_n1`: equality on all 4096 n=1 instances.
- G3 `dp_dxx_equal_structured_n2`: equality on all 9261 instances.
- G4 `dp_dxx_equal_random_panel`: equality on all 240 instances.
- G5 `critical_set_receipt_crosscheck`: structured-n2 gap set (`C_DP <
  C_D+`) has size exactly 486 and contains all 20 receipt verbatim rows
  with matching costs; random gap set equals the receipt's 73 (n, index)
  rows exactly and all 240 rows match the receipt's three recorded costs.
- G6 `critical_set_closed_at_weight_two`: `C_DP == C_D++` on all 486 + 73
  critical instances (the headline sub-gate of G3/G4).
- G7 `chemistry_pinched_quadruple_tie`: on all 30 matchings,
  `C_D+`(recomputed) == R6O receipt `C_Dplus` == R6M receipt `C_R6M` ==
  `C_R6L`(recomputed) == receipt `C_R6L`; hence `C_D++` equals all of them
  by the pinch.
- G8 `dxx_enumerator_binding`: independent F3 table equals `r6m._F3`;
  weight-one-restricted enumerator equals frozen `dplus_pairs` on all
  binding samples; per-n anticommuting support-<=2 pair counts match the
  asserted closed forms; witness `Uanti` equals `r6m._uanti_m2`.
- G9 `dp_reader_binding_exact`: the fast n=1/n=2 DP readers agree exactly
  with `_dp_config_cost` / `exact_r6m_matching` on all binding samples and
  the block-A-swap invariance check passes.
- G10 `tag_minimality_verified`: every re-verified witness's `S` is a
  minimum-weight feasible Tag under exhaustive brute force over all `4^n`
  Paulis, and satisfies the six label constraints.
- G11 `witness_reverification_pass`: every sampled/critical `D++` witness
  and every domain-(e) DP witness passes the frozen checks with recomputed
  cost equality.
- G12 `no_new_subject_data`: chemistry only via the frozen
  `r6f._frozen_batch` path with blob verification; stretched-N2 unread.

Hard integrity assertions (abort nonzero, no authority emitted, on
failure): `C_DP <= C_D++` and `C_D++ <= C_D+` on every instance where both
sides are computed; `C_D+ <= C_R6L` where R6L is computed; receipt /
recomputation mismatches; binding failures; blob mismatches; internal
backtrack cost-recomputation mismatches.

## Honest outcome space

- All of G1-G12 pass: authority
  `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_VERIFIED__FAMILY_CLOSURE_RESTORED_AT_SUPPORT_TWO_ON_VERIFIED_DOMAINS__NOT_R6`.
  `D++` restores exact family closure on the stated finite domains,
  repairing the R6O gap at exactly the observed weight-2 trade. Bounded
  machine evidence, not an unconditional theorem for all n; no novelty
  credit (the weight-2 admission is bookkeeping over the trade the R6O
  refutation already characterized).
- Any instance with `C_DP < C_D++` in G1-G4: the hypothesis is FALSE; that
  is a THIRD regime (some DP optimum needs frame support >= 3, beyond both
  the R6N Tag-anchor coupling and the R6O weight-2 trade). Authority
  `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_REFUTED__THIRD_REGIME_BEYOND_SUPPORT_TWO_FOUND__NOT_R6`;
  every violating instance is serialized verbatim (targets, matching, both
  costs, D+ cost, DP witness where computed) and reported prominently.
  Refutation is a fully acceptable outcome.
- Any integrity failure: abort nonzero with the failing assertion; no
  authority string.

## Claim boundary (must be restated in the receipt)

The claim covers exactly the frozen R6L/R6M three-block TARE-M2
shared-one-bit-Tag grammar with the donor-owned all-three Restore
common-factor rule under the frozen raw support-count objective. Equality is
machine-evidenced only on the stated finite domains (exhaustive at n=1 and
on the structured weight-one n=2 slice — including every R6O critical
instance — plus the 5 panels, the 240-instance seeded random panel, and the
30 recorded chemistry matchings, the latter via the exact containment
pinch); it is NOT a theorem for all n or all instances. Support dominance
(R6N) motivates but does not prove the closure; the coupling term remains
analytically unbounded and is repaired empirically by family enlargement.
`D++` is donor-owned machinery — weight-one frames, minimal shared Tags and
the Restore factor rule are R6L donor concepts, and the support-2 admission
is bookkeeping over the R6O-characterized trade; it earns no novelty credit
and no donor credit. Other objectives, rotation-count trade-offs, larger
Tag ranks, grammars outside the frozen family, support-3+ frame families,
and all fresh subject data (including the protected stretched-N2
discriminator) are out of scope. Not R6.

## Receipt

Single stdout line
`ORIONQ_MAX_R6P_WEIGHT2_FRAME_DONOR=<canonical sorted json>` plus pretty
`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`, containing: the frozen
`D++` definition summary, per-domain instance counts and equality counts,
the full critical-set closure table (every one of the 486 + 73 rows with
`C_DP`/`C_D+`/`C_D++`; full targets verbatim for the random criticals and
for the first 20 structured criticals, the rest derivable from the frozen
instance_index), any violating instance verbatim, the 30-matching chemistry
table with the receipt DP / recomputed R6L / `D+` / pinched `D++` sandwich,
all gates, binding and Tag-minimality results, the authority string
(containing `NOT_R6`), and the claim-boundary text above. Determinism: the
canonical stdout receipt line and the RESULTS body exclude wall-clock
values; `runtime_seconds` is appended to the RESULTS file as the single
non-deterministic field. A double run must produce a byte-identical stdout
receipt line and RESULTS files identical up to `runtime_seconds`.

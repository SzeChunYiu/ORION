# MAX-R6N support-dominance lemma audit protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Status: FROZEN BEFORE R6N OUTCOME.
Authority: explanatory family-closure audit over already-frozen open-subject receipts; not R6, not novelty authority, no new subject data.

## Scientific question

Four exact-DP lanes (R6I, R6K, R6L, R6M) all collapsed onto weight-one donor
families: every unrestricted exact optimum equalled the weight-one-restricted
donor optimum on every frozen partition/matching of both open subjects. R6N
freezes and machine-verifies the candidate lemma that explains all four
collapses analytically rather than empirically:

> **Support dominance.** Within the frozen TARE frame-grammar families and
> support-count objectives, each unit of frame support costs at least 2
> (central branch) or 4 (non-central branch) in the raw Uanti term, while its
> maximum achievable savings in the Restore / factor terms is at most 2 per
> unit. Hence removing frame support never increases structural cost faster
> than it releases Uanti cost, and an exact optimum is always attained by
> frames of minimal support — the weight-one donor family is optimal within
> the full grammar.

R6N is an audit of existing receipts plus exhaustive finite verification. It
reads no chemistry source files, recomputes no heavy chemistry DP, and never
touches the protected stretched-N2 discriminator.

## Frozen lemma statements

Local Pauli letters are coded `0=I, 1=X, 2=Y, 3=Z` with the frozen
`local_mul` / `local_symp` / `local_wt` algebra of the R6 stack
(`max_r4d_h2o_ducc_confirmation`). `w` denotes support (letter count).

### Lemma N-M (per-qubit support dominance, R6M three-M2 grammar)

Fix one system qubit. Let

- frame letters `f = (rA0,rA1,rB0,rB1,rC0,rC1) in {I,X,Y,Z}^6`,
- tag letter `s in {I,X,Y,Z}`,
- central choices `c = (cA,cB,cC) in {0,1}^3`,
- target letters `t = (pA0,pA1,pB0,pB1,pC0,pC1) in {I,X,Y,Z}^6`.

The frozen R6M local raw cost (exactly the `_local_table` construction of
`max_r6m_exact_three_tare2_shared_factor_dp`) is

`L(f,s,c,t) = Phi_c(f) + 2 w(s) + F3(pA0*rA0, pB0*rB0, pC0*rC0) + F3(pA1*rA1, pB1*rB1, pC1*rC1)`

where `Phi_c(f) = sum_j m_{j,0} w(f_{j,0}) + m_{j,1} w(f_{j,1})` with
`m_{j,k} = 2` if `c_j = k` else `4`, and `F3(a,b,c) = 1` if `a=b=c!=I`, else
`w(a)+w(b)+w(c)` (the frozen donor-owned all-three Restore common-factor
rule).

**Claim.** For every `(f,s,c,t)`:

`TotalSavings(f,t) := [F3(pA0,pB0,pC0)+F3(pA1,pB1,pC1)] - [F3(pA0*rA0,pB0*rB0,pC0*rC0)+F3(pA1*rA1,pB1*rB1,pC1*rC1)] <= Phi_c(f)`,

equivalently `L(f,s,c,t) >= L(0,s,c,t)` for every tag letter `s` (the tag term
is additive and identical on both sides by the frozen table construction; the
verification nevertheless loops over all 4 tag letters as part of the stated
domain).

Exhaustive domain: `4^6` frame configs x `4` tag letters x `8` central
choices x `4^6` target configs = **536,870,912** configurations.

### Lemma N-M' (letterwise exchange monotonicity, R6M factor rule)

For every branch multiplier triple `m in {2,4}^3`, branch frame letters
`f = (fA,fB,fC) in {I,X,Y,Z}^3`, every letterwise sub-configuration `g` of `f`
(each `g_j in {I, f_j}`), and every branch target letters `t`:

`F3(tA*gA, tB*gB, tC*gC) - F3(tA*fA, tB*fB, tC*fC) <= sum_{j: g_j=I != f_j} m_j`.

This is the exchange step needed when one qubit hosts anchor letters of one
block and non-anchor letters of another: zeroing any subset of frame letters
at a qubit, refunding their marginal frame cost, never increases the branch
cost. Exhaustive domain: `343` (f,g) letterwise pairs x `64` targets x `8`
multiplier triples = **175,616** configurations.

### Lemma N-I (per-qubit support dominance, R6I two-block rank-2 grammar)

Fix one system qubit. Per block, frame letters `(r0,r1)` with the dependent
third letter `r2 = r0*r1`; central `c in {0,1,2}` gives multipliers
`(m_0,m_1,m_2) = (4,4,4)` with `m_c = 2`; targets `(p0,p1,p2)`. The frozen
R6I local raw cost (`_local_table` of `max_r6i_exact_rank2_shared_tag_dp`)
for two blocks A,B and tag letters `(s0,s1)` is

`L = PhiA_cA(rA0,rA1) + PhiB_cB(rB0,rB1) + 2(w(s0)+w(s1)) + sum over the six restore slots of w(p_k * r_k)`

with `Phi_c(r0,r1) = m_0 w(r0) + m_1 w(r1) + m_2 w(r0*r1)`.

**Claim.** For every per-qubit configuration:

`TotalSavings := sum_{blocks, k=0..2} [ w(p_k) - w(p_k * r_k) ] <= PhiA_cA(rA0,rA1) + PhiB_cB(rB0,rB1)`,

equivalently `L(F,s,c,T) >= L(0,s,c,T)` for every tag letter pair (again
additive and identical on both sides; looped over anyway).

Exhaustive domain: `4^4` frame configs x `16` tag letter pairs x `9` central
pairs x `4^6` target configs = **150,994,944** configurations.

No letterwise-subset analogue is claimed for R6I: zeroing only one of
`(r0,r1)` moves the dependent letter `r2` between multiplier classes and the
naive subset inequality is false there. The R6I exchange always zeroes the
whole per-qubit block pair, which is exactly Lemma N-I with the other block
letters held fixed.

## Weight-one-restricted families (frozen definitions)

- **R6M restricted family** = the frozen R6L weight-one donor grammar exactly
  as implemented by `donor_r6l_matching` in
  `max_r6m_exact_three_tare2_shared_factor_dp` (weight-one anticommuting
  frame letters at one anchor qubit per block, shared weight-one Tag with a
  common `(S, labels)` key, both target permutations per block, frozen
  factored Restore objective). Zero Uanti support by construction.
- **R6I restricted family** = `RA0,RA1` two distinct non-identity letters at
  one anchor qubit `qA` (so `RA2` is the third letter at `qA`; all three
  frame Paulis weight one, Uanti support 0 for every central choice), same
  for block B at `qB`; all 6 relative B-target permutations; all 6 shared
  label assignments (permutations of `(1,2,3)` with the dependent third label
  automatic); Tag `S0,S1` taken as the unique minimum-weight solutions: at
  each anchor qubit the required syndrome pair against the local frame basis
  forces a unique non-identity letter, so `w(S_i) = 1` when the two blocks'
  forced letters coincide at a common anchor qubit, `w(S_i) = 2` when anchors
  differ, and the combination is infeasible (skipped) when a shared anchor
  qubit forces two different letters. All other qubits carry the identity
  (any extra Tag support only adds cost and changes no constraint).

Both families are strict sub-families of the corresponding full grammars, so
`C_restricted >= C_unrestricted` always; support dominance predicts equality.

## Proof sketch (qubit-wise exchange / induction) and its declared gap

Take any feasible configuration of the full grammar. Because
`<R_j0,R_j1> = 1`, each block has at least one qubit where its two frame
letters both act and anticommute; pick one such anchor per block and truncate
every frame Pauli to its anchor letters. Lemmas N-M / N-M' / N-I state that at
every qubit the Restore/factor savings released by the removed letters never
exceed their raw frame cost, so the raw cost net of Restore/factor terms does
not increase, qubit by qubit (induction over qubits; the parity state of the
DP is repaired at the anchors, where the truncated letters still anticommute).
The frozen constants (6 per M2 block, 18 total for R6M; 10 per rank-2 block,
20 total for R6I) exactly cover one support unit per frame Pauli, so the
truncated weight-one configuration pays zero Uanti support.

**Declared gap:** the truncation changes the Tag syndromes, and the repaired
minimum-weight Tag can cost more than the original spread-frame Tag (by at
most `2*Delta w(S)`). The local inequalities do not bound this Tag-coupling
term. The audit therefore closes the lemma on finite domains only:
exhaustively at the per-qubit level (the three domains above), and exactly at
the joint level on every recorded instance — the two frozen subjects and a
deterministic synthetic n=1 / n=2 panel where the unrestricted DP optimum is
compared directly with the weight-one-restricted optimum. A Tag-coupling
counterexample, if one exists, must therefore show up as a strict gap in one
of the joint comparisons and is reported as a discovery, not suppressed.

## Verification plan (all prespecified)

1. **Local exhaustive checks** (numpy-vectorized): Lemma N-M over
   536,870,912 configs; Lemma N-M' over 175,616 configs; Lemma N-I over
   150,994,944 configs. Report the number of configurations checked, the
   maximum observed `TotalSavings / FrameCost` ratio over configurations with
   positive frame cost, and every violating configuration verbatim (frame
   letters, tag letters, centrals, targets, savings, cost).
2. **Implementation binding**: the audit's `F3`, frame-cost and tag-cost
   tables must be bound to the frozen modules by direct array comparison
   against `max_r6m_exact_three_tare2_shared_factor_dp._F3` /
   `_FRAME_COST` / `_TAG_COST` and by reconstructing the frozen per-option
   raw cost arrays of both DPs (`_local_table`) for a deterministic sample of
   at least 64 R6M `(p6, centrals)` keys and 64 R6I keys, requiring exact
   equality on every option.
3. **Frozen-subject equality, R6M** (receipts only): read
   `MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json`; require
   `C_R6M == C_R6L_same_matching` on all 30 recorded matchings (15 x H4,
   15 x N2); reconstruct the six frozen targets per subject from the recorded
   witnesses (targets field, consistency-checked across all 15 matchings and
   against `T*R` recomputation), re-run the imported weight-one donor
   `donor_r6l_matching` on the reconstruction, and require its cost to equal
   the recorded `C_R6L_same_matching` on every matching. No chemistry source
   file is read; the heavy R6M DP is not re-run.
4. **Frozen-subject equality, R6I** (receipts only): read
   `MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_RESULTS.json`; reconstruct block
   targets from each recorded witness via `target_k = T_k * R_k` (binary
   identity re-checked, cost recomputation re-checked); compute the R6I
   weight-one-restricted optimum by the frozen enumeration above and require
   equality with the recorded `C_shared` on all 20 partitions (10 x H4,
   10 x N2). The heavy R6I DP is not re-run.
5. **Deterministic synthetic joint panel** (imports the frozen modules'
   machinery, no edits): for R6I, all 7 frozen `HOSTILE_PANELS` instances
   (n=1 and n=2), comparing `shared_tag_exact` (unrestricted exact DP) with
   the restricted enumeration; for R6M, the 3 frozen n=1 panels and 2 frozen
   n=2 panels built by `_synthetic_terms` on the frozen hostile target pairs
   with `_SYNTHETIC_MATCHING`, comparing `exact_r6m_matching` (unrestricted)
   with `donor_r6l_matching` (restricted). Soundness requires
   `restricted >= unrestricted` on every instance; support dominance predicts
   equality on every instance.

## Prespecified gates

- G1 `r6m_local_inequality_holds`: zero violations in the 536,870,912-config
  Lemma N-M domain.
- G2 `r6m_letterwise_monotonicity_holds`: zero violations in the
  175,616-config Lemma N-M' domain.
- G3 `r6i_local_inequality_holds`: zero violations in the 150,994,944-config
  Lemma N-I domain.
- G4 `frozen_table_binding_exact`: implementation-binding comparisons all
  exact.
- G5 `r6m_weight_one_equality_on_frozen_subjects`: all 30 matchings satisfy
  `C_R6M == C_R6L_same_matching` and the recomputed donor cost matches.
- G6 `r6i_weight_one_equality_on_frozen_subjects`: all 20 partitions satisfy
  `restricted == C_shared`.
- G7 `synthetic_joint_equality`: all 12 synthetic instances satisfy
  `restricted == unrestricted` (with `restricted >= unrestricted` as a hard
  integrity assertion).
- G8 `no_new_subject_data`: no chemistry source read; stretched-N2 unread.

## Honest outcome space

- All of G1–G8 pass: the receipt authority is
  `MAX_R6N_SUPPORT_DOMINANCE_VERIFIED__FAMILY_CLOSURE_EVIDENCE__NOT_R6`.
  The lemma is machine-verified on the stated finite domains: the local
  inequalities exhaustively, the joint weight-one closure on every recorded
  instance of the family. This is bounded family-closure evidence, not an
  unconditional theorem for all n and not R6 authority.
- Any violation in G1–G3, or any strict gap `unrestricted < restricted` in
  G5–G7: the lemma is FALSE as stated; that is a DISCOVERY of a regime where
  spread-support frames beat weight-one donors. The receipt authority is
  `MAX_R6N_SUPPORT_DOMINANCE_REFUTED__NEW_REGIME_FOUND__NOT_R6` and every
  violating configuration / instance is serialized verbatim and reported
  prominently. Refutation is a fully acceptable outcome of this audit.
- Any integrity failure (G4, reconstruction inconsistency, restricted <
  unrestricted, receipt mismatch): the run aborts nonzero with the failing
  assertion; no authority string is emitted.

## Claim boundary (must be restated in the receipt)

The lemma covers exactly: the frozen R6I two-block rank-2 dependent TARE-3
shared-two-bit-Tag grammar with plain Restore support, and the frozen
R6L/R6M three-block TARE-M2 shared-one-bit-Tag grammar with the donor-owned
all-three Restore common-factor rule, under the frozen raw support-count
objectives with multiplicities (4 non-central / 2 central) and the frozen
constants. It explains the empirical collapses of R6I, R6K and R6M onto their
weight-one donors (R6L/R6H/R6J family): R6K combines the two verified
mechanisms (rank-2 frame costs as in Lemma N-I; common-factor savings bounded
as in Lemma N-M'), although the R6K-specific local table is not separately
enumerated here. It does NOT cover: other objectives (coefficient-weighted or
non-support cost models), rotation-count trade-offs beyond the frozen fixed
counts, larger Tag ranks, grammars outside the frozen families, or subjects /
qubit counts beyond the finite equality domains (the local inequalities hold
per qubit for every n; the joint Tag-coupling closure is verified only on the
recorded instances). No novelty credit, no donor credit, no R6 authority.

## Receipt

Single stdout line
`ORIONQ_MAX_R6N_SUPPORT_DOMINANCE=<canonical sorted json>` plus pretty
`MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json`, containing: both lemma statements'
domain sizes and violation counts, the maximum observed savings/cost ratios,
any violating configurations verbatim, the 30-matching and 20-partition
equality tables, the 12-instance synthetic panel, all gates, the runtime, and
the claim-boundary text above.

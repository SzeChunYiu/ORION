# QG-1 rank-2 all-n composition protocol (generator-support exchange theorem for the R6I shared-Tag grammar)

Date: 2026-08-21
Parent programme: ORION-QG (PROGRAMME_CHARTER_V1.md, issue #740), lane QG-1;
grandparent ORION-Q MAX (#679).
Predecessors (all committed, replay-verified):
- MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_PROTOCOL.md + receipt: the frozen rank-2
  shared-Tag grammar and its exact 10-bit DP (`max_r6i_exact_rank2_shared_tag_dp`).
  The R6I objective has NO Restore common-factor rule (that was added later by
  R6K); its Restore term is the plain sum of Restore supports.
- MAX_R6S_ALL_N_COMPOSITION_PROTOCOL.md + receipt: the all-n support
  composition theorem for the R6M grammar (F2^2 pigeonhole zero-sum-subset
  exchange), whose claim boundary explicitly names the R6I rank-2
  dependent-triple grammar as NOT covered. This lane attacks exactly that
  exclusion.

Status: FROZEN BEFORE QG-1 OUTCOME. The exchange construction, the class
spaces, the case-analysis domains and their sizes, the predicted exceptional
patterns, the gates, the panel seed/sizes and the outcome space below were
written before any lemma enumeration, descent, or panel comparison was run.
The only computations performed before freezing were budget constants: one
timing of the frozen R6I DP at n=3 (~0.85 s/instance), one n=2 spot equality
of the committed DP vs the committed brute (11 == 11) used to size the panel,
and the count identity 63*32 = 2016 for ordered symplectic-1 Pauli pairs at
n=3. The analytic case analysis below (move-type inequalities and pigeonhole
characterizations) was derived on paper before freezing and is exactly what
the machine checks must confirm or refute.

Authority ceiling: explanatory family-closure theorem attempt over the frozen
R6I grammar; NOT_R6, no novelty credit, no donor credit, no new subject data.
No chemistry data is read (the R6I module is imported for its grammar tables
and DP only; its subject loaders are never invoked). The protected
stretched-N2 discriminator is never read or referenced.

## Open object

Extend the all-n support-composition theorem to the frozen R6I rank-2
shared-Tag grammar: prove, for every qubit count n, every pair of target
triples, every relative B permutation and every central pair, that the exact
optimum of the frozen R6I objective is attained by a configuration whose
four frame GENERATORS `RA0, RA1, RB0, RB1` all have global support <= B,
with B stated by the theorem, and characterize the exceptional support
patterns that delineate the boundary (the R6I-grammar analogue of the R6M
weight-2 boundary).

## Frozen grammar recap (bound to the frozen R6I module)

Local letters `0=I, 1=X, 2=Y, 3=Z` with the frozen `local_mul` /
`local_symp` / `local_wt` algebra (`r6i._MUL/_SYMP/_LW`). An instance is a
pair of target triples (block A, block B) over n qubits; block A's
target-to-branch assignment is frozen to source order, block B carries a
relative permutation `pi in S_3`; each block has a central branch
`c_j in {0,1,2}`. A feasible configuration is

- generators `Rj0, Rj1` per block with `symp(Rj0, Rj1) = 1` and the
  dependent third frame letter `Rj2 = Rj0 * Rj1` (phase-free binary Pauli
  product), so the three `Rjk` are pairwise anticommuting and rank-2;
- one shared Tag pair `(S0, S1)` with branch labels
  `c_jk = 2<S0,Rjk> + <S1,Rjk>` equal across blocks branch-by-branch and
  `{c_j0, c_j1}` nonzero and distinct (then `c_j2 = c_j0 xor c_j1` is
  automatically the third nonzero label);

exactly the acceptance predicate of the frozen 10-bit DP
(`r6i._DELTA` bits 0-9, `r6i.ACCEPTING`, exactly 6 accepting states). Its
cost is the frozen R6I objective (NO Restore factor rule):

`C = C_Uanti(A) + C_Uanti(B) + 2(w(S0)+w(S1)) + sum_k w(TAk) + sum_k w(TBk)`,

with `Tjk = Pj,k' * Rjk` (`k'` the branch's assigned target index),
`C_Uanti(j) = sum_k m_jk w(Rjk) - 10`, multipliers `(m_j0,m_j1,m_j2)` equal
to `(4,4,4)` with the central entry reduced to `2`
(`p10.uanti_support`; the two `-10`s are the frozen constant-20 subtraction).

## Structural differences from the R6M lane (handled explicitly)

(a) **Dependent third letter.** Zeroing a letter of `Rj0` at qubit q also
changes `Rj2` at q (from `r0*r1` to `r1`), moving cost in BOTH affected
branch Restores (branch 0 and branch 2) AND in the branch-2 frame
multiplier term whenever `r1_q in {I, r0_q}`. The per-qubit exchange
inequality must therefore be proved over the full dependent-triple case
analysis, not per-letter as in R6M.

(b) **2-bit Tag.** The Tag syndrome of a generator is a 2-bit label, so the
repair-free class of a support qubit is
`class(q) = (alpha, beta0, beta1) in F_2^3` (anticommutation parity,
S0-syndrome parity, S1-syndrome parity). The F_2^2 pigeonhole of R6S
("odd-alpha multisets of size >= 3 contain a proper zero-sum subset of size
<= 2") is FALSE in F_2^3 (the Davenport constant of (Z/2)^3 is 4, and
zero-sum-free sets of size 3 with odd alpha-sum exist); the pigeonhole must
be re-derived, and it yields a larger support bound.

## Column taxonomy

Fix a feasible configuration and a block j. For qubit q let
`r0_q, r1_q` be the local letters of `Rj0, Rj1`. Define

- the **coincidence set** `C_j = { q : r0_q = r1_q != I }` (there `r2_q = I`
  and the letters commute locally);
- the **non-coincidence support** of generator g:
  `N_jg = supp(Rjg) \ C_j` (letters `r_g,q != I` with `r_other,q != r_g,q`,
  including `r_other,q = I`).

So `supp(Rjg) = N_jg  (disjoint union)  C_j` and
`supp(Rj2) subset N_j0 union N_j1`.

**Classes.**
- For `q in N_jg`:
  `classN(q) = (alpha, beta0, beta1) in F_2^3`,
  `alpha = local_symp(r_g,q, r_other,q)`,
  `beta_i = local_symp(s_i,q, r_g,q)` (`s_i,q` the letters of `S_i`).
  Code: `4*alpha + 2*beta0 + beta1` in 0..7.
- For `q in C_j` with common letter `c_q`:
  `classC(q) = (beta0, beta1) in F_2^2`, `beta_i = local_symp(s_i,q, c_q)`.
  Code: `2*beta0 + beta1` in 0..3.

**Support-parity identity.** Coincidence columns contribute
`local_symp(c,c) = 0` and non-support columns contribute 0, so
`sum_{q in N_jg} alpha(q) = symp(Rjg, Rj,other) = 1`: the N-class multiset
of EVERY generator has ODD alpha-sum (hence `N_jg` is nonempty and any
zero-sum subset of it is automatically PROPER).

## Frozen move set (the exchange)

Only two move types are used; each changes generator letters only (Tag,
targets, permutation, centrals, the other block: untouched), so Tag repair
is identically ZERO.

**SOLO(j, g, Q)**, `Q` a nonempty subset of `N_jg` with zero F_2^3 class
sum: zero `Rjg`'s letters on Q. Preserved: `symp(Rjg, other)` (even
alpha-sum; stays 1, so `Rjg != 0`), both Tag syndromes of `Rjg` (even
beta-sums), everything else untouched. Exact per-qubit cost change at q
(`f = r_g,q`, `o = r_other,q`, `p_g, p_2` the branch-g and branch-2
assigned target letters, `m_g, m_2` the multipliers):

`dC_q = [lw(p_g) - lw(p_g*f)] + [lw(p_2*o) - lw(p_2*f*o)]
        - m_g + m_2*(lw(o) - lw(f*o))`.

Predicted (Lemma E-solo): `dC_q <= 0` on the whole domain; if `o = I` then
`dC_q <= 2 - m_g - m_2 <= -4`; if `o not in {I, f}` then
`dC_q <= 2 - m_g`, with ties (`dC_q = 0`) exactly at
`m_g = 2 (central_j = g), p_g = f, p_2 = f*o`.

**PAIR(j, Q)**, `Q` a nonempty subset of `C_j` with zero F_2^2 class sum:
zero BOTH generators' letters on Q. Both generators' Tag syndromes move by
the same even beta-sums; `symp(Rj0,Rj1)` is unchanged (coincidence columns
contribute 0 before and after); `r2` stays I on Q so branch-2 Restore and
frame terms are untouched; both generators keep their nonempty `N_jg`, so
they stay nonzero. Exact per-qubit change (`c = r0_q = r1_q`):

`dC_q = [lw(p_0) - lw(p_0*c)] + [lw(p_1) - lw(p_1*c)] - m_0 - m_1`.

Predicted (Lemma E-pair): `dC_q <= 2 - (m_0+m_1) <= -4` always (strict).

**Why coincidence columns cannot be solo-zeroed (the boundary).** Solo
zeroing at `q in C_j` resurrects `r2_q` (I -> c), with exact change
`dC_q = [lw(p_g) - lw(p_g*c)] + [lw(p_2*c) - lw(p_2)] + m_2 - m_g`,
maximal `+4` at `p_g = c, p_2 = I, m_g = 2, m_2 = 4`. This positive case is
the QG-1 analogue of the R6M weight-2 boundary: it is why the move set
splits by column taxonomy, and it is documented by an exhaustive sweep (not
used by the proof).

## Lemma B (re-derived pigeonhole; written proofs, machine-corroborated)

**Lemma B-N (F_2^3, odd alpha-sum).** Every multiset of `w >= 4` classes in
F_2^3 with odd alpha-sum contains a nonempty zero-sum subset (automatically
proper, since the full multiset sums to an alpha=1 vector != 0). Proof: if
no element is 0 and no two are equal, the elements are distinct nonzero
vectors; any 4 distinct vectors in F_2^3 are linearly dependent, and a
minimal dependency is a nonempty zero-sum subset. QED. The zero-sum-free
multisets (no nonempty zero-sum subset) are exactly the linearly
independent sets of distinct nonzero vectors, size <= 3; with the odd-alpha
constraint the EXCEPTIONAL PATTERNS are predicted to be exactly:
- `w = 1`: the 4 singletons with alpha = 1;
- `w = 2`: the 12 distinct nonzero pairs with exactly one alpha = 1;
- `w = 3`: the 16 distinct nonzero triples with odd alpha-count (1 or 3;
  independence is automatic: an odd-alpha triple sums to an alpha=1 vector
  != 0);
- `w >= 4`: none. Total 32 patterns.

**Lemma B-C (F_2^2, no parity constraint).** Every multiset of `w >= 3`
classes in F_2^2 contains a nonempty zero-sum subset (Davenport constant of
(Z/2)^2 is 3; the only distinct-nonzero triple {01,10,11} sums to zero).
Exceptional (zero-sum-free) patterns predicted: `w = 1`: the 3 nonzero
singletons; `w = 2`: the 3 distinct nonzero pairs; `w >= 3`: none. Total 6.

## Lemma E (exhaustive local inequalities — the machine-checked step)

All sweeps over the frozen local algebra; `s0, s1` letters do not enter the
inequalities but are swept as declared because they define the class
tabulations reported alongside.

- **E-solo**: `g in {0,1}` (zeroed generator; fixes which multiplier is
  refunded), `f in {X,Y,Z}`, `o in {I,X,Y,Z} \ {f}` (3 values; the
  coincidence case is excluded from the move set), `central_j in {0,1,2}`,
  `(p_0,p_1,p_2) in {I,X,Y,Z}^3`, `(s_0,s_1) in {I,X,Y,Z}^2`:
  `2*3*3*3*64*16 = 55,296` cases. Gate: `dC_q <= 0` on all; the tie set
  must match the prediction above.
- **E-pair**: `c in {X,Y,Z}`, `central_j in {0,1,2}`, `p` (64), `s` (16):
  `3*3*64*16 = 9,216` cases. Gate: `dC_q <= -4` on all (strict).
- **E-boundary** (documentation sweep, NOT part of the proof): solo zeroing
  at a coincidence column, `g` (2), `c` (3), `central` (3), `p` (64),
  `s` (16): `18,432` cases. Gate: positive cases exist and the maximum net
  is exactly `+4`, at the predicted letters.

Lemma B machine corroboration: all class MULTISETS
(combinations-with-replacement) for `w = 1..8` — F_2^3 side filtered to odd
alpha-sum (12,869 multisets before the filter), F_2^2 side unfiltered (494
multisets) — each checked for a nonempty zero-sum subset by exhaustive
subset enumeration; plus full TUPLE corroboration for `w <= 5` (8^w and 4^w
tuples). Gates: zero failures at `w >= 4` (B-N) and `w >= 3` (B-C);
the failing patterns at small w must equal the predicted 4/12/16 and 3/3
sets exactly, and every failing multiset must be a distinct-nonzero
linearly independent set.

## Induction and theorem statement

Fix (n, targets, relative B permutation, centrals) and let `Sigma`
minimize `(C, w(RA0)+w(RA1)+w(RB0)+w(RB1))` lexicographically over the
finitely many feasible configurations. If any `N_jg` admits a nonempty
zero-sum subset, SOLO applies: `C` does not increase (Lemma E-solo summed
over Q) and total generator support drops by `|Q| >= 1` — contradiction.
If any `C_j` admits one, PAIR applies: `C` strictly drops — contradiction.
Hence in `Sigma` every `N_jg` and every `C_j` class multiset is
zero-sum-free, so by Lemma B-N/B-C:

`|N_jg| <= 3` for all four generators and `|C_j| <= 2` per block, giving

> **THEOREM (target).** For every n and every instance of the frozen R6I
> grammar (every target pair, relative permutation and central pair), the
> exact optimum is attained by a configuration with
> `w(Rjg) = |N_jg| + |C_j| <= 3 + 2 = 5` for all four generators
> (**B = 5**), `w(Rj2) <= |N_j0| + |N_j1| <= 6`, and per-block joint
> support `|supp(Rj0) u supp(Rj1)| <= 8`. Equivalently the
> generator-support-capped grammar `cap-5` satisfies
> `C_cap5 == C_unrestricted` for every n. The irreducible support patterns
> are exactly: N-class multisets among the 32 odd-alpha zero-sum-free
> patterns and C-class multisets among the 6 zero-sum-free patterns (or
> empty C).

Minimizing over permutations and centrals preserves attainment. Tightness
of B = 5 (realizability of a `3+2` irreducible optimum at some n) is NOT
claimed; the panel below probes the small-n boundary empirically.

## Verification plan (all prespecified)

1. **Bindings**: independent MUL/SYMP/LW tables rebuilt from the frozen
   `h` algebra must equal `r6i._MUL/_SYMP/_LW` exactly;
   `len(r6i.ACCEPTING) == 6`; the uanti identity
   `p10.uanti_support(rs, c) == sum_k m_k w(Rk) - 10` verified exhaustively
   over all 120 ordered symplectic-1 pairs at n=2 times 3 centrals; ordered
   symplectic-1 pair count at n=3 must equal 2016.
2. **Lemma E**: the three sweeps above (numpy, exhaustive); every violating
   case verbatim (capped at 20 rows); tie characterization and per-class
   worst-net tabulation reported.
3. **Lemma B**: enumerations above; per-w checked/failure counts; failing
   patterns verbatim; predicted-set equality; characterization check.
4. **Capped-brute machinery + hostile binding**: an independent capped
   optimizer (generator pairs restricted to `w <= cap`, exact Tag
   syndrome-class scan over all Pauli keys, exact Uanti/Restore terms, B
   permutation sweep) is validated by: `cap-1 at n=1` and `cap-2 at n=2`
   (caps vacuous there) must equal BOTH the committed `r6i.brute_shared_cost`
   and the committed `r6i.shared_tag_exact` DP on all 7 committed
   `r6i.HOSTILE_PANELS` instances.
5. **Stress panel** (runs regardless of the analytic outcome):
   `numpy.random.default_rng(20260823)`; 44 instances at n=3 (>= 40); per
   instance six iid uniform nonzero targets (A = first three, B = last
   three). Per instance: `C_dp` and witness from the committed
   `r6i.shared_tag_exact` (unrestricted optimum; `r6i._LOCAL_CACHE` is
   cleared per instance — runtime state only, no repository file is
   modified); `C_brute` (my cap-3 = unrestricted-at-n=3 brute; gate
   `C_dp == C_brute` on every instance — a NEW n=3 DP-vs-brute hostile
   surface beyond the committed n<=2 panels); `C_cap2`, `C_cap1`
   (containment gate `C_dp <= C_cap2 <= C_cap1`); witness cost rebound
   through my independent cost function (must equal `C_shared`); witness
   class multisets and max generator support recorded. `C_cap2` equality is
   REPORTED, not gated: `C_cap2 > C_dp` instances are realized
   support-boundary regime data (the analogue of the R6O weight-2 trade),
   and for each such instance a descent from the DP witness must terminate
   with max generator support >= 3 (else integrity failure of the capped
   brute), with its irreducible exceptional patterns recorded verbatim.
6. **Exchange-descent machine verification**: descents run the frozen move
   set (scan order: block A then B; within a block SOLO g=0, SOLO g=1,
   PAIR; first available move; frozen subset rule: smallest nonempty
   zero-sum subset in (size, lexicographic-on-positions) order). Per step
   assert: recomputed-from-scratch feasibility and label equality; observed
   `dC` EQUALS the predicted per-qubit decomposition exactly (catches
   unmodeled coupling); `dC <= 0` (`< 0` for PAIR); support drop equals
   `|Q|` (SOLO) / `2|Q|` (PAIR). On termination assert: all four N-class
   multisets and both C-class multisets are zero-sum-free AND match the
   Lemma-B characterization (distinct, nonzero, independent; `|N| <= 3`,
   `|C| <= 2`), hence all generator supports `<= min(n, 5)`. Plan: 2
   descents per panel instance (88, seeded spread configurations on the
   panel targets: RA0 conditioned `w >= 3`, odd-indexed descents
   coincidence-seeded by copying RA0's letters onto RA1 on a seeded
   nonempty subset of supp(RA0)); plus fresh-target groups: 16 at n=4, 10
   at n=5, 6 at n=6 (last 3 of the n=6 group conditioned `w(RA0) = 6`, so
   the nontrivial `w > 5` regime of the theorem is exercised directly).
   Tag drawn by enumerating the full feasible-Tag class table (numpy
   popcount at n>=5); generators resampled (bounded 500 attempts, counts
   reported) if no feasible Tag exists. Centrals and B permutation seeded.
   At n=3 additionally assert the containment triangle
   `C_dp <= final descent cost`.
7. **No new subject data**: no chemistry loader invoked; the protected
   stretched-N2 path never read; `r6i.main()` / `r6i.run_subject()` never
   called.

## Prespecified gates

- G1 `lemma_e_solo_zero_violations`: 0 violations over 55,296 cases; ties
  match the predicted characterization.
- G2 `lemma_e_pair_strict`: 0 cases with `dC_q > -4` over 9,216 cases.
- G3 `boundary_documented`: E-boundary max net == +4 with positive cases
  present (documentation gate).
- G4 `lemma_b_n_w4_to_w8_zero_failures` and
  `lemma_b_n_exceptional_exact`: failing patterns are exactly the
  predicted 4/12/16 with the independence characterization.
- G5 `lemma_b_c_w3_to_w8_zero_failures` and
  `lemma_b_c_exceptional_exact`: exactly the predicted 3/3.
- G6 `descents_all_verified`: every descent passes every per-step and
  termination assertion; containment triangles hold at n=3.
- G7 `panel_dp_equals_brute` and `panel_containment`: `C_dp == C_brute`
  and `C_dp <= C_cap2 <= C_cap1` on all 44 instances; witness rebinding
  exact; every cap-2 gap instance's witness descent ends with max
  generator support >= 3.
- G8 `bindings_exact`: item 1 plus the capped-brute hostile binding
  (item 4).
- G9 `no_new_subject_data`.

## Honest outcome space (frozen)

- **THEOREM_MACHINE_CHECKED** (G1-G9 all pass): authority
  `ORIONQ_QG1_RANK2_ALL_N_THEOREM_MACHINE_CHECKED__GENERATOR_SUPPORT5_SUFFICES_ALL_N__CAP5_EQUALS_UNRESTRICTED__NOT_R6`.
  The induction is a complete proof for every n of the B = 5 generator
  bound on the frozen R6I grammar, with the exceptional patterns
  characterized (32 N-patterns, 6 C-patterns); the only computational steps
  are Lemma E (G1/G2) and Lemma B (G4/G5). The cap-2 equality/gap counts
  are reported as the empirical small-n boundary either way.
- **GAP_FOUND** (any G1/G2 violation, or any Lemma B failure at `w >= 4`
  (N) / `w >= 3` (C)): the exchange fails at a stated case, reported
  verbatim; the run then tests empirically whether the gap is realizable as
  a DP optimum (panel rows with `C_dp < C_cap2` whose witness descents
  fail, plus every failed descent verbatim) — a realized irreparable case
  would be a new regime discovery for the QG programme. Authority
  `ORIONQ_QG1_RANK2_ALL_N_GAP_FOUND__EXCHANGE_CASE_FAILS__NOT_R6`.
- **PARTIAL** (lemmas pass but a descent, panel, or binding-corroboration
  assertion fails): primarily indicts the implementation or an unmodeled
  coupling; the receipt states exactly which cases close and which remain.
  Authority
  `ORIONQ_QG1_RANK2_ALL_N_PARTIAL__STATED_CASES_ONLY__NOT_R6`.
- **Integrity failure** (binding mismatch, `C_dp > C_cap2` containment
  violation, cap-2 gap with a support-<=2 witness descent, hostile-binding
  inequality): abort nonzero with the failing assertion; no authority
  string is emitted.

No gate may be weakened after the outcome is known. The authority string
always contains `NOT_R6` and grants nothing: no scientific, novelty,
promotion, donor, or R6 authority flows from this lane; it is a
mathematical claim about the stated grammar only.

## Claim boundary (must be restated in the receipt)

The theorem covers exactly: the frozen R6I two-block rank-2 dependent
TARE-3 shared-2-bit-Tag grammar under the frozen R6I objective
(`(4,4,4)`/central-2 multiplicities, Tag paid twice, per-branch Restore
supports with NO factor rule), for every n, every target-triple pair, every
relative B permutation and every central pair: generator supports <= 5
suffice. It does NOT cover: the R6K restore-factor variant, the R6M/R6S
three-block grammar (already closed separately), coefficient-weighted or
non-support objectives, larger Tag ranks, tightness of B = 5, or any claim
that support-2 suffices (the panel measures that boundary empirically at
n=3 only). The stress panel and descents are corroboration, not the proof.

## Receipt

Single stdout line `ORIONQ_QG1_RANK2_ALL_N=<canonical sorted json>` plus
pretty `QG1_RANK2_ALL_N_RESULTS.json` (research/extensions/orion-qg/),
containing: all binding results, the three Lemma E domains with case
counts, violation/tie counts and verbatim rows, both Lemma B enumerations
with per-w counts and the exceptional-pattern sets, the descent statistics
and per-descent rows, the 44-row panel with `C_dp/C_brute/C_cap2/C_cap1`,
gap-instance regime analyses, all gates, the authority string (containing
`NOT_R6`), and the claim-boundary text. Determinism: the stdout receipt
and the RESULTS body exclude wall-clock values; `runtime_seconds` is
appended to the RESULTS file as the single non-deterministic field.
Double run must produce byte-identical stdout receipts. Runtime budget:
under 25 minutes per run with the session scratchpad venv python. Exit 0
on THEOREM/GAP/PARTIAL; nonzero only on integrity failure.

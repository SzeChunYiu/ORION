# MAX-R6S all-n composition protocol (support >= 3 exchange theorem with Tag repair)

Date: 2026-08-21
Parent programme: #679 / PR #689
Predecessors:
- MAX_R6N_SUPPORT_DOMINANCE_PROTOCOL.md (local exchange inequality verified on
  688,041,472 configurations; DECLARED GAP: Tag-repair coupling after frame
  truncation is not bounded by the local inequalities).
- MAX_R6O_ENLARGED_TAG_DONOR_PROTOCOL.md (REFUTED D+: the weight-2 trade —
  one weight-2 frame Pauli at the central multiplier buys Tag compression and
  Restore-factor alignment; 486 + 73 realized counterexamples).
- MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_PROTOCOL.md (VERIFIED: D++, frames of
  global support <= 2, equals the unrestricted exact DP on every verified
  finite domain; explicitly NOT a theorem for all n — that open object is
  named by the R6P receipt and is the subject of this protocol).

Status: FROZEN BEFORE R6S OUTCOME. The exchange construction, the case
domains, the gates, the panel seed/sizes and the outcome space below were
written before any lemma enumeration, descent, or panel comparison was run.
The only computations performed before freezing were budget constants: the
ordered anticommuting support-<=2 pair count at n=4 (1968) and a rough
single-instance timing of the frozen n=4 DP reader and D++ enumerator
(~1.5 s), used solely to fix the panel sizes without subsampling.

Authority ceiling: explanatory family-closure theorem attempt over the frozen
R6M grammar; not R6, no novelty credit, no donor credit, no new subject data.
The protected stretched-N2 discriminator is never read; this run reads no
chemistry data at all.

## Open object

Convert R6P's bounded machine evidence into a theorem: in the frozen R6M
grammar, frame Paulis of global support >= 3 never strictly pay — for every
qubit count n, every target six-tuple, every matching, every relative
permutation pair and every central-bit triple, the unrestricted exact DP
optimum equals the D++ (all six frame Paulis of global support <= 2) optimum:

`C_DP == C_D++  for every n and every target configuration.`

## Frozen grammar recap (bound to the frozen R6M module)

Local letters `0=I, 1=X, 2=Y, 3=Z` with the frozen `local_mul` / `local_symp`
/ `local_wt` algebra. For a fixed instance (six targets grouped by a matching
into ordered blocks A, B, C), fixed relative permutations `pi_j` and central
bits `c_j`, a feasible configuration is

- six nonzero frame Paulis `R_jk` with `symp(R_j0, R_j1) = 1` per block
  (nonzeroness is implied by the anticommutation bit),
- a Tag `S` with common labels `symp(S, R_j0) = l0`, `symp(S, R_j1) = l1`
  for all `j`, and `l0 != l1` (which forces `S != 0`),

exactly the acceptance predicate of the frozen 9-bit XOR DP
(`max_r6m_exact_three_tare2_shared_factor_dp`, bits b0..b8). Its cost is

`C = sum_j [4 w(R_j,nc) + 2 w(R_j,c)] - 18 + 2 w(S)
     + sum_{k in {0,1}} F3support(T_Ak, T_Bk, T_Ck)`,

`T_jk = P_{j, pi_j(k)} * R_jk`, `F3support` = per-qubit sum of
`F3(a,b,c) = 1 if a=b=c!=I else w(a)+w(b)+w(c)` (the frozen donor-owned
all-three Restore common-factor rule). There are NO constraints between the
frames of different blocks; the Tag couples blocks only through the six
symplectic labels. `C_DP <= C_D++` holds by containment; the theorem is the
reverse inequality via an optimum witness with all supports <= 2.

## Frozen exchange construction (the entire proof, stated before verification)

**Classes.** Fix a feasible configuration and a frame Pauli `R := R_jk` with
partner `R_p := R_j,1-k` and Tag `S`. For each qubit `q in supp(R)` define

`class(q) = (alpha(q), beta(q)) in F_2^2`,
`alpha(q) = local_symp(f_q, fp_q)`, `beta(q) = local_symp(sigma_q, f_q)`,

where `f_q, fp_q, sigma_q` are the local letters of `R`, `R_p`, `S` at `q`.

**Support-parity identity.** Qubits outside `supp(R)` contribute
`local_symp(I, .) = 0`, so `sum_{q in supp(R)} alpha(q) = symp(R, R_p) = 1`:
the class multiset over the support always has ODD alpha-sum.

**Lemma B (zero-sum subset; written pigeonhole proof, machine-corroborated
for w <= 8).** Every multiset of `w >= 3` classes in `F_2^2` with odd
alpha-sum contains either a class-`(0,0)` element or two elements of equal
class; hence a nonempty subset `Q` with `|Q| <= 2` and
`sum_Q alpha = sum_Q beta = 0 (mod 2)`, and `|Q| <= 2 < 3 <= w` makes `Q` a
PROPER subset of the support. Proof: if no `(0,0)` class occurs and no class
repeats, all classes are distinct members of `{(0,1),(1,0),(1,1)}`, so
`w <= 3`; `w = 3` forces the multiset `{(0,1),(1,0),(1,1)}`, whose alpha-sum
is `0 + 1 + 1 = 0`, even — contradicting the odd alpha-sum. QED. The proof is
w-independent; the machine check enumerates all `4^w` class tuples with odd
alpha-sum for `w = 3..8` as corroboration.

**The exchange.** Given `w(R) >= 3`, choose `Q` by the frozen deterministic
rule: (i) the lowest qubit `q in supp(R)` with `class(q) = (0,0)`, `Q = {q}`;
else (ii) the lexicographically lowest pair `q1 < q2` in `supp(R)` with
`class(q1) = class(q2)`, `Q = {q1, q2}` (Lemma B guarantees one of the two
exists). The modified configuration zeroes `R`'s letters on `Q` and changes
NOTHING else (partner, other blocks, `S`, labels, centrals, permutations,
matching all identical).

**Feasibility is preserved with ZERO Tag repair.**
- `R' != 0`: `Q` is a proper subset of the support.
- `symp(R', R_p) = symp(R, R_p) + sum_Q alpha = 1 + 0 = 1`.
- `symp(S, R') = symp(S, R) + sum_Q beta = l_k + 0 = l_k`.
- All other acceptance bits involve untouched Paulis.

The even-beta-sum choice of `Q` is what removes R6N's declared Tag-coupling
gap: the repaired-Tag cost term is identically zero because `S` never needs
repair at support >= 3. (The a-priori repair bounds sketched in the R6P-era
discussion — `Delta w(S) <= 1` per syndrome flip at cost 2 — are NOT relied
upon; the construction avoids the flip altogether, which is stronger.)

**Cost change.** Only two objective terms move: the raw frame term drops by
`m` per qubit of `Q`, where `m in {2,4}` is `R`'s multiplier (`2` iff
`c_j = k`), and the branch-`k` F3 term at each `q in Q` changes because the
zeroed slot's letter moves from `p_q * f_q` (old) to `p_q` (new), `p_q` the
branch-target letter of `R`'s slot at `q`; the other two slots' letters
`u_q, v_q` are unchanged. Tag term, other branch, other qubits: unchanged.
Hence, exactly,

`Delta C = sum_{q in Q} [ F3(slot=p_q; u_q, v_q) - F3(slot=p_q*f_q; u_q, v_q) - m ]`.

**Lemma E (single-zeroing local exchange inequality — the ONLY exhaustively
machine-checked computational step of the proof).** For every zeroed letter
`f in {X,Y,Z}`, partner letter `fp in {I,X,Y,Z}`, tag letter
`sigma in {I,X,Y,Z}`, target letter `p in {I,X,Y,Z}`, other-slot letters
`u, v in {I,X,Y,Z}`, multiplier `m in {2,4}` and zeroed-slot position in
{A,B,C} (F3 is symmetric; the position is swept anyway):

`F3(new) - F3(old) - m <= 0`,

with `new`/`old` the triples above. Exhaustive domain:
`3 * 4 * 4 * 4 * 4 * 4 * 2 * 3 = 18,432` cases (`fp` and `sigma` do not
enter the inequality; they are swept as declared because they define the
class tabulation reported alongside). Expected structure: max
`F3(new) - F3(old) = 2` (breaking an all-three match), so ties
(`Delta = 0`) can occur only at the central multiplier `m = 2`; every case
verdict and the tie characterization are reported.

**Induction (theorem from the two lemmas).** Fix (instance, matching, perms,
centrals) and let `Sigma` minimize `(C, sum_jk w(R_jk))` lexicographically
over the finitely many feasible configurations. If some `w(R_jk) >= 3`, the
exchange produces a feasible `Sigma'` with `C(Sigma') <= C(Sigma)` (Lemma E,
summed over `Q`) and total support smaller by `|Q| >= 1` — contradicting
minimality. Hence the lexicographic minimum has all six frame supports <= 2,
so the unrestricted optimum is attained inside the support-<=2 sub-grammar
for EVERY config; minimizing over perms/centrals/matchings preserves this.
By the frozen R6P Tag-relaxation identity, the D++ optimum equals the
minimum over support-<=2 grammar configurations (for fixed frames and labels
the grammar's Tag sweep includes the minimum-weight feasible Tag). Therefore
`C_DP = C_D++` for every n and every target configuration. QED.

## Why support 2 differs from support 3 (the R6O trade boundary, exactly)

At `w = 2` the class multiset `{(alpha1,beta1), (alpha2,beta2)}` has odd
alpha-sum, so exactly one qubit has `alpha = 0`; a repair-free exchange needs
a nonempty PROPER zero-sum subset, i.e. a singleton of class `(0,0)`. It
exists iff the alpha-0 qubit has `beta = 0`. The failing patterns are exactly
the four odd-alpha tuples whose alpha-0 qubit has `beta = 1`
(`{(1,0),(0,1)}`, `{(1,1),(0,1)}` in both orders): the qubit where the pair
commutes locally anticommutes with the Tag, so zeroing it MUST flip the Tag
syndrome — and R6O exhibited 559 realized DP optima where exactly this
weight-2 letter (placed on the central multiplier, m = 2) purchases Tag
compression plus factor alignment worth more than its refund. At `w >= 3`
Lemma B makes the failing pattern unrealizable — this, and nothing about the
per-unit price of support (which is the same at w = 2 and w = 3), is the
whole difference. Machine check: enumerate all `w = 2` odd-alpha class
tuples and confirm the failing set is exactly the predicted four.

## Verification plan (all prespecified)

1. **Binding**: independent LW/LM/SY/F3 tables must equal the frozen
   `r6m._LW/_LM/_SY/_F3` arrays exactly; `_factor_support_fast` must equal
   the per-qubit F3 sum on every descent cost evaluation.
2. **Lemma E**: exhaustive 18,432-case sweep (numpy); zero violations
   expected; report max `F3(new)-F3(old)`, the tie count and the class
   tabulation; any violating case verbatim (letters, multiplier, slot).
3. **Lemma B**: `w = 2..8`, all `4^w` class tuples filtered to odd
   alpha-sum (`sum_w 4^w/2 = 43,688` tuples checked); for `w >= 3` zero
   failures expected (singleton-(0,0) or equal pair, `|Q| <= 2`); for
   `w = 2` the failing set must equal the four predicted patterns.
4. **Exchange-descent machine verification**: for every stress-panel
   instance below, 3 seeded spread-frame feasible configurations (210
   descents): frames uniform nonzero anticommuting per block with block A's
   first frame forced to support >= 3, Tag drawn by the seeded rng uniformly
   from the exhaustively enumerated feasible-Tag set (resample frames if the
   set is empty; attempts bounded and reported), centrals random,
   permutations fixed at 0. Descend by the frozen exchange rule until all
   six supports <= 2. Per step, assert: recomputed-from-scratch feasibility;
   `Delta C <= 0`; support drop == `|Q|`; and `Delta C` EQUALS the predicted
   local decomposition `sum_Q [Delta F3_q - m]` exactly (this catches any
   unmodeled coupling term). Assert the containment triangle
   `C_DP <= C_D++ <= final descent cost` on every instance. Report step and
   tie statistics.
5. **Stress panel** (runs regardless of the analytic outcome):
   `numpy.random.default_rng(20260822)`; 40 instances at n=3 then 30 at n=4
   (70 >= 60; pre-freeze timing shows ~1.5 s per n=4 instance, so the full
   panel runs without subsampling — if the run were ever to exceed budget
   the panel would be truncated honestly with the realized count reported);
   six iid uniform nonzero Paulis per instance, matching
   `((0,1),(2,3),(4,5))`. `C_DP` from the frozen R6M machinery via the
   frozen R6P reader `dp_cost_frozen_configs` (full 32-config
   `_dp_config_cost` sweep); `C_D++` from the frozen R6P enumerator
   `dxx_search`. n=4 requires the runtime injection
   `r6p.EXPECTED_PAIR_COUNTS[4] = 1968` (the ordered anticommuting
   support-<=2 pair count at n=4, recomputed independently in-run before
   injection and asserted; 6/120/666/1968 at n=1/2/3/4); no repository file
   is modified. D++ witness re-verification (`verify_dxx_witness`, including
   the exhaustive Tag-minimality brute over all `4^n` Paulis) on every 5th
   instance; weight-1-restricted binding
   `dxx_search(max_weight=1) == r6o.dplus_pairs` on every 7th instance.
6. **No new subject data**: no chemistry loader is invoked; the protected
   stretched-N2 path is never read.

## Prespecified gates

- G1 `lemma_e_zero_violations`: 0 violations over the 18,432-case domain.
- G2 `lemma_b_w3_to_w8_zero_failures`: every odd-alpha class tuple for
  `w = 3..8` admits a zero-sum subset of size <= 2.
- G3 `lemma_b_w2_boundary_exact`: the `w = 2` failing set equals the four
  predicted patterns exactly.
- G4 `exchange_descents_all_verified`: all 210 descents pass every per-step
  assertion and end with all supports <= 2; all containment triangles hold.
- G5 `stress_panel_equality`: `C_DP == C_D++` on all 70 instances.
- G6 `bindings_exact`: table bindings, pair-count assertion (1968 at n=4),
  weight-1-restricted binding rows, and witness re-verification all pass.
- G7 `no_new_subject_data`: no chemistry read; stretched-N2 unread.

## Honest outcome space

- **THEOREM_MACHINE_CHECKED** (G1-G7 all pass): authority
  `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N__NOT_R6`.
  The induction above is a complete proof for every n and every target
  configuration of the frozen R6M grammar, whose only computational steps
  are Lemma E (exhaustive, G1) and Lemma B (written pigeonhole, G2/G3
  corroborated). R6P's bounded evidence is thereby converted into a theorem
  on the stated grammar.
- **GAP_FOUND** (any Lemma E violation, or any Lemma B failure at
  `w >= 3`): the exchange argument fails at a stated case; every failing
  case is reported verbatim. The run then tests empirically whether the gap
  is realizable as an actual DP optimum: the stress panel plus a targeted
  re-examination of any instance with `C_DP < C_D++` (which would be a
  THIRD regime beyond R6N Tag-anchor coupling and the R6O weight-2 trade,
  reported prominently). Authority
  `MAX_R6S_ALL_N_COMPOSITION_GAP_FOUND__EXCHANGE_CASE_FAILS__NOT_R6`.
- **PARTIAL** (lemmas pass but a descent assertion or a stress-panel
  equality fails): this configuration contradicts the written proof and
  therefore primarily indicts the implementation or an unmodeled coupling;
  every failing case is reported verbatim and the receipt states exactly
  which cases close and which remain. Authority
  `MAX_R6S_ALL_N_COMPOSITION_PARTIAL__STATED_CASES_ONLY__NOT_R6`.
- **Integrity failure** (binding mismatch, sandwich violation
  `C_DP > C_D++`, blob/receipt inconsistency): abort nonzero with the
  failing assertion; no authority string is emitted.

## Claim boundary (must be restated in the receipt)

The theorem covers exactly: the frozen R6L/R6M three-block TARE-M2
shared-one-bit-Tag grammar with the donor-owned all-three Restore
common-factor rule under the frozen raw support-count objective with
multipliers 4 (non-central) / 2 (central), for every qubit count n, every
target six-tuple, every matching, every relative permutation and every
central choice. It does NOT cover: the R6I rank-2 dependent-triple grammar
(zeroing one letter moves the dependent third letter between multiplier
classes; no claim is made), coefficient-weighted or non-support objectives,
rotation-count trade-offs beyond the frozen fixed counts, larger Tag ranks,
or grammars outside the frozen family. The stress panel is corroboration,
not the proof. No novelty credit, no donor credit, not R6; the theorem's
authority is mathematical over the stated grammar only.

## Receipt

Single stdout line `ORIONQ_MAX_R6S_ALL_N_COMPOSITION=<canonical sorted json>`
plus pretty `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`, containing: both lemma
domains with case counts, violation/failure counts and verbatim failures,
the tie characterization and class tabulation, the w=2 boundary set, the
descent statistics (steps, ties, per-step assertion counts), the 70-row
stress panel with `C_DP`/`C_D++` per row, all gates, the authority string
(containing `NOT_R6`), and the claim-boundary text. Determinism: the stdout
receipt line and the RESULTS body exclude wall-clock values;
`runtime_seconds` is appended to the RESULTS file as the single
non-deterministic field. Exit 0 on THEOREM/GAP/PARTIAL outcomes; nonzero
only on integrity failure.

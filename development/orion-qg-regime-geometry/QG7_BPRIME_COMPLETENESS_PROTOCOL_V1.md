# QG-7 B' Completeness Protocol V1 (FROZEN BEFORE ANY OUTCOME)

Lane: ORION-QG QG-7 (issue #757) — all-n enlarged-borrow completeness:
prove B' exact for all n, or discover a fourth support-two TARE regime.

Frozen at base revision `c796944d82c19cdceef0302b2a0cb6de7fc41b80` (branch
`claude/orion-harness-verification-b17qdj`, synced with main) BEFORE the
hostile search, the normalization checks, or any per-instance family value
under this protocol was computed. The only pre-freeze computation was a
machinery timing probe (per-instance wall times of the committed referees on
four throwaway seeded random instances per n outside every frozen enumeration
below, plus one rerun of the committed R6S lemma verifiers to time them);
no H-shape instance was generated and no family-minimum comparison was
recorded before this freeze. Committed receipts
(`QG5B_EXACT_FORECASTER_RESULTS.json`, `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`)
were read for binding constants; they are prior committed outcomes, not
outcomes of this lane.

## Question (charter, frozen verbatim intent)

Does every support-two D++ optimum, for every n and target configuration in
the frozen unit-cost R6M grammar, normalize without cost increase into D+ or
the enlarged borrow B'? Equivalently, with the committed exact evaluators:

    C_D++(t) == min( C_D+(t), f_B'(t) )   for every instance t, every n?

A single exact witness with `C_D++ < min(C_D+, f_B')` is a fourth support-two
regime. Theorem-or-counterexample; no preferred outcome. Everything is
indexed by the unit support-count objective only (QG-2/QG-8: no transfer to
O1 or any reweighted objective).

## Imported committed machinery (UNMODIFIED)

- `research/extensions/orion-q/max_r6m_exact_three_tare2_shared_factor_dp.py`
  (`_synthetic_terms`, `_local_table`, `exact_r6m_matching`, tables)
- `research/extensions/orion-q/max_r6o_enlarged_tag_donor_closure.py`
  (`dp_cost_frozen_configs` — unrestricted-DP truth; `_letter_key`)
- `research/extensions/orion-q/max_r6p_weight2_frame_donor_closure.py`
  (`dxx_search` exact D++/D+ enumerator, `verify_dxx_witness` referee)
- `research/extensions/orion-q/max_r6s_all_n_composition.py`
  (`bind_tables`, `verify_lemma_e`, `verify_lemma_b`, `config_cost`,
  `config_labels` — the machine-checked all-n theorem C_DP == C_D++)
- `research/extensions/orion-qg/qg5b_exact_forecaster.py`
  (`bprime_family_min`, `verify_bprime_witness` — the EXACT committed QG-5b
  enlarged borrow family B'. B' is imported as committed and is NEVER
  enlarged, redefined, or patched by this lane, before or after any
  counterexample.)

Runtime guard extension (declared, no file modified): the committed r6p
enumerator is n-generic but its `EXPECTED_PAIR_COUNTS` integrity guard only
lists n <= 3. QG-7 executes
`r6p.EXPECTED_PAIR_COUNTS.setdefault(4, r6s.PAIR_COUNTS_SUPPORT2[4])`
(= 1968, a committed R6S constant) so the same unmodified enumerator runs at
n = 4. The D++ family definition is unchanged; the guard still hard-fails on
any pair-count mismatch.

## Definitions (per instance t = three target pairs over n qubits)

- `C_DP`   := `r6o.dp_cost_frozen_configs(r6m._synthetic_terms(t), n)`
  (committed unrestricted frozen-config DP truth).
- `C_D++`  := `r6p.dxx_search(t, n, max_weight=2)["C_Dxx"]`.
- `C_D+`   := `r6p.dxx_search(t, n, max_weight=1)["C_Dxx"]`.
- `f_B'`   := `qg5b.bprime_family_min(t, n)[0]` (None -> +INF).
- gap4     := `C_D++ - min(C_D+, f_B')`. `gap4 < 0` = fourth-regime candidate.

Per-instance hard assertions (every evaluated instance):
- sandwich: `C_DP <= C_D++ <= C_D+`;
- B' soundness: `C_DP <= f_B'` whenever f_B' is finite;
- R6S binding: `C_DP == C_D++` (the machine-checked theorem). Any violation
  is a first-class R6S contradiction, serialized verbatim, and routes the
  lane to the CANNOT_CHECK terminal.

## ARM 1 — COUNTEREXAMPLE-FIRST (mandatory, runs before any closure claim)

### Skeleton notation

Letters coded 0=I, 1=X, 2=Y, 3=Z. `L@q` is the weight-one Pauli with letter
L at qubit q; products are binary Pauli products. A skeleton is
`(n, frames6, S)` with `frames6 = (R_A0, R_A1, R_B0, R_B1, R_C0, R_C1)`.
Builders:
- `anchored(q, v, c)` -> frames `(v@q, c@q)`;
- `phantom(h, (m0,m1), b, ell)` -> frames `(m0@h, ell@b * m1@h)`.

Skeletons are witness SHAPES: they exist to derive adversarial target
instances (below). Whether a skeleton is itself a feasible grammar
configuration is recorded (`r6s.config_labels`) but feasibility is not
required for the derived instance to enter the panel.

### Frozen skeleton menus

H1 — multi-block borrow, different borrowed Tag anchors.
Letter rule for phantom blocks under a tag letter at the home qubit
(S_h != I): `(m0, m1, ell) = (X, Y, X)`; otherwise `(m0, m1) = mv` and
`ell = Y` (mv from the menu).
- n=3, S = X@0*X@1: for hA in (1,2), hB in (0,2), aC in (0,1):
  A = phantom(hA, mv=(X,Y), 0, rule), B = phantom(hB, mv=(X,Y), 1, rule),
  C = anchored(aC, X, Y).                                  [8 skeletons]
- n=4: (a) S = X@0*X@1, hA in (1,3), hB in (0,3), aC in (0,1), mv=(X,Y)
  [8]; (b) S = X@0*X@1*X@2, three-borrow: A = phantom(3, mvA, 0, rule),
  B = phantom(3, mvB, 1, rule), C = phantom(3, mvC, 2, rule) with
  (mvA,mvB,mvC) in {((X,Y),(X,Y),(X,Y)), ((X,Y),(Y,Z),(X,Y))} [2].
                                                           [10 skeletons]

H2 — support-two/support-two within one block (all overlap classes).
Block A = two weight-2 frames; blocks B, C anchored. Anchor qubit
`qa = min(supp(S))`; B = anchored(qa, X, Y), C = anchored(qc, X, Z) with
qc = second-lowest qubit of supp(S) if |supp(S)| >= 2 else qa.
Deterministic block-A frame-order fix: try (R0,R1) then (R1,R0); keep the
first order for which `config_labels` passes; else keep (R0,R1).
- n=3 same-support class (R0 = u0@0*v0@1, R1 = u1@0*v1@1), letters
  (u0,v0,u1,v1) in {(X,X,Y,X),(X,X,Y,Y),(Y,X,X,X),(X,Y,X,X)};
  S in {X@0*X@1, X@0}.                                     [8]
- n=3 shared-one-qubit class (R0 = u0@0*v0@1, R1 = u1@1*v1@2), letters in
  {(X,X,Y,X),(X,X,Y,Y),(X,Y,X,X),(Y,Y,X,Y)}; S in {X@0*X@2, X@2}. [8]
                                                           [16 skeletons]
- n=4: disjoint class (R0 = u0@0*v0@1, R1 = u1@2*v1@3), letters in
  {(X,X,X,X),(X,Y,X,Y)}, S in {X@0*X@2, X@1*X@3} [4]; shared class as n=3
  letters list with S = X@2*X@3 [4]; same-support class first two letter
  rows with S = X@0*X@3 [2].                               [10 skeletons]

H3 — cyclic borrow. Homes carry tag letters, so per-block letters follow
the feasibility-solved menu (m0 = X forced at tag-letter homes):
- n=3 3-cycle, S = X@0*X@1*X@2: block j in (A,B,C) has home h_j = (0,1,2)_j
  and anti frame `X@b_j * m1@h_j` with borrows b_j = (1,2,0)_j, i.e.
  frames_j = (X@h_j, X@b_j * m1@h_j), m1 in {Y, Z} uniform.  [2]
- n=3 2-cycle, S = X@0*X@1: A = (X@0, X@1 * m1@0), B = (X@1, X@0 * m1@1),
  C = anchored(aC, X, Y); m1 in {Y,Z} uniform, aC in (0,1).  [4]
                                                           [6 skeletons]
- n=4: off-cycle shared home 3, S = X@0*X@1:
  A = phantom(3, (X,Y), 1, ellA=Y), B = phantom(3, (Y,Z), 0, ellB) with
  ellB in (Y,Z), C = anchored(aC, X, Y), aC in (0,1) [4]; plus the n=3
  3-cycle embedded at n=4 (same frames/S, qubit 3 empty), m1 in {Y,Z} [2].
                                                           [6 skeletons]

H4 — multi-anchor Tag + phantom hybrid.
- n=3 (a) S = X@0*X@1: A = phantom(2, (X,Y), 0, Y), B = anchored(1, X, Y),
  C = anchored(cC, X, cL), cC in (0,1), cL in (Y,Z).       [4]
- n=3 (b) l1-phantom, S = X@0*Z@2: A = (Y@0*Y@2, X@2) (weight-1 frame on
  the label-1 branch, tag letter at the home), B = anchored(0, X, Y),
  C in {anchored(0, X, Z), phantom(1, (X,Y), 0, Y)}.       [2]
                                                           [6 skeletons]
- n=4 (a) S = X@0*X@1: A = phantom(h, (X,Y), 0, Y) with h in (2,3),
  B = anchored(1, X, Y), C = anchored(cC, X, cL), cC in (0,1),
  cL in (Y,Z).                                             [8 skeletons]

H5 — restore-factor F3 adversarial coupling (template-driven; the
skeletons are the canonical B'-like shapes, the RESTRICTED template set
below supplies the coupling):
- per n in (3,4), S = X@0:
  (i)  A = phantom(1, (X,Y), 0, Y), B = anchored(0, X, Y),
       C = anchored(0, X, Z);
  (ii) A = phantom(1, (X,Y), 0, Y), B = phantom(1, (Y,Z), 0, Z),
       C = anchored(0, X, Y);
  (iii) as (ii) but B's home = 2 for n=3 / 3 for n=4.      [3 skeletons]

### Frozen Restore-template grammar

Single-qubit branch add-ons. A branch choice is NONE or `(P, q_c, rot)`
with `q_c in 0..n-1` and base block-letter triples (applied to blocks
(A,B,C) rotated cyclically by `rot`):
- P1 single       (X,I,I)  rot in (0,1,2)
- P2 two-equal    (X,X,I)  rot in (0,1,2)
- P3 two-equal-one-different (X,X,Y) rot in (0,1,2)
- P4 all-three common factor (X,X,X) rot = 0
- P5 anti-aligned (X,Y,Z)  rot in (0,1,2)
Single-branch choice order (frozen rank): NONE first, then all `(P,q_c,rot)`
sorted by `(rot, P, q_c)`. Template pair (c0 for branch 0, c1 for branch 1)
order: sorted by `(count_non_NONE(c0,c1), rank(c0)+rank(c1), rank(c0),
rank(c1))` — identity first, then all single-branch templates in rank order,
then double-branch combos by rank sum. "Cross-anchor" columns are realized
by q_c ranging over every qubit including other blocks' anchor/borrow
qubits. H5 restriction: only pairs with BOTH branches non-NONE and both
q_c in the skeleton's occupied qubit set (union of frame and tag support),
ordered by `(rank(c0)+rank(c1), rank(c0), rank(c1))`.

### Instance derivation

For skeleton frames R_jk and template letters T_jk (product of the active
branch-choice letters for block j at their q_c): target `t_jk = T_jk * R_jk`
(binary product; T = t * R restores exactly the template column). An
instance is the target tuple `((t_A0,t_A1),(t_B0,t_B1),(t_C0,t_C1))`.
Skip (and count) any derivation with a zero target.

### Canonicalization (quotient representatives)

Cost symmetry group used: qubit permutations x per-qubit permutations of
{X,Y,Z}. Canonical key: write the 6 x n letter matrix; per column take the
minimum image over the 6 letter permutations (identity fixed on I); sort the
n canonicalized columns ascending; the key is that sorted tuple plus n.
Block/branch permutations are NOT quotiented (disclosed). Global dedupe map
across all H-panels; duplicates are counted, never re-evaluated. The
symmetry claim is gate-checked (below), not assumed silently.

### Enumeration order, caps, counts

Per (H, n) panel: iterate pairs `(template_pair_index tp, skeleton_index s)`
sorted by `(tp, s)`; derive, canonicalize, dedupe, evaluate; stop at the
panel cap. Frozen caps (hard, disclosed — the template space is much larger
than the caps by design; cap_hit is recorded per panel, never silent):
- n=3: H1 120, H2 160, H3 90, H4 90, H5 120  (<= 580 instances)
- n=4: H1 40, H2 40, H3 24, H4 32, H5 24     (<= 160 instances)
Recorded per panel: skeleton count, full template-pair space size, raw
scanned, zero-target skips, duplicate skips, evaluated, cap, cap_hit,
infeasible-skeleton count, regime census over {split, borrow, tie, fourth}
where split: C_D++ == C_D+ < f_B'; borrow: C_D++ == f_B' < C_D+;
tie: C_D++ == C_D+ == f_B'; fourth: gap4 < 0; min/max gap4.

### Hostile referee gates (Arm 1)

- Skeleton containment: for every feasible skeleton (config_labels ok, all
  frames weight <= 2, labels distinct), assert
  `C_D++ <= min over 8 centrals of r6s.config_cost(t6, frames6, S, centrals, n)`
  on the derived instance. Zero failures required.
- D++ witness referee (`r6p.verify_dxx_witness`): every instance with
  `C_D++ < C_D+`, plus every 7th evaluated instance. Zero failures.
- B' witness referee (`qg5b.verify_bprime_witness`): every instance with
  finite f_B'. Zero failures.
- Exact witnessed matcher (`r6m.exact_r6m_matching`, all internal checks):
  every 20th n=3 instance, every 8th n=4 instance, and every fourth-regime
  candidate; must reproduce C_DP exactly. Zero failures.
- Canonicalization symmetry: every 17th evaluated instance, re-evaluate all
  four family values on the canonical-form image; must be identical.
- Fourth-regime candidate replay (terminal-grade): every candidate with
  gap4 < 0 is replayed through verify_dxx_witness AND exact_r6m_matching
  AND the sandwich/soundness asserts; only a candidate passing ALL replays
  is a confirmed witness. Candidates and replays serialized verbatim
  (cap 50 verbatim rows; counts always exact).

## ARM 2 — NORMALIZATION THEOREM (runs regardless; closure claims only if
Arm 1 is empty)

All local-domain checks are COMPLETE enumerations with sizes recorded; every
exchange inequality is proved against worst-case adversarial other-block
letters via full-domain F3 tables (never independent per-block sums) — this
is the L5 discipline applied to every closed step.

Frozen finite checks:
- N0 (committed lemma reruns): `r6s.verify_lemma_e()` must return
  domain 18432, violations 0, max_delta_f3 2; `r6s.verify_lemma_b()` must
  return total 43688, w3..w8 all admit a zero-sum subset, w2 boundary
  exactly {(1,2),(1,3),(2,1),(3,1)}; both bound to the committed R6S
  receipt values.
- N1 (slot-replacement F3 bound): domain = 3 slots x old x new x 4^2
  environments = 768 cases; record max Delta f3 for in-place change
  (expected 2), removal new=I (expected 1), addition old=I (expected 1).
- N2 (colocation/subadditivity): 64 cases; f3(a,b,c) <= lw(a)+lw(b)+lw(c)
  with equality iff not all-equal-nonzero (discount exactly 2).
- N3 (w=2 class dichotomy): the 8 odd-alpha class tuples ((a1,b1),(a2,b2));
  each either contains class (0,0) (reducible by Lemma-E zeroing) or is
  exactly {(1,*),(0,1)} (one anticommuting qubit + one Tag-syndrome borrow
  qubit); the 4 irreducible patterns must equal the committed R6S w2
  boundary under code 2*alpha+beta.
- N4 (central placement): u(wc,wnc) = 4(wnc-1)+2(wc-1) over {1,2}^2;
  central-on-heavier is minimal, strictly by 2 when weights differ;
  u(2,2) = 6, u(2,1) = 2, u(1,1) = 0.
- N5 ((2,2) block elimination — the main new complete-domain lemma):
  support patterns ({0,1},{0,1}), ({0,1},{1,2}), ({0,1},{2,3}); frame
  letters in {X,Y,Z}^4; tag letters in {I,X,Y,Z}^|union|; per case compute
  symp(R0,R1) (infeasible_pair if != 1), labels l0,l1 (infeasible_labels
  if equal), classes (alpha,beta) per support qubit; if any class is (0,0)
  the case is REDUCIBLE_BY_ZEROING (Lemma E, support strictly drops, cost
  non-increasing); otherwise search a weight-one replacement `w@q'`,
  q' in the union support, for the label-1 frame with
  sy(S_q', w) = 1 and sy(w, cold-frame letter at q') = 1; if found the
  exchange refunds Delta_u = 4 (N4: 6 -> 2) against a worst-case F3 delta
  bounded via N1 by (2+1) or (1+1+1) = 3 <= 4 across the changed qubits,
  for EVERY adversarial environment — case REPLACED. Any remaining case is
  an L1 failure, serialized verbatim. Expected domain sizes: 1296 + 5184 +
  20736 = 27216 cases.
- N7 (tag-support pruning, L4a): complete domain at n=2 — all 6^3 ordered
  anticommuting weight-one frame letter pairs at qubit 0, base tag letters
  s0 in {X,Y,Z} filtered to config_labels-valid, extra letter e in {X,Y,Z}
  at qubit 1, over a frozen panel of 5 target sextuples; dropping the extra
  tag letter must preserve labels and reduce config_cost by exactly 2 in
  every case (counts recorded).

Obligation adjudication (frozen mapping):
- L1 (canonical block shape): CLOSED_ALL_N iff N5 has zero failures (with
  N1/N4 backing); else PARTIALLY_CLOSED with the exceptional overlap
  patterns serialized.
- L2 (support-two orientation): CLOSED_ALL_N iff N3 dichotomy exact + N0
  binds + N4 strict central rule holds.
- L3 (borrow-home normalization): at best CLOSED_CONDITIONAL — closed for
  configurations already in the weight-one-Tag pre-B' normal form, by N2
  colocation (empty homes merge into the single frozen empty representative
  without cost increase; in-support homes are already in B's frozen pool);
  the reduction TO that normal form is L4's open consolidation, so L3 can
  never adjudicate above CLOSED_CONDITIONAL while L4 is open. OPEN if N2
  fails.
- L4 (multi-block/cyclic/hybrid consolidation): L4a (tag letters outside
  the union frame support strictly prune, exact refund 2) closed by N7.
  The consolidation of multi-anchor borrows (H1), cyclic borrows (H3),
  hybrid split+borrow (H4) and l1-phantom shapes is NOT claimed closed by
  this protocol unless a complete-domain proof materializes in the run;
  the frozen expectation is PARTIALLY_CLOSED with these named open shapes:
  H1_multi_anchor_borrow_tag_weight_ge_2, H3_cyclic_borrow,
  H4_hybrid_split_borrow, H4b_l1_phantom_tag_letter_at_home. OPEN if N7
  fails.
- L5 (F3 interaction closure): PARTIALLY_CLOSED = every closed exchange
  above is proved against full adversarial branch tables (N1/N2 are
  complete-environment domains; no independent per-block summation is used
  anywhere); the obligation remains open exactly where L4 is open.
  OPEN if N1 or N2 fails.

## Receipt bindings (exact, hard gates)

- QG-5b: authority string must equal
  `ORIONQG_QG5B_EXACT_FORECASTER_THEOREM_BACKED_ZERO_ERROR__DPP_FAMILY_MIN__ENLARGED_BORROW_CLOSES__NOT_R6`;
  q1.dp_compared_instances_total == 9547; q2.outcome ==
  `Q2_ENLARGED_BORROW_CLOSES`; the QG-5 refuting instance (panel A row:
  n=3, target_pairs [[[3,6],[7,3]],[[7,3],[3,4]],[[0,3],[2,2]]]) is replayed
  through this lane's evaluators and must reproduce C_DP = 10 = C_D++,
  C_D+ = 11, f_B' = 10 exactly as receipted.
- R6S: authority must start with
  `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED`; lemma_e/lemma_b
  receipt values must equal the N0 rerun values exactly.
- Tables: `r6s.bind_tables()` all true; r6p.F3 == r6q-independent F3 ==
  r6m._F3 as int64; r6p pair counts {1:6, 2:120, 3:666} plus the declared
  n=4 extension 1968 re-derived by the enumerator itself.

## Terminals and frozen authority strings

1. Any CONFIRMED fourth-regime witness (gap4 < 0, all replays pass) ->
   `QG7_FOURTH_SUPPORT2_REGIME_FOUND`, authority
   `ORIONQG_QG7_FOURTH_SUPPORT2_REGIME_FOUND__HOSTILE_SEARCH_WITNESS_REFEREE_CONFIRMED__NOT_R6`.
2. Candidate exists but ANY replay fails, or any R6S contradiction, or any
   integrity/receipt gate fails ->
   `QG7_CANNOT_CHECK`, authority
   `ORIONQG_QG7_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6`
   (everything serialized verbatim).
3. Hostile search empty AND L1–L5 all CLOSED_ALL_N ->
   `QG7_ENLARGED_BORROW_COMPLETENESS_ALL_N_MACHINE_CHECKED`, authority
   `ORIONQG_QG7_ENLARGED_BORROW_COMPLETENESS_ALL_N_MACHINE_CHECKED__L1_L5_CLOSED_WITH_R6S__NOT_R6`.
   (Requires every named hybrid/multi-anchor shape closed; a finite panel
   can never authorize this on its own.)
4. Hostile search empty AND some obligation below CLOSED_ALL_N ->
   `QG7_PARTIAL_NORMALIZATION__HYBRID_SHAPE_OPEN`, authority
   `ORIONQG_QG7_PARTIAL_NORMALIZATION__HYBRID_SHAPE_OPEN__HOSTILE_SEARCH_EMPTY__NOT_R6`.
5. `QG7_DONOR_PARENT_FOUND` (authority
   `ORIONQG_QG7_DONOR_PARENT_FOUND__NOT_R6`) is listed per charter; no
   construction in this protocol can emit it, and it is frozen as unused.

Authority ceiling: NOT_R6 (hard-asserted on the final authority string).
No novelty credit, no donor credit, no physical quantum-advantage claim.

## Artifacts, determinism, runtime

- Analyzer: `research/extensions/orion-qg/qg7_bprime_completeness.py`
  (imports committed machinery unmodified; no RNG anywhere in the lane;
  fully deterministic enumeration).
- Results: `research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json`
  with `result_digest` = sha256 of the canonical JSON of the result without
  the digest and without the timing section. Canonical stdout receipt line:
  `ORIONQG_QG7_BPRIME_COMPLETENESS=` + canonical JSON (timing excluded per
  the R6P convention; timing only in the RESULTS timing section and on
  stderr).
- Verification sample for the independent verifier: for every (H, n) panel,
  the evaluated instances at local indices {0, floor(count/2)} are stored
  verbatim (targets + all four family values).
- Double run: the analyzer is executed twice; the canonical stdout lines
  and the RESULTS-minus-timing serializations must be byte-identical.
- Independent verifier:
  `development/orion-qg-regime-geometry/qg7_generic_verify.py` — rebuilds
  N1–N5 from primitive local operations (p10.h) WITHOUT importing the
  analyzer or its tables, replays the stored verification sample through the
  committed referees (r6o DP truth, r6p D++/D+, qg5b B'), re-verifies the
  protocol sha256, the result digest, gate booleans, terminal consistency,
  and prints an ACCEPT/REJECT token
  (`ORIONQG_QG7_GENERIC_VERIFY=...`), writing
  `artifacts/orion-qg-qg7-generic-verification.json`.
- Runtime cap: 25 minutes per analyzer run (frozen; the caps above were
  sized from the pre-freeze timing probe: ~0.7 s/instance at n=3,
  ~2.6 s/instance at n=4). Cache hygiene: `r6m._local_table` cleared every
  128 evaluated instances and between panels; `r6o._block_cache` and
  `qg5b._bprime_block_cache` cleared per instance.
- Prohibitions: no committed file is modified; the protected
  `N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`
  is never read; no chemistry data is read anywhere in this lane.

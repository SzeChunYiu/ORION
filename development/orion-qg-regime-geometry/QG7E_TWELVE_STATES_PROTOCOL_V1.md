# QG-7e twelve-states protocol V1 (FROZEN BEFORE OUTCOME)

Lane: ORION-QG QG-7e — **the twelve states**: close the residue left by QG-7d so that
`C_DP == min(C_D+, f_B′, f_B″)` becomes an all-n theorem for unit-cost TARE, or establish
precisely why it cannot close. Successor registered in `QG_WAVE2_RECORD.md` under
"Registered successor — QG-7e — the twelve states". Base revision `84f34f69`
(working branch as recorded by the orchestrator). Authority ceiling **NOT_R6**.
No chemistry data is read; the protected stretched-N2 subject
(`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/...`) is never touched. No repository file
is modified; every inherited lane script and receipt is read-only and every piece of
committed machinery is imported unmodified. In particular
`research/extensions/orion-qg/qg7d_last_link.py` is imported but never edited and
`research/extensions/orion-qg/QG7D_LAST_LINK_RESULTS.json` is read but never rewritten;
this lane writes only to `research/extensions/orion-qg/QG7E_TWELVE_STATES_RESULTS.json`.

## Where the chain stands (bound, not re-argued)

QG-7d (`QG7D_LAST_LINK_RESULTS.json`, terminal `QG7D_PARTIAL__P1_RESIDUE_OPEN`, authority
`ORIONQG_QG7D_PARTIAL__P1_RESIDUE_OPEN__NOT_R6`, `result_digest`
`cdca51a19c2f764f5e71c408abe0f08e3929eb878c90c17e02bd0f1b0ff9650c`, `protocol_sha256`
`e9ebe4e69144e092ff7852691b74dfcb3e29b3f5f0133b4bad74e3be3c65bd0e`) closed **373 of 378**
geometries over the complete **6,341,787,648**-state P1 domain (27 roles → 378 geometries
× 16,777,216 states), dispatched all **135,604** T4b census patterns CLOSED, and left a
residue of exactly **12 states** in **5** geometries at worst local deficit **+1**,
serialized verbatim in its receipt. Its hostile arm realized the residue-extremal states at
n = 2/3/4 and found **0 gap rows**: the identity is believed true at those states; what is
missing is the lemma. Step 7 of QG-7d's `proof_audit` is therefore closed on
6,341,787,636 of 6,341,787,648 states; steps 1–6 and 8–11 carry.

## Question (frozen)

Does every configuration containing a comm-s2 block admit, at the twelve residual states,
a Δ ≤ 0 alternative with strictly fewer comm-s2 blocks — closing step 7 on the complete
domain and hence `C_DP == min(C_D+, f_B′, f_B″)` for all n under the unit support-count
objective — or is there a referee-confirmed instance where the identity actually fails?

## Attack set (frozen verbatim BEFORE any outcome under this protocol is computed)

- **E1 (primary): a composition/fixpoint argument.** Strict descent fails, so replace the
  descent measure. Candidates: a well-founded order on (comm-s2 count, secondary
  structural rank) that the replacement *does* decrease; or a fixpoint/absorption argument
  showing the rewrite cannot cycle among residual states — i.e. iterating the Δ ≤ 0
  replacement from any residual state terminates in a non-comm-s2 configuration. Because
  the replacement moves comm-s2 to a *different* block, the natural object is the orbit of
  the replacement map over the 12 states and their images; enumerate that orbit exactly.
- **E2: enlarge the geometry class.** The 12 lie in 5 geometries; test whether a joint
  treatment of those 5 (rather than geometry-by-geometry) closes them — the QG-7d A2 win
  came from exactly such a widening (MG mirror + per-block target permutation).
- **E3: direct exhaustive settlement.** 12 states is tiny. For each, exhaustively verify
  over the complete configuration space at the smallest n realizing it that
  `C_DP == min(C_D+, f_B′, f_B″)` holds, with a proof-carrying referee. This does not by
  itself give all-n, but a clean 12/12 plus an argument that these states' behaviour is
  n-independent may suffice — state precisely what that argument requires and whether it
  was established.

No attack outside E1/E2/E3 is admitted. If the frozen attack set leaves a residue, the
residue is serialized exactly and the lane terminates PARTIAL.

## Realization of the attacks (frozen constructions and their complete domains)

### E1 — replacement orbit (exact enumeration)

For each of the 12 residual states, bound verbatim from the QG-7d receipt, enumerate:

1. `Δ_P1` = the minimum, over QG-7d's own frozen P1 alternative menu (block 0 must not be
   comm-s2; another block may be comm-s2 only if it already was), of `cost(Y) − cost(X)`.
2. `Δ_W` = the same minimum over the **widened** menu in which either other block may
   become comm-s2 even if it was not — i.e. the menu in which the comm-s2 count is allowed
   to stay constant by moving comm-s2 to a different block. Every `Δ_W ≤ 0` optimum is a
   *replacement image*.
3. The **replacement map** `R` on the 12 states: for each residual state, every `Δ_W ≤ 0`
   image whose comm-s2 block sits on a different block index is emitted, canonicalised
   back into a (geometry, state) pair when its symp-0 support is again `{b, a}` and its
   external profile is empty, and tested for membership in the residue set. The orbit of
   `R` over the 12 states and their images is enumerated **exactly** (breadth-first to
   fixpoint, cycle detection on the canonical image set), and the resulting relation is
   serialized: orbit size, images per state, images inside/outside the residue, cycles.

Complete domain per state: both branches × both label orientations × all 16 tag pairs ×
the full product of feasible per-block local frame assignments (each block's four local
letters over `4^4` filtered by the two label constraints, the inter-frame anticommutation
and the weight bounds, each including its external profile). Enumerated exhaustively, not
sampled; the enumerated option counts are recorded.

**E1 closes only if** every residual state has at least one `Δ ≤ 0` image, the orbit is
acyclic, and every terminal element of the orbit is P1-closed. If some residual state has
an **empty** replacement set — i.e. no `Δ ≤ 0` alternative exists at all in the frozen move
class — then the residue is a *local-optimality* failure, not a descent failure, the orbit
of `R` is empty at that state, and E1 is reported as unable to close, with the exact
reason serialized.

### E2 — geometry-class enlargement (joint treatment of the residual geometries)

The five residual geometries are treated jointly through the **per-block target
permutation**: which of a block's two targets is carried by its label-0 frame. This is a
configuration degree of freedom of the committed `r6p.dxx_search` — `r6p._block_arrays`
enumerates `for perm in (0, 1)` **independently for each of the three blocks**, and
`dxx_search` minimises over the concatenated per-block arrays — and QG-7d's own protocol
declares it in its cost-model section. QG-7d's implemented P1 menu realizes it **only as
the global MG mirror** (all three blocks' branches swapped simultaneously, together with
the state swap `SWAP`), i.e. only the two group elements `p ∈ {000, 111}` of the eight.
E2 admits all **eight** per-block subsets `p ∈ {0,1}³`.

**P1E (the enlarged domination lemma).** Identical to QG-7d's P1 in every other respect —
same role inventory, same geometry list, same alternative menu `block_options`, same exact
local cost difference, same comm-s2 constraints (v) — with the alternative additionally
allowed to read the state through any of the eight per-block target permutations
`PERM[p]`, `p ∈ {0,1}³`, where `PERM[0]` is the identity and `PERM[7] = SWAP` is the
global MG state swap. Complete domain, no sampling:

  **27 roles → 378 geometries × 4^6 states at b × 4^6 states at a = 6,341,787,648 states.**

**GATE: zero states with Δ > 0, over every geometry.** Any residue is censused exactly
(per geometry, verbatim rows capped at 200, cap disclosed) and forces PARTIAL.

Two obligations attach to E2 and are gated separately:

- **R1 (residue reproduction).** With the enlargement switched off (`p ∈ {000, 111}` only,
  exactly QG-7d's menu) the lemma must reproduce QG-7d's residue **row for row** over the
  complete **5 × 16,777,216 = 83,886,080**-state domain of the five residual geometries:
  the same 12 states, the same per-geometry counts. This is what makes the enlargement,
  and not an implementation difference, responsible for the closure.
- **GP (permutation binding).** The per-block target permutation must be bound to the
  committed machinery on a complete domain, not asserted. For every `n ∈ {1, 2, 3}`, every
  ordered anticommuting frame pair of `r6p._tables(n, 2)` and every ordered pair of
  non-identity target Paulis, both halves of `r6p._block_arrays` are re-derived from
  first principles — `base[k] = uanti[k] + wt(t0·R0_k) + wt(t1·R1_k)` and
  `base[P+k] = uanti[k] + wt(t1·R0_k) + wt(t0·R1_k)`, with the position codes rebuilt
  letter by letter — and compared elementwise against the committed arrays. Domain:
  `6·9·2 + 120·225·2 + 666·3969·2 = 108 + 54,000 + 5,286,708 = 5,340,816` rows.
  **GATE: zero mismatches.** (Arithmetic of this declared constant corrected in place
  before any run under this protocol produced any outcome; see the disclosure section.)

### E3 — direct exhaustive settlement at the twelve states

- **E3a — complete local configuration space.** For each of the 12 residual states, an
  independent brute-force enumeration (no covering bitset, no grouping, no sparse
  fallback — a different algorithm from P1E's) over the *whole* enlarged alternative menu:
  eight permutations × two branches × two label orientations × 16 tag pairs × the full
  per-block option product. It recomputes `cost(X)` and `min_Y cost(Y)` directly and
  serializes the **achieving alternative verbatim** (permutation, branch, orientation, tag
  pair, frame pattern at b, frame pattern at a, cost) as a proof-carrying witness for each
  of the 12. Enumerated option counts recorded. **GATE: every one of the 12 has an
  achieving alternative with Δ ≤ 0 and strictly fewer comm-s2 blocks.**
- **E3b — realized-instance referee.** Each of the 12 states is realized as concrete
  instances through the committed realization map and refereed end to end:
  (i) `n ∈ {2, 3, 4}` by `qg7d_last_link._instance_from_state` (identity-target states
  skipped and counted); (ii) a **complete third-qubit sweep** at `n = 3` over the frozen
  complete sub-domain "third-qubit target weight ≤ 1" — the 1 empty state plus the 18
  single-letter states, `12 × 19 = 228` candidate instances, identity-target instances
  skipped and counted. For every instance: `C_Dxx = r6p.dxx_search` with witness,
  `C_D+` (`max_weight=1`), `f_B′ = qg5b.bprime_family_min`, `f_B″ = qg7b.bsecond_family_min`;
  hard **sandwich assertions** `C_Dxx ≤ C_D+`, `C_Dxx ≤ f_B′`, `C_Dxx ≤ f_B″` on every
  finite value; `r6p.verify_dxx_witness` refereed on 100% of rows; any gap row
  (`C_Dxx < min(C_D+, f_B′, f_B″)`) replayed through `r6o.dp_cost_frozen_configs` +
  `r6m.exact_r6m_matching` and the B′/B″ witness verifiers and serialized verbatim
  (cap 50, disclosed).
- **What n-independence requires, stated in advance.** E3b alone is finite evidence and
  never yields an all-n theorem. The all-n statement is carried by E2 and by E2 only,
  because P1E's alternatives change letters **only at the two comm-s2 qubits** (and read
  the state only through a per-block target permutation, which permutes targets without
  moving support), so the Δ it computes is the exact global cost difference at every n and
  for every external target data. E3b is therefore recorded as a refutation arm, and the
  RESULTS states explicitly whether the n-independence argument rests on E2's locality
  (accepted) or on E3b's finite panels (not accepted).

## P2 — QG-7c T4b census dispatch (hostile gate, inherited)

`qg7c_classification.t4b_pinned()` is re-run unmodified inside this lane; its census must
reproduce **verbatim** (domain 536,870,912; 135,604 failures; worst Δ = +2; the six
per-(case, ja, Δ) counts `{PA_ja0_delta1: 97072, PA_ja0_delta2: 2376, PA_ja1_delta1: 3600,
PP_ja0_delta1: 30500, PP_ja0_delta2: 440, PP_ja1_delta1: 1616}`). Every censused pattern is
then dispatched individually against P1E's per-geometry verdicts, by the committed QG-7d
dispatchers `census_dispatch`, `census_state_dispatch` and `explicit_verbatim_dispatch`
imported unmodified. The per-pattern dispatch counts must sum exactly to 135,604.

## P3 — hostile realization arm (counterexample-first, referee-confirmed)

(C1) The first 25 verbatim T4b census rows realized at n=3 and the first 6 at n=4 by the
committed `qg7c_classification._realize_row`. (C2) A frozen dense-random control: n=3, 60
instances, seed 20260921; n=4, 15 instances, seed 20260922 (uniform nonzero targets).
(C3) The **12 QG-7d residual states bound verbatim from its receipt**, realized at
n = 2, 3, 4 (cap 40, disclosed). Same referee obligations as E3b: witness verification on
100% of rows, sandwich assertions, gap replay and verbatim serialization.

## Imported committed machinery (UNMODIFIED)

`max_r6_p10_candidate_blind_frame_optimizer`, `max_r6m_exact_three_tare2_shared_factor_dp`,
`max_r6o_enlarged_tag_donor_closure`, `max_r6p_weight2_frame_donor_closure` (with the
committed runtime guard extension installed by importing `qg7_bprime_completeness`,
exactly as QG-7/QG-7b/QG-7c/QG-7d declared), `max_r6s_all_n_composition`,
`qg5b_exact_forecaster` (f_B′), `qg7_bprime_completeness`, `qg7b_hybrid_family` (f_B″),
`qg7c_classification` (`bind_tables`, `mg_gauge`, `m1_inventory`, `t1_prune`,
`t3_consolidation`, `t4a_unpinned`, `t4b_pinned`, `t5_home_merge`, `_realize_row`) and
`qg7d_last_link` (`bind_tables`, `bind_receipts`, `mirror_identity`, `gauge_permutations`,
`build_roles`, `OURS`, `mirror_block`, `block_options`, `menu_pairs`, `_mask_rows`,
`GP`, `SWAP`, `uanti`, `code6`, `census_dispatch`, `census_state_dispatch`,
`explicit_verbatim_dispatch`, `_instance_from_state`, `_eval_instance`) — all read-only
imports of committed files. The only randomness is the frozen dense-random control stream.

## Cost model (bound, not re-defined)

Unchanged from QG-7d and bound by G1/G2/G3 and by GP:
`cost = Σ_j uanti_j + 2·wt(σ) + Σ_{j,k,q} wt(t_jk·f_jk) − 2·(#triple collisions)` with
`uanti(w0,w1) = 4·(min−1) + 2·(max−1)` and per-position
`F3(a,b,c) = 1 if a==b==c≠0 else wt(a)+wt(b)+wt(c)`.

## Receipt bindings (exact values, gated)

- **QG-7d** `QG7D_LAST_LINK_RESULTS.json`: terminal `QG7D_PARTIAL__P1_RESIDUE_OPEN`;
  authority `ORIONQG_QG7D_PARTIAL__P1_RESIDUE_OPEN__NOT_R6`; `result_digest`
  `cdca51a19c2f764f5e71c408abe0f08e3929eb878c90c17e02bd0f1b0ff9650c`; `protocol_sha256`
  `e9ebe4e69144e092ff7852691b74dfcb3e29b3f5f0133b4bad74e3be3c65bd0e`; P1 role count 27,
  geometry count 378, state domain per geometry 16,777,216, total states 6,341,787,648,
  geometries closed 373, residue total 12; the 12 residue rows verbatim in their five
  geometries; census dispatch 135,604 closed / 0 open; hostile arm 0 gap rows; all 10 gates
  true.
- **QG-7c / QG-7b / QG-7 / R6S**: exactly the bindings QG-7d gates, re-run here through
  `qg7d_last_link.bind_receipts()` unmodified.
- **Tables (G1)**: `MY_LM/MY_SY/MY_LW/MY_F3` equal to the frozen `r6m` tables, `r6p.F3`
  equal to `MY_F3`, pair counts `{1: 6, 2: 120, 3: 666, 4: 1968}`.

## Terminals (frozen; no post-outcome changes)

- **`QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE`** — requires ALL of: every gate G1–G12
  true; the QG-7d residue reproduced row-for-row by R1; the permutation binding GP exact on
  its complete domain; **P1E residue exactly zero over every one of the 378 geometries**
  (6,341,787,648 states); the T4b census reproduced verbatim and all 135,604 patterns
  dispatched closed; E3a exhibiting a Δ ≤ 0 achieving alternative for all 12; E3b and P3
  with zero gap rows, 100% referee coverage and all sandwiches asserted. The RESULTS then
  carries the assembled `proof_audit` chain end to end, each link naming its receipt.
  Authority `ORIONQG_QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE__COMM_S2_SECTOR_CLOSED_BY_
  PER_BLOCK_TARGET_PERMUTATION_DOMINATION__NOT_R6`.
- **`QG7E_PARTIAL__<residue>_OPEN`** — any P1E residue (`P1E_RESIDUE`), any undispatched
  censused pattern (`CENSUS_RESIDUE`), or any state E3a cannot settle (`E3_RESIDUE`), with
  the referee arms empty of gap rows and every other gate passing. The residue is
  serialized verbatim. Authority `ORIONQG_QG7E_PARTIAL__<residue>_OPEN__NOT_R6`.
- **`QG7E_IDENTITY_REFUTED`** — a referee-recomputed instance with
  `C_Dxx < min(C_D+, f_B′, f_B″)`, replay-confirmed through the independent DP referee and
  the B′/B″ witness verifiers, serialized verbatim. First-class discovery. Authority
  `ORIONQG_QG7E_IDENTITY_REFUTED__WITNESS_REFEREE_CONFIRMED__NOT_R6`.
- **`QG7E_CANNOT_CHECK`** — any binding, domain-size, sandwich, referee or integrity gate
  failure. Authority `ORIONQG_QG7E_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6`.

## Gates

- **G1** tables and pair counts bound (`qg7d_last_link.bind_tables`).
- **G2** mirror identity: complete `16,777,216`-case F3 exchange domain, zero failures;
  QG-7c `mg_gauge` re-run and `holds` true.
- **G3** letter-permutation gauge: complete domain per permutation, zero failures.
- **G4** M1 re-derived unmodified: raw domain 262,144, zero unclassified, shape counts
  exactly {anchored 288, phantom 864, comm_s2 864}.
- **G5** T1/T3/T4a/T5 re-derived unmodified with the exact committed domain sizes and
  failure counts.
- **G6** QG-7d receipt bound verbatim, including the 12 residue rows and every number
  listed under *Receipt bindings*.
- **G7** R1: the un-enlarged menu reproduces the 12 residual states row-for-row over the
  complete 83,886,080-state domain of the five residual geometries.
- **G8** GP: the per-block target permutation binding is exact on its complete
  5,340,816-row domain (zero mismatches), and the supplementary n=2 operational panel
  against `r6p.dxx_search` (the 144 ordered pairs formed from the twelve residual
  `state_b` and the twelve residual `state_a` values, identity-target instances skipped
  and counted) shows zero disagreements.
- **G9** P1E: every geometry's state domain exactly `16,777,216`, geometry count 378, total
  `6,341,787,648`, residue recorded; the theorem terminal requires residue 0.
- **G10** census: T4b reproduces the committed values verbatim; per-pattern dispatch counts
  sum exactly to 135,604 with 0 open.
- **G11** referee: 100% witness coverage (`dxx_witness_rows == rows`) across E3b and P3,
  zero sandwich failures, zero replay failures; any gap row replay-confirmed.
- **G12** no silent truncation: every cap disclosed in the RESULTS (P1E residue verbatim
  cap 200; E1 image cap 64; census verbatim cap 40 inherited; gap verbatim cap 50; C1 caps
  25 + 6; C3 cap 40; E3b third-qubit sweep is complete, not capped).

## Runtime and reproducibility

Runtime cap **1500 s per run (< 25 min)**; timing excluded from the canonical stdout line
and from the result digest (R6P convention: timing lives in the RESULTS `timing` section
and on stderr only). Two runs; the canonical stdout line
`ORIONQG_QG7E_TWELVE_STATES=<canonical json>` and RESULTS-minus-timing must be
byte-identical. Independent pure-primitive verifier
`development/orion-qg-regime-geometry/qg7e_generic_verify.py` rebuilds the Pauli algebra,
the F3 objective, the frame charge, the role inventory and the geometry list from the
protocol's own definitions — importing nothing from the analyzer lanes and nothing from
`orion-q` — re-derives P1E with a deliberately different traversal (grouped by the frame
pattern at the SECOND comm-s2 qubit, coverage bitset transposed), re-derives the
un-enlarged residue and checks it against the QG-7d receipt, re-checks the census dispatch
arithmetic, the terminal selection and the result digest; prints ACCEPT/REJECT.

## Design-phase disclosure (scoping exploration, not part of the outcome)

Disclosed in full: before this file was frozen, a scoping exploration (i) re-derived the 12
residual states from the QG-7d receipt and decoded them (all twelve are *alignment-maximal*
states: at each of the two comm-s2 qubits and each branch the three blocks' composed
letters coincide, so the original configuration collects the maximal triple-collision
refund); (ii) measured the P1 and widened-menu deficits at those states, finding that ten
of the twelve admit **no** Δ ≤ 0 alternative at all in QG-7d's move class, so the residue is
a local-optimality failure rather than the descent failure E1 assumes; (iii) probed a
third-qubit enlargement and found it closes most but not all of the c-data domain; and
(iv) identified the per-block target permutation as the E2 widening by reading
`r6p._block_arrays` and `dxx_search`. The frozen constructions, domains, gates and
terminals above are final and no outcome under them has been computed at freeze time; the
official runs compute every domain from scratch.

**Pre-outcome corrections (recorded in full).** After the first freeze and *before any run
under this protocol produced any outcome or any receipt existed*, two transcription errors
in declared constants were corrected in place: (a) the GP domain size, mis-summed as
`5,342,016`, is `6·9·2 + 120·225·2 + 666·3969·2 = 5,340,816`; (b) the G8 gate line was
extended to name the supplementary n=2 operational panel that the lane also runs. Neither
correction changes a gate's meaning, a domain's definition, a terminal, or an attack. No
other change was made after the first freeze.

## Stop rules and scope

Inherited verbatim from the wave-1 packet and charter: theorem, donor absorption,
receipted saturation, confirmed prospective test, first-class refutation, or cannot-check;
no post-outcome gate changes; the protected stretched-N2 subject remains sealed. This lane
proves nothing about other objectives, other grammars, rotation counts, or any chemistry
subject; no novelty credit; no donor novelty credit; no R6 authority; **NOT_R6**.

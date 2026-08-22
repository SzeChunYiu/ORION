# QG-7d last-link protocol V1 (FROZEN BEFORE OUTCOME)

Lane: ORION-QG QG-7d — **the last link**: close the comm-s2 **pinned** sector so that
`C_DP == min(C_D+, f_B′, f_B″)` becomes an all-n theorem for unit-cost TARE, or establish
precisely why the lemma cannot close. Successor registered in `QG_WAVE2_RECORD.md` under
"QG-7c — classification chain machine-checked to one link". Base revision
`509f962c` (branch `claude/orion-harness-verification-b17qdj`). Authority ceiling
**NOT_R6**. No chemistry data is read; the protected stretched-N2 subject
(`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/...`) is never touched. No repository file
is modified; all inherited machinery is imported unmodified.

## Question (frozen)

For pinned comm-s2 blocks (label-0 support-2 frame across two tag qubits, both
borrow-syndrome, σ_b pinned by another block's use), prove by complete local-domain
machine check that every configuration containing such a block either

  (a) reduces at Δ ≤ 0 into D+ ∪ B′ ∪ B″ shape, or
  (b) is strictly dominated by the family min,

or exhibit a referee-confirmed instance where the identity actually fails in that sector.

## Attack set (frozen verbatim BEFORE any outcome is computed)

- **A1 (sharper exchange — pair move).** QG-7c's T4b move menu was per-block: it rewrote
  the comm-s2 block and allowed only an in-place re-letter of the pinning block, never
  rewrote the third block, and never moved the tag letters. A1 replaces it by a **joint
  (pair/triple) rewrite**: the comm-s2 block, the pinning block and the third block are
  re-lettered **simultaneously** at the two comm-s2 qubits, together with a free re-choice
  of the tag letters at those two qubits (T3-style anchor re-lettering and the T1 refund
  are special cases of this joint menu, and both remain separately receipt-proven exact).
- **A2 (domination instead of reduction) — PRIMARY.** The theorem needs every D++
  *optimum value* to be attained by some reducible configuration, not every configuration
  to be individually reducible. A2 therefore replaces "min over a fixed move menu" by
  "**min over every comm-s2-free configuration reachable without touching any other
  qubit**" — i.e. the exact local optimum of the comm-s2-free family on the two comm-s2
  qubits — and, as a second admissible dominating branch, the **MG mirror image** of the
  configuration (frames, targets and centrals of every block swapped, label orientation
  flipped), which QG-7c's MG lemma proves is an exactly cost-preserving involution of the
  whole configuration, followed by the same exact local optimisation. The mirror branch is
  a *global* move and therefore carries no locality obligation; the local optimisation
  changes letters only at the two comm-s2 qubits and therefore leaves every other qubit's
  F3 contribution and every other block's external letters untouched.
- **A3 (sub-case composition).** The two QG-7c declared-open sub-cases — **double pinners**
  (two other blocks using σ_b) and **comm-s2 chains** (the pinning block itself comm-s2) —
  are folded into A1/A2 by enumerating them as *geometries* of the same lemma, and closed
  by induction on the number of comm-s2 blocks: each application of the lemma removes
  exactly one comm-s2 block at Δ ≤ 0 and never creates a new one, so the induction
  terminates at a comm-s2-free configuration, which the QG-7c closed chain
  (M1/T1/T2/T3/T5) maps into D+ ∪ B′ ∪ B″ at Δ ≤ 0.

No other attack is admitted. If the frozen attack set leaves a residue, the residue is
serialized with its census and the lane terminates PARTIAL.

## Imported committed machinery (UNMODIFIED)

`max_r6_p10_candidate_blind_frame_optimizer`, `max_r6m_exact_three_tare2_shared_factor_dp`,
`max_r6o_enlarged_tag_donor_closure`, `max_r6p_weight2_frame_donor_closure` (with the
committed runtime guard extension `r6p.EXPECTED_PAIR_COUNTS.setdefault(4, ...)` installed
by importing `qg7_bprime_completeness`, exactly as QG-7/QG-7b/QG-7c declared),
`max_r6s_all_n_composition`, `qg5b_exact_forecaster` (f_B′), `qg7_bprime_completeness`,
`qg7b_hybrid_family` (f_B″), and **`qg7c_classification`** — from which `m1_inventory`,
`t1_prune`, `t3_consolidation`, `t4a_unpinned`, `t4b_pinned`, `t5_home_merge`, `mg_gauge`
and `bind_tables` are called unmodified to re-derive the inherited lemmas and the T4b
census inside this run. The only randomness is the frozen dense-random control stream.

## Cost model (bound, not re-defined)

`cost = Σ_j (m_j0·wt(f_j0) + m_j1·wt(f_j1)) + 2·wt(s) − 18 + Σ_{k,q} F3`, per-position
`F3(a,b,c) = 1 if a==b==c≠0 else wt(a)+wt(b)+wt(c)`, `(m_j0,m_j1) ∈ {(2,4),(4,2)}` by the
per-block central. Writing `uanti(w0,w1) = 4·(min−1) + 2·(max−1)` for the central-optimal
per-block frame charge, `cost = Σ_j uanti_j + 2·wt(s) + Σ_{j,k} wt(t_jk·f_jk) − 2·(#triple
collisions)`. G1 binds this to `r6s.config_cost` and to the frozen `r6p` block bases on a
complete slice; the per-block **target permutation** (which of the block's two targets is
carried by its label-0 frame) is a configuration degree of freedom of the committed
`r6p.dxx_search` and is treated as such throughout.

## Geometry inventory (complete, derived from the receipt-bound M1 lemma)

Gauge (all cost-invariant, each separately receipt-bound or machine-checked in G2/G3):
labels (0,1) WLOG (MG); per-qubit letter permutations fix `σ_b = σ_a = Z`; the residual
{X,Y} transposition at each of the two qubits fixes the comm-s2 comm letters
`R_b = R_a = X`, hence its anti letter `w = Y` at `a`.

By M1 (262,144-case complete domain, receipt-bound: irreducible blocks are exactly
anchored / phantom / comm-s2) each of the two other blocks stands in exactly one of the
following **roles** relative to the comm-s2 pair `{b,a}`; `p,u,v ∈ {X,Y}`:

| role | letters at b | letters at a | external profile (w0,w1,sy0,sy1,x) |
|---|---|---|---|
| `OUT` | — | — | irrelevant (never rewritten) |
| `ANCH_B(p)` | (Z, p) | — | (0,0,0,0,0) |
| `ANCH_A(p)` | — | (Z, p) | (0,0,0,0,0) |
| `BORROW_B(p)` | (0, p) | — | (1,1,0,0,1) |
| `BORROW_A(p)` | — | (0, p) | (1,1,0,0,1) |
| `CS2_BA_ANTIA(u,v)` | (u, 0) | (v, third letter ∉{Z,v}) | (0,0,0,0,0) |
| `CS2_BA_ANTIB(u,v)` | (u, third letter ∉{Z,u}) | (v, 0) | (0,0,0,0,0) |
| `CS2_B_ANTIOUT(u)` | (u, 0) | — | (1,1,1,1,1) |
| `CS2_B_ANTIB(u)` | (u, third ∉{Z,u}) | — | (1,0,1,0,0) |
| `CS2_A_ANTIOUT(v)` | — | (v, 0) | (1,1,1,1,1) |
| `CS2_A_ANTIA(v)` | — | (v, third ∉{Z,v}) | (1,0,1,0,0) |

(the external profile records, for the block's label-0 and label-1 frames, the frame weight
carried outside `{b,a}`, the symplectic product of that outside part with the tag, and the
outside part of the block's own inter-frame symplectic product). The **unordered pair** of
roles of the two other blocks is the geometry; its size is recorded in the RESULTS as a
gate. The geometry list covers, by construction and with no sampling:
the **unpinned** sector (neither other block touches `b`), the **pinned single-pinner**
sector (exactly one does), the **double-pinner** sub-case (both do) and the **comm-s2
chain** sub-case (a role beginning `CS2_`) — i.e. both QG-7c declared-open sub-cases.

## New machine lemmas (complete local domains; sizes are gates)

- **G2 — mirror identity (MG re-derivation, all n).** Machine-check that swapping every
  block's two frames, its two targets and its central, and flipping the label orientation,
  leaves the cost formula invariant term-by-term: complete domain over one qubit's six
  frame letters × six target letters (`4^6 × 4^6 = 16,777,216` cases) for the F3 branch
  exchange, plus the complete `uanti` table (`3 × 3` weight pairs) and the label flip.
  GATE: zero failures. QG-7c's `mg_gauge` is additionally re-run unmodified and bound.
- **G3 — gauge normalisation.** Complete check that per-qubit letter permutations act as
  cost-preserving relabelings of (frames, tag, targets): complete domain over one qubit's
  six frame letters × six target letters × all 6 letter permutations
  (`4^6 × 4^6 × 6`, evaluated as the `16,777,216`-case F3 identity per permutation).
  GATE: zero failures.
- **P1 — pinned/unpinned comm-s2 domination lemma (the last link).**
  For every geometry `G` the complete domain is the **raw target letters of all three
  blocks in both branches at the two comm-s2 qubits**: `4^6 = 4096` states at `b` ×
  `4^6 = 4096` states at `a` = **16,777,216 states per geometry** (no sampling; the whole
  product is enumerated as a dense array). For each state the lemma computes

      Δ(state) = min( Δ_direct(state), Δ_mirror(state) ) ,

  `Δ_direct = min over ALL comm-s2-free reassignments Y` of `cost(Y) − cost(X)`, where `Y`
  ranges over: both tag letters `σ′_b, σ′_a ∈ {I,X,Y,Z}` and, for each of the three blocks,
  every assignment of its four local frame letters `(L0b,L1b,L0a,L1a) ∈ 4^4` subject to
  (i) the two label constraints including the block's external symplectic contribution,
  (ii) the inter-frame anticommutation including its external contribution, (iii) global
  frame weights `1 ≤ w ≤ 2` including its external weight, (iv) the comm-s2 block is **not**
  comm-s2 in `Y`, and (v) no other block is comm-s2 in `Y` unless it already was in `X`
  (so the comm-s2 count strictly decreases and never increases);
  `Δ_mirror` is the identical construction applied to the **MG mirror** of `X` and read at
  the branch-swapped state, which by G2 has exactly `cost(mirror(X)) = cost(X)`.
  Costs are compared through the exact local difference
  `Δ = Σ_j [uanti_j(Y) − uanti_j(X)] + 2[wt(σ′)|_{b,a} − wt(σ)|_{b,a}] + ΔF3(b) + ΔF3(a)`;
  every other qubit is untouched, so `Δ` is the exact global cost difference.
  **GATE: zero states with Δ > 0, over every geometry.** A nonzero residue is censused
  exactly (per geometry, per Δ value, verbatim rows capped and the cap disclosed) and
  forces a PARTIAL terminal.
- **P2 — QG-7c T4b census dispatch (hostile gate).** `qg7c_classification.t4b_pinned()` is
  re-run unmodified inside this lane; its census must reproduce **verbatim** (domain
  536,870,912; 135,604 failures; worst Δ = +2; the six per-(case, ja, Δ) counts). Every
  censused pattern is then dispatched individually: each failing pattern is decoded into
  its (case, ja, R_b, R_a, p, coreB, envB, coreA, envA) coordinates, mapped into the P1
  geometry class and P1 state that contains it, and recorded as **closed by P1** (naming
  the attack) or **listed open**. The per-pattern dispatch counts must sum exactly to the
  census total. The 40 verbatim census rows are additionally dispatched **explicitly**, by
  recomputing P1's Δ at their exact P1 coordinates and serializing it.
- **P3 — hostile realization arm (counterexample-first, referee-confirmed).**
  (C1) Every one of the 40 verbatim T4b census rows is realized as a concrete instance at
  n=3 (first 40) and n=4 (first 10) by the committed QG-7c realization map
  (`qg7c_classification._realize_row`, imported unmodified). (C2) A frozen dense-random
  control: n=3, 120 instances, seed 20260901; n=4, 30 instances, seed 20260902 (uniform
  nonzero targets). (C3) A frozen **P1-extremal** panel: from the P1 domain, the states
  attaining the smallest `cost(X) − Δ` margin (worst-case first, frozen tie-break by state
  index), realized at n=2, n=3 and n=4, ≤ 60 instances (cap disclosed).
  For every C1/C2/C3 instance: `C_Dxx = r6p.dxx_search` (with witness), `C_D+`
  (`max_weight=1`), `f_B′ = qg5b.bprime_family_min`, `f_B″ = qg7b.bsecond_family_min`;
  hard **sandwich assertions** `C_Dxx ≤ C_D+`, `C_Dxx ≤ f_B′`, `C_Dxx ≤ f_B″` on every
  finite value; `r6p.verify_dxx_witness` refereed on 100% of rows (no sampling); any gap
  row (`C_Dxx < min(C_D+, f_B′, f_B″)`) additionally replayed through
  `r6o.dp_cost_frozen_configs` + `r6m.exact_r6m_matching` and the B′/B″ witness verifiers,
  and serialized verbatim (cap 50, disclosed). A replay-confirmed gap row is the
  `QG7D_LINK_REFUTED` terminal and is serialized verbatim.

**Reduction order / termination (the assembled argument).** Measure
`(cost, #comm-s2, wt(s) beyond 2, total frame support, #distinct empty homes)`. R6S gives
`C_DP == C_D++` (all n); MG fixes the label orientation; the receipt-bound closed moves
(R6S support-≥3, L1, L2, Lemma-E, L4a, T1) drive any configuration to an irreducible one;
M1 says its blocks are anchored/phantom/comm-s2; **P1** removes one comm-s2 block per
application at Δ ≤ 0 without creating another, so induction on `#comm-s2` terminates at a
comm-s2-free irreducible configuration; T1/T2/T3 then bound and consolidate the tag, and
T5 + M1 map the terminal shapes into `D+ ∪ B′ ∪ B″`. With the sandwich
`C_D++ ≤ min(C_D+, f_B′, f_B″)` (each family is a sub-family of D++) this yields equality.

## Receipt bindings (exact values, gated)

- **QG-7c** `QG7C_CLASSIFICATION_RESULTS.json`: terminal `QG7C_PARTIAL__L4B_OPEN`;
  authority `ORIONQG_QG7C_PARTIAL__L4B_COMM_S2_PINNED_SECTOR_OPEN__L4C_CLOSED_CONDITIONAL__NOT_R6`;
  `result_digest` `0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6`;
  `protocol_sha256` `14129aea3894bff276d3b4ef625640b1563e3b7b2299ac12ca82d578d1592646`;
  M1 raw domain 262,144 with irreducible shape counts {anchored 288, phantom 864,
  comm_s2 864}; T1 domain 12,288; T3 domain 14,680,064 with zero failures; T4a domain
  134,217,728 with worst Δ = 0; T4b domain 536,870,912 with 135,604 failures at worst
  Δ = +2 and census `{PA_ja0_delta1: 97072, PA_ja0_delta2: 2376, PA_ja1_delta1: 3600,
  PP_ja0_delta1: 30500, PP_ja0_delta2: 440, PP_ja1_delta1: 1616}`; T5 cases 1,158;
  the two declared-open sub-cases verbatim.
- **QG-7b** `QG7B_HYBRID_FAMILY_RESULTS.json`: terminal
  `QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS`, authority as committed,
  `result_digest` as committed, 64/64 QG-7 witnesses covered.
- **QG-7** `QG7_BPRIME_COMPLETENESS_RESULTS.json`: terminal
  `QG7_FOURTH_SUPPORT2_REGIME_FOUND`; L1 domains {N1: 768, N5: 27216}; L2 domains
  {N3: 8, N0_lemma_e: 18432, N0_lemma_b: 43688}; L4a N7_checked = 1440; Lemma-E domain
  18,432 with max ΔF3 = 2.
- **R6S** `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`: authority prefix
  `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED`; `r6s.bind_tables()` all true.
- **Tables (G1)**: `MY_LM/MY_SY/MY_LW/MY_F3` equal to the frozen `r6m` tables, `r6p.F3`
  equal to `MY_F3`, pair counts `{1: 6, 2: 120, 3: 666, 4: 1968}`.

## Terminals (frozen; no post-outcome changes)

- **`QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE`** — requires ALL of: G1/G2/G3 pass;
  M1/T1/T3/T4a/T5/MG re-derived with the exact committed values; **P1 residue exactly zero
  over every geometry of the complete inventory** (which includes both QG-7c declared-open
  sub-cases); P2 census reproduced verbatim and every one of the 135,604 patterns
  dispatched closed; P3 zero gap rows with 100% referee coverage and all sandwiches
  asserted; every receipt binding exact. Authority
  `ORIONQG_QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE__COMM_S2_PINNED_SECTOR_CLOSED_BY_
  JOINT_EXCHANGE_AND_MIRROR_DOMINATION__NOT_R6`.
- **`QG7D_PARTIAL__<residue>_OPEN`** — any P1 residue, or any censused pattern left
  undispatched, with P3 empty of gap rows and every gate otherwise passing. `<residue>` is
  the frozen residue tag: `P1_RESIDUE` (P1 leaves failing states) or `CENSUS_RESIDUE`
  (P1 closes but some censused pattern is not dispatched). Authority
  `ORIONQG_QG7D_PARTIAL__<residue>_OPEN__NOT_R6`.
- **`QG7D_LINK_REFUTED`** — a referee-recomputed instance with
  `C_Dxx < min(C_D+, f_B′, f_B″)`, replay-confirmed through the independent DP referee and
  the B′/B″ witness verifiers, serialized verbatim. Authority
  `ORIONQG_QG7D_LINK_REFUTED__PINNED_COMM_S2_FIFTH_CONFIGURATION_WITNESS_REFEREE_
  CONFIRMED__NOT_R6`.
- **`QG7D_CANNOT_CHECK`** — any binding, domain-size, sandwich, referee or integrity gate
  failure. Authority `ORIONQG_QG7D_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6`.

## Gates

- **G1** tables and pair counts bound.
- **G2** mirror identity: complete `16,777,216`-case F3 exchange domain, zero failures;
  QG-7c `mg_gauge` re-run and `holds` true.
- **G3** letter-permutation gauge: complete domain per permutation, zero failures.
- **G4** M1 re-derived unmodified: raw domain 262,144, zero unclassified, shape counts
  exactly {288, 864, 864}.
- **G5** T1/T3/T4a/T5 re-derived unmodified with the exact committed domain sizes and
  failure counts.
- **G6** P1: every geometry's state domain size exactly `16,777,216`, recorded; total
  recorded; **residue count recorded**; theorem terminal requires residue 0.
- **G7** P2: the T4b census reproduces the committed values verbatim; the per-pattern
  dispatch counts sum exactly to 135,604.
- **G8** P3: 100% referee coverage (`dxx_witness_rows == rows`), zero sandwich failures,
  zero replay failures; gap rows (if any) replay-confirmed.
- **G9** receipt bindings QG-7c / QG-7b / QG-7 / R6S all exact.
- **G10** no silent truncation: every cap disclosed in the RESULTS (P1 residue verbatim cap
  200; census verbatim cap 40 inherited; gap verbatim cap 50; C1 caps 40 + 10; C3 cap 60).

## Runtime and reproducibility

Runtime cap **1500 s per run (< 25 min)**; timing excluded from the canonical stdout line
and from the result digest (R6P convention: timing lives in the RESULTS `timing` section
and on stderr only). Two runs; the canonical stdout line
`ORIONQG_QG7D_LAST_LINK=<canonical json>` and RESULTS-minus-timing must be byte-identical.
Independent pure-primitive verifier
`development/orion-qg-regime-geometry/qg7d_generic_verify.py` re-derives the P1 lemma from
first-principles primitives (no analyzer / orion-q / qg7c imports, deliberately different
internals — an independent brute-force local optimiser over an independently rebuilt
configuration space), re-checks the geometry inventory, the mirror identity, the census
dispatch arithmetic, the terminal selection and the result digest; prints ACCEPT/REJECT.

## Design-phase disclosure (exploration, not part of the outcome)

Pre-freeze exploration, disclosed in full: (i) re-derivation of the QG-7c T4b census and a
structural profile of its failing patterns (they are protected by triple collisions or
all-identity positions at the two label-0 positions); (ii) a complete n=2 configuration
sweep, built independently and checked against `r6p.dxx_search`, used to discover that the
per-block **target permutation** is a configuration degree of freedom that T4b's menu did
not exploit and that the comm-s2 shape never strictly pays once it is admitted;
(iii) prototype timings of the P1 kernel; (iv) hand-built swap-penalising n=3 embeddings
evaluated through the committed exact machinery (zero gap rows). The frozen constructions
above are final; the official runs compute every domain from scratch.

## Stop rules and scope

Inherited verbatim from the wave-1 packet and charter. This lane proves nothing about
other objectives, other grammars, rotation counts, or any chemistry subject; no novelty
credit; no donor novelty credit; no R6 authority; NOT_R6.

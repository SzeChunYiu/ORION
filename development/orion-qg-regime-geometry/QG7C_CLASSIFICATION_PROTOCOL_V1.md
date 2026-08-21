# QG-7c classification-endgame protocol V1 (FROZEN BEFORE OUTCOME)

Lane: ORION-QG QG-7c — the classification endgame (wave-2 keystone successor
registered in `QG_WAVE2_RECORD.md`). Base revision
`67845e5bd81e2eb23eb8dd86a9159f53bfbc63e4`. Authority ceiling **NOT_R6**.
No chemistry data is read; the protected stretched-N2 subject
(`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/...`) is never touched.

## Question

Close the two obligations frozen verbatim by QG-7b's Q3 delimitation
(`QG7B_HYBRID_FAMILY_RESULTS.json`, section `q3_toward_all_n`):

- **L4b (consolidation)**: for each still-open feasible weight-≤2-Tag shape
  class — tag-supported phantoms, double-borrow phantoms, cyclic borrows,
  l1-phantom-at-home — prove by complete local-domain enumeration (with
  full-environment F3 tables, never per-block sums) that every such
  configuration is cost-dominated by a member of D+ ∪ B′ ∪ B″, or exhibit a
  referee-confirmed instance where the open shape strictly beats all three
  families.
- **L4c (tag-weight bound)**: prove an exchange lemma showing weight-≥3 Tags
  never strictly pay under the unit support-count objective (the lemma must
  handle frame-supported tag letters, which L4a's out-of-support prune does
  not), or exhibit a referee-confirmed weight-3-Tag instance beating
  min(C_D+, f_B′, f_B″).

If BOTH close, combined with QG-7's L1/L2 (all-n), L3, L4a, and R6S
(C_DP == C_D++ all n), `C_DP == min(C_D+, f_B′, f_B″)` becomes an all-n
theorem for unit-cost TARE.

## Imported committed machinery (UNMODIFIED)

`max_r6_p10_candidate_blind_frame_optimizer`, `max_r6m_...dp`,
`max_r6o_enlarged_tag_donor_closure`, `max_r6p_weight2_frame_donor_closure`
(with the committed runtime guard extension
`r6p.EXPECTED_PAIR_COUNTS.setdefault(4, r6s.PAIR_COUNTS_SUPPORT2[4])`, exactly
as QG-7/QG-7b declared), `max_r6s_all_n_composition`, `qg5b_exact_forecaster`
(f_B′), `qg7_bprime_completeness`, `qg7b_hybrid_family` (f_B″). No repository
file is modified. The only randomness is the frozen dense-random control panel
stream (seeds below); every lemma domain is deterministic and complete.

## Configuration framework (definitions used by every lemma)

A support-≤2 configuration is `(t6, frames6, s, centrals)` feasible under
`r6s.config_labels` with every frame Pauli of support ≤ 2, costed by
`r6s.config_cost`. By the committed R6S theorem (receipt-bound), the
unrestricted optimum C_DP equals C_D++ = min over support-≤2 configurations
(= `r6p.dxx_search`). Cost decomposition (from the committed formula):
`cost = Σ_j (m_j0·wt(f_j0) + m_j1·wt(f_j1)) + 2·wt(s) − 18 + Σ_{k,q} F3`,
with per-position `F3(a,b,c) = 1 if a==b==c≠0 else wt(a)+wt(b)+wt(c)`.
Facts used and re-checked: the tag enters only through `2·wt(s)` and the six
symplectic label constraints; branch sums are symmetric; per-qubit letter
permutations and qubit permutations are cost-invariant.

**Gauge (MG)**: labels are WLOG (0,1) — the mirror map (swap the two frames,
the two targets, and the central bit in every block) is a cost-preserving
involution exchanging the label orientations. Machine check: the complete
n=1 domain — every feasible n=1 configuration (all 3-letter tags × all
ordered anticommuting letter-pair triples with common labels × 8 centrals)
× all 4096 target 6-tuples — mirror cost equality, plus binding of the
lemma-local cost formula to `r6s.config_cost` on a complete sub-slice
(all feasible n=1 configs × the first 64 target tuples in frozen order).
"Comm frame" of a block always names the frame with ⟨s,·⟩ = 0, "anti frame"
the ⟨s,·⟩ = 1 one.

**Reduction moves already closed all-n (receipt-bound, reused not re-proven)**:
R6S support-≥3 exchange; L1 (2,2)-block elimination (N5 = 27,216 / N1 = 768
complete domains); L2 orientation (N3 = 8, N0_e = 18,432, N0_b = 43,688);
Lemma-E zeroing of class-(0,0) qubits on support-2 frames (18,432-case
domain, max ΔF3 = 2 ≤ refund); L4a out-of-frame-support tag prune (N7 =
1,440 checks, exact refund 2). An **irreducible** configuration is one where
none of these moves and none of the new moves below applies.

## New machine lemmas (complete local domains; sizes are gates)

- **M1 — irreducible block-shape inventory.** Complete domain: one block's
  two frames over 3 qubits (letters `4^3 × 4^3`) × tag letters at those
  qubits (`4^3`) = **262,144 raw cases**; filter: nonzero frames, supports
  ≤ 2, pairwise anticommutation, labels (0,1) (local sums are exact because
  frames vanish elsewhere); classify reducible cases ((2,2) shape → L1;
  class-(0,0) qubit on a support-2 frame → Lemma E). ASSERT: every
  irreducible feasible block is exactly one of
  (a) **anchored**: both frames weight-1 on one common qubit q, comm letter
      = σ_q ≠ 0, anti letter ≠ σ_q;
  (b) **phantom**: anti frame support-2 on {b,h}, comm frame weight-1 at h,
      σ_b ≠ 0 anticommuting the anti letter at b (borrow ON the tag),
      σ_h = 0 (home OFF the tag), home letters distinct;
  (c) **comm-s2**: comm frame support-2 on {b,a}, anti frame weight-1 at a,
      σ nonzero and anticommuting the comm letters at BOTH b and a, anti
      letter = the third letter ∉ {σ_a, comm_a};
  and no other shape occurs. Corollaries asserted by the same enumeration:
  tag-supported phantoms (σ ≠ 0 at the home) and l1-phantom-at-home are
  infeasible-or-reducible; every borrow qubit carries a tag letter, every
  home carries none, hence **cyclic borrows cannot occur** in irreducible
  configurations. This closes three of the four L4b shape classes outright.
- **T1 — commuting-tag prune.** Domain: σ_q ∈ {X,Y,Z} × six frame letters
  ∈ `4^6` = **12,288 cases**. ASSERT: if no frame letter at q anticommutes
  σ_q, zeroing σ_q preserves every label contribution exactly and refunds 2
  (F3 untouched). Extends L4a to frame-supported but non-anticommuted tag
  letters.
- **T2 — tag occupancy bound.** Over the M1 inventory: the set of qubits
  where a block's letters anticommute the tag has size exactly 1 (anchored:
  its qubit; phantom: its borrow) or 2 (comm-s2: both qubits). ASSERT by
  counting over every irreducible inventory row. Corollary: after T1,
  wt(s) ≤ 3 + #comm-s2; with no comm-s2 block, wt(s) ≤ 3, and wt(s) = 3
  forces exactly one block per tag qubit.
- **T3 — weight-3 consolidation (the L4c exchange).** Setting: wt(s) = 3,
  no comm-s2, ≥ 1 phantom (all-anchored configs are in D+ with any tag),
  blocks 0,1,2 at tag qubits 0,1,2, per-qubit gauge σ ≡ Z. Complete domain:
  per tag qubit the state (own-block slot-1 target letter `tw` ∈ 4, its
  anti/borrow letter L ∈ {X,Y}, the other two blocks' raw slot-1 letters
  u,v ∈ 4) = 128 states/qubit; **7 shape combinations × 128³ = 14,680,064
  cases**. (Branch-0 letters never change under any menu move: anchored →
  phantom conversions keep the comm letter in place as m0 = σ; phantom
  re-borrows keep home letters; hence the branch-1-only domain is complete.)
  Menu (each move drops ≥ 1 tag letter):
  (i) single retarget of block i's label point to qubit j ≠ i — anchored:
  convert in place to phantom(home=i, borrow=j), m1 ∈ {X,Y}, arrival letter
  ℓ′ ∈ {X,Y}, structural 0 (+2 raw − 2 tag); phantom: re-borrow, removal at
  i, structural −2; result is B″-shaped (wt 2).
  (ii) consolidation at j — both other blocks retarget to j; σ_j re-chosen
  freely when block j is a phantom (σ′ ∈ {X,Y,Z}, all borrow letters
  anticommute σ′), forced Z when block j is anchored (own anti re-letter
  c ∈ {X,Y} allowed); structural −4 + 2·(#anchored moved); result is
  B′-shaped (wt 1).
  GATE: **zero cases** with min-over-menu Δ > 0. (Design probe: passes with
  worst Δ = 0.)
- **T4a — comm-s2 elimination, unpinned sector.** Setting: a comm-s2 block
  at {b,a}, gauge σ_b = σ_a = Z, with **jb = 1**: no other block's frame
  letters at b (M1 ⇒ then b hosts only our letters). Complete domain:
  (R_b, R_a) ∈ {X,Y}² × our four target letters `4^4` × ja ∈ {0,1} ×
  full adversarial env (two letters per position, `16^4` over the four
  positions (0,b),(1,b),(0,a),(1,a)) = **2,048 cores × 65,536 envs =
  134,217,728 cases**. Menu: with and without sigma-swap — anchored@a
  (c ∈ {X,Y}), anchored@b (c ∈ {X,Y}), phantom(home=b, borrow=a) (m0 ∈ 3,
  m1 ≠ m0, ℓ ∈ {X,Y}; σ_b dropped, −2), and when ja = 1 also
  phantom(home=a, borrow=b) (σ_a dropped, −2; this includes the exact
  role-swap that turns the comm-s2 into a phantom with all four letters
  preserved across branches). Structural constants: raw 8 → 6 for anchored
  (−2), 8 → 8 for phantom; tag prune −2 per freed letter (a freed when our
  new shape vacates it and ja = 1). GATE: **worst Δ ≤ 0 over the whole
  T4a domain**. (Design probe: worst = 0.)
- **T4b — comm-s2 pinned sector (jb = 0), honest census.** Setting: one
  other block pins σ_b — case PA (anchored@b: c2 ∈ {X,Y}, its slot-1 target
  at b `t2_1b` ∈ 4 in-core) or case PP (phantom borrowing at b: ℓ2 ∈ {X,Y},
  `t2_1b` ∈ 4) — × its slot-1 target letter at a `t2_1a` ∈ 4 × ja ∈ {0,1}
  × our core as in T4a × remaining env letters. Menu: all T4a singles
  (jb-moves excluded), pinner in-place re-letter (c2′/ℓ2′) alone and
  combined with our singles, and the joint move J (our
  phantom(home=b, borrow=a) full letter menu × pinner conversion-in-place
  to phantom(home=b, borrow=a) with m1₂ ∈ {X,Y}, ℓ₂ ∈ {X,Y} for PA /
  re-borrow b→a with ℓ₂′ ∈ {X,Y} for PP; σ_b dropped). Domain sizes are
  serialized in the RESULTS. NO zero-failure gate: the exact failing-case
  census (count per (case, ja, Δ), capped verbatim at 40 rows) is the
  deliverable; a nonzero census leaves the double-borrow (comm-s2) class
  **PARTIALLY_CLOSED** (unpinned sector closed by T4a, pinned sector open).
  Sub-cases declared OPEN without a domain run (disclosed, not gated):
  two pinners at b; a pinning block that is itself comm-s2 (mutually pinned
  multi-comm-s2 chains).
- **T5 — empty-home merge (grammar pinch).** Phantom homes at all-identity
  ("empty") qubits merge onto ≤ 2 shared representatives without cost
  increase: complete domain over 1–3 phantoms' home letters (m0, m1) and
  sharing patterns at up to 3 empty qubits, replacement letters chosen
  all-equal per branch. ASSERT: merged per-branch F3 total ≤ original in
  every case. With M1/T2 this maps every terminal shape into the committed
  grammars: all-(1,1) → D+ (`r6p.dxx_search max_weight=1`, free tag);
  wt-1 + phantom → B′ (`qg5b.bprime_family_min` pool); wt-2 + phantom → B″
  (`qg7b.bsecond_family_min` pool, ≤ 2 empty representatives).

**Reduction order / termination**: measure (cost, #comm-s2, wt(s) beyond 2,
total frame support, #distinct empty homes) — every move above strictly
decreases the measure lexicographically at non-increasing cost; terminal
irreducible shapes are exactly D+/B′/B″-shaped except the T4b-open sector.

## Arm C — hostile realization search (counterexample-first)

- **C1 (pinned comm-s2 realizations)**: from the T4b failing census in
  frozen order, take the first ≤ 40 cores; for each, realize the argmax
  (first-index tie-break) worst environment as a concrete instance at n=3
  (and an n=4 variant with a spare qubit for the first ≤ 10), assembling
  targets deterministically from the core/env letters (spare-qubit letter Z
  keeps every target nonzero). ≤ 50 instances total.
- **C2 (dense-random control)**: frozen seeds — n=3: 120 instances, seed
  20260827; n=4: 30 instances, seed 20260828 (uniform nonzero targets).
- Every C1/C2 instance: `C_Dxx` (r6p, with witness), `C_D+`
  (max_weight=1), `f_B′`, `f_B″`; hard sandwich assertions
  `C_Dxx ≤ C_D+`, `C_Dxx ≤ f_B′`, `C_Dxx ≤ f_B″` (finite values);
  referee `r6p.verify_dxx_witness` on every row; on any gap row
  (`C_Dxx < min(C_D+, f_B′, f_B″)`) additionally `r6o.dp_cost_frozen_configs`
  + `r6m.exact_r6m_matching` replay and B′/B″ witness verifiers; gap rows
  serialized verbatim (cap 50).

## Receipt bindings (exact values, gated)

R6S authority prefix `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED`;
QG-7 receipt: authority/terminal/protocol-sha as committed, L1 domains
{N1: 768, N5: 27216}, L2 domains {N3: 8, N0_lemma_e: 18432, N0_lemma_b:
43688}, L4a N7_checked = 1440, open-shape list verbatim; QG-7b receipt:
terminal `QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS`, authority and
`result_digest` as committed, 64/64 witnesses covered, `q3_toward_all_n`
naming exactly the L4b/L4c obligations addressed here; table bindings
(`r6s.bind_tables`, F3 equality, pair counts {1:6, 2:120, 3:666, 4:1968}).

## Terminals (frozen; no post-outcome changes)

- `QG7C_FOUR_CONFIGURATION_CLASSIFICATION_ALL_N_MACHINE_CHECKED` — requires
  ALL of: MG/M1/T1/T2/T5 hold with exact domain sizes; T3 zero failures;
  T4a worst ≤ 0; **T4b zero failures AND its declared-open sub-cases
  proven empty or closed**; Arm C zero gap rows; all bindings pass. (A
  single unresolved shape class forces a PARTIAL terminal.)
  Authority `ORIONQG_QG7C_FOUR_CONFIGURATION_CLASSIFICATION_ALL_N_MACHINE_
  CHECKED__L4B_L4C_CLOSED_WITH_R6S__NOT_R6`.
- `QG7C_TRADE_BASIS_EXTENDED` — a referee-confirmed Arm-C instance with
  `C_Dxx < min(C_D+, f_B′, f_B″)` (replay-confirmed, serialized verbatim).
  Authority `ORIONQG_QG7C_TRADE_BASIS_EXTENDED__FIFTH_CONFIGURATION_
  WITNESS_REFEREE_CONFIRMED__NOT_R6`.
- `QG7C_PARTIAL__L4B_OPEN` — MG/M1/T1/T2/T3/T4a/T5 all pass (so L4c closes
  conditional on L4b's comm-s2 elimination, and three L4b classes close
  all-n), but the T4b census is nonzero (or its declared-open sub-cases
  remain) and Arm C is empty. Authority `ORIONQG_QG7C_PARTIAL__L4B_COMM_S2_
  PINNED_SECTOR_OPEN__L4C_CLOSED_CONDITIONAL__NOT_R6`.
- `QG7C_PARTIAL__L4C_OPEN` — T4a/T4b close fully but T3 fails, Arm C empty.
  Authority `ORIONQG_QG7C_PARTIAL__L4C_OPEN__NOT_R6`.
- `QG7C_PARTIAL__L4B_L4C_OPEN` — both T3 and T4 leave failures, Arm C
  empty. Authority `ORIONQG_QG7C_PARTIAL__L4B_L4C_OPEN__NOT_R6`.
- `QG7C_CANNOT_CHECK` — any binding, domain-size, sandwich, referee, or
  integrity gate failure. Authority
  `ORIONQG_QG7C_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6`.

## Gates

G1 tables/pair-counts bound; G2 QG-7 receipt bound (exact values above);
G3 QG-7b receipt bound (incl. q3 obligations verbatim); G4 MG mirror
invariance zero failures + cost-formula binding; G5 M1 inventory complete
(raw size 262,144 recorded) with zero unclassified irreducible blocks;
G6 T1/T2/T5 zero failures with recorded domain sizes; G7 T3 domain complete
(7 × 128³) — failure count recorded (zero required for L4c closure);
G8 T4a worst ≤ 0 over the full recorded domain; G9 Arm C: every row
sandwich-asserted and dxx-witness-refereed (100%, no sampling), gap rows
replay-confirmed before the EXTENDED terminal; G10 no silent truncation
(every cap disclosed in the RESULTS: census verbatim cap 40, gap verbatim
cap 50, C1 instance caps 40+10).

## Runtime and reproducibility

Runtime cap **1500 s per run** (< 25 min), timing excluded from canonical
stdout and the result digest (R6P convention: timing in the RESULTS file
timing section and stderr only). Two runs; canonical stdout line
`ORIONQG_QG7C_CLASSIFICATION=<canonical json>` and RESULTS-minus-timing must
be byte-identical. Independent pure-primitive verifier
`development/orion-qg-regime-geometry/qg7c_generic_verify.py` re-derives
MG/M1/T1/T2/T3/T4a/T5 from primitives (no analyzer/orion-q imports), rechecks
census digests, Arm-C rows, terminal selection, and the result digest;
prints ACCEPT/REJECT.

## Design-phase disclosure

Pre-freeze exploration (disclosed, not part of the outcome): shape census of
the committed QG-7 witnesses (all 64 are B″-shaped); dense-random identity
probes (n=2: 400, n=3: 300, n=4: 60 — zero gaps); hand-built aligned
instances for the wt-3 and comm-s2 shapes (all dominated by family members
through borrow-cancellation restructures); prototype domain runs that fixed
the T3/T4a menus (T3 earlier single-menu failures closed by the own-anchor
re-letter and free-σ′ consolidation enrichments; T4 v1–v3 iterations
delimited the pinned sector). The frozen menus above are final; the official
runs compute every domain from scratch.

## Stop rules and scope

Inherited verbatim from the wave-1 packet and charter. This lane proves
nothing about other objectives, other grammars, rotation counts, or any
chemistry subject; no novelty credit; NOT_R6.

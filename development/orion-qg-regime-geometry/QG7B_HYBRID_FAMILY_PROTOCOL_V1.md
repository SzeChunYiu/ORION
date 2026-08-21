# QG-7b protocol V1 — the frozen hybrid-family closed form B″

Status: FROZEN BEFORE OUTCOME. This protocol is written and frozen before any
outcome under it is computed. No post-outcome gate, cap, family, panel or
terminal change is permitted. Charter: `PROGRAMME_CHARTER_V1.md` (issue #740).
Registered successor entry: `QG_WAVE2_RECORD.md` § "Registered successor"
(QG-7b). Base revision: `e633a4619624de01bec639a804dce02ca0be277a`.

Lane: ORION-QG QG-7b — the closed form for QG-7's fourth support-two regime.
Analyzer: `research/extensions/orion-qg/qg7b_hybrid_family.py` (new file; all
committed machinery imported UNMODIFIED). Results:
`research/extensions/orion-qg/QG7B_HYBRID_FAMILY_RESULTS.json` plus the
canonical stdout line `ORIONQG_QG7B_HYBRID_FAMILY=<canonical json>`. Generic
verifier: `development/orion-qg-regime-geometry/qg7b_generic_verify.py`
(independent primitive re-derivation, prints ACCEPT/REJECT).

Authority ceiling: **NOT_R6** on every branch. No novelty credit, no donor
credit, no chemistry claim. No chemistry data is read anywhere in this lane.
The protected file
`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`
is never read (nothing in this lane opens any chemistry file at all).

## Frozen question

QG-7 (receipt `QG7_BPRIME_COMPLETENESS_RESULTS.json`, authority
`ORIONQG_QG7_FOURTH_SUPPORT2_REGIME_FOUND__HOSTILE_SEARCH_WITNESS_REFEREE_CONFIRMED__NOT_R6`,
digest `159d174fbb17a66aeb39a3efb53cf4c505f0a86ce8ef1dff76337d00837d152f`)
found 64 fourth-regime witnesses with `C_D++ < min(C_D+, f_B′)` (all gap −1),
mechanism: **weight-2-Tag + phantom hybrid**. QG-7b freezes an enlarged family
B″ admitting exactly that mechanism (as delimited by QG-7's L4a
non-consolidatability classification) and tests, on the frozen domains below:

    C_DP == C_D++ == min(C_D+, f_B′, f_B″)          (the QG-7b identity)

Either the identity holds everywhere on the verified domains
(terminal `QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS`), or a single
referee-confirmed instance with `C_D++ < min(C_D+, f_B′, f_B″)` exists
(terminal `QG7B_FIFTH_CONFIGURATION_FOUND`, serialized verbatim), or the run
cannot be trusted (terminal `QG7B_CANNOT_CHECK`).

## Q1 — the frozen family B″(t) (definition, verbatim; no post-hoc enlargement)

Notation: letters {0,1,2,3} = {I,X,Y,Z}; `v@q` is the weight-one Pauli with
letter `v` at qubit `q`; products are symplectic-key products (`p10.mul`).
Grammar, cost and labels are the committed frozen ones
(`r6s.config_cost`, `r6s.config_labels`, F3 = the committed branch table).

For an instance `t` = three target pairs on `n` qubits:

- **Pool** `P(t)`: the union target support qubits `U`, plus the lowest-index
  qubits not in `U` — as many as exist, up to **two** empty representatives.
  (One empty representative is the committed B′ choice for phantom homes; the
  second admits the degenerate shape where a tag anchor occupies the first.
  All empty qubits are exchangeable under the grammar, and the QG-7 witnesses
  use none — this is a frozen superset choice, not a fit to any outcome.)
- **Tag**: an unordered pair of distinct qubits `{q_a < q_b} ⊆ P(t)` with
  letters `v_a, v_b ∈ {1,2,3}`; `s = v_a@q_a · v_b@q_b` (weight-2 Tag,
  two distinct tag anchors). Homes `H = P(t) ∖ {q_a, q_b}`; a tag choice with
  `H = ∅` is skipped (in particular **f_B″ is infeasible for every n ≤ 2**).
- **Per-block options** (block `j ∈ {A,B,C}`, target permutation
  `σ ∈ {0,1}`), with `centrals = (1,1,1)` throughout:
  - **anchored** at `(q, v) ∈ {(q_a,v_a), (q_b,v_b)}`: frames
    `(v@q, c@q)` with `c ∈ {1,2,3} ∖ {v}`; surcharge (extra) 0.
  - **phantom**: home `q_h ∈ H`, borrow point `(q_x, v_x) ∈
    {(q_a,v_a), (q_b,v_b)}`, borrow letter `ℓ ∈ {1,2,3} ∖ {v_x}`, home
    letters `m_0 ∈ {1,2,3}`, `m_1 ∈ {1,2,3} ∖ {m_0}`: frames
    `(m_0@q_h, ℓ@q_x · m_1@q_h)` — the support-two label-1 frame borrows its
    syndrome at an existing tag qubit; surcharge (extra) 2.
- **Corner exclusion**: at least one block must be phantom. (The all-anchored
  corner has all frames weight 1 and is definitionally inside D+.)
- **Value**:
  `f_B″(t) = min over all admitted choices of [ Σ_j extra_j + Σ branch-F3 ] + 4`,
  which equals `r6s.config_cost(t6, frames6, s, (1,1,1), n)` for the induced
  configuration (branch-F3 accumulated over `P(t)` only; all letters vanish
  outside it). `f_B″(t) = INF` when no tag choice admits a home.
- **Determinism**: frozen sweep order (tag pairs in `itertools.combinations`
  order over sorted `P(t)`, letters in (1,2,3)×(1,2,3) order, per-block rows
  anchored-before-phantom in construction order, per-class letter-signature
  dedupe keeping first occurrence, numpy flat argmin tie-break) — mirrors the
  committed B′ enumerator `qg5b.bprime_family_min`.

Every member of B″ is by construction a feasible configuration of the frozen
grammar with labels (0,1) (proof: anchored comm frame carries the tag letter,
phantom comm frame is off-tag-support, every anti frame anticommutes with `s`
exactly once, every pair anticommutes at exactly one qubit), hence
**soundness `C_DP ≤ f_B″(t)` holds structurally**; it is additionally
referee-asserted per exactly-computed instance (gate G5).

**Coverage of the QG-7 witnesses**: every QG-7 fourth-regime witness
configuration (two anchored blocks at the two distinct tag qubits + one
phantom borrowing at a tag qubit, centrals irrelevant for weight-(1,1)
anchored blocks, phantom central 1) is a member of B″; the degenerate
reductions (single-anchor, zero-anchor/all-phantom, multi-phantom) are all
admitted. The weight-1-Tag reduction is B′ itself and is carried by the
`f_B′` term of the min, not by B″.

**Proof-carrying witness verifier** `verify_bsecond_witness(t, n, wit)`
(analog of QG-5b's B′ verifier): rebuilds `s` from `(q_ta, v_a, q_tb, v_b)`;
requires distinct tag qubits and `wt(s) == 2`; per block requires the frozen
shape (anchored: both frames weight 1 at the same tag qubit, comm frame equal
to the tag letter there; phantom: comm frame weight 1 with support disjoint
from the tag pair, anti frame weight 2 meeting the tag pair); requires ≥ 1
phantom block; requires `r6s.config_labels == (0,1)`; and requires
`r6s.config_cost(t6, frames6, s, (1,1,1), n) == wit["value"]`. Every exact
finite `f_B″` computed anywhere in this lane is witness-verified (100%, no
sampling), and failures fail gate G4.

## Q2 — frozen panels and the completeness re-test

Identity test per instance: `covered_min := min(C_D+, f_B′, f_B″)` and the
instance is **covered** iff `C_D++ == covered_min` (with `C_DP == C_D++`
required everywhere by the committed R6S theorem; any violation is an R6S
contradiction, serialized, → CANNOT_CHECK).

**Frozen lazy-exact (pinch) policy for f_B″** (disclosed, no silent
truncation; counts of exact vs pinched rows are recorded): `f_B″` is computed
exactly on (i) every Panel W row, (ii) every instance with
`C_D++ < min(C_D+, f_B′)` (the only rows where B″ can be needed), and
(iii) a frozen stride sample (below). Elsewhere the identity is decided by
the structural pinch: `C_D++ = C_DP ≤ f_B″`, so
`min(C_D+, f_B′) == C_D++  ⇒  covered_min == C_D++` regardless of the exact
`f_B″` value. This is the committed R6P/QG-5b containment-pinch precedent.

- **Panel W — the 64 QG-7 witnesses, verbatim** (Q2a). Bound verbatim from
  `QG7_BPRIME_COMPLETENESS_RESULTS.json`
  `arm1_hostile_search.fourth_regime_candidates_verbatim` (must number
  exactly 64, all `replay_confirmed`); `n` parsed from the panel name. Per
  row: recompute `C_DP` (`r6o.dp_cost_frozen_configs`), `C_D++`
  (`r6p.dxx_search`, with witness), `C_D+` (`max_weight=1`), `f_B′`
  (`qg5b.bprime_family_min`, with witness), `f_B″` exact (with witness);
  verify the B″ witness (always), the D++ witness (always), and the exact
  witnessed matcher `r6m.exact_r6m_matching` (always, all 64); bind the
  receipt row values (`C_DP`, `C_Dxx`, `C_Dplus`, `f_Bprime`, `gap4`)
  exactly. **Every row must be covered with `f_B″ == C_DP`**; an uncovered
  row is a fifth-configuration finding (B″ as frozen fails) and is
  serialized verbatim.
- **Panel H — the full QG-7 H1–H5 panels re-evaluated** (Q2b, 740
  instances). Regenerated with the committed QG-7 generator imported
  unmodified (`qg7_bprime_completeness`: `SKELETON_BUILDERS`,
  `template_pairs`, `template_pairs_h5`, `derive_instance`,
  `canonical_key`), identical `PANEL_ORDER`, identical frozen caps
  (`qg7.CAPS`), identical shared-dedupe/cap-break control flow. Binding
  gates: per-panel `evaluated / raw_scanned / zero_target_skipped /
  duplicate_skipped / regime_census / min_gap4 / max_gap4` equal to the
  QG-7 receipt; the receipt's `verification_sample` rows and all 64
  fourth-candidate rows (panel, local index, values, target pairs) equal.
- **Panel S — the QG-5b structured n=2 slice** (Q2c, 9,261 instances,
  enumeration verbatim from `qg5b.panel_b`: all triples over the 21
  unordered weight-1 pairs on 2 qubits). Per instance: `C_DP` via
  `r6o.dp_cost_n2_reader`, `C_D+`, `f_B′` always; `C_D++` exact on stride
  `idx % 97 == 0` and on every row with `min(C_D+, f_B′) > C_DP` (pinch
  `C_D++ == C_DP` by R6S elsewhere); `f_B″` exact on stride
  `idx % 64 == 0` and on every gap row (structurally INF at n=2 — B″ must
  not break anything B′ already covered).
- **Panel F — the QG-5b fresh seeded panel** (Q2c, seed 20260826, 120 per
  n for n ∈ {2,3}, 240 instances, generator digit-frozen from
  `qg5b.panel_c`). Per instance: `C_DP` via `r6o.dp_cost_frozen_configs`,
  `C_D++` (witness), `C_D+`, `f_B′` always; `f_B″` exact on stride
  `i % 64 == 0` per n and on every gap row. Binding gates: instance count
  240; the QG-5b receipt's panel-A refuting instance (n=3, its
  `index_in_fresh_panel`) reappears with identical target pairs and
  `C_DP == F2_C_Dxx == f_B′ == 10, C_D+ == 11`; our recomputed
  `min(C_D+, f_B′) == C_DP` count must equal the receipt's
  `q2_zero_error_count == 240`.
- **Panel X — NEW frozen adversarial panel designed against B″ itself**
  (Q2d). Same Restore-template grammar as QG-7 (`qg7.template_pairs`,
  `qg7.derive_instance`, `qg7.canonical_key`; fresh dedupe set shared
  across the X panels only), frozen skeletons below (helpers
  `K(v,q) = v@q`, `anch(q,v,c) = (v@q, c@q)`,
  `ph(h,(m0,m1),b,ℓ) = (m0@h, ℓ@b·m1@h)`; `s2 = X@0·X@1`,
  `s3 = X@0·X@1·X@2`). The shapes are exactly what the frozen grammar
  admits and B″ does **not** by construction cover: weight-3 Tags (X1),
  phantom-phantom syndrome chains borrowing at a non-tag qubit (X2),
  tag-supported phantom blocks with the comm frame at a tag qubit (X3 —
  grammar-feasible, verified at freeze time), and double-borrow phantoms
  with both frames support-two (X4). Triple-phantom weight-2-Tag
  configurations are inside B″ by construction (≥1 phantom, all-phantom
  admitted) and need no adversarial arm. Frozen skeleton list:
  - `X2_n3` (tag `s2`): 4 skeletons —
    `ph(2,(X,Y),0,Y) + (K(X,1), K(Y,2)·K(Y,1)) + anch(0,X,Y)`;
    `ph(2,(X,Y),0,Y) + (K(X,1), K(Z,2)·K(Y,1)) + anch(0,X,Z)`;
    `ph(2,(X,Y),0,Y) + (K(X,0), K(Y,2)·K(Y,0)) + anch(1,X,Y)`;
    `ph(2,(X,Y),1,Y) + (K(X,1), K(Y,2)·K(Z,1)) + anch(0,X,Y)`.
  - `X3_n3` (tag `s2`): 4 skeletons —
    `anch(0,X,Y) + (K(X,1), K(X,0)·K(Y,1)) + anch(0,X,Z)`;
    `anch(0,X,Y) + (K(X,1), K(X,0)·K(Z,1)) + ph(2,(X,Y),0,Y)`;
    `anch(1,X,Y) + (K(X,0), K(Y,0)·K(X,1)) + anch(1,X,Z)`;
    `ph(2,(X,Y),0,Y) + (K(X,1), K(X,0)·K(Y,1)) + anch(1,X,Z)`.
  - `X4_n3` (tag `s2`): 4 skeletons —
    `(K(X,0)·K(X,2), K(Y,1)·K(Y,2)) + anch(0,X,Y) + anch(1,X,Y)`;
    `(K(X,0)·K(Y,2), K(Z,1)·K(Z,2)) + anch(0,X,Z) + anch(1,X,Y)`;
    `(K(X,0)·K(X,2), K(Y,1)·K(Y,2)) + ph(2,(X,Y),0,Y) + anch(1,X,Y)`;
    `(K(X,1)·K(X,2), K(Y,0)·K(Y,2)) + anch(0,X,Y) + anch(1,X,Z)`.
  - `X1_n4` (tag `s3`): 5 skeletons —
    `anch(0,X,Y)+anch(1,X,Y)+ph(3,(X,Y),2,Y)`;
    `anch(0,X,Y)+anch(1,X,Z)+ph(3,(X,Y),2,Z)`;
    `anch(0,X,Y)+ph(3,(X,Y),1,Y)+ph(3,(Y,Z),2,Y)`;
    `ph(3,(X,Y),0,Y)+ph(3,(Y,Z),1,Y)+ph(3,(X,Z),2,Y)`;
    `anch(0,X,Y)+anch(1,X,Y)+anch(2,X,Y)` (all-anchored weight-3 control).
  - `X2_n4` (tag `s2`): 2 skeletons —
    `ph(2,(X,Y),0,Y) + (K(X,3), K(Y,2)·K(Y,3)) + anch(1,X,Y)`;
    `ph(2,(X,Y),0,Y) + (K(X,3), K(Z,2)·K(Y,3)) + anch(1,X,Z)`
    (grammar-infeasible as configurations — the chain borrow at a non-tag
    qubit breaks the label predicate; the derived targets are still frozen
    adversarial probes, and skeleton infeasibility is recorded).
  - `X3_n4` (tag `s2`): 2 skeletons —
    `anch(0,X,Y) + (K(X,1), K(X,0)·K(Y,1)) + ph(3,(X,Y),0,Y)`;
    `ph(2,(X,Y),0,Y) + (K(X,1), K(X,0)·K(Z,1)) + anch(0,X,Y)`.
  - `X4_n4` (tag `s2`): 2 skeletons —
    `(K(X,0)·K(X,2), K(Y,1)·K(Y,2)) + anch(0,X,Y) + ph(3,(X,Y),1,Y)`;
    `(K(X,0)·K(Y,3), K(Z,1)·K(Z,3)) + anch(0,X,Z) + anch(1,X,Y)`.
  - Frozen caps (evaluated instances; hard, disclosed, `cap_hit` recorded):
    X2_n3 40, X3_n3 40, X4_n3 40, X1_n4 20, X2_n4 12, X3_n4 12, X4_n4 12
    (≤ 176 total). Panel order: X2_n3, X3_n3, X4_n3, X1_n4, X2_n4, X3_n4,
    X4_n4. `f_B″` exact on stride `gidx % 32 == 0` (X-global evaluation
    ordinal) and on every gap row.
  Panels H and X share the referee cadences frozen below.

**Frozen referee cadences** (hostile gates; all counts recorded):
- D++ witness (`r6p.verify_dxx_witness`): every gap row, plus H/X global
  ordinal `% 7 == 0`, Panel F `i % 10 == 0`, Panel S rows where `C_D++` is
  computed exactly.
- B′ witness (`qg5b.verify_bprime_witness`): every finite-`f_B′` gap row,
  plus H/X global ordinal `% 13 == 0`, Panel S `idx % 191 == 0`, Panel F
  `i % 10 == 0` (exempt when `f_B′` infinite, counted).
- B″ witness (`verify_bsecond_witness`): every exact finite `f_B″` (100%).
- Exact witnessed matcher (`r6m.exact_r6m_matching` — "every claimed
  optimum recomputed by the witnessed exact referee on a sample"): all 64
  Panel W rows, every gap row and every fifth-candidate row (replay), plus
  H/X local index `% 20 == 0` at n=3 and `% 8 == 0` at n=4, Panel S
  `idx % 1153 == 0`, Panel F `i % 24 == 0`.
- Sandwich, per instance wherever the quantities are computed (hard):
  `C_DP ≤ C_D++ ≤ C_D+`; `C_DP ≤ f_B′` (finite); `C_DP ≤ f_B″` (exact
  finite); and the covered-min sandwich `C_DP ≤ covered_min` with equality
  required for coverage. Violations are serialized verbatim and fail G5.

## Receipt bindings (exact, gate-controlled)

- QG-7: authority string above; terminal `QG7_FOURTH_SUPPORT2_REGIME_FOUND`;
  `protocol_sha256 ==
  04281622fdbf5a71436e60e3b3aaee66d1b7b0e025f14eafdf073e9b52373645` (and the
  committed protocol file re-hashes to it); 740 evaluated / 64 candidates /
  64 confirmed; the Panel H per-panel and per-row bindings above; the L1/L2
  obligation statuses `CLOSED_ALL_N` with domains N1=768, N5=27216, N3=8,
  N0_lemma_e=18432, N0_lemma_b=43688 (bound for Q3).
- QG-5b: authority
  `ORIONQG_QG5B_EXACT_FORECASTER_THEOREM_BACKED_ZERO_ERROR__DPP_FAMILY_MIN__ENLARGED_BORROW_CLOSES__NOT_R6`;
  `q1.dp_compared_instances_total == 9547`; `q2.outcome ==
  Q2_ENLARGED_BORROW_CLOSES`; panel_b instances 9261 with q2 zero-error
  9261; panel_c instances 240 with q2 zero-error 240; the panel-A refuting
  instance replay (Panel F binding above).
- R6S: `r6s.bind_tables()` all true; F3 tables bit-equal across r6p/r6m and
  a locally rebuilt table; pair counts {1:6, 2:120, 3:666, 4:1968}; the
  committed receipt's authority prefix
  `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED`.
- Runtime guard extension (declared, identical to QG-7):
  `r6p.EXPECTED_PAIR_COUNTS.setdefault(4, r6s.PAIR_COUNTS_SUPPORT2[4])` — no
  file modified.

## Gates (all must pass; any failure → CANNOT_CHECK)

- G1 tables_bound (R6S bind + F3 equality + pair counts).
- G2 qg7_receipt_bound (authority/terminal/sha/counts + Panel H bindings +
  Panel W row bindings).
- G3 qg5b_receipt_bound (authority/counts + Panel F bindings).
- G4 witness_referees_pass (D++ / B′ / B″ witness verifications, zero
  failures; B″ at 100% of exact rows).
- G5 sandwich_and_soundness_pass (zero serialized violations).
- G6 exact_matcher_binding_pass (zero failures on the frozen sample).
- G7 no_r6s_contradiction (`C_DP == C_D++` wherever both computed).
- G8 enumeration_counts_complete (every panel reports raw/skip/cap counts;
  no silent truncation).
- G9 witness_coverage_accounted (all 64 Panel W rows adjudicated covered or
  serialized as failures — never dropped).

## Terminals (frozen; exactly one)

- `QG7B_FIFTH_CONFIGURATION_FOUND` — ≥ 1 referee-confirmed instance with
  `C_D++ < min(C_D+, f_B′, f_B″)` (including any uncovered Panel W row),
  gates G1–G9 pass, every finding serialized verbatim. Authority:
  `ORIONQG_QG7B_FIFTH_CONFIGURATION_FOUND__HOSTILE_SEARCH_WITNESS_REFEREE_CONFIRMED__NOT_R6`.
- `QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS` — zero gap everywhere:
  every instance on every panel covered, all 64 witnesses covered with
  `f_B″ == C_DP`, gates pass. Authority:
  `ORIONQG_QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS__WEIGHT2_TAG_PHANTOM_BORROW_BSECOND__NOT_R6`.
- `QG7B_CANNOT_CHECK` — any gate failure, any unconfirmed fifth candidate,
  any R6S contradiction, everything serialized. Authority:
  `ORIONQG_QG7B_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6`.

The closes-terminal claims machine-evidenced finite-domain completeness ONLY
("on verified domains"); the all-n identity remains CONJECTURE gated by the
Q3 obligations. A finite panel cannot authorize the all-n theorem.

## Q3 — the remaining normalization obligation (stated in the results,
receipt-bound, no new computation)

Bind QG-7's closed lemmas verbatim (L1 `CLOSED_ALL_N`, domains N1=768,
N5=27216; L2 `CLOSED_ALL_N`, domains N3=8, N0_e=18432, N0_b=43688; L4a
closed on the complete 1,440-check domain with exact refund 2). Between
"B″ closes on verified domains" and "`C_DP == min(C_D+, f_B′, f_B″)` for
all n" the remaining obligation is exactly:

- **L4b (weight-≤2-Tag consolidation)** — prove every support-two optimum
  with tag weight ≤ 2 consolidates without cost increase into
  D+ ∪ B′ ∪ B″. Honest open shape classes remaining AFTER B″ (each
  grammar-admitted, none covered by B″ by construction):
  (a) tag-supported phantom blocks (comm frame at a tag qubit; the X2_n3/X3
  shapes, grammar-feasible), (b) double-borrow phantom blocks (both frames
  support-two; X4), (c) cyclic borrow chains (QG-7 open shape
  `H3_cyclic_borrow`), (d) `H4b_l1_phantom_tag_letter_at_home` (QG-7 open
  shape list, bound verbatim).
- **L4c (tag-weight bound)** — L4a only prunes tag letters outside the
  union FRAME support; a weight-≥3 Tag whose letters all sit inside the
  frame support is not covered. A weight-≥3-Tag analysis owes either an
  exchange lemma reducing any such Tag to weight ≤ 2 without cost increase,
  or a further family B‴. Panel X1 probes this empirically only.

If L4b and L4c close, L5 inherits closure and the identity becomes all-n.
These obligations define QG-7c if any remain open. This section states them;
it proves nothing new.

## Runtime, determinism, and replay discipline

- Runtime cap: **1500 s per run (< 25 min)**, recorded in the RESULTS timing
  section (R6P convention: timing excluded from the canonical stdout line
  and the result digest; stderr + file only). All panel caps, strides and
  skip counts are disclosed in the RESULTS file.
- Fully deterministic: the only RNG is the digit-frozen Panel F generator
  (seed 20260826, committed QG-5b stream). Two full runs are required; the
  canonical stdout line and the RESULTS file minus its `timing` section must
  be byte-identical.
- No existing file is modified; no commit/push from this lane (orchestrator
  handles VCS). The stop rules of the wave-1 packet and charter apply
  verbatim.

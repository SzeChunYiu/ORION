# QG-18 — the intrinsic support number of TARE (κ_TARE ∈ {1,2} → settled)

Date: 2026-08-21
Lane: ORION-QG / regime geometry, wave 3
Branch: `claude/orion-harness-verification-b17qdj`
Base revision: `3a3e820e`
Status: **FROZEN BEFORE ANY OUTCOME-DETERMINING RUN.**

Authority ceiling: **NOT_R6**. No novelty authority, no donor-novelty authority, no
physical-quantum-advantage claim, no new chemistry data. The protected
stretched-N₂ discriminator is never read. Every committed analyzer imported by
this lane is imported **unmodified**; no repository file outside the three files
listed in §10 is created or changed.

Runtime cap: **< 25 minutes per run** (wall clock, single process). The frozen
domains of §3–§6 are sized against that cap in §9 and every cap is disclosed.
No silent truncation: every declared domain is executed in full, and every
domain size is recorded verbatim in the RESULTS file.

---

## 0. The open question this lane closes

`papers/candidates/qg-paper-03-stub/MANUSCRIPT_V1.md` (§7 table) records

| Family | Objective | Support bound | κ status |
|---|---|---|---|
| R6I | frozen unit R6I objective | 1 | **κ_R6I = 1 exactly** (QG-9 V6) |
| R6M / TARE | frozen unit-cost support objective | 2 | **κ_TARE ≤ 2; exact value OPEN** |

R6S proves support ≤ 2 for every n over the frozen R6M grammar. Nobody has
tested whether 2 is *necessary*. Per the manuscript's own definition,

> κ(F, C) is the least B such that every instance's exact optimum is attained by
> a configuration with all structural generators of global support ≤ B.
> Equivalently: B is a valid support bound and B − 1 is not.

κ_TARE = 2 iff some exact R6M instance has `C_DP < C_cap1`; κ_TARE = 1 iff
`C_DP = C_cap1` for every instance and every n.

## 1. Frozen objects

**Grammar (R6M/TARE).** Three TARE-M2 blocks j ∈ {A,B,C}. Block j owns an
ordered pair of frame Paulis `(R_j0, R_j1)` on n qubits with
`symp(R_j0, R_j1) = 1`. One shared one-bit Tag Pauli `S`. Acceptance (frozen
9-bit parity predicate of `max_r6m_exact_three_tare2_shared_factor_dp`):

* `symp(R_j0, R_j1) = 1` for all j;
* `symp(S, R_A0) = symp(S, R_B0) = symp(S, R_C0) =: l0`;
* `symp(S, R_A1) = symp(S, R_B1) = symp(S, R_C1) =: l1`;
* `l0 ≠ l1`.

Free coordinates: the three ordered frame pairs, the Tag `S`, the three central
bits `c_j ∈ {0,1}`, and the two relative target permutations
`perm_B, perm_C ∈ {0,1}` (block A canonical, frozen matching `((0,1),(2,3),(4,5))`).

**Objective (frozen unit-cost support objective O0).** With
`T_jk = P_jk · R_jk` the Restore of block j on branch k, and with `F3` the
donor-owned all-three common-factor rule
`F3(a,b,c) = 1 if a=b=c≠I else w(a)+w(b)+w(c)`,

```
C(config) = Σ_j [ m_{j0}·w(R_j0) + m_{j1}·w(R_j1) ]        (frame, m = 2 central / 4 non-central)
          + 2·w(S)                                          (Tag)
          + Σ_{q} F3( T_A0(q), T_B0(q), T_C0(q) )           (branch-0 Restore)
          + Σ_{q} F3( T_A1(q), T_B1(q), T_C1(q) )           (branch-1 Restore)
          − 18                                              (frozen normalization)
```

This is exactly `max_r6s_all_n_composition.config_cost` and exactly the quantity
the frozen R6M DP minimizes (`_dp_config_cost` returns `min dp[accepting] − 18`).

**Three exact optima per instance.**

* `C_DP` — unrestricted exact optimum (frozen R6M 9-bit XOR DP over all
  perms × centrals). Referee: `max_r6p_weight2_frame_donor_closure.dp_cost_frozen_configs`
  (and its `dp_cost_n1_reader` / `dp_cost_n2_reader` at n ≤ 2).
* `C_Dxx` — exact optimum over configurations whose six frame Paulis all have
  global support ≤ 2. Referee: `r6p.dxx_search(·, max_weight=2)`.
* `C_cap1` — exact optimum over the **support-≤1 family** (§2). Referee: the
  QG-18 referee `R1` of §2, cross-checked three ways.

Hard sandwich, asserted on every computed row: `C_DP ≤ C_Dxx ≤ C_cap1`.
Any violation is a terminal hard failure (§8).

## 2. The exact cap-1 referee (frozen definition)

**Support-≤1 family.** All six frame Paulis have global support ≤ 1. A frame
Pauli of support 0 is the identity and has `symp(I, ·) = 0`, so acceptance forces
every frame Pauli to have support exactly 1; and `symp(R_j0, R_j1) = 1` then
forces the two Paulis of a block onto the **same** anchor qubit `q_j` with
distinct non-identity letters. Hence the family is exactly:

* anchors `(q_A, q_B, q_C) ∈ [n]³`;
* ordered distinct non-identity local letter pairs `(a_j, b_j) ∈ ORD`, where
  `ORD = {(a,b) : a,b ∈ {X,Y,Z}, a ≠ b}`, `|ORD| = 6`;
* a shared Tag `S` — **any** key in the full `4^n` key space;
* centrals `(c_A,c_B,c_C) ∈ {0,1}³`;
* relative permutations `(perm_B, perm_C) ∈ {0,1}²`.

**Referee R1 (enumerative, closed form for the Tag).** Two facts are proved
inside the checker on complete finite domains and gate the referee:

* *R1-a (frame invariance)*: every support-1 block contributes
  `m_{j0}·1 + m_{j1}·1 = 6` for both central choices, so the frame term is
  identically 18 and the `− 18` normalization cancels it; centrals are
  cost-irrelevant in this family. Domain: 6 ordered bases × 2 centrals = 12 rows;
  all must equal 6.
* *R1-b (forced minimal Tag)*: with `l0 ≠ l1` the constraints on `S` are purely
  local at each anchor. For labels `(0,1)`, `symp(S(q_j), a_j) = 0` and
  `symp(S(q_j), b_j) = 1` force `S(q_j) = a_j`; for `(1,0)` they force
  `S(q_j) = b_j`. Off-anchor letters are unconstrained and cost 2 each, so the
  cost-minimal Tag is supported exactly on the distinct anchors and
  `2·w(S) = 2·|{q_A,q_B,q_C}|`. Blocks sharing an anchor must force the same
  letter or the configuration is infeasible. Domain: 6 ordered bases × 4 local
  Tag letters × 2 label orientations = 48 rows, verifying uniqueness of the
  forced letter and the non-existence of a weight-0 solution.

R1 therefore enumerates `n³ · 6³ · 2 · 4 = 1728·n³` configurations and returns
the exact minimum. **Declared domain sizes**: n=1 → 1,728; n=2 → 13,824;
n=3 → 46,656; n=4 → 110,592.

R1 is implemented twice inside the checker:

* `cap1_reference` — flat quadruple loop, no algebraic shortcut;
* `cap1_grouped` — identical enumeration re-associated by anchor group
  (blocks that do not share an anchor decouple), used for the large sweeps.

Gate `cap1_reference == cap1_grouped` on **every** instance of the exhaustive
n=1 domain D4 (729 rows) and on **every** instance of the complete n=2
brute-force sub-domain BF-2 (§3), plus on every witness instance.

**Brute-force cross-checks (hostile gate).** Two *from-primitives* complete
sweeps, which assume none of R1-a/R1-b:

* **BF-1 (complete, n = 1).** Instance domain: all `3^6 = 729` six-tuples of
  non-identity single-qubit targets. Configuration domain per instance: all six
  frame Paulis over the weight-≤1 key set `W(1)` (`|W(1)| = 3n+1 = 4`), all
  `4^1 = 4` Tag keys, all 8 centrals, all 4 permutations — enumerated in full
  and filtered by the acceptance predicate rebuilt from primitives. At n = 1 the
  support-≤1 restriction is vacuous, so BF-1 must additionally satisfy
  `C_cap1 = C_DP` on all 729 rows, cross-checked against the committed
  independent full n=1 enumerator `r6m._brute_config_n1` swept over all
  perms × centrals.
* **BF-2 (complete, n = 2).** Instance domain: all `2^6 = 64` six-tuples over
  the frozen 2-key alphabet `{X₀ = (1,0), Z₁ = (0,2)}`. Configuration domain per
  instance: all six frame Paulis over `W(2)` (`|W(2)| = 7`, i.e. `7^6 = 117,649`
  frame tuples), all `4^2 = 16` Tag keys, all 8 centrals, all 4 permutations,
  enumerated in full and filtered by the from-primitives acceptance predicate.
  BF-2 must equal R1 on all 64 rows.

Additional independent bindings on a frozen 40-row seeded panel
(`seed = 20260821`, n ∈ {1,2,3}): `R1 == r6o.dplus_pairs(...)['C_Dplus']` and
`R1 == r6p.dxx_search(..., max_weight=1)['C_Dxx']`.

## 3. Q1 — necessity hunt (runs first)

For every instance of the domains below compute `C_DP` and `C_cap1`
(and `C_Dxx` on every gap row plus on a frozen verification subsample), assert
the sandwich, and record every row with `C_DP < C_cap1`.

* **D1** — committed QG-7 witness set:
  `QG7_BPRIME_COMPLETENESS_RESULTS.json`,
  `arm1_hostile_search.fourth_regime_candidates_verbatim` (64 rows, panels
  H1–H4 at n = 3 and n = 4). These are the borrow / phantom-borrow minimal
  witnesses.
* **D2** — committed QG-7b witness set:
  `QG7B_HYBRID_FAMILY_RESULTS.json`, `q2.panel_w_witnesses.rows` (64) ∪
  `verification_sample` (40), de-duplicated by target six-tuple. These are the
  weight-2-Tag hybrid witnesses.
* **D3** — committed R6O gap set:
  `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`,
  `discovery.instances_with_dp_strictly_below_dplus` (40 rows).
* **D4** — **exhaustive n = 1 domain**: all `3^6 = 729` six-tuples of
  non-identity single-qubit targets. Complete. (At n = 1 no gap is possible; D4
  is the completeness control and the BF-1 carrier.)
* **D5** — **frozen structured n = 2 slice**: all `6^6 = 46,656` six-tuples over
  the six weight-one n=2 keys
  `W1(2) = {X₀=(1,0), Y₀=(1,1), Z₀=(0,1), X₁=(2,0), Y₁=(2,2), Z₁=(0,2)}`.
  Complete for that alphabet; executed in full.

De-duplication across D1–D3 is by canonical target six-tuple; the per-domain row
counts and the de-duplicated total are recorded.

**Canonical witness selection (frozen, deterministic).** Among all rows with
`C_DP < C_cap1`, order by
`(n, C_DP, C_cap1, canonical-JSON of the target six-tuple)` ascending and take
the first. The minimal-n preference is deliberate: it keeps the generic
verifier's complete support-≤1 brute force tractable (§7).

**Full independent recomputation of the canonical witness** (all must agree):

* `C_DP` by (i) the frozen R6M DP `r6p.dp_cost_frozen_configs`, (ii) the frozen
  n-specific reader (`dp_cost_n1_reader` / `dp_cost_n2_reader`) when n ≤ 2,
  (iii) the committed independent full enumerator `r6m._brute_config_n2` swept
  over all perms × centrals when n = 2.
* `C_cap1` by (i) `cap1_reference`, (ii) `cap1_grouped`, (iii) the
  from-primitives complete brute force of BF-2 shape at that n, (iv)
  `r6o.dplus_pairs`, (v) `r6p.dxx_search(max_weight=1)`.
* `C_Dxx` by `r6p.dxx_search(max_weight=2)`, its explicit witness re-verified by
  `r6p.verify_dxx_witness` **and** by an independent from-primitives
  recomputation of that explicit configuration's acceptance and cost. The
  explicit support-2 configuration is serialized verbatim (frames, Tag,
  centrals, permutations, labels, per-block supports).

**Q1 terminal condition.** A referee-confirmed strict gap
(`C_DP < C_cap1`, sandwich intact, all recomputations agreeing, the explicit
support-2 configuration feasible with cost `= C_DP`) establishes κ_TARE ≥ 2;
combined with the bound R6S receipt (κ_TARE ≤ 2) it gives κ_TARE = 2 exactly.

## 4. Q2 — the V6 Tag-relocation transfer (conditional) and its always-run diagnostic

Q2's lemma chain is **executed as a diagnostic on every run** (it is cheap and it
is what Q3 reads); it becomes the *terminal-bearing* arm only if Q1 finds no
witness on any of D1–D5.

V6's chain for R6I is: localize each block to one anticommuting core; pay for it
with the credit earned by deleting non-core columns; then **rebuild/relocate the
shared Tag** rather than preserving its columnwise syndrome. The TARE analogues,
each with its complete finite local domain:

### L1 — TARE deletion credit for a non-core frame column

Zeroing both frame letters of block j at a locally *commuting* qubit q preserves
the block's anticommutation bit. Domain, swept in full:

* slot position of block j in the F3 triple ∈ {A,B,C} — 3;
* block central bit ∈ {0,1} (→ multipliers `(m₀,m₁) ∈ {(2,4),(4,2)}`) — 2;
* frame letters `(f₀,f₁) ∈ {0..3}²` with `symp(f₀,f₁) = 0`, `(f₀,f₁) ≠ (I,I)` — 9;
* block-j target letters `(p₀,p₁) ∈ {0..3}²` — 16;
* the other two blocks' branch-0 and branch-1 slot letters
  `(u₀,v₀,u₁,v₁) ∈ {0..3}⁴` — 256.

**Declared size: 3·2·9·16·256 = 221,184 rows.** Quantity

```
Δ_del = [F3(p₀,u₀,v₀) − F3(p₀·f₀,u₀,v₀)] + [F3(p₁,u₁,v₁) − F3(p₁·f₁,u₁,v₁)]
        − ( m₀·w(f₀) + m₁·w(f₁) )
```

(the F3 arguments placed at the slot position under test). **Credit floor
:= −max Δ_del.** The V6 analogue floor is 4. Obligation **L1**:
`credit_floor ≥ 1`. The locally *anticommuting* class
(`symp(f₀,f₁) = 1`, 6 letter pairs, **3·2·6·16·256 = 147,456 rows**) is swept and
reported for completeness.

### L2 — TARE core alignment cost

Replacing the surviving one-qubit ordered anticommuting basis `(a,b)` of a
support-1 block by another `(a',b')`. Domain:

* slot ∈ {A,B,C} — 3; central ∈ {0,1} — 2;
* old basis ∈ ORD — 6; new basis ∈ ORD — 6;
* block target letters `(p₀,p₁)` — 16; other slots `(u₀,v₀,u₁,v₁)` — 256.

**Declared size: 3·2·6·6·16·256 = 884,736 rows.** Record (i) frame-contribution
invariance (must be identically 6) and (ii) `alignment_ceiling := max Δ_align`
over the two branch F3 terms. V6 analogue: invariant 10, ceiling 3.

### L3 — TARE same-core Tag rigidity

Two support-1 blocks anchored at the same qubit with ordered bases
`A, B ∈ ORD` and a local Tag letter `s ∈ {0..3}`. Domain
**6·6·4·2 (label orientations) = 288 rows.** Obligation **L3** (V6 form): every
row feasible under a common label orientation with `l0 ≠ l1` must have `A = B`.
Record the complete census of feasible `A ≠ B` rows.

### L4 — TARE distinct-core Tag lower bound

Complete n = 3 sweep of anchors `(q_A,q_B,q_C) ∈ [3]³` (27) × ordered basis
triples (6³ = 216) × label orientations (2) × **all** `4³ = 64` Tag keys =
**746,496 rows**, extracting the exact minimum feasible Tag cost `2·w(S)` as a
function of the number of distinct anchors k ∈ {1,2,3}. V6 analogues: same-core
new Tag 4, distinct-core new Tag 8, old Tag floor 4.

### Composition C (two-case, machine-evaluated)

* **C-1 (alignment payable)**: `credit_floor > alignment_ceiling`.
* **C-2 (same-core)**: `same_core_new_tag ≤ old_tag_floor` and, when alignment is
  needed, `credit_floor ≥ alignment_ceiling`.
* **C-3 (distinct-core)**: `old_tag_floor + credit_floor ≥ distinct_core_new_tag`.
* **C-4**: support-0 infeasible (`symp(I,I) = 0`), so κ_TARE ≥ 1 unconditionally.

Q2 closes only if L1 ∧ L2 ∧ L3 ∧ L4 ∧ C-1 ∧ C-2 ∧ C-3 all hold. The **first**
failing obligation in the fixed order `L1, L2, L3, L4, C-1, C-2, C-3` names the
terminal `QG18_PARTIAL__<obligation>_OPEN` when Q2 is the terminal-bearing arm,
and in all cases is serialized as the obstruction census (verbatim extremal
witnesses, capped at 20 per obligation with the uncapped count recorded).

## 5. Q3 — structural diagnosis (always)

Regardless of terminal, the RESULTS file must state, **derived from the measured
L1–L4 numbers and (if present) the witness anatomy**, which structural
difference between R6M and R6I explains the outcome, in the form:

> Tag relocation is available for family F iff `<measured predicate>`.

Required fields: the R6I reference numbers (credit floor 4, alignment ceiling 3,
same-core Tag 4, distinct-core Tag 8, old-Tag floor 4 — read from
`QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json`, not re-derived), the measured
TARE numbers, the per-obligation comparison, and the named mechanism. The
diagnosis must be falsifiable from the serialized numbers alone.

## 6. Receipt bindings (exact, hard gates)

sha256 + terminal/authority equality for:

| Receipt | sha256 (base revision `3a3e820e`) |
|---|---|
| `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` | `b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875` |
| `research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` | `e40e7a948061b9e4b647ba091c04a73b39cffa619ca829bbf4cef4beacdad352` |
| `research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` | `3eef07d16353b606a133d7fb977d5039ad1c639c7a531a47ae82be4be9051190` |
| `research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json` | `7341f9630c2ca32b8a6cc601e9c1201db68f21212e04eb3b2e36bca63f214159` |
| `research/extensions/orion-qg/QG7B_HYBRID_FAMILY_RESULTS.json` | `70cee5a5f80482d84e89a92365286e1043cf3e5cf9f847a204fa84d3abcab530` |
| `research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json` | `398d9592023ccf0edeb3e1ea260f9e4cdf1df8132a94110f0e6eda722b914ea9` |
| `research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json` | `f9b505d908bcafec97e7114c04e29fc1f4b8d650d29ecb9ac69842a971ebaf77` |
| `research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json` | `f8df10d5604267e43701adb032f33baf1dfaa5a6572e5bdeaeda7707c4100b66` |

Semantic bindings additionally required:

* R6S `outcome == "THEOREM_MACHINE_CHECKED"` and its authority string contains
  `SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N` — this is the κ_TARE ≤ 2 half.
* QG-8 `terminal == "QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED"`,
  `support2_cone.certificate_boundary_sharpness == "CENTRAL_HYPERPLANE_EXACT"`,
  and its `r6s_binding.receipt_sha256` equal to the R6S sha above.
* QG-9 V6 `terminal == "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED"`
  and `intrinsic_support_number == 1`.
* QG-7 `terminal == "QG7_FOURTH_SUPPORT2_REGIME_FOUND"`; QG-7b
  `terminal == "QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS"`; QG-7c
  `terminal == "QG7C_PARTIAL__L4B_OPEN"`.
* Local-algebra binding: `LW/LM/SY/F3` rebuilt from `p10.h` must equal
  `r6m._LW/_LM/_SY/_F3` exactly.
* `EXPECTED_PAIR_COUNTS[4]` injection into `r6p` is runtime-only (as R6S does);
  the RESULTS file records `repository_files_modified: false`.

## 7. Generic verifier

`development/orion-qg-regime-geometry/qg18_generic_verify.py` — **pure
primitives**: standard library only, no import of any analyzer, no numpy. It
rebuilds from scratch the 2-bit symplectic Pauli algebra, the F3 factor rule, the
R6M acceptance predicate and the O0 objective, then:

1. reads `QG18_TARE_KAPPA_RESULTS.json`;
2. re-verifies every declared receipt sha256 in §6 by hashing the files;
3. rebuilds the **complete support-≤1 brute force** at the witness's n (all
   `(3n+1)^6` weight-≤1 frame six-tuples × all `4^n` Tag keys × 8 centrals × 4
   permutations, filtered by the rebuilt acceptance predicate) and recomputes
   `C_cap1`;
4. rebuilds the serialized explicit support-2 configuration, checks acceptance
   and recomputes its exact cost `c₂`;
5. rebuilds the serialized explicit cap-1 optimal configuration, checks
   acceptance and recomputes its exact cost, which must equal `C_cap1`;
6. ACCEPT iff `C_cap1(rebuilt) == C_cap1(claimed)`, `c₂ == C_DP(claimed) ==
   C_Dxx(claimed)`, `c₂ < C_cap1(rebuilt)`, all sha256 match, and the R6S
   semantic binding holds; otherwise REJECT with the failing reasons.

Token: exactly one line `QG18_GENERIC_VERIFY=ACCEPT` or
`QG18_GENERIC_VERIFY=REJECT` plus a JSON reason object. Step 3 is complete and
exact for n ≤ 2; if the canonical witness has n ≥ 3 the verifier REJECTs with
reason `witness_n_exceeds_complete_bruteforce_reach` rather than approximating.

## 8. Terminals

Exactly one of:

* `QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS` — Q1 produced a
  referee-confirmed strict gap and all gates hold. Authority
  `ORIONQG_QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS_REFEREE_CONFIRMED__CAP1_BRUTE_FORCE_CROSSCHECKED__NOT_R6`.
  Reports `intrinsic_support_number: 2`.
* `QG18_TARE_KAPPA_IS_1__TAG_RELOCATION_ALL_N_MACHINE_CHECKED` — Q1 empty on
  D1–D5 **and** the full Q2 chain L1–L4 + C-1..C-3 closes. Authority
  `ORIONQG_QG18_TARE_KAPPA_IS_1__TAG_RELOCATION_ALL_N_MACHINE_CHECKED__NOT_R6`.
  Reports `intrinsic_support_number: 1`.
* `QG18_PARTIAL__<obligation>_OPEN` — Q1 empty and Q2 blocked at
  `<obligation> ∈ {L1_DELETION_CREDIT, L2_ALIGNMENT_CEILING,
  L3_SAME_CORE_RIGIDITY, L4_DISTINCT_CORE_TAG, C1_CREDIT_EXCEEDS_ALIGNMENT,
  C2_SAME_CORE, C3_DISTINCT_CORE}`. Authority
  `ORIONQG_QG18_PARTIAL__<obligation>_OPEN__NOT_R6`. Reports
  `intrinsic_support_number: null`, `kappa_interval: [1,2]`.
* `QG18_CANNOT_CHECK__REFEREE_BINDING_FAILED` — any binding, brute-force
  cross-check, or referee-agreement gate fails.
* `QG18_INCONSISTENT__SANDWICH_VIOLATED` — a hard failure of
  `C_DP ≤ C_Dxx ≤ C_cap1` anywhere. Raised as an assertion with the offending
  row verbatim.

Terminal precedence: `INCONSISTENT` > `CANNOT_CHECK` > `KAPPA_IS_2` >
`KAPPA_IS_1` > `PARTIAL`.

**Gates** (all must be true for a non-`CANNOT_CHECK` terminal):
`protocol_present`, `production_algebra_exact`, `r6m_tables_exact`,
`receipts_sha256_exact`, `receipt_semantics_exact`, `r1a_frame_invariance`,
`r1b_forced_tag_unique`, `cap1_reference_equals_grouped`,
`cap1_equals_bruteforce_n1`, `cap1_equals_bruteforce_n2`,
`cap1_equals_dplus_panel`, `cap1_equals_dxx_weight1_panel`,
`n1_cap1_equals_dp_complete`, `sandwich_holds_everywhere`,
`domains_complete_no_truncation`, `no_chemistry_read`,
`protected_subject_not_read`, `authority_ceiling_not_r6`.
Terminal-specific: `witness_fully_recomputed` and `witness_support2_config_verified`
for `KAPPA_IS_2`; `q2_chain_closes` for `KAPPA_IS_1`.

## 9. Runtime budget (disclosed)

Measured on the lane host at protocol-freeze time, per run:

| Stage | Size | Est. |
|---|---|---|
| Algebra/receipt bindings | — | < 1 s |
| R1-a / R1-b micro-domains | 12 + 48 rows | < 1 s |
| Q2 diagnostic L1/L2/L4 (numpy) | 221,184 + 147,456 + 884,736 + 746,496 | < 20 s |
| BF-1 complete n=1 | 729 instances | ≈ 30 s |
| BF-2 complete n=2 | 64 instances | ≈ 60 s |
| D1–D3 witness recomputation | ≤ 170 instances, n ≤ 4 | ≈ 60 s |
| D4 exhaustive n=1 | 729 instances | ≈ 10 s |
| D5 structured n=2 slice | 46,656 instances × (3.5 ms cap1 + 5.8 ms DP) | ≈ 7.5 min |
| Witness full recomputation | 1 instance, 5 referees | < 30 s |

Total budget ≈ 10–12 min, cap **25 min**. If the measured total exceeds the cap
the run aborts with `QG18_CANNOT_CHECK__REFEREE_BINDING_FAILED` and
`runtime_cap_exceeded: true` rather than truncating a domain.

## 10. Outputs, determinism, discipline

Files created by this lane (and no others):

1. `development/orion-qg-regime-geometry/QG18_TARE_KAPPA_PROTOCOL_V1.md` (this file);
2. `research/extensions/orion-qg/qg18_tare_kappa.py`;
3. `research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json`;
4. `development/orion-qg-regime-geometry/qg18_generic_verify.py`.

No existing file is modified. `qg7d_*` / `QG7D_*` files are out of scope and are
never read or written. The protected file
`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`
is never opened. No AI model name appears in any produced file. Nothing is
committed or pushed by this lane.

**Determinism.** The checker is seeded (`seed = 20260821` for the binding panel
only; every other domain is a complete deterministic enumeration). Per R6P the
canonical stdout receipt line
`ORIONQG_QG18=<canonical JSON summary>` carries **no timing**; wall-clock numbers
appear only in `RESULTS.timing` and on stderr. Two consecutive runs must produce
a byte-identical canonical stdout line and byte-identical RESULTS content after
removing the `timing` key.

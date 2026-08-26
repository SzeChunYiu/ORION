# Paper QG3 figures plan

All figures are generated from committed receipts only; no new computation on
subjects, no chemistry or protected-subject access. Paths relative to repository
root. Every panel that renders a cone must carry its receipt's sharpness
annotation verbatim (see Fig. 4 and the note at the end).

1. **Fig. 1 — Support bound versus intrinsic support number.** Two number lines
   for the R6I grammar under its frozen unit objective. Top: the *proof-reachable*
   bounds as the ladder descends, 5 → 4 → 3 → 2 → 1, each tick labelled with its
   terminal string. Bottom: the *true* interval, collapsed to the single point
   κ = 1, with the lower bound marked "support 0 infeasible: symp(0,0) = 0". A
   bracket between the two lines is annotated "four polynomial orders of
   certified search" citing the O(n^d A^d) corollary. Sources:
   `research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json`
   (`support_bound_B: 5`);
   `research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json`
   (`intrinsic_support_number: 1`, `support0_infeasible: true`);
   `research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json`
   (`search_complexity_corollary`).

2. **Fig. 2 — The descent ladder and its chained obstruction censuses.** Five
   stacked rungs, each a box with (a) the rung's edit grammar in one line
   (combined deletion / relabel+delete / no new edit, realizability filter /
   inverse-design search / whole-system Tag relocation), (b) the closure result,
   and (c) the residual census. Arrows carry the census *count* from each rung to
   the next, making the chaining visible: V2's 36 unsafe support-4 descriptor
   patterns → V3's parent survivors (288 type cases, 0 unsafe); V3's 21 unsafe
   support-3 profile cases → V4's acceptance filter (300 accepted, 0 unsafe);
   V4's 36 accepted unsafe support-2 type cases → V5's candidate seed (1,296
   blocks, 4,104 pairs, 211,248 candidates). V5 is drawn as a dead-end arrow
   labelled `selected_witness: null` that nonetheless feeds V6 as *motivation
   only*, with the protocol clause "without using the negative panel as proof"
   in the caption. Sources: `QG9_SUPPORT4_COMBINED_EXCHANGE_RESULTS.json`
   (`support5_boundary`, `support4_control`);
   `QG9_SUPPORT3_RELABEL_EXCHANGE_RESULTS.json` (`support4_parent_survivors`,
   `support3_boundary_control`);
   `QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json` (`support3_full_acceptance`,
   `support2_boundary_control`);
   `QG9_V5_SUPPORT2_TIGHTNESS_RESULTS.json` (`candidate_generator`,
   `candidates_tested`, `selected_witness`);
   `QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json` (`terminal`).

3. **Fig. 3 — The V6 normalization, drawn as a cost ledger.** Left: a two-block
   R6I configuration with generators spread over several columns and a shared Tag
   in place. Right: both blocks localized to their anticommuting cores with the
   Tag relocated to canonical (c0, c1) = (1, 2) letters. Between them, a ledger
   bar showing the exact lemma constants: deletion credit ≤ −4 (commuting) /
   ≤ −7 (anticommuting) per extra active column; alignment ≤ +3; new Tag cost 4
   (same core) or 8 (distinct cores) against an original Tag floor of 4 (or 8
   when both blocks are already support-1). Each constant is badged with its
   complete domain size (2,880 / 6,912 / 576 / 9,216). Caption states
   `all_cases_closed: true` and that credit floor 4 > alignment ceiling 3 is what
   makes the composition close. Source:
   `QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json` (`finite_lemmas`, `composition`).

4. **Fig. 4 — Two objective cones, side by side, with their open boundaries.**
   (a) The R6I support-1 cone: a 2-D slice (t_c + t_nc against t_r and t_tag)
   showing the four half-spaces `2·t_nc ≥ 5·t_r`, `t_c + t_nc ≥ 5·t_r`,
   `2·t_nc ≥ 2·t_r + 2·t_tag`, `t_c + t_nc ≥ 2·t_r + 2·t_tag`, with the five
   exact rational controls plotted and labelled by their exact margins — O0 **on**
   the Tag-relocation facet at margin 0, O_in at 2, O_tag_out at −1,
   O_restore_out at −1/2, O_nc_out at −2. (b) The R6M support-2 cone
   `t_c ≥ 2·t_r ∧ t_nc ≥ 2·t_r` with O0 on the central hyperplane (margin 0.0),
   O2 identical, and O1 outside (central margin −5.0) carrying the exact
   support-3 witness `C_DP = 11 < C_Dxx = 13 < C_Dplus = 23` as an annotated
   point. **The exterior of both cones must be hatched and labelled "certificate
   does not apply — NOT support-2/3 required", and both captions must print
   `GLOBAL_PHASE_BOUNDARY_SHARPNESS = OPEN` verbatim.** Sources:
   `research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json`
   (`full_cone_halfspaces`, `controls`, `global_phase_boundary_sharpness`,
   `outside_cone_semantics`);
   `research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json`
   (`support2_cone`, `qg2_binding.objectives`, `proof_audit`);
   `research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`
   (`objectives.O1.new_trade_witnesses.NEW_SUPPORT3`).

5. **Fig. 5 — Sound but loose: the 5-versus-1 gap.** A two-column panel. Left
   column, R6M: syndrome rank 2 (six frame slots, complete 16,384-row domain)
   sitting exactly on the earned support-2 theorem — pipeline and truth coincide,
   badged `RECOVERED_FROM_EXISTING_R6S_CERTIFICATE`. Right column, R6I: syndrome
   rank 5 (both blocks, complete 4,096-row domain) drawn as a tall bar against
   κ = 1 drawn as a single unit, with the gap shaded and labelled "sound but
   loose — the rank bounds the search, not the optimum". A footer strip converts
   the gap into search sizes, O(n⁵A⁵) versus O(nA), scoped
   `CERTIFIED_COMPONENT_ONLY`. Caption records QG-6's own refusal
   (`support_theorem_status: PENDING_QG1_INDEPENDENT_DUAL_HARNESS`). Sources:
   `QG6_SYNDROME_DIMENSION_RESULTS.json` (`r6m`, `r6i`,
   `search_complexity_corollary`); `QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json`
   (`intrinsic_support_number`).

6. **Fig. 6 — Where per-block syndrome-preserving grammars can and cannot go.**
   A schematic of the rank-5 syndrome quotient as a shaded region containing all
   V2/V3/V4 moves (per-block, Tag fixed, zero five-bit syndrome change), with the
   V6 move drawn as an arrow leaving the region entirely — relocating the shared
   Tag across the whole system. Inside the region, the three residual censuses
   (36 / 21 / 36) are plotted as shrinking-but-never-empty remainders across the
   three grammars, with the closure fractions 324/324 and 396/432; 288/288 and
   591/612; 300/300 and 36/72. Caption: enlarging the move menu repairs the last
   residue and produces a new one; the rank is the ceiling the class cannot pass.
   Sources: the four QG-9 receipts of Fig. 2; `QG6_SYNDROME_DIMENSION_RESULTS.json`
   (`r6i.auto_dimension: 5`, `r6i.rewrite`);
   `development/orion-qg-regime-geometry/QG_WAVE2_RECORD.md` ("Method finding";
   "sound but loose").

Table candidates (already in the manuscript, may render as figures at
submission): the ladder rung/terminal table (Section 2), the QG-16 exact rational
control table (Section 5.1), and the cross-family κ table (Section 7). The κ
table must keep its OPEN cells — κ_TARE's exact value and both cones' global
sharpness — rendered as explicit OPEN badges rather than blanks.

Forward slots: if a successor lane establishes κ_TARE from below, Fig. 1 gains a
second collapsed interval for R6M and the Section 7 table's OPEN cell closes; if
a phase-sharpness counterexample or a larger cone lands for either family
(registered successors under `successor_permission` in
`QG16_PROTECTED_RUN_RECEIPT_2026-08-21.json`, and the QG-17 sharpness protocol
`development/orion-qg-regime-geometry/QG17_R6I_PHASE_SHARPNESS_PROTOCOL_V1.md`),
Fig. 4's hatched exteriors are redrawn and the OPEN badges update — but not
before, and never by inference from the current receipts.

Prohibited in every rendering: any depiction of a cone exterior as "support N
required"; any bar chart that shows an obstruction census as a tightness result;
any presentation of V5's empty result as positive evidence for support 1; and any
axis, badge or caption implying hardware, wall-clock, or physical
quantum-advantage claims.

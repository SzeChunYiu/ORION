# Paper QG1 figures plan

All figures are generated from committed receipts only; no new computation on
subjects. Paths relative to repository root.

1. **Fig. 1 — The template as a pipeline, with both instances.** Five-component
   schematic (donor-optimal region → elementary trades → sufficiency bounds →
   membership predicate → prospective forecast) with the lane discipline rail
   underneath (freeze → exact implementation → hostile gates → receipts →
   double-run replay), annotated with the TARE and SixLCU stage outcomes side by
   side (TARE: dominance PASSED with declared gap / two trades / support-2 →
   R6S theorem / exact P1 / R6R+QG-3 confirmed; SixLCU: dominance REFUTED at 30
   columns / trades generic / no strict sub-extension / exact P0 / forecast
   slot open). Sources: `papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V1.md`;
   `research/extensions/orion-qg/QG4_SECOND_FAMILY_RESULTS.json`
   (`stage_outcomes`).

2. **Fig. 2 — Two geometries, two shapes.** Side-by-side regime maps:
   (a) TARE structured-n2 (donor-exact 6453 / split 2322 / borrow 486 of 9261;
   `research/extensions/orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json`,
   `panels`); (b) SixLCU exhaustive-n2 (trades 38,759 of 38,760, the unique
   incumbent-exact instance {XI,YI,ZI,IX,IY,IZ} marked as a point;
   `QG4_SECOND_FAMILY_RESULTS.json`, `stage2_trade_search.domains.exhaustive_n2`;
   packet lane QG-4). Caption states the field lesson: the template transfers,
   the shape does not.

3. **Fig. 3 — The bound grows with the grammar.** Diagram contrasting the R6S
   F₂² pigeonhole (support bound 2, R6M grammar; four w=2 failing patterns)
   with the QG-1 F₂³ pigeonhole (support bound 5, R6I grammar; exceptional
   census 32 N-side + 6 C-side patterns, coincidence/non-coincidence column
   split, solo worst case +4 vs pair ≤ −4). Sources:
   `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`;
   `research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json`
   (`exchange_construction`, `lemma_e_solo`, `lemma_e_pair`,
   `boundary_solo_at_coincidence`, `lemma_b_n`, `lemma_b_c`).

4. **Fig. 4 — The geometry is objective-indexed.** Sankey/transition diagram of
   the 9,261 structured-n2 instances from O0 regimes to O1 regimes (6,014
   DONOR_EXACT→BORROW, 1,738 SPLIT→BORROW; chemistry inset 30/30 donor-exact →
   0/30), with the O2 panel as an unchanged identity map (constant shift +45),
   and the NEW_SUPPORT3 witness (C_DP 11 < C_D++ 13 < C_D+ 23) called out.
   Source: `research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`
   (`objectives.O1.membership_transitions`, `objectives.O1.panels`,
   `objectives.O2`, `objectives.O1.new_trade_witnesses.NEW_SUPPORT3`).

5. **Fig. 5 — Prospective validity across the regime map.** (a) QG-3 staged-row
   table: 90 library matchings (benzene, 12 and 14 qubits) + 12 engineered
   instances (4 split / 4 borrow / 4 donor-exact), predicted-vs-truth all
   102/102, with the stage-1 digest timeline (digest `1335f058…` printed before
   any DP). (b) QG-5 benchmark bar: 9,261 + 45 + 239 exact vs the single n=3
   miss, with the counterexample's costs (C_DP 10 vs forecast 11) and the
   out-of-support borrow-home mechanism sketched. Sources:
   `research/extensions/orion-qg/QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`
   (`track_a`, `track_b`, `stage1_digest`);
   `research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json`
   (`benchmark`, `nonzero_errors_verbatim`).

6. **Fig. 6 — SixLCU sufficiency ladder.** Residual counts along the frozen
   enlargement ladder 39,723 → 39,663 → 36,509 → 11,466 → 0 and along the
   block-size axis 8,673 / 1,131 / 168 / 60 / 0 (s = 2..6), annotated with the
   closing point (j = 4, s = 6) and the contrast to TARE's support-2 closure.
   Source: `QG4_SECOND_FAMILY_RESULTS.json` (`stage3_sufficiency`).

Table candidates (already in the manuscript, may render as figures at
submission): the wave-1 lane-outcome table implicit in Sections 4–7 (five lanes
× closure mode × headline number), and the residual ledger R1–R7 (Section 9)
as a wave-2 roadmap graphic sourced verbatim from
`development/orion-qg-regime-geometry/QG_WAVE1_CLOSURE_PACKET.md`.

Forward slots: if the QG-5b exact forecaster (residual R1) lands, Fig. 5(b)
gains a "repaired by theorem" panel showing zero error over the re-based
support-≤2 family and the caption upgrades from refutation to
refutation-plus-repair; if a QG-1 tightness witness (R5) lands, Fig. 3 gains a
"bound attained" badge at 5; if the R7 hunt finds a real trade-regime chemistry
batch, Fig. 5(a) moves it to the front of the figure.

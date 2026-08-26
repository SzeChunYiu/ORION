# Paper ORION-01 figures plan

All figures are generated from committed receipts only; no new computation on
subjects. Paths relative to repository root.

1. **Fig. 1 — Family lattice and containment sandwich.** Diagram of
   R6L ⊂ D+ ⊂ D++ ⊂ full R6M grammar with the cost sandwich
   `C_DP ≤ C_D++ ≤ C_D+ ≤ C_R6L`, annotated with which result separates or
   collapses each inclusion (Result 2 separates R6L/D+; Result 3 separates
   D+/D++; Result 4 collapses D++/DP on verified domains). Source:
   `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` (`dxx_definition`).

2. **Fig. 2 — The two trade witnesses, drawn as circuits/frames.**
   (a) `n2_b`: anchors A@q0, B/C@q1, Tag Y⊗Y, cost 8 vs donor 9
   (`MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`, `domains.r6n_panels` row `n2_b`).
   (b) instance_index 16: weight-2 central frame Y⊗Y on block C, Tag X@q0, with
   the cost ledger 0+0+2+2+1=5 broken out per term
   (`MAX_R6P_..._RESULTS.json`, `domains.structured_n2.critical_witness_samples[0]`).

3. **Fig. 3 — Regime map of the structured n=2 panel.** 9261 instances
   partitioned into donor-exact 6453 / split 2322 / borrow 486, with the
   predicate's zero-error confusion matrices for all four panels as an inset
   table. Source: `MAX_R6Q_REGIME_PREDICATE_RESULTS.json` (`panels`,
   `selected_confusion`).

4. **Fig. 4 — Critical-set closure.** Histogram of the 559 R6O critical gaps
   (all of size 1–2) and their closure at weight two (C_D+ − C_DP vs
   C_D++ − C_DP = 0). Source: `MAX_R6P_..._RESULTS.json`
   (`domains.structured_n2.critical_rows`, `domains.random_panel.critical_rows`).

5. **Fig. 5 — Applied grounding.** (a) R4B: LiH subnormalization of the optimal
   split (0.9009) against the random-split distribution (p05/p50/p95 =
   1.0177/1.1121/1.1703) and Pauli-L1 floor 0.8971
   (`MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`, `lih_public_subject`).
   (b) R4D: H2O C reduction 8078 → 4972 at 9.1e-6 overhead
   (`MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json`).

Table candidates (already in the manuscript, may render as figures at
submission): the Lemma 1 domain/violation table (Section 3.1) and the D++
closure-domain table (Section 3.4).

Forward slots: if `MAX_R6R` (prospective fresh subject) lands, its
predicted-vs-computed table becomes Fig. 6 and moves to the front of the applied
section; if `MAX_R6S` (all-n composition) lands, Fig. 1 gains a "theorem" badge
on the D++/DP collapse and Fig. 4's caption upgrades accordingly.

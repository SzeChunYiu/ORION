# Paper ORION-10 figures plan

All figures are generated from committed receipts only; no new computation on
subjects, no DP re-runs. Paths relative to repository root.

1. **Fig. 1 — The certificate architecture.** Block diagram of the forecaster
   F(t) = min(C_R6L, C_Dplus, f_B) with its four certificate components, each
   badged with its verbatim proof status (PROVEN_CONSTRUCTIVE /
   PROVEN_ALL_N_MACHINE_CHECKED_THEOREM /
   MACHINE_EVIDENCED_ON_VERIFIED_DOMAINS__CONJECTURE_FOR_ALL_N /
   MACHINE_EVIDENCED_ON_VERIFIED_DOMAINS) and its backing receipt. Overlay:
   which components held and which failed on the counterexample (Section 5).
   Source: `research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json`
   (`forecaster.certificate_basis`).

2. **Fig. 2 — Prospective staging timeline (QG-3).** Timeline strip: protocol
   freeze → stage-1 digest `1335f058…` printed → DP referee → 102/102 matches.
   Two lanes: Track B engineered quotas (4 split predicted 11 → refereed 11;
   4 borrow predicted 7 → refereed 7; 4 donor-exact) and Track A library scan
   (6 batches, 90/90 donor-exact, first 14-qubit subjects). Source:
   `research/extensions/orion-qg/QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`
   (`stage1_digest`, `track_b.staged_instances`, `track_a`).

3. **Fig. 3 — Benchmark accuracy panel.** Stacked bar or table-figure of the
   9,546 DP-compared instances by domain (structured n=2: 9,261/9,261; H4
   15/15; eq-N2 15/15; Benzene 15/15; fresh panel 239/240), with the single
   miss rendered as an explicit, labeled cell — not absorbed into a
   percentage. Inset: fresh-panel predicted regime census 153/26/61. Source:
   `QG5_CERTIFIED_FORECAST_RESULTS.json` (`benchmark`).

4. **Fig. 4 — Speedup distributions.** Violin/box plots of per-instance
   forecast-vs-DP speedup: fresh panel cold (median 9.84x, p10 3.58x, p90
   18.44x, max 25.09x), split by n (n=2 median 15.72x, n=3 median 4.21x), and
   warm-cache structured n=2 (median 3.24x, min < 1 shown honestly). Caption
   notes the R6P convention (timing non-canonical, stderr/receipt-only).
   Source: `QG5_CERTIFIED_FORECAST_RESULTS.json` (`timing`).

5. **Fig. 5 — The counterexample, drawn.** (a) The verbatim n=3 instance
   (seed 20260826, index 7) with its cost line C_DP = 10 < 11 = C_R6L =
   C_Dplus = f_B. (b) Mechanism sketch: the support-2 frame with its borrow
   home qubit outside the block's target support, contrasted with the frozen
   B(t) family's in-support restriction — the third elementary trade
   configuration. (c) Certificate scorecard for this instance: components 1–2
   HELD, components 3–4 FAILED. Sources:
   `QG5_CERTIFIED_FORECAST_RESULTS.json`
   (`benchmark.fresh_seeded_panel.nonzero_errors_verbatim[0]`);
   `development/orion-qg-regime-geometry/QG_WAVE1_CLOSURE_PACKET.md` (QG-5
   slot, mechanism localization).

6. **Fig. 6 — Repair lattice and objective indexing.** (a) Family lattice
   {C_R6L, C_Dplus, f_B} ⊂ D++ = DP (all n, by the R6S theorem), showing the
   counterexample living in D++ \ (three enumerated families) and the QG-5b
   repair path (minimize over full support-≤2; provably exact). (b) The same
   lattice under objective O1, where support-3 pays (C_DP = 11 < C_Dxx = 13 <
   C_Dplus = 23; 53 support-2 closure failures) — a visual warning that every
   badge in Fig. 1 is objective-scoped. Sources:
   `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`
   (`theorem_statement`);
   `development/orion-qg-regime-geometry/QG_WAVE1_CLOSURE_PACKET.md` (residual
   R1); `research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`
   (`objectives.O1`).

Table candidates (already in the manuscript, may render as figures at
submission): the certificate-basis table (Section 2.2), the benchmark domain
table (Section 4), and the library forecast table with per-row
DP_RECEIPT_COMMITTED / UNVERIFIED_FORECAST status badges — the latter must keep
its "verification authority: NONE" annotation in any rendered form.

Forward slots: when the QG-5b receipt lands (wave-2 R1), Fig. 1's component-3
badge upgrades to PROVEN for the enlarged forecaster and Fig. 6a gains an
"executed" marker; if the frozen hunt for a real trade-regime chemistry batch
(residual R7) ever lands a positive, it becomes a new panel in Fig. 2.

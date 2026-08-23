# QG-23 — converting N4: the forecast was refuted by leaving its own support, not by being wrong

Date: 2026-08-22
Lane: ORION-QG / regime geometry, wave 3
Branch: `claude/orion-harness-verification-b17qdj`
Base revision: `aaf0987a`
Status: **FROZEN BEFORE ANY OUTCOME-DETERMINING RUN.**

Authority ceiling: **NOT_R6**. `novelty_authority: false`,
`physical_quantum_advantage_claim: false`. No chemistry data is read. No network. The
protected stretched-N₂ discriminator
`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`
is never read. Every committed analyzer is imported **unmodified**.

Runtime cap: **< 45 minutes per run**, wall clock, single process. Every cap disclosed.

---

## 0. The negative being converted, stated as it stands

N4 in the conversion ledger: **prospective forecast refuted at n=4**. Concretely, from two
receipts:

* QG-15 component 5: the held-out n=4 panel refutes the forecast — regime 100/120, cost
  67/120 — with the stage digest stamped before any n=4 referee call.
* QG-15c: the V2 cell-lookup rule is refuted **32/120**, and the receipt records the
  reason in one line — ***120/120 V2 vectors are unseen at n=4***, because `C_D`, `LB` and
  `C_E3` leave the n≤3 grid entirely. The lattice predicate does better, 3/120, the best
  held-out number in the series, and still not exact.

The reopen adjudication classified N4 `FAILED_DEFINITION` and predicted the move: **make
the n-dependence explicit**; expected positive, an n-scaling law or a certified
extrapolation range.

## 1. The hypothesis this lane freezes, before measuring anything

**H0 (the support hypothesis).** The n=4 refutation is dominated by **support failure, not
model failure**. Several V2 features are *extensive* — they grow with n — so an n=4
instance's feature vector is outside the convex/lattice support of the n≤3 training grid
by construction, and any lookup or grid rule is being asked to extrapolate, not predict.

**H1 (the normalization hypothesis).** There is a normalization of the extensive features,
derivable **from n≤3 alone**, under which n=4 vectors fall back inside the n≤3 support for
a measurable fraction of the panel, and the forecast on that covered fraction is
substantially better than the uncovered fraction.

**H0 and H1 can both fail, and the lane must report it if they do.** If normalized n=4
vectors remain outside support, or if in-support accuracy is no better than out-of-support
accuracy, that refutes H1 and the correct terminal is the refutation branch in §6. A lane
that finds the extensive/intensive split explains nothing has still converted N4 — into a
*diagnosed* negative rather than an unexplained one — and must say so plainly rather than
searching for a rule that rescues the forecast.

## 2. Frozen objects

* Family: **StabPrep**, exactly as committed in QG-15/15b/15c. Gates H/S/SDG cost 1,
  CNOT cost 3. Exact Dijkstra referee over the complete stabilizer-state graph.
  |S_n| = 6, 60, 1080, 36720 at n = 1,2,3,4.
* Vocabulary: **V2 verbatim** from QG-15c — V1's 13 features plus the 20 schedule/path-aware
  features. No feature is added, removed or redefined by this lane. In particular the
  **negative-sign census that QG-15c deliberately declined to add is still declined**;
  adding it here would be the same post-hoc tuning one lane removed.
* Training domain: **n ∈ {1,2,3}**, complete.
* Held-out domain: the **same 120-instance n=4 panel** QG-15c used, identified by its
  committed selection rule, so this lane's number is directly comparable to 32/120 and
  3/120 rather than to a fresh panel of its own choosing.

## 3. Q1 — the extensive/intensive census (measured, no forecasting)

For each of the 33 V2 features, computed on the complete n ≤ 3 domains:

1. Fit `f(n)` against n over n ∈ {1,2,3} in both a linear and a log-log coordinate, and
   report slope, intercept, `r²`, residuals and domain for both — never a slope alone.
2. Classify each feature into exactly one frozen class:
   * `INTENSIVE` — range does not grow with n (bounded ratio across n);
   * `EXTENSIVE_LINEAR` — range grows ~linearly in n;
   * `EXTENSIVE_OTHER` — grows, but not linearly; the measured form is reported;
   * `DEGENERATE` — constant or single-valued on the training domain, hence carrying no
     information about n.
3. Report, per class, how many of the 120 n=4 panel vectors fall outside the n≤3 observed
   range **on that feature alone**. This is the per-feature support-failure census, and it
   is what tests H0: if `INTENSIVE` features alone already put the panel out of support,
   H0 is wrong and the lane must say so.

Three points is a weak fit and the receipt must say so at every use: slopes from n ∈
{1,2,3} are reported as **measured trends with three points**, never as scaling laws.

## 4. Q2 — the normalization, derived from n≤3 only, then frozen

Derive a normalization map `φ_n` from the Q1 census **using only n ≤ 3 data**:
`EXTENSIVE_LINEAR` features are divided by their fitted linear form in n; `EXTENSIVE_OTHER`
by their measured form; `INTENSIVE` and `DEGENERATE` features pass through unchanged.

Then, in this order, with the ordering enforced by the staging gate G3:

1. **Stamp**, before any n=4 referee call: the frozen `φ_n`, the frozen predictor
   (QG-15c's cell-lookup rule and lattice predicate, unchanged, refit on normalized n≤3
   features), the 120 normalized n=4 feature vectors, and the 120 **predictions**. Digest
   this stage-1 object and print the digest. It must contain **no referee output**.
2. **Only then** call the referee on the n=4 panel and score.

Report:
* **coverage** — how many of 120 normalized vectors are in-support at n=4, against 0/120
  un-normalized (QG-15c's `120/120 unseen`);
* **accuracy on the covered set** and **accuracy on the uncovered set**, separately. The
  comparison of those two numbers is the entire test of H1; a normalization that raises
  coverage without separating accuracy has explained nothing.
* the un-normalized baselines **32/120** (cell lookup) and **3/120** (lattice) recomputed
  in-run rather than copied, so the comparison is like-for-like.

## 5. Q3 — the abstaining forecaster and its certified competence region

The object N4's conversion is actually worth: a forecaster that **declares where it is
entitled to predict**.

Define `PREDICT` if the normalized vector is in-support, `ABSTAIN` otherwise. Report the
full **coverage/accuracy trade-off curve** over a frozen ladder of support-radius
thresholds — at each threshold, the fraction predicted and the error rate among predicted.
An abstaining forecaster is only meaningful with both numbers; either alone is trivially
gameable (abstain always, or predict always).

**Prospective component, conditional and capped.** If a complete n=5 referee is reachable
inside the runtime cap — |S_5| = 2,423,520 states, and costs are in {1,3} so a Dial
bucket queue applies — hold out **n=5 entirely**, stamp the abstaining forecaster's
predictions and its abstain set **before** any n=5 referee call, and score. If it is not
reachable, **do not attempt a partial n=5 panel**: record `n5_attempted: false` with the
measured reason and the observed state count, and leave the prospective component
`NOT_ATTEMPTED`. A sampled n=5 panel chosen after seeing n=4 results is not a prospective
test and is forbidden by G5.

## 6. Terminals, frozen

* `QG23_N_DEPENDENCE_EXPLAINS_THE_REFUTATION__CERTIFIED_REGION_ESTABLISHED` — H0 and H1
  both borne out: normalization raises coverage materially and in-support accuracy
  separates from out-of-support accuracy, and the abstaining forecaster carries a stated
  competence region with its trade-off curve.
* `QG23_PARTIAL__SUPPORT_DIAGNOSED_BUT_NORMALIZATION_DOES_NOT_TRANSFER` — H0 borne out
  (the panel is out of support, and the census says on which features), H1 refuted
  (normalization does not restore coverage, or coverage rises without accuracy
  separating). N4 converts to a diagnosed negative.
* `QG23_H0_REFUTED__THE_FORECAST_IS_WRONG_NOT_MISAPPLIED` — the panel is substantially
  in-support already, so extrapolation is not the explanation and the refutation is a
  genuine model failure. This is a real possible outcome and must be reported as such.
* `QG23_BLOCKED__REFEREE_OR_DOMAIN_UNREACHABLE` — with the measured reason.

## 7. Gates

* **G1 — receipt bindings exact.** QG-15, QG-15b and QG-15c receipts are re-read and the
  bound values (32/120, 3/120, 100/120, 67/120, floor 1, 1 mixed cell, the V2 feature
  count) matched exactly. Any mismatch fails the gate rather than being reconciled.
* **G2 — no vocabulary change.** The 33 V2 features are used verbatim. The negative-sign
  census stays out. Any added feature fails the gate.
* **G3 — prospective staging enforced structurally.** During stage 1 the referee entry
  points are replaced by a raising stub, exactly as QG-15c enforced admissibility, so a
  referee call during prediction is impossible rather than merely prohibited. The stub
  must be recorded as never triggered.
* **G4 — both fits, both coordinates, residuals and domain.** No slope reported alone; no
  three-point fit described as a law.
* **G5 — no panel reselection.** The n=4 panel is QG-15c's, by its committed rule. No
  n=5 sub-panel may be chosen after any n=5 outcome is observed.
* **G6 — abstention reported two-sided.** Coverage and accuracy always together.
* **G7 — no silent truncation.** Every declared domain executed in full with its size
  recorded, or named as not attempted with the reason and the measured obstacle.
* **G8 — authority ceiling NOT_R6**, `novelty_authority: false`.
* **G9 — determinism.** Double run, byte-identical outside the timing section; timing
  excluded from `result_digest`.
* **G10 — H0/H1 stated before measurement.** §1 is frozen here; the results must state
  for each hypothesis whether it was borne out, including when the answer is no.

## 8. Files this lane may create

1. `research/extensions/orion-qg/qg23_forecast_n_dependence.py`
2. `research/extensions/orion-qg/QG23_FORECAST_N_DEPENDENCE_RESULTS.json`
3. `development/orion-qg-regime-geometry/qg23_generic_verify.py`
4. `development/orion-qg-regime-geometry/QG23_GENERIC_VERIFICATION.json`

No other repository file is created or modified.

## 9. What this lane cannot do

It cannot revise QG-15's or QG-15c's receipts — their refutations stand as issued, and
this lane's outcome is scored beside them, not substituted for them. It cannot claim the
forecast was "really right all along": a forecaster restricted to a competence region is a
**different, weaker object** than the one that was refuted, and the results file must say
so in those words. It cannot grant novelty. It cannot read the protected subject.

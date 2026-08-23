# QG-24 — the applied ceiling: does regime geometry reach the rotations, or only the Cliffords?

Date: 2026-08-22
Lane: ORION-QG / quantum application, wave 3
Branch: `claude/orion-harness-verification-b17qdj`
Status: **FROZEN BEFORE ANY OUTCOME-DETERMINING RUN.**

Authority ceiling: **NOT_R6**. `novelty_authority: false`,
`physical_quantum_advantage_claim: false`. The protected stretched-N₂ subject
`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`
is never read. Committed analyzers are imported **unmodified**.

Runtime cap: **< 45 minutes per run**. Every cap disclosed.

---

## 0. The ceiling this lane exists to attack

QG-21 measured the applied ceiling of this entire programme and it is severe.
Every compilation in the frozen grammar carries exactly **9 arbitrary-angle
rotations** (`ROTATIONS_R6M == 9`, verified in-run) that **no family member can
change**. Under a fault-tolerant objective those rotations dominate: T cost is
paid per rotation and is *independent of axis weight*. So TARE regime geometry
can only optimize Clifford structure — **under 1 % of fault-tolerant cost**.

The improvement is real and it is negligible where it counts. That is the honest
statement, and it bounds every applied claim the programme can make.

The question this lane asks is the only one that lifts it: **is the rotation
count itself a regime-geometry object, or is it structurally out of reach?**

## 1. Donor search runs FIRST, and gates the rest

**This lane may not freeze a novelty claim before its donor search completes.**
Enforced by `orion_research_harness.donor_search`, which fails closed on a
novelty assertion lacking a verdict, the three query families, or a verbatim
passage. This is QG-19's finding turned into a precondition: six novelty claims
frozen without literature access, six subsumed.

**Prior expectation, recorded before searching (this lane expects to be
subsumed).** Rotation-count and T-count reduction is a heavily worked area.
Phase polynomials, Pauli-rotation merging, `T`-par, matroid partitioning, TODD,
Gray-Synth and the Clifford+T resynthesis literature all live here. The honest
prior is that **the merging criterion is known** and that this lane's
contribution, if any, is a *regime* statement about it — where the optimum sits,
decidably — not the merging rule.

Query families (all three mandatory, per `QUERY_FAMILIES`):
1. **Own vocabulary** — regime geometry, trade currency, decidable membership
   predicate, intrinsic support number, applied to rotation count.
2. **Donor-field translation** — phase polynomial optimization, T-count
   reduction, Pauli rotation merging, `{CNOT, T}` circuit synthesis, matroid
   partitioning for T-par, symplectic/Clifford conjugation of rotation axes.
3. **Inverted or survey** — lower bounds on T-count, hardness of T-count
   minimization, surveys of fault-tolerant resource estimation.

Every verdict binds a verbatim passage. `NO_PRIOR_ART_FOUND` binds the query log.
**A subsumed claim is a successful outcome here, exactly as in QG-19.**

## 2. Frozen objects

* Family: the committed R6M/TARE grammar, unmodified, with its 9 arbitrary-angle
  rotations as the object of study rather than a fixed background.
* Objective: **θ_rot**, rotation count, frozen here — one unit per
  arbitrary-angle rotation, **independent of axis weight**, exactly as QG-21
  derived from fault-tolerant accounting (and explicitly *not* O1, which QG-21
  refuted as non-derivable).
* Merge relation: two rotations are **mergeable** when they are about the same
  axis and separated only by operations that commute with that axis. Angles add;
  a merged pair costs one rotation. This relation is **donor mathematics and
  carries zero novelty credit** in this lane.

## 3. Q1 — is the count actually invariant? (measured, decides the lane)

QG-21 established `ROTATIONS_R6M == 9` *within the frozen family menu*. That is
a statement about the family, not about the grammar. So:

1. Enumerate the complete configuration space at the sizes the committed
   machinery admits, and record the rotation count of **every** configuration,
   not just family-optimal ones. Report the exact distribution.
2. If the count is 9 on every configuration, the ceiling is **structural** and
   Q2 is moot — report that and stop, because a rotation the grammar cannot
   remove is not a regime-geometry object.
3. If any configuration carries fewer than 9, the ceiling was a **family
   artifact**, not a grammar property — and QG-21's applied statement needs the
   qualification recorded here, in this lane's own results file, without editing
   QG-21's receipt.

Both outcomes are results. Outcome 2 is the more likely and is not a failure:
it converts a soft applied claim into a proved structural bound.

## 4. Q2 — conditional on Q1 finding variation: is there a regime?

Only if Q1 finds configurations below 9. Instantiate the five-component template
against θ_rot: donor-optimal region, elementary trades with minimal witnesses,
sufficiency bounds, a decidable membership predicate, and a **prospective
forecast on a held-out panel with its stage-1 digest stamped before any referee
call** (gate G4, structurally enforced with a raising stub, as QG-15c and QG-23
enforced it).

## 5. Q3 — the applied number, stated the way QG-21 stated its own

Whatever Q1 and Q2 find, report the **fault-tolerant fraction actually moved**:
rotations removed as a share of total FT cost, on the committed cost model. If
that fraction is again under 1 %, say so as plainly as QG-21 did. A lane that
lifts the ceiling by nothing must report the nothing.

## 6. Terminals, frozen

* `QG24_ROTATION_COUNT_IS_A_REGIME_OBJECT__CEILING_LIFTED` — Q1 finds variation,
  Q2 instantiates the template, Q3 reports a materially non-trivial FT fraction.
* `QG24_PARTIAL__VARIATION_FOUND_BUT_NO_CLEAN_REGIME` — Q1 finds variation, Q2
  fails to produce a decidable predicate or the forecast is refuted.
* `QG24_CEILING_IS_STRUCTURAL__ROTATION_COUNT_INVARIANT_IN_THE_GRAMMAR` — Q1
  finds 9 everywhere. The applied ceiling is proved, not merely measured, and
  the programme's applied claim is settled downward for good.
* `QG24_BLOCKED__DONOR_SEARCH_UNAVAILABLE` — retrieval unavailable, so §1's
  precondition cannot be met and no novelty claim may be frozen. The measured
  parts of Q1/Q3 may still be reported; nothing may be called new.

## 7. Gates

* **G1** — donor search complete and validated by
  `orion_research_harness.donor_search` before any novelty claim is frozen; the
  record is embedded verbatim in the results file.
* **G2** — θ_rot is derived from QG-21's fault-tolerant accounting and bound to
  its receipt; O1 is not used, and the reason is stated.
* **G3** — Q1 enumerates a complete domain at each declared size, or names the
  size as not attempted with the measured obstacle. No sampling presented as
  enumeration.
* **G4** — any prospective component stages predictions before referee access,
  enforced by a raising stub recorded as never triggered.
* **G5** — Q3's fault-tolerant fraction is reported even when it is negligible.
* **G6** — no edit to QG-21's receipt; a qualification is recorded here instead.
* **G7** — independent from-primitives verifier, demonstrated capable of failing
  on tampered copies.
* **G8** — determinism: double run, byte-identical outside timing; timing
  excluded from `result_digest`.
* **G9** — caps disclosed; NOT_R6; protected subject unread.

## 8. Files this lane may create

1. `research/extensions/orion-qg/qg24_rotation_regime.py`
2. `research/extensions/orion-qg/QG24_ROTATION_REGIME_RESULTS.json`
3. `development/orion-qg-regime-geometry/qg24_generic_verify.py`
4. `development/orion-qg-regime-geometry/QG24_GENERIC_VERIFICATION.json`
5. `development/orion-qg-regime-geometry/QG24_DONOR_SEARCH.md`

## 9. What this lane cannot do

It cannot claim physical quantum advantage. It cannot grant novelty — §1 can only
remove or narrow it. It cannot revise QG-21's applied ceiling by assertion; only
a measured distribution over a complete domain can qualify it. It cannot read the
protected subject.

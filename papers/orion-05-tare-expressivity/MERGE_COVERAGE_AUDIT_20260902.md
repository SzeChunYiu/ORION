# ORION-05 merge-coverage audit — 2026-09-02

**Audit basis:** `papers/orion-05-tare-expressivity/CLAIM_LEDGER_V4.md` (O5-P1..O5-P10) and
the claim statements of `papers/orion-05-tare-expressivity/MANUSCRIPT_V3_REFINED.md`
(§Abstract, §Contributions, §3, §4, §9 Claim boundary).
**Compared against:** ORION-01 canonical V4 surfaces —
`papers/orion-01-certificate-realization/MANUSCRIPT_V4.md` and `CLAIM_LEDGER_V4.md`.
**Predecessor:** `papers/orion-01-certificate-realization/submission/tier-b-closure-20260901/ORION05_MERGE_COVERAGE_AUDIT.md`
(2026-09-01, decided `MERGE_WITH_SIBLING`).

## Coverage table

| ORION-05 claim (V4 ledger) | ORION-01 V4 location checked | Coverage |
|---|---|---|
| O5-P1 all-`n` support-two exact optimum, frozen R6M three-block grammar/objective | `MANUSCRIPT_V4.md` §7 (Theorem 7 ceiling), §8 ("an exact optimum of support at most two for every admitted size"); ledger O1-V4-C6 `PROVEN-EXACT` | **Covered** |
| O5-P2 sharpness: complete support-one family cost 6 vs unrestricted optimum 5 | §8 two-site witness table, 117,649-tuple exact enumeration "minimum is 6", feasible support-two state costs 5, `kappa(F_M;C_M)=2`; ledger O1-V4-C6 | **Covered** |
| O5-P3 weight-two frame-for-Tag obstruction as the mechanism | §8 witness plus frame/Tag/Restore cost decomposition (Restore 1 vs 4 at the trade point) | **Partially covered** — the trade is exhibited by the witness and cost table; ORION-05's dedicated obstruction-mechanism narration (V3 §4) is not restated |
| O5-P4 raw `O(n^12)` six-slot support-two candidate count | Absent; §10.1's `Theta(n^B)` corollary concerns the dependent-triple product enumerator, a different family and statistic | **Not covered** (deliberately not promoted, per the 2026-09-01 audit) |
| O5-P5 static evaluator, 9,547 agreements | Absent from ORION-01 V4; `CLAIM_LEDGER_V4.md` submission rule routes ORION-05 static-evaluator records to the merged ORION-09/10 object | **Not covered** (routed to ORION-09/10 by design) |
| O5-P6 688,041,472-row local audit | Absent; §12's verifiers have different denominators (2,880 / 6,912 / 576 / 9,216 rows) | **Not covered** |
| O5-P7 refuted closed-form regime families; one open classification lemma | Absent from ORION-01 V4; ledger routes ORION-05 regime-refutation records to ORION-09/10 | **Not covered** (routed to ORION-09/10 by design) |
| O5-P8 bounded census carries no manuscript authority; unrun bridges stay `NOT_RUN`/`CANNOT_CHECK` | §12-§13 carry the analogous non-authority boundaries for ORION-01's own checks ("do not replace the all-size proofs or constitute external replication") | **Partially covered** (as boundary discipline; the ORION-05 census statement itself is absent) |
| O5-P9 no runtime, full-circuit, hardware, fault-tolerant, objective-robustness, or global-optimality claim | Abstract final sentence, §13 Limitations, ledger O1-V4-C15 `FORBIDDEN` (+ C16/C17 adverse) | **Covered** |
| O5-P10 bounded submission-date literature finding | §11 positions the work against donors; the ORION-05-specific bounded-search statement lives in `NOVELTY_REFRESH_FINAL_2026-08-22.md` | **Partially covered** (each paper carries its own bounded-search statement) |

## Verdict

**Omissions exist and are acceptable under the 2026-09-02 filing plan.** The uncovered
claims are O5-P4, O5-P5, O5-P6, and O5-P7 (plus the partial P3/P8/P10 elements); none is a
theorem the ORION-01 submission needs for its own argument, and each remains owned either by
ORION-05's own manuscript and ledger (P3 detail, P4, P6, P10) or by the merged ORION-09/10
object (P5, P7).

**Which situation holds:** the 2026-09-02 issue-#78 Tier-B plan files **ORION-05 separately
as the companion paper on the same QIC-class route (arXiv quant-ph first)**, so omissions
from ORION-01 are acceptable because ORION-05's own filing carries them. This supersedes,
**for filing routing only**, the 2026-09-01 local decision recorded in
`papers/orion-01-certificate-realization/CLAIM_LEDGER_V4.md` (submission rule: "ORION-05 is
absorbed into this submission rather than filed separately") and the 2026-09-01 audit's
"standalone package is retired and must not be submitted" terminal. That 2026-09-01 record
remains the science-coverage authority (the absorption analysis above independently
reproduces its dispositions from the ledgers); the 2026-09-02 re-route changes only where
each paper files, not what either may claim. The routing supersession is recorded in both
papers' `PUBLICATION_FREEZE_ADDENDUM_V2.md` (2026-09-02). No scientific ceiling is widened by
this audit.

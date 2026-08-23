# Q3 replacement prospective instances — protocol V2

**Frozen:** 2026-08-22  
**Scientific base:** `main@c5ba39fef4f25c46de5fb69bf07f50530f4693ca`  
**Authority:** protocol only until both instruments are frozen, independent scientific outcomes are later produced, and deferred scoring/replay completes.

This protocol is additive to V1. The original QG-7d and QG-15c slots are retained in the audit ledger but are not used prospectively because result-oriented remote successor branches became visible before Lane-A/Lane-B freeze. No outcome file from those branches was opened to score the instruments.

## Global contract

For both replacements:

1. No `qg19`/`qg20` branch and no `QG19*`/`QG20*` result artifact existed at the contamination check.
2. Q3 Lane A and Lane B must be frozen in repository commits before any QG19/QG20 scientific analyzer/result is added.
3. Q3 instruments may read only the scientific base and this protocol; QG19/QG20 result paths are excluded.
4. The later QG19/QG20 analyzers are independent scientific outcome producers: they must not import or read Q3 lane outputs.
5. `AGREE`, `PARTIAL`, `DISAGREE`, and `CANNOT_CHECK` are valid pre-outcome instrument relations.
6. Deferred scoring uses only the maps below. No denominator reduction is allowed.
7. Result replay must reproduce the outcome from the scientific analyzer independently of Q3 scoring code.

---

# Q3-R1 / QG-19 — outside-cone sharpness probe for R6M support two

## Frozen scientific state

QG8 proves all-`n` support-two sufficiency for R6M inside

`t_c >= 2*t_r` and `t_nc >= 2*t_r`.

The QG8 receipt explicitly states that **outside the cone the certificate is silent**; it is not evidence that support three is required. QG2 provides a farther-out objective with an exact support-three witness, so global objective-independence is already false, while local sharpness near a cone face remains unresolved.

## Frozen objective and panel

`O19 = (t_nc=4, t_c=3, t_tag=2, t_r=2, rho=0)`.

Margins relative to the QG8 sufficient cone:
- central: `3 - 2*2 = -1`;
- noncentral: `4 - 2*2 = 0`.

The scientific outcome producer will evaluate:
- every committed R6M hostile `n=1` and `n=2` panel;
- a deterministic random panel with seed `20260822`, 24 instances at `n=2` and 24 at `n=3`;
- exact unrestricted DP cost and exact support-<=2 family cost for every row.

The primary scientific event is whether any row has `C_DP < C_Dxx`.

## Question

> At a newly frozen objective just outside the central QG8 face, what is the responsible diagnosis before exact truth is opened, and what next scientific move should be taken?

## Diagnosis vocabulary

- `R1_CERTIFICATE_SILENCE_SHARPNESS_OPEN` — the theorem does not apply; current evidence does not decide whether support two remains exact at O19.
- `R2_SUPPORT3_LIKELY_NEAR_CENTRAL_FACE` — evidence is strong enough to predict a real support-three requirement near this face.
- `R3_OBJECTIVE_PARAMETERIZATION_OR_REFEREE_DEFECT` — the weighted evaluator should be audited before interpretation.
- `R4_CANNOT_CHECK`.

## Move vocabulary

- `M1_TARGETED_EXACT_OUTSIDE_CONE_PANEL` — run the frozen exact DP vs D++ panel before changing the family or theorem.
- `M2_ATTEMPT_STRONGER_BEYOND_CONE_PROOF` — seek a proof that extends support-two sufficiency beyond the QG8 face.
- `M3_ENLARGE_FAMILY_BEFORE_WITNESS` — add support-three structure before an exact witness.
- `M4_REAUDIT_WEIGHTED_REFEREE`.
- `M5_STOP_CANNOT_CHECK`.

## Deferred scoring

- any exact `C_DP < C_Dxx` row -> strongest alignment with `R2`; `M1` receives move credit because it is the frozen falsifier; `M3` does not receive primary credit without a pre-witness family definition;
- zero gaps on the entire frozen panel -> strongest alignment with `R1`; `M1` receives primary move credit; this remains finite evidence and does not prove an enlarged cone;
- evaluator mismatch -> `R3/M4`;
- invalid/unresolved run -> `UNRESOLVED`.

---

# Q3-R2 / QG-20 — objective scope of the SixLCU P0 boundary

## Frozen scientific state

QG12 proves, under the frozen equal-weight SixLCU objective, that the unrestricted family equals the unary incumbent iff predicate P0 holds for every admitted instance/all `n`. The theorem is objective-specific because its gain inequalities combine SELECT, PREP, and WIDTH coefficients.

## Frozen reweighted objective and domain

`O20 = 2*SELECT + 1*PREP + 1*WIDTH`.

The unary incumbent remains cheaper than the binary incumbent for every admitted nonzero batch because

`C_U = 4W + 15`, `C_B = 8W + 14`, and `W >= 1`.

The scientific outcome producer will recompute exact reweighted family cost using the same 203 partitions, factor choices and shared-width construction, and will test the **original P0 predicate unchanged** on:
- the complete ordered `n=1` domain (729 instances);
- the complete reorder-quotiented `n=2` multiset domain (38,760 instances).

## Question

> Before opening the reweighted census, should the theorem-grade P0 boundary be treated as structurally invariant or objective-scoped, and what is the responsible next move?

## Diagnosis vocabulary

- `S1_P0_BOUNDARY_OBJECTIVE_SCOPED` — changing SELECT weight can change which partition gains are profitable, so the old P0 iff boundary should be retested rather than transferred.
- `S2_P0_STRUCTURALLY_INVARIANT_UNDER_SELECT_RESCALE` — P0 is expected to remain the exact boundary despite the positive SELECT rescaling.
- `S3_REWEIGHTED_INCUMBENT_OR_REFEREE_SCOPE_DEFECT` — the comparison object is not stable enough to score.
- `S4_CANNOT_CHECK`.

## Move vocabulary

- `N1_COMPLETE_REWEIGHTED_CENSUS` — recompute exact labels and compare them with frozen P0 on the complete n=1/n=2 domain.
- `N2_PROVE_WEIGHTED_P0_THEOREM_FIRST` — attempt a symbolic weighted theorem before the census.
- `N3_TRANSFER_P0_WITHOUT_RETEST`.
- `N4_REAUDIT_REWEIGHTED_REFEREE`.
- `N5_STOP_CANNOT_CHECK`.

## Deferred scoring

- one or more P0/label mismatches under O20 -> strongest alignment with `S1/N1`;
- zero mismatches on the complete frozen n=1/n=2 domain -> finite alignment with `S2`, while theorem-level invariance remains unproved; `N1` receives move credit;
- incumbent/referee correction -> `S3/N4`;
- invalid/unresolved run -> `UNRESOLVED`.

## Required artifacts

For each replacement, before scientific execution:
- `QUESTION_FREEZE.json`;
- `SHARED_PACKET.json`;
- `LANE_A_RECEIPT.json`;
- `LANE_B_MANIFEST.json`;
- `LANE_B_RECEIPT.json`;
- `PREOUTCOME_AGREEMENT.json`;
- `EXPERIMENT_LOG.md`.

After scientific execution:
- independent QG result JSON;
- `DEFERRED_OUTCOME_BINDING.json`;
- `FINAL_SCORE.json`;
- replay receipt.

## Paper gate

Q3 can become content-ready only after both replacements are validly frozen, both independent outcomes exist, both scores are produced from this map, both scientific results replay, and D2/D3 instrument defects are explicitly disposed. The original contaminated slots remain visible in the series audit.
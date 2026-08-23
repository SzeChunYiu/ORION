# P4 H3 metric-degeneration revival receipt V1 (NR-03)

**Date:** 2026-08-23
**Lane:** NR-03 of `research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`
**Negative revived:** `P4.H3.V2.SATURATED` (`papers/paper-04-verified-scientific-discovery/CLAIM_LEDGER_V4.md`) — the backlog's "H3.V2 metric saturated at 1.0 for all 11 systems — comparison impossible". The saturated quantity is the registered H3 abstention-competence measurement `correct_cannot_check_rate` (`protocol/STATISTICAL_ANALYSIS_PLAN_V1.md:32`, hypothesis `P4.H3` in `protocol/PROTOCOL_V1.json`); the backlog's "method-authority" descriptor is loose naming for the same axis.
**Artifacts:** pre-registration `P4_H3_V21_PROTOCOL_PREREG.json` (this directory), computation `nr03_v21_informedness.py`, raw output `P4_H3_V21_RESULTS_V1.json`, machine receipt `P4_H3_METRIC_DEGENERATION_REVIVAL_RECEIPT_V1.json`.
**Pre-registration proof:** the protocol was committed as `dc8ec570` (author date 2026-08-23 23:00:20 +0200) before any outcome was computed. A concurrent session's branch reset in the shared checkout orphaned that commit; it is re-landed on this branch verbatim with the original author timestamp, and the orphan hash is preserved here as the ordering evidence.

## 1. What saturated, precisely

The frozen V2 campaign (`evidence/protected_v2/PUBLICATION_METRICS_V2.json`, campaign 31976589735) scored eleven systems on a 420-case mechanical-gold battery (60 PROMOTE / 330 BLOCK / 30 CANNOT_CHECK, 13 families). The registered H3 metric is the one-class marginal over the eligible family: `m(s) = (1/30)·Σ_{gold=CC} 1{terminal_s = CC}`. Published result: `m(s) = 1.0` for all eleven systems; registered comparison ORION − strongest frozen comparator (`provenai-citation-fidelity-influence`) = 0, CI [0,0], `NOT_SUPPORTED`.

## 2. Saturation root cause (the math)

Define the observable **cue** `z(case) = 1{evidence = [] ∧ retrieval_pool = []}` on the candidate-visible view of the v1 construction (the construction the published V2 campaign ran against, retained behind `--construction v1`).

**Fact 1 (cue sufficiency — verified 420/420).** On the v1 battery, `z = 1{gold = CANNOT_CHECK}` exactly: the `INSUFFICIENT_EVIDENCE` mutation is the only one that empties both lists (`generate_protected_cases.py`, v1 branch of `_case`), and every non-CC case carries a non-empty evidence list and pool (gate `GATE_CUE`).

**Fact 2 (forced abstention — verified per policy).** Every one of the eleven frozen policies contains an abstention trigger that fires whenever `z = 1`:
- six pool-emptiness triggers: `_attribution`, `_fire`, `_claimbench`, `_reward`, `_pooled` (`CANNOT_CHECK` iff `not _pool(view)`) (`host/run_baselines.py`);
- three assigned-object-absence triggers: `_provenanceguard`, `_provenai`, `_auditability` (`CANNOT_CHECK` iff `item is None`) (same file);
- one citation-absence trigger: `_citation` (`CANNOT_CHECK` iff no citation object present);
- `deepsciverify` stage-1 (`item is None` → `CANNOT_CHECK`, `host/run_baselines_v2.py`);
- ORION's non-compensatory gate aggregate (`host/run_candidate.py`): `item is None` forces `EXACT_CONTENT_BINDING`, `SOURCE_OWNERSHIP`, `SEMANTIC_SUPPORT`, `BEHAVIORAL_INFLUENCE` into `HardGateState.CANNOT_CHECK` while the untouched well-formed fields leave no gate FAIL, so the aggregate terminal is `CANNOT_CHECK`.

**Corollary (saturation is forced by the data, not by the scoring).** Facts 1+2 give, for every system s, the abstention set `A_s = {case : terminal_s = CC} ⊇ {z=1} = F`. The re-run verifies equality battery-wide: TP = 30 and **FA = 0 for all eleven systems**, so `A_s = F` identically. Therefore:

1. the published `m ≡ 1` is an identity of the decision data, and any statistic of the decisions restricted to F is constant across systems;
2. **strengthened:** the abstention decision vectors are identical on all 420 cases, so *every* abstention-axis statistic — one-class marginal, precision, informedness, any strictly monotone transform `φ(m)` of any of them — is constant across systems. A monotone transform of a constant is a constant; de-degeneration by re-normalization is mathematically impossible;
3. the registered H3 comparison is **unidentifiable on this instrument**: the observed decisions are compatible with any ordering of the eleven systems' evidential abstention competence.

## 3. One-stage attribution

**Data defect (instrument), not a metric-design defect.** The measured per-system quantities — the abstention decisions themselves — are identical across systems, and Fact 1+2 show this identity is *forced by the construction* (label recoverable from a construction cue; failure class `LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE`, `research/failures/2026-08-label-recoverable-from-construction-cue/`). The metric's one-class marginal is merely why the defect surfaced as a ceiling. The battery does separate the systems on the neighbouring promotion axis (false promotions 0–330 of 360, reproduced exactly below), which rules out "all eleven systems genuinely identical" as an explanation of the tie.

## 4. V2.1: pre-registered de-degenerate metric

`J_CC(s) = TPR_CC(s) + TNR_CC(s) − 1` (Youden informedness / bookmaker invariant) over the **full frozen battery** with the **same frozen decisions**: positives = 30 gold-CC, negatives = 390 gold-non-CC, `TNR = 1 − FA/390`. Measurement-theory justification, fixed before computation: a binary-terminal instrument measures a competence only chance-corrected over both error directions — J is 0 for every constant predictor (including always-abstain, which scores 1.0 under the V2 marginal) and 1 only for exact abstention-set identification. It reads exactly the decisions the V2 marginal discarded (negative-side abstentions), changes no case, gold label, or policy.

Gates (all green, `P4_H3_V21_RESULTS_V1.json`):
- `GATE_REPRO` — the regenerated v1 battery plus the eleven frozen policies reproduce every published per-system false-promotion count (0, 180, 210×3, 240×2, 300, 330×3 of 360) and 30/30 correct-CC. The re-run is the published campaign.
- `GATE_CUE`, `GATE_FAMILY_DECISIONS` — Facts 1 and 2 verified on the battery.
- `GATE_SEED` — an unrelated seed gives the identical (TP, FA, FP) triple for all eleven systems.

## 5. V2.1 scores (frozen eleven-system data)

| system | TP | FA | FP (published) | J_CC |
|---|---|---|---|---|
| ORION | 30 | 0 | 0 | 1.0 |
| provenai-citation-fidelity-influence | 30 | 0 | 180 | 1.0 |
| deepsciverify-abstract-to-full-escalation | 30 | 0 | 210 | 1.0 |
| provenanceguard-style-source-routing | 30 | 0 | 210 | 1.0 |
| rewardhackingagents-search-contamination | 30 | 0 | 210 | 1.0 |
| attributionbench-multisource-attribution | 30 | 0 | 240 | 1.0 |
| claim-level-auditability-provenance | 30 | 0 | 240 | 1.0 |
| fire-iterative-retrieve-or-verify | 30 | 0 | 300 | 1.0 |
| citation-presence-format | 30 | 0 | 330 | 1.0 |
| claimbench-sciclaimhunt-scientific-evidence | 30 | 0 | 330 | 1.0 |
| pooled-evidence-nli-support | 30 | 0 | 330 | 1.0 |

Registered pairing ORION − provenai: ΔJ = 0.0, paired case-bootstrap 95% CI [0.0, 0.0] (B = 10,000). All ten ORION-minus-other pairings are 0.0 with CI [0.0, 0.0].

## 6. Verdict (pre-registered outcome (b) INSTRUMENT_NULL)

The registered H3 comparison is **not supportable on the frozen V2 battery by any abstention-axis metric** — the corrected, chance-corrected metric saturates too, and §2 proves it had to. The honest converted claim: **the eleven systems are equivalent on this instrument's abstention axis** — an instrument null (the abstention family is cue-separable and every policy realizes the cue), *not* a competence equivalence and *not* a metric artifact. The comparison requires a construction whose abstention family is not cue-separable; that successor exists and has already run — the audited V3 battery (`research/campaigns/2026-08-21-p4-battery-v3-identifiable/`), where H3 is supported under its pre-registered exact-axis reading (`P4.H3.V3.CANNOT_CHECK.EXACT_AXIS`, `SUPPORTED_FOR_EXACT_AXIS_ONLY` in `CLAIM_LEDGER_V4.md`). This receipt closes the gap between those two records: it is the proof that no re-scoring of V2 could ever have produced the V3 result.

## 7. Boundary

- The v1 construction's label is recoverable from `z`; therefore even a non-null V2.1 would have measured how policies realize the cue, not evidential competence. The null reported here is the stronger, correct statement.
- No historical terminal is relabeled: `P4.H3.V2.SATURATED` stands exactly as recorded; this receipt adds the mechanism and the boundary, it does not convert the V2 record into a win.
- PR-956 discipline: FA counts only CANNOT_CHECK decisions on gold-non-CC cases; the PROMOTE/BLOCK distinction among non-abstentions enters only through the published reproduction gate. No unlike labels are aggregated into the abstention axis.
- Concurrent-lane note: NR-03 was transferred to the codex lane by the 2026-08-23 ownership split while this lane was in flight. This receipt is offered for absorption by whichever lane the programme keeps; the PR is left unmerged for that reconciliation.

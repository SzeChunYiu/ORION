# P14E specification-separated governance superiority — result receipt V1

**Terminal:** `P14E_SPECIFICATION_SEPARATED_SUPERIORITY_SUPPORTED` (first execution; all twelve frozen gates green)

**Result SHA-256:** `410db4554585e5ce9b6f94b01cc92d7f116f9fd693b60bca2e1ac1eeb4f51679`

**Freeze-before-execution:** protocol, rule table, and runner committed before the first benchmark execution. Two fresh-subprocess replay, cores byte-identical (`sha256 9950c27c2eebf885…`). Runtime ~4 s per subprocess, single process, stdlib only.

## What was executed

6,720 protected cases (fresh seed `2026082401`; 12 held-out families × 7 strata × 80), gold assigned by a generic interpreter over the frozen machine-readable rule table `P14E_ADJUDICATION_RULES_V1.json`, policies independently implemented facts-only functions (gold/stratum/case identity stripped before every call, verified live on every case). Nuisance reminting verified per family-by-stratum cell; fully pinned strata verified deterministic. Every arm charged the same seven-check decision receipt.

## One failure stage, three mechanic repairs (upward, thresholds unchanged)

| Parent | Defect (recorded) | P14E repair |
|---|---|---|
| P14A (gate-not-met) | case mixture capped the discriminator at 1.8375% prevalence; attainability supremum 0.042326 < 0.05/0.08 bars | balanced 7-strata protected mixture: history/reopen discriminator carries 2/7 of mass |
| P14B (non-authoritative) | ORION arm called the gold function (circularity) | gold = interpreted frozen rule table; ORION arm independently written from protocol prose; no-gold-leak gate live on all 6,720 cases |
| P14B (non-authoritative) | nuisance booleans not reminted across strata (conformance) | per-stratum free-coordinate sets frozen in the rule table; both-values-in-every-cell verification gate |

P14A thresholds unchanged: accuracy gain >= 0.08, strongest-baseline false promotion >= 0.05.

## Gate results

| Gate | Result |
|---|---|
| full disposition accuracy = 1 | GREEN — 1.0 (empirical, vs interpreted rule table) |
| full false promotion = 0 | GREEN — 0.0 |
| full useful-discovery recall = 1 | GREEN — 1.0 |
| retain-negative and supported-reopen exact | GREEN — 1.0 / 1.0 |
| strongest-baseline false promotion >= 0.05 | GREEN — MULTI_REVIEW 0.142857 |
| accuracy gain >= 0.08 | GREEN — 0.142857 |
| strongest baseline is MULTI_REVIEW | GREEN |
| every ablation strictly worse | GREEN — worst gap: screening ablations 0.978–0.980 accuracy; donor/interaction/history ablations 0.857143 |
| matched decision budget | GREEN — 7 checks every arm |
| gold never enters policy input | GREEN — 6,720/6,720 checks |
| nuisance reminting + determinism verified | GREEN — 0 violations |
| byte-identical two-subprocess replay | GREEN |

## Headline numbers

| Arm | Accuracy | False promotion |
|---|---|---|
| ORION_RSE_FULL (independent implementation) | 1.000000 | 0.000000 |
| MULTI_REVIEW (strongest baseline) | 0.857143 | 0.142857 |
| DONOR_AWARE_REVIEW | 0.714286 | 0.285714 |
| REFLECTION_CHECKLIST | 0.571429 | 0.428571 |
| RAW_POSITIVE | 0.428571 | 0.504762 |

MULTI_REVIEW retains 1.0 recall and reopen accuracy but 0.0 retain-negative accuracy — its misses concentrate exactly on the same-evidence rereading stratum the negative-history component exists to catch.

## Claim authority

In a preregistered, specification-separated, strata-balanced hidden-gold benchmark of 6,720 scientific admissibility decisions, the full ORION-RSE governance contract — implemented independently of the adjudicated gold specification — makes no false promotions, loses no valid discoveries, and strictly dominates the strongest partial-governance rule baseline at the original P14A thresholds.

Not authorized: real-agent, cross-domain, blinded external, longitudinal human-review, or autonomous-scientist superiority (P14D/external gates). P14A's negative, P14B's diagnostic status, and P14C's conformance authority are retained verbatim.

## Replay

```
python papers/paper-14-orion-rse/run_p14e_specification_separated_superiority_v1.py
```

Success condition: terminal `P14E_SPECIFICATION_SEPARATED_SUPERIORITY_SUPPORTED`, all twelve gates green, byte-identical two-subprocess replay. Failure terminal: `P14E_SPECIFICATION_SEPARATED_SUPERIORITY_GATE_NOT_MET` (exit 1).

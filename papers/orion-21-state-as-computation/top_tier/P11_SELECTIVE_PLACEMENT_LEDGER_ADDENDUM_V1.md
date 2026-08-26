# P11 selective placement ledger addendum V1

Additive evidence-ledger entry for NR-12 (`research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`),
to be folded into `CLAIM_EVIDENCE_LEDGER.md` / `README.md` / `P11_ACTIVE_CLAIM_AUTHORITY_V1.json`
in a later integration pass (this lane does not open PRs).

## Entry

- **Study:** `P11_SELECTIVE_PLACEMENT_V1` (protocol + runner + checker frozen pre-execution in commit `e8d76d93`).
- **Execution:** local (lane rule: no CI); primary and independent checker both exit 0; byte-identical replays; receipt `P11_SELECTIVE_PLACEMENT_RESULT_RECEIPT_V1.md` with digests.
- **Terminal:** `P11_SELECTIVE_PLACEMENT_V1_SUPPORTED` — selectively-placed family support LINEAR 9/10, RBF 10/10, KNN 10/10 vs the frozen >=8/10 bar (V1 compile-all: 3/5/5); no family below its frozen baseline; all resource identities hold (memory 64+16|S_f| never wins; break-even 1917/1918 per placed query; arrival tax only on the placeable subset).
- **Attribution (verified read-only on the frozen V1 receipt):** delta variance partitions 77.4% responsibility / 2.4% access / 20.2% interaction; q1,q3,q5,q8,q9 intolerant under every access class; failure stage of the V1 policy = PLACEMENT (compile-all), not compilation per se.
- **Claim impact:** the README's boundary sentence ("retain the raw 64-float state unless the responsibility family is small AND each member is individually compile-tolerant") gains a constructive counterpart: individual compile-tolerance is estimable train-only (inner-CV at the same frozen tolerance), and placement decided by that estimate meets the family bar that compile-all fails. The V1 negative itself is untouched.
- **Honesty record:** selector fold-cell LINEAR precision 7/16; query-level FP q5/q7/q9 (LINEAR), diluted by conservative partial placement (sizes 2–4 per fold); one genuine LINEAR miss (q9: inner −0.0019/−0.0014 vs test −0.0296); secondary seeds 20261122/23/24 all SUPPORTED.

## What closes / what opens

- **Closes:** NR-12 under stopping criterion (a) — revived positive with receipt + structurally independent second checker (exact agreement: identical placement bits, identical support counts, 0.0 mean deviation) + pre-registered generalization seeds.
- **Opens (not authorised here):** selector-precision improvement (fold-cell 7/16 is the honest weak point — a stricter inner threshold would need its own frozen protocol and would shrink |S_f| toward the laundering boundary); cross-dataset transfer of the selector rule; a deployed-cost study charging real compiler wall-clock. None of these may be run as quiet retunes.

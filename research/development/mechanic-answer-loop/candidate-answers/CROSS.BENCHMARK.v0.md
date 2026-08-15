# Candidate answer — CROSS.BENCHMARK.v0

**Target dimensions:** VERIFICATION, TRANSITION_MODEL, FAILURE.
**Incumbent evidence:** RAKL `publication/papers/paper-03-method-evolution-mechanics/sections/05_governed_upgrade_protocol.tex` @ `bd4ce50f` (§development evaluation versus fresh assurance; §evaluator migration) and `publication/papers/paper-05-verified-discovery-in-mathematics/ASSURANCE_V3_BINDING_ADDENDUM_20260815.md` @ `bd4ce50f` (executor-invariance replay).

## Proposed step-specific contract

**Verification — two evidence phases that never mix.** Visible development evaluation guides debugging; once exposed to the optimizer it is no longer blind. Strong claims consume a **fresh assurance packet frozen before the candidate existed and hidden from the proposer**; each peek spends a declared exposure budget, and an exhausted budget forces a new frozen packet, never reuse. Matched resources are part of the packet (a challenger with more compute has not beaten its parent). Hostile near-misses and negative controls ship with the packet, not after outcomes.

**Transition model.** Benchmark lifecycle: `PACKET_FROZEN(pre-candidate) -> DEVELOPMENT_EVAL(visible, repeatable) -> FRESH_ASSURANCE(hidden, budgeted) -> {ASSURED | REJECTED | META_OVERFIT | CANNOT_CHECK}`. The evaluator is frozen within an evaluation epoch; evaluator evolution is a separately governed parent mutation at an epoch boundary, benchmarked against known-answer and adversarial cases before prospective use — the optimizer never rewrites its own ruler after an inconvenient score. Executor-invariance replays are a licensed benchmark form: the same frozen artifact chain re-run across executor classes must reproduce the same verdicts.

**Failure.** Signatures: *assurance leakage* (fresh packet contents visible to the optimizer before judgment), *ruler rewrite* (evaluator changed inside the epoch that judges the candidate), *resource mismatch* (challenger beat parent on unequal budgets), *retrospective calibration* (results predating their packet presented as preregistered). Falsifier for any benchmark claim: show the packet's freeze timestamp does not precede the candidate's construction — one such case voids the claim class.

## Known-answer / hostile test candidates

1. Candidate evaluated only on exposed development cases → cannot leave `DEVELOPMENT_VALIDATED`.
2. Evaluator patched mid-epoch, candidate re-scored → verdict inadmissible.
3. Hostile: rerun assurance until it passes, discarding failures → exposure budget accounting must surface every consumption.

## Not licensed

Packet discipline does not by itself supply good benchmark *content* for any specific mechanic; step-specific known-answer and hostile cases remain per-cell obligations (several are proposed in the sibling candidate answers).

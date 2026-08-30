# Reusable sealed promotion for longitudinal self-improvement

Let `F_(j-1)` contain every public artifact before protected test `j`: prior candidate bytes, released decision bits, public/replay results, append-only history, resource receipts, evaluator-epoch metadata, and all previous error spending. Candidate `j`, its stopping decision, and its spend `alpha_j` may be arbitrary `F_(j-1)`-measurable functions.

Assume (i) `alpha_j >= 0` is predictable and the pathwise ledger satisfies `sum_j alpha_j <= alpha`; (ii) for every null candidate, its protected p-value is conditionally super-uniform, `Pr(p_j <= u | F_(j-1)) <= u`; and (iii) promotion requires `p_j <= alpha_j` plus every non-statistical veto.

## Global adaptive false-promotion theorem

Under those assumptions, arbitrary adaptive candidate generation and stopping satisfy

`Pr(at least one null candidate is promoted) <= alpha`.

For each null candidate, conditional validity gives `Pr(p_j <= alpha_j | F_(j-1)) <= alpha_j`. The promotion event is contained in the union of those rejection events. Conditional expectation, the union bound, and the pathwise spend constraint give the result. No fixed number of candidates is required.

The theorem does not make an invalid reused holdout valid. Conditional super-uniformity must be supplied by a prospectively valid reusable-holdout, e-process/confidence-sequence construction, fresh protected refreshes, or another proof that includes the actual one-bit feedback channel and evaluator epochs.

Promotion is non-compensatory. In addition to statistical rejection it requires fresh-task LCB `> +0.05`, retention LCB `> -0.02`, harm UCB `< 0.02`, no replay-only support, no authority violation, no resource overrun, and a complete hash-chained receipt. Large aggregate gain cannot compensate a protected harm or missing authority.

Negative, adverse, blocked, crashed, and `CANNOT_CHECK` episodes are inherited state. Every receipt binds the pre-history and post-history roots. Exact duplicates are idempotent; conflicting duplicates, history rewinds, stale evaluator epochs, alpha overrun, malformed receipts, and hash tampering block promotion.

The deterministic packet establishes the theorem statement under explicit assumptions and independently checks the control plane. It does not execute frontier agents, acquire external protected tasks, estimate longitudinal transfer, establish a negative-history effect, or authorize submission claims.

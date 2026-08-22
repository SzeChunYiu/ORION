# P2 comparison-resolution gate V1 — development packet

Date frozen: 2026-08-22
Branch: `codex/p2-resolution-gate`
Authority: prospective instrument precondition only; historical V1/V3 terminals and bytes remain unchanged.

## Development question

Can P2 prevent an all-ties, byte-identical, measurement-floor comparison from emitting a non-inferiority/equivalence/superiority interpretation in a successor campaign?

## Atomic questions

1. Are at least two candidate artifacts and at least two evaluator-output artifacts distinct?
2. Is the best arm's absolute measured IoU large enough that the registered effect margin is arithmetically reachable?
3. Does the paired split contain at least one discordant task rather than all ties?
4. Are sampled `max_iou_at_k` values monotone and excluded from the exact headline family when the upstream sampler is unseeded?
5. Are runtime/resource totals measured rather than uniformly encoded as zero?
6. Does any failed instrument precondition block every scientific comparison terminal?

## Negative history and saturation

P2 Wide V1 scored one candidate digest against itself. V3 had three candidate digests but one evaluator-output digest. Both produced 399/399 ties and `[0,0]` intervals with every arm near IoU 0.004 against a required 0.03 effect. The existing audit diagnoses this but the successor terminal interface does not yet require the audit to pass. A deterministic precondition over artifact identities, absolute headroom, paired discordance, monotonic reporting and measured runtime is sufficient for this defect.

## Frozen implementation hypothesis

If comparison resolution is an explicit fail-closed prerequisite, both historical Wide summaries will be refused while a non-degenerate control with distinct artifacts, reachable scale, mixed paired outcomes, monotone exact metrics and measured runtime will pass.

## Hostile tests

- identical candidates fail;
- distinct candidates with one evaluator output fail;
- an all-ties `[0,0]` interval fails at any N;
- arms below the effect margin fail even if their digests differ;
- non-monotone sampled metrics and uniformly zero runtime fail reporting integrity;
- a caller cannot request `NON_INFERIOR`, `SUPPORTED`, or another scientific terminal when the gate fails;
- the committed V1 and V3 audit entries fail; the committed control passes.

## Reopen triggers

Reopen if a legitimate non-IoU campaign needs another reachability calculation, if runtime is genuinely not part of its claim, or if evaluator outputs are content-addressed at a different granularity. Such a campaign requires a new typed adapter, not deletion of a check.


# ORION-19 V2 — the obvious fix for V1's blind spot does not work, and the reason is useful

**Terminal: `ESCALATION_PROBE_NOT_SUPPORTED`.**

V1 found that conflict count is blind wherever the solver is not conflict-driven.
The natural repair is to stop using a proxy and ask the question directly: re-run
at twice the failing budget and see whether more compute helps. It was frozen,
run, and it does not beat what it was meant to replace.

## All 40 instances, no split

| arm | accuracy | **false compute escalation** | factoring accuracy | solver-seconds to decide |
|---|---|---|---|---|
| `always_compute` | 0.3750 | 1.0000 | 0.3636 | 0.00 |
| `verdict_only` | 0.7500 | 0.4000 | 0.7273 | 0.00 |
| `resource_vector` (V1) | **0.9250** | 0.1200 | **0.7273** | 0.00 |
| `escalation_probe` | 0.6250 | **0.0000** | 0.6364 | **105.52** |
| `oracle` | 1.0000 | 0.0000 | 1.0000 | 0.00 |

## It wins the primary endpoint and still fails

`escalation_probe` never once falsely escalates compute — **0.0000**, better than
`resource_vector`'s 0.1200 and the only arm besides the oracle to reach it. On the
endpoint the protocol names primary, it is the best arm in the study.

The terminal is `NOT_SUPPORTED` because the frozen rule required **both** a lower
false-escalation rate **and** no loss on the factoring family, and factoring
accuracy fell from 0.7273 to 0.6364. The rule was written that way before the
numbers existed, and it is applied as written.

## Why it is conservative, which is the mechanism

**Doubling resolved only 15 of 40 instances.** The compute-starved variants run at
20% of the reference's own solving time, so doubling gives 40% — still short of
what the reference needed. Those instances do not resolve, the probe reads "more
compute did not help", and calls them `ACCESSIBILITY`.

So the probe is wrong in exactly one direction. It never says `COMPUTE` when
compute cannot help, which is why its false-escalation rate is zero, and it says
`ACCESSIBILITY` whenever its own escalation was too small, which is why its
accuracy is poor. **An escalation probe is only as informative as its escalation
factor, and a factor of two applied to a deliberately starved budget is still
starved.**

This is not a tuning oversight to be corrected by re-running with a bigger factor.
A practitioner does not know the reference budget — recovering it is the thing
being diagnosed — so the factor must be chosen blind, and any blind factor has a
regime where it is too small. The conservatism is structural.

## What it costs

105.52 solver-seconds spent purely on deciding, against zero for every other
non-oracle arm. The probe **spends compute to decide whether to spend compute**,
and on this instance set it spends roughly as much as re-running everything would.
An arm that reaches zero false escalation by paying more compute than the
escalation it avoids has not saved anything, and the accounting is reported here
rather than left implicit.

## What both versions together say

Neither feature is right. V1's statistic is accurate where the solver is
conflict-driven and blind where it is not. V2's probe is safe everywhere and
uninformative where its factor is too small, at a compute price that undermines the
saving it exists to make.

The pair localises the difficulty rather than resolving it: **diagnosing why a
formal-reasoning task failed is not free, and the two obvious instruments fail in
opposite directions.** A useful diagnoser would need to be cheap like the statistic
and architecture-independent like the probe, and this study contains no such thing.

V1's record and terminal are unedited.

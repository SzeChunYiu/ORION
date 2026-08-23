# P12B equal-action signal-complementarity protocol v1

**Frozen before protected execution.**  No P12B result is present in this
protocol commit.

## Claim

In the registered four-regime allocation world, a policy reading both noisy
pre-outcome signals selects the exact required allocation more often than the
stronger policy reading either signal alone when every policy has the same
four-action set and the same two-unit budget.

This is a controlled signal-complementarity claim.  It is not a claim about
naturalistic agents, open-ended tasks or superiority over external systems.

## Frozen world and arms

The four regimes and exact correct actions are:

| regime | exact action |
| --- | --- |
| `EASY` | `(0,0)` |
| `ACCESS` | `(2,0)` |
| `REASON` | `(0,2)` |
| `BOTH` | `(1,1)` |

Every evaluated arm may select exactly
`{(0,0), (2,0), (0,2), (1,1)}` and every action respects budget two.  The
`TWO_SIGNAL` arm sees `(s_c,s_r)` and chooses the nearest action by squared
Euclidean distance.  `STATE_SIGNAL` sees only `s_c`; `REASON_SIGNAL` sees only
`s_r`.  Each one-signal arm chooses the action with the nearest coordinate on
its visible axis, ties by the table order above.  The typed observation passed
to an arm contains no field for its withheld signal.

An episode scores one exactly when the chosen action equals the registered exact
action, and zero otherwise.  Coverage/dominance scoring from P12A is not reused.

## Units, panel and generation

- master protected seed: `2026082312`;
- 32 independent family RNG blocks (`n=32`);
- 1,024 technical episodes per family, exactly 256 per regime in random order;
- fixed noise strata `sigma={0.2,0.4,0.6,0.8}`, eight independently seeded
  families per stratum;
- signals equal the action coordinates plus independent zero-mean Gaussian noise
  of the family's fixed sigma;
- no episode is an independent inferential unit.

Family seed `f` is generated from `SeedSequence([2026082312,f])`.  The family
block, not the 32,768 episodes, is the unit in the uncertainty calculation.

## Estimand and multiplicity

For family `f`,

`delta_f = accuracy_f(TWO_SIGNAL) - max(accuracy_f(STATE_SIGNAL), accuracy_f(REASON_SIGNAL))`.

The primary estimand is the unweighted mean of `delta_f` across the 32 family
blocks.  A single 95% percentile bootstrap interval is computed by resampling
the 32 family blocks 20,000 times with seed `2026083303`.

There is one confirmatory claim.  The mean, interval and minimum-stratum checks
are noncompensatory conjuncts of that claim, not separately promoted discoveries.
The minimum over four fixed strata is an intersection requirement, so no
selection of a favourable stratum is permitted and no multiplicity credit is
claimed.

## Attainability and frozen gates

Both terminals are reachable.  With exact signals the two-signal arm can score
one while either one-signal arm is unable to distinguish at least one balanced
regime pair.  With an uninformative or deliberately corrupted second signal the
two-signal arm can fail the effect gates.

All gates must pass:

1. all three arms expose the identical four-action set;
2. all chosen actions respect budget two;
3. all 32 families have exactly 256 episodes in each regime;
4. typed observation boundaries hide the unavailable signal;
5. mean `delta_f >= 0.15`;
6. family-block bootstrap 95% lower bound `>= 0.12`;
7. mean `delta_f >= 0.12` in every fixed sigma stratum;
8. `delta_f > 0` in every family;
9. two fresh subprocess executions are byte-identical.

Success terminal:
`P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_SUPPORTED`.

Failure terminal:
`P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_GATE_NOT_MET`.

The failure terminal and all failing gate identities must be retained if any
conjunct fails.  Gates may not be edited after outcome inspection.


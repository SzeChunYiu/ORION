# OSTC-T17 successor narrowing V1

**Status:** successor record. **The merged theory is not modified by this file.**
`THEOREM_DERIVATIONS_T0_T23_V1.md` and `THEOREM_LEDGER_V1.json` are unchanged;
#1234's constitutional rule requires a genuine counterexample to narrow a theorem
in a separately identified record rather than silently mutating it.

**Source:** `EXEC-P12-01`, terminal `P12_ALLOCATOR_TRANSFER_OR_ROBUSTNESS_FAILS`,
receipt `RESULT_RECEIPT.json` in this directory. Independent checker green, zero
disagreements, hedge classification reproduced 3/3.

## What T17 states

> With finite action set `A`, exact per-case cost vector and an independently
> supplied objective, selecting the minimum feasible action has zero hindsight
> regret. If two cases share the same visible certificate but have different
> unique optimal actions, every certificate-only deterministic allocator incurs
> positive regret on at least one; under equal prior its expected regret is at
> least half the smaller cross-action loss gap.

## What holds

**Clause 1 is confirmed universally in the enumerated class.** Over all 588
ambiguous certificate classes on a 3-action, 4-cost grid, and over *every*
deterministic certificate-only allocator on each, zero allocators achieved zero
regret on both members. This was verified by exhaustive search over allocators,
not by an argument about a particular one. The oracle allocator scored exactly
zero regret on all 64 cases.

## What does not hold

**Clause 2, the half-gap bound, fails in 3 of 588 classes.** It holds and is
tight in the other 585. Every one of the three failures is a *hedge*: the
expected-regret-minimising action is a third action, belonging to neither case's
optimum. There are zero non-hedge violations.

Canonical witness:

| | action 0 | action 1 | action 2 |
|---|---|---|---|
| case 1 cost | **0** | 1 | 3 |
| case 2 cost | 3 | 1 | **0** |

Unique optima are 0 and 2. Both cross-action gaps are 3, so the claimed bound is
`3/2 = 1.5`. But action 1 costs 1 in both cases: regret 1 on each, expected
regret **1.0 < 1.5**. Hedging beats committing.

## Why it fails, precisely

T17 is stated as the allocation analogue of T12, and the disanalogy is exactly
where it breaks.

T12 is **0/1 error over terminals**: a deterministic rule returns one terminal
and is simply wrong on one world, so expected error `>= 1/2` follows with no
escape. T17 carries that argument into **real-valued loss**, where a third
action can be near-optimal for *both* cases. There is no hedge in 0/1 error;
there is one in a cost vector.

The half-gap bound implicitly assumes the allocator must commit to one of the two
optima. That is true when `|A| = 2` and false in general.

## Narrowed statement

> Under equal prior, expected regret is at least half the smaller cross-action
> loss gap **provided no action is simultaneously suboptimal for both cases by
> less than half that gap** — in particular whenever `|A| = 2`, or whenever the
> allocator is restricted to the two cases' optima.

Clause 1 is unaffected and holds for any `|A|`.

## Bounds on this narrowing

- Demonstrated on a 3-action, 4-cost grid by total enumeration. It shows the
  bound is **not universal**; it does not characterise every loss structure in
  which hedging is available.
- Clause 1 is untouched. The result does not weaken T17's central point that
  exact hidden charge certificates cannot be silently assumed available — a
  certificate-only allocator still pays on at least one member of every
  ambiguous class.
- No proof-assistant correspondence. `EXEC-PA-01` remains open.
- No external adjudication. Runner and checker are two implementations inside
  one programme, written in one session.

## Paper authority

`NONE`. P12's paper terminal does not move. Its manuscript already reports the
price-aware successor as a conditional construction-level result requiring exact
charge certificates, which is consistent with and independent of this narrowing.

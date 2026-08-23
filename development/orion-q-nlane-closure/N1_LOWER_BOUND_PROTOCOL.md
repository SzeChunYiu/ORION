# ORION-Q N1 frozen protocol — finite-candidate lower bound (machine-checked closure of the old QC2 class)

Date frozen: 2026-08-21
Lane: ORION-Q N1 (issue #674), lower-bound / stop programme
Registered design source: issue comment 5355100391 ("Proposition — complete finite candidate
verification"), never committed as code.
Status of this document: protocol frozen BEFORE the run of
`research/extensions/orion-q/nlanes/n1_lower_bound.py`.

## Registered proposition (restated)

Let `C` be a finite candidate edit set for one task, `V : C -> {0,1}` an exact deterministic
validity predicate, and let the budget permit evaluating `V(c)` for every `c in C`
(FULL_ENUMERATION_BUDGET). Exhaustive search succeeds iff `exists c in C : V(c) = 1`. Then for any
policy `pi` whose output is restricted to `C` (or abstention) and whose success requires returning
some `c` with `V(c) = 1`:

`Success(pi) <= Success(exhaustive)` pointwise on every task.

A policy can improve only secondary quantities (number/cost/order of verifier calls), never the
solve rate. This closes exactly the class of the old `QC2_NO_INCREMENTAL_VALUE` benchmark.

## Machine-check plan (exact, deterministic)

1. **Complete finite check over all worlds and all outputs** (`|C| = 12`): enumerate every validity
   assignment `V in {0,1}^12` (4,096 worlds) and every possible policy output
   `o in C ∪ {ABSTAIN}` (13 outputs); assert `success(o) = V(o) <= [exists c : V(c)=1] =
   success(exhaustive)` for all 53,248 pairs. Because ANY policy realization — deterministic,
   randomized, or adaptive in its verification order — terminates by emitting some `o`, this
   exhausts the full policy-outcome space per world and is a complete finite proof of pointwise
   dominance for this class, not a sample.
2. **Adaptivity irrelevance check:** for every world, assert exhaustive success equals the
   existence bit regardless of any verification order (order-permutation invariance over a full set
   of 12-cycles plus reversal; exact).
3. **Illustrative battery** (seed 20260821): 5,000 random tasks with `|C| = 12`,
   `P(V(c)=1) = 0.08`; concrete policies (exhaustive, fixed-single-guess, random-order-first-valid,
   greedy-learned) checked for pointwise dominance on every task.

## Prespecified gates

- `G1_COMPLETE_ENUMERATION_CHECK`: all 53,248 dominance comparisons hold.
- `G2_ORDER_INVARIANCE`: all order-invariance assertions hold.
- `G3_BATTERY_POINTWISE`: no policy exceeds exhaustive on any sampled task.

## Terminal rule (frozen)

All gates pass -> `LOWER_BOUND_CLOSED_FOR_FINITE_COMPLETE_CLASS` with closed scope exactly
`FINITE_COMPLETE_EDIT_SET + EXACT_VERIFIER + FULL_ENUMERATION_BUDGET`.
Any gate failing -> `LOWER_BOUND_CHECK_FAILED` (no closure claim).

## Explicit non-closure (registered; must appear in the receipt)

NOT closed: parameterized/infinite schemas; generated representations; incomplete applicability;
costly verification; resource-bounded search; edits that change the candidate language itself.
This lower bound explains the old QC2 negative as a structural ceiling of that benchmark class and
grants no statement about P10 globally.

## Claim boundary

Exact-synthetic scope only; the receipt line is
`ORIONQ_N1_LOWER_BOUND=<canonical sorted json>`; pretty receipt at
`research/extensions/orion-q/nlanes/N1_LOWER_BOUND_RESULTS.json`.

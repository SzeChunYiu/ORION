# SELF_ORION.ANYTIME_SAFE_REVISION.v1 — predictable alpha spending for adaptive revisions

**Paper:** ORION-15 — Self-ORION  
**Status:** `THEORY_PROVED__EMPIRICAL_LONGITUDINAL_SUCCESSOR_NOT_EXECUTED`  
**Scientific authority delta:** `NONE`  
**Novelty authority:** `NONE`

This packet supplies the safety theorem named by the longitudinal successor plan. It does
not claim that any revision process achieves useful improvement, and it does not reinterpret
existing V3/V4 outcomes.

## 1. Setting

Revision rounds are indexed by `t = 1,2,...`. Let `F_{t-1}` denote everything legitimately
known before the protected evaluation of round `t`: prior proposals, prior protected
terminals, retained negatives, previous stopping decisions and all non-protected state.
The next candidate revision, its gate thresholds and its error budgets may depend on
`F_{t-1}`.

A promotion rule has non-compensatory gates indexed by `j in J_t` — for example fresh
transfer, retention, harm and authority. A candidate is **bad for gate j** when the true
quantity violates that gate's required property. Promotion requires every gate to pass.

Before protected outcomes at round `t`, choose nonnegative predictable error budgets
`alpha_{t,j}` that are `F_{t-1}`-measurable. Assume the gate test is conditionally valid:

`P(pass_{t,j} | F_{t-1}, candidate is bad for gate j) <= alpha_{t,j}`.

No independence between gates or rounds is assumed.

## 2. Theorem 1 — anytime bad-promotion control

If almost surely

`sum_t sum_{j in J_t} alpha_{t,j} <= alpha`,

then

`P(there exists any round at which a bad candidate is promoted) <= alpha`.

This remains true when proposals, stopping times, future budgets and which gates are active
are chosen adaptively from the legitimate past.

### Proof

For a round `t` to promote a bad candidate, at least one gate `j` is truly bad and yet
passes. Let `E_{t,j}` be that false-pass event. Because `alpha_{t,j}` is selected before the
protected outcome and the gate test is conditionally valid,

`P(E_{t,j}) = E[P(E_{t,j}|F_{t-1})] <= E[alpha_{t,j}]`.

The event "ever promote a bad candidate" is contained in `union_{t,j} E_{t,j}`. The union
bound therefore gives

`P(ever bad promotion) <= sum_{t,j} P(E_{t,j}) <= E[sum_{t,j} alpha_{t,j}] <= alpha`.

No optional-stopping correction beyond the spending condition is needed because the proof
already ranges over every round that can be reached. ∎

## 3. Corollary — round-level alpha is enough if the within-round family is controlled

Suppose each round has a single valid familywise promotion test with conditional bad-promotion
error at most `alpha_t`, and `sum_t alpha_t <= alpha`. Then the same theorem gives

`P(ever promote a bad revision) <= alpha`.

Thus implementations may either allocate alpha directly over individual non-compensatory
gates or use a valid within-round multiple-testing procedure and spend only its round-level
familywise budget.

## 4. Theorem 2 — predictable random spending is allowed

The budgets need not be deterministic. They may depend on all legitimate prior information,
including how many rounds have failed, provided they are fixed before the current protected
outcome and the cumulative realized spend never exceeds `alpha`.

Examples include geometric spending, finite-horizon equal spending, or an adaptive rule that
spends less after weak non-protected evidence. The proof of Theorem 1 is unchanged because
predictability is exactly what allows conditional validity to be applied.

## 5. Theorem 3 — rejected candidates need not consume scientific identity, but alpha spend is not refundable

A candidate may fail a gate and remain unpromoted without changing earlier accepted claims.
However, once protected evidence for a gate has been accessed under budget `alpha_{t,j}`, that
budget has been spent for the anytime guarantee. Re-labeling the same protected look as a
"new round" cannot restore it.

Formally, the safety proof counts false-pass opportunities, not successful promotions. A
second decision from the same protected evidence is another test only if its joint error is
already covered by the original gate procedure. Otherwise it requires additional preallocated
error budget or a fresh protected sample.

This is the statistical analogue of the repository's no-rescue rule.

## 6. Counterexample — reusing alpha every round is not anytime-safe

Let every candidate be bad, and at each round let a valid one-round test falsely pass with
probability exactly `alpha`, independently across rounds. If the same `alpha` is reused for
`T` rounds, then

`P(at least one false promotion by T) = 1 - (1-alpha)^T`,

which is strictly greater than `alpha` for every `T>1` and `0<alpha<1`.

For an unbounded sequence, this probability tends to one. Therefore "each round is a
5%-level test" does **not** imply a 5% anytime-safe revision process.

## 7. Counterexample — outcome-dependent budget selection is not licensed

Predictability is load-bearing. If a procedure first inspects the current protected result
and only then chooses which test/budget to report, the conditional premise of Theorem 1 is
not established. The theorem therefore grants no authority to post-outcome gate selection,
threshold changes or relabelled rescue attempts.

A valid implementation must commit the current gate family, thresholds and `alpha_{t,j}`
before protected outcomes are opened.

## 8. Non-compensatory safety is structural, not a weighted score

The theorem assumes a bad revision is one that violates **any** required safety property and
promotion requires all gates. It does not justify replacing retention, harm or authority
constraints by a weighted average against fresh-transfer benefit. A large benefit cannot
compensate statistically for a failed hard gate unless the scientific claim itself is
prospectively redefined under a new identity.

## 9. Suggested six-round instantiation

For the successor described in issue #1608, one conservative familywise plan is:

`alpha_t = alpha / 6` for `t=1..6`,

with each round internally controlling all promotion gates at familywise level `alpha_t`.
A geometric plan such as `alpha_t = alpha / 2^t` supports an unbounded horizon and spends
strictly less than `alpha` in any finite prefix.

The theorem does not select between these plans; that choice belongs in the frozen empirical
protocol.

## 10. Authority boundary

Earned: an exact anytime familywise-error guarantee for adaptive revision proposals under
predictable alpha spending and conditionally valid protected gate tests.

Not earned:

- power, sample-size adequacy or the existence of three promotable revisions;
- longitudinal improvement, cumulative transfer gain or model-family generalization;
- independence of same-programme AI reviewers;
- validity of any particular confidence-bound construction not separately justified;
- retrospective authority for existing V3/V4 outcomes;
- novelty or venue authority.

The empirical successor still needs prospectively separated motivating, replay,
fresh-transfer and safety sets plus actual protected execution.

**Terminal:** `ANYTIME_BAD_PROMOTION_CONTROL_PROVED__LONGITUDINAL_BENEFIT_UNTESTED`.

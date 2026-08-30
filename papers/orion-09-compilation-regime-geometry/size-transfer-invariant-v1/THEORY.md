# The size-transfer invariant — ORION09.SIZE_TRANSFER_INVARIANT.v1

Tier B promotion target from issue #1649. `scientific_authority_delta: NONE`.

## What is already frozen

The `k* = 4` exact law holds on `n <= 3`. Direct transfer to `n = 4` is **negative**, and
sign-aware mechanism attribution is **falsified**. `CLAIM_LEDGER_V2` records the sharper
statement: *no predicate in the frozen natural feature vocabulary separates donor-exactness*,
refuting the universal low-order-boundary motif.

#1649 asks for a **structural invariant** predicting whether a four-feature separator
remains sufficient under size extension, or where new **mixed fibres** must appear.

## The observation that makes this tractable

"Mixed fibre" is not incidental vocabulary. A feature map `phi` with `k` features induces
fibres `F_z = {x : phi(x) = z}`, and a separator that reads only `phi` is a function of `z`
alone. That is exactly the structure `ORION02.FIBRE_DIAMETER_FLOOR.v1` analyses and
`ORION22.OBSERVATION_ALIASING_ROBUSTNESS.v1` analyses in the allocation setting. This
packet applies it to classification.

## Theorem S1 (purity criterion)

A separator reading only `phi` exists **iff** every fibre of `phi` is **pure** — contains
instances of at most one class.

*Proof.* (⇐) If every fibre is pure, define the separator to output that fibre's unique
class. (⇒) A separator reading only `phi` is constant on each fibre, so a fibre containing
two classes forces at least one misclassification. ∎

This is the `eps = 0` case of the ORION-02 floor and the empty-intersection case of the
ORION-22 criterion, and it is why the frozen `n = 4` negative is **structural**: it is not
that search failed to find a predicate, it is that a fibre is mixed.

## Theorem S2 (capacity bound — the invariant)

Let `phi` have `k` binary features, so `|image(phi)| <= 2^k`. If the instances at size `n`
require more than `2^k` distinct classification outcomes under any behaviour-preserving
refinement, some fibre is **necessarily** mixed and no `phi`-separator exists.

*Proof.* Pigeonhole: more required distinctions than available feature cells forces two
instances of different classes into one cell. ∎

The invariant is therefore

    C(n) = ( number of distinct required outcomes at size n )  versus  2^k.

`C(n) > 2^k` **predicts failure**, and does so without searching the predicate space.

## Theorem S3 (transfer characterisation)

The `k`-feature separator transfers from size `n` to size `n+1` **iff** no fibre that was
pure at `n` becomes mixed at `n+1`. Combining with S2: capacity exhaustion is a *sufficient*
condition for non-transfer, and fibre purity is the *exact* condition.

*Proof.* S1 at each size, plus the observation that fibres at `n+1` refine or coincide with
fibres at `n` under the same feature map. ∎

## What this does and does not claim

It **explains** the frozen `n = 4` negative as forced mixing rather than failed search, and
it gives a computable predictor `C(n)` vs `2^k` that needs no predicate search.

It does **not** claim to predict every transition. S2 is one-directional: capacity
exhaustion forces failure, but a separator can also fail below capacity if the specific
assignment mixes a fibre. The exact condition is purity (S3), which requires inspecting the
fibres, not just counting them.

Being explicit about that gap is the point. #1649's stop rule for this lane is:

> If no invariant predicts [the] transition better [than] existing bounded geometry, stop
> PRX-Quantum promotion [and] submit [the] strongest defensible specialist venue.

So the decisive question is not whether S1–S3 are true — they are proved — but whether the
**one-directional** capacity invariant predicts *better than the existing bounded geometry
already does*. The protocol tests exactly that, and is allowed to answer no.

## What would refute this

A mixed fibre with a working `phi`-separator; a pure-fibre configuration with none; a
configuration with `C(n) > 2^k` that nonetheless separates; or the invariant failing to
improve on the bounded geometry's own predictions.

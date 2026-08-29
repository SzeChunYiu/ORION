# The source-complete quotient — ORION01.CONTEXTUAL_MOVE_COMPLETENESS.v1

Frozen before outcome access. `scientific_authority_delta: NONE`.

## The adverse parent

`REGISTRY_NONIDENTIFIABILITY_R12` records that over all `2^(n(n-1)/2)` registries the
direct optimizer signature is **constant**, while terminal complexity spans `1..n`. It
therefore sets `r6m_registry_completeness: false` and `production_transfer: false`:
completeness proved on a freely chosen registry does not transfer to production.

#1615 Priority 6 proposes that completeness be proved not on the free registry family
but on a **source-complete scheduler/context quotient**.

## The model, exactly as frozen

States are `1..n`. The candidate moves are all `(s, t)` with `s > t` — strictly
resource-decreasing. A registry `R` is any subset. Then

    terminal_complexity(n, R) = max { s in 1..n : s has no outgoing edge in R }

Call `R` **source-complete** when every state in `2..n` has at least one outgoing edge.

## Theorem A (exact characterisation)

    terminal_complexity(n, R) = 1   <==>   R is source-complete.

*Proof.* State `1` never has an outgoing edge, since every move strictly decreases and
there is nothing below `1`; so `1` is always terminal and the max is at least `1`.

(⇐) If `R` is source-complete then every `s` in `2..n` has an outgoing edge, so no such
`s` is terminal, so the terminal set is exactly `{1}` and the max is `1`.

(⇒) If the max is `1` then no `s` in `2..n` is terminal, so every such `s` has an
outgoing edge, which is source-completeness. ∎

The direction that carries the content is (⇐): it says the quotient is not merely
correlated with completeness but **coextensive** with it.

## Theorem B (closed form)

The number of source-complete registries on `n` states is

    N(n) = prod_{s=2}^{n} ( 2^(s-1) - 1 ).

*Proof.* State `s` has exactly `s - 1` candidate targets below it, so `2^(s-1)` possible
outgoing sets, of which the empty one is excluded. Choices at distinct sources are
independent because the candidate edges out of different sources are disjoint. ∎

`N(2) = 1`, `N(3) = 3`, `N(4) = 21`, `N(5) = 315`, `N(6) = 9765`. These must equal the
count at terminal complexity `1` already frozen in the R12 histogram. That cross-check
is control `K1`: it is what distinguishes quotienting the frozen object from quietly
re-modelling it.

## Claim C — the half that is expected to stay adverse

The direct optimizer signature is `{feasible_state_count: n, optimum_value: 1,
optimum_witness: 1}` and does not depend on `R`. Restricting to source-complete
registries therefore cannot make the **registry** identifiable, only the **completeness
value**.

R12 conflated two failures — completeness was not identifiable, and the registry was not
identifiable. Theorems A and B repair the first. Claim C says the second survives. A
report of A and B alone would overstate the repair, which is why C is registered as a
claim to be measured rather than a caveat to be written afterwards.

## What would refute this

Any source-complete registry with terminal complexity other than `1`, any
non-source-complete registry with complexity `1`, or a count disagreeing with the frozen
R12 histogram. `PROTOCOL.json` checks the iff in **both** directions over every registry;
checking one direction would not distinguish an equivalence from an implication.

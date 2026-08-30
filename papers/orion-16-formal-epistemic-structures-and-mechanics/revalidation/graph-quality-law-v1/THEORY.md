# The dependency-graph quality law — ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1

Top-tier promotion target from issue #1649, Tier A. `scientific_authority_delta: NONE`.

## What is already frozen

`ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1` shows the affected transitive closure
`A(Delta)` is sound and every proper subset unsound under separation witnesses, across
1,099 DAGs and 33,866 updates.

`revalidation/P6_REVALIDATION_COMPARISON_V1.json` holds real-system evidence over
**numpy, scipy and flask** — 604,542 certificate decisions — where the `selective` policy
retains 74.87% / 84.90% / 89.33% with **zero** invalid retentions, while a `native-dep`
baseline retains more but wrongly retains 28,709 and 51,353 certificates on numpy and
scipy.

Both assume **a correct dependency graph is given**. #1649 asks for the theorem that drops
that assumption and distinguishes graph qualities.

## Setting

A finite DAG `G`, a change set `Delta`, and the affected set

    A_G(Delta) = { v : v is reachable from some node of Delta in G }, including Delta.

A revalidation policy names a set `R`; it is **sound** when every artefact whose validity
could change lies in `R`. Write `G*` for the true dependency graph.

## Theorem N1 (monotonicity)

If `G ⊆ G'` then `A_G(Delta) ⊆ A_{G'}(Delta)` for every `Delta`.

*Proof.* Every `G`-path is a `G'`-path. ∎

## Theorem N2 (over-approximation is sound; its price is exact)

If `G' ⊇ G*`, revalidating `A_{G'}(Delta)` is sound, and the extra work is exactly

    |A_{G'}(Delta) \ A_{G*}(Delta)|,

every element of which is reachable in `G'` from the head of some edge in `G' \ G*`.

*Proof.* Soundness is N1 at `G = G*`. If `v` is in the difference, some `G'`-path reaches
it and no `G*`-path does, so that path uses an edge of `G' \ G*` and `v` is reachable from
its head. ∎

**Conservative edges cost only reachability from their heads**, not a global penalty —
the explicit extra-work bound #1649 asks for.

## Theorem N3 (under-approximation is unsound; its failures are exactly located)

If `G'' ⊆ G*`, then `v` is **wrongly retained** iff `v ∈ A_{G*}(Delta)` and
`v ∉ A_{G''}(Delta)`, which holds iff **every** `G*`-path from `Delta` to `v` uses an edge
absent from `G''`.

*Proof.* The first statement is the definition. For the second, `v ∉ A_{G''}(Delta)` says
no `G''`-path reaches `v`, and every `G*`-path is a `G''`-path unless it uses a missing
edge. ∎

So missing-edge risk is not merely bounded but **exactly the set of nodes whose entire
connection to `Delta` runs through missing edges**. A missing edge bypassed by another path
costs nothing — the second explicit bound #1649 asks for.

## Theorem N4 (weights do not move the optimum)

For any nonnegative weighting `w` of revalidation obligations, the minimum-weight **sound**
set is `A_{G*}(Delta)` itself.

*Proof.* By the frozen separation-witness result every proper subset of `A_{G*}(Delta)` is
unsound, so it is the unique inclusion-minimal sound set; any sound `R` contains it, and
`w >= 0` gives `w(R) >= w(A_{G*}(Delta))`. ∎

This is the opposite of what "cost-optimal revalidation under weighted obligations"
suggests. **There is no weighting to tune.** Soundness is a hard constraint, so cost
optimisation has no freedom left, and all achievable savings come from graph *quality*
rather than from prioritising expensive obligations.

## Corollary N5 (the quality ladder)

Ordering graphs by inclusion orders cost and safety in **opposite** directions: enlarging
beyond `G*` buys only work (N2); shrinking below `G*` buys work but forfeits soundness
(N3). `G*` is the unique point optimal in both, and learned or incomplete graphs sit on the
unsound side exactly to the extent that they miss edges.

## Scope — prospective versus retrospective

**Prospective.** N1–N5 are proved here and verified by exhaustive enumeration over small
DAGs, all change sets, and all over- and under-approximations, under a protocol frozen
before that verification runs.

**Retrospective, licensing nothing.** `P6_REVALIDATION_COMPARISON_V1.json` records
`outcome_accessed: true`. Its numbers were read before this theory was written, so **no
frozen test may be run against them and none is.** Any reference to them in
`CLAIM_DISPOSITION.md` is a labelled consistency observation, not evidence.

**#1649's stop rule.** *If real dependency extraction cannot be made authoritative, keep
the general theorem [as a] bounded paper; do not manufacture deployed-system claims.*
Python import graphs are a real but **over-approximate** dependency relation — imports are
a superset of true semantic dependencies — so they are exactly the `G' ⊇ G*` case of N2 and
cannot certify `G*`. Extraction is **not** authoritative for the exact graph, the stop rule
applies, and no deployed-system claim is made on any outcome.

## What would refute this

A pair `G ⊆ G'` with `A_G(Delta) ⊄ A_{G'}(Delta)`; an over-approximation that is unsound;
an under-approximation whose wrongly-retained set differs from N3; or a nonnegative
weighting under which some sound set beats `A_{G*}(Delta)`.

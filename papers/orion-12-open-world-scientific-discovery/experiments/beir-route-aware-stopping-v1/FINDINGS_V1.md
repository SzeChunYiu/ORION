# ORION-12 route-aware stopping on BEIR — findings V1

**Terminal: `ROUTE_AWARE_STOPPING_NOT_SUPPORTED`.** All three predeclared
conditions fail. The design had power: mean pairwise Jaccard@100 between routes is
0.314 (ArguAna), 0.377 (SciFact), 0.444 (NFCorpus), so the routes are genuinely
heterogeneous and `CANNOT_CHECK_INSUFFICIENT_ROUTE_HETEROGENEITY` does not apply.

| condition | required | observed |
|---|---|---|
| recall within 0.02 of fusion at equal cost | yes | **no** — worst deficit **+0.101** |
| false-complete no worse than generic active by >0.02 | yes | **no** — worst gap **+0.084** |
| strictly cheaper than fusion at matched recall | yes | **no** — 5 of 15 cells |

## The rule never adapts; it saturates

The failure is not noise and it is not a near miss. The stopping rule is bimodal,
and each corpus sits at one pole:

- **ArguAna** — stops after the **first route, every time**. Its cost equals the
  depth exactly at all five depths, so no second route is ever read. It gives up
  0.101 recall against fusion at depth 10 and is never cheaper at matched recall.
- **NFCorpus** — **never stops**. Its cost equals the exhaustive oracle's at every
  depth (83, 153, 279 …), and its recall equals the oracle's too. It buys recall,
  but by reading everything, which is the one thing a stopping rule must not do.
- **SciFact** — sits between and is behind fusion at four of five depths.

The mechanism is the threshold. The rule stops when no unread route is expected to
contribute **one** new relevant document — an absolute count. The number of
relevant documents per query differs by more than an order of magnitude across
these corpora: ArguAna has essentially one relevant document per query, so after
the first route no route can possibly be expected to add a whole further one and
the rule always halts; NFCorpus queries have dozens, so every route clears the bar
and the rule never halts.

A threshold on an absolute count cannot adapt across corpora whose relevance
density differs by that much. It degenerates into "always stop at once" or "never
stop", and the corpus decides which. That is why the safety number is bad too: the
false-complete rate exceeds generic active by up to 8.4 points, entirely from the
pole where it stops immediately.

## This is not rescued here

The protocol froze `TAU`, `P`, `k`, the depth grid and the overlap statistic, and
says a failure is not to be rescued by re-tuning any of them. It is not. Re-running
this study with a relative threshold would be exactly the outcome-driven tuning the
freeze exists to prevent.

The diagnosis does point somewhere: a threshold expressed as a **fraction of the
relevant documents already found**, rather than as an absolute count, is
scale-free and would not saturate at either pole. That is a hypothesis for a
successor under a new identity, with its own freeze, and it has no standing here.

## What this does and does not say about ORION-12

It does **not** touch the TREC-COVID result. That corpus was not retrieved, not
scored and not pooled, per #1701. The failed recall@100 gate and the +175.7% reads
stand exactly as they were, and nothing in this study was permitted to override
them — nor would it, since this study is also negative.

It does say that route-aware stopping, in the form ORION-12 registered, does not
survive contact with three untouched corpora under a frozen safety margin. The
routes here are retrieval functions over one local corpus rather than live
providers, so this tests the rule under route *heterogeneity* and not under
provider *availability*; a rule that fails under heterogeneity has not been given
the harder test.

`bm25_title` was kept in every denominator despite ArguAna having only 2,699
non-empty titles out of 8,674 documents.

Corpus digests are in `CORPUS_DIGESTS.txt`; they pin corpus, queries and qrels
together.

## The secondary endpoint says the opposite, and that is the point

nDCG@10, the registered secondary:

| corpus | best single | fusion | generic active | **route-aware** | oracle |
|---|---|---|---|---|---|
| SciFact | 0.6246 | 0.6162 | 0.6421 | **0.6421** | 0.6421 |
| NFCorpus | 0.2699 | 0.2861 | 0.2862 | **0.2953** | 0.2953 |
| ArguAna | 0.3846 | 0.3690 | 0.3172 | **0.3172** | 0.3172 |

**Route-aware stopping beats fusion on nDCG@10 in 10 of 15 cells**, and on two of
three corpora it ties the exhaustive oracle.

Read alone, that is a favourable result. It is not one, and the protocol said so
before the numbers existed: nDCG is secondary and cannot carry the terminal. The
arm fails every primary endpoint — 0.101 recall behind fusion at equal cost, a
false-complete rate 8.4 points worse than generic active, cheaper at matched
recall in 5 of 15 cells.

This is the **same shape as the TREC-COVID result** the ORION-12 lane already
carries, where favourable nDCG accompanied a failed recall gate and a 175.7% read
increase. Seeing it recur on three untouched corpora, with a different rule and a
different failure mechanism, suggests the divergence is systematic rather than an
accident of that corpus: a rule that stops early keeps a short, precise head and
loses the tail, and a top-10 metric cannot see the tail it lost. That is a reason
to distrust nDCG as an endpoint for stopping rules, not a reason to promote this
one.

**One caveat that cuts against the arm's own nDCG numbers.** The union-based arms
(`generic_active`, `route_aware_stop`, `oracle`) present documents in
route-concatenation order rather than a fused relevance ranking, so their top-10
is not rank-optimised. On ArguAna this drags all three to 0.3172 while a single
ranked route reaches 0.3846. The nDCG column is therefore not a clean
apples-to-apples comparison across arm families, which is a further reason it
cannot carry a terminal here.

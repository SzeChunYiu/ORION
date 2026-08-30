# ORION-12 route-aware stopping on BEIR — protocol V1

**Committed before any retrieval is run.**

## What this does and does not touch

The TREC-COVID result stays as it is: the recall@100 gate failed and reads rose
175.7%, and no favourable nDCG anywhere in this study is permitted to override
it. #1701 is explicit that TREC-COVID is excluded from fresh-confirmation claims,
so it is not retrieved, not scored, and not pooled here. This is a successor on
untouched corpora under a new identity, not a rescue of the old one.

## Corpora

BEIR `scifact`, `nfcorpus`, `arguana`, fetched as the official UKP zips. The
SHA-256 of each zip is recorded in the receipt, which is what "freeze exact
dataset/qrels versions" means operationally: the archive digest pins corpus,
queries and qrels together, and a later BEIR revision cannot silently substitute.

## Routes, frozen here

A "route" in the ORION-12 sense is a way of reaching documents. This study runs
entirely on local corpora, so the routes are **retrieval functions over the same
corpus**, not live web providers. That is a real limitation and is stated in the
findings rather than papered over: it tests route-aware stopping under route
*heterogeneity*, not under provider *availability*.

Five routes, fixed before any query is issued:

- `bm25_full` — Okapi BM25 (k1=0.9, b=0.4, the BEIR default) over title + text
- `bm25_title` — BM25 over title only
- `bm25_text` — BM25 over text only
- `tfidf_word` — L2-normalised word TF-IDF, cosine
- `tfidf_char` — L2-normalised char 3–5-gram TF-IDF, cosine

Tokenisation is lowercase alphanumeric with a fixed English stoplist, applied
identically to every route. No route's parameters are tuned after seeing recall.

## Unavailable routes stay in the denominator

`bm25_title` is undefined for any corpus whose documents carry no title, and
ArguAna's are largely empty. That route is **not dropped**: it is recorded as
returning nothing and remains in the denominator of every fusion and coverage
statistic. Removing an unavailable route from the denominator is precisely the
error that makes a stopping rule look safer than it is, and #1701 names it.

## Cost

Cost is the number of distinct documents read, pooled across routes. A document
read twice by two routes costs once. The depth grid is frozen at
`[10, 20, 50, 100, 200]` documents per query.

## Arms

- `best_single` — the single route with the highest recall on a **development
  half of the queries**, then applied to the held-out half. Route choice never
  sees the scored half.
- `fusion` — reciprocal rank fusion, `k=60`, over all five routes.
- `generic_active` — round-robin over routes, stopping after `P=2` consecutive
  reads that add no new relevant document. This is the generic active-retrieval
  baseline and it is deliberately given the same budget as everything else.
- `route_aware_stop` — the ORION-12 arm. Stops when the routes still unread
  cannot, by their observed rank-overlap with routes already read, be expected to
  contribute a new relevant document. The overlap statistic is computed from the
  development half only.
- `oracle` — exhaustive over all five routes to full depth. Defines recall 1.0 at
  maximum cost and is the only arm allowed to see qrels during retrieval.

## Endpoints

Primary, both at each frozen depth:

1. **recall at fixed cost** — macro-averaged over held-out queries.
2. **false-complete stop rate** — the fraction of held-out queries where an arm
   declared the search complete while a relevant document remained reachable by
   an unread route. Only the stopping arms (`generic_active`, `route_aware_stop`)
   can register this; the fixed-depth arms are reported as not-applicable rather
   than as zero, because scoring a non-stopper as never-falsely-stopping would
   flatter it by construction.

Secondary: nDCG@10. It is secondary and cannot carry the terminal, for the same
reason it could not on TREC-COVID.

## Predeclared non-inferiority and safety margin

`route_aware_stop` is **supported** only if, on the held-out half and pooled over
the three corpora:

- its recall is within `0.02` of `fusion` at equal or lower cost, **and**
- its false-complete rate is no worse than `generic_active`'s by more than
  `0.02`, **and**
- it reads strictly fewer documents than `fusion` at matched recall.

All three. A cheaper arm that stops early and misses more is not a result; the
whole point of the ORION-12 lane is that a favourable cost number cannot buy a
recall loss.

## Terminals

- `ROUTE_AWARE_STOPPING_SUPPORTED_ON_FRESH_CORPORA` — all three conditions hold.
- `ROUTE_AWARE_STOPPING_NOT_SUPPORTED` — any condition fails. Recorded with the
  failing corpus and margin; not rescued by re-tuning `P`, `k`, the depth grid or
  the overlap statistic, all of which are frozen above.
- `CANNOT_CHECK_INSUFFICIENT_ROUTE_HETEROGENEITY` — if on all three corpora the
  five routes return near-identical document sets, there is no route structure
  for a route-aware rule to exploit and the design has no power. This is a real
  possible outcome and is declared here so it cannot later be presented as a
  negative result about stopping.

A pass does not establish anything about live provider routes, open-world web
discovery, or the failed TREC-COVID recall gate. It establishes that under frozen
route heterogeneity on three untouched corpora, route-aware stopping is
non-inferior to fusion at lower cost.

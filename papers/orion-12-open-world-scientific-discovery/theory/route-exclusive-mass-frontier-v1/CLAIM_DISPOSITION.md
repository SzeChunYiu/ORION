# Claim disposition — ORION12.ROUTE_EXCLUSIVE_MASS_FRONTIER.v1

**Terminal:** `ROUTE_EXCLUSIVE_MASS_FRONTIER_PROVED__FRESH_ROUTE_VALUE_UNTESTED`  
**Scientific authority delta:** `NONE`

## Closed by this packet

- When a frozen baseline route outputs its complete baseline candidate set `A`, added routes
  can increase recall only through relevant documents outside `A` that those routes make
  reachable.
- The maximum recall gain is bounded by that **exclusive relevant mass**; zero exclusive
  mass implies zero possible recall gain regardless of fusion/model capacity.
- Route count alone has no recall meaning: arbitrarily many redundant routes can add no
  exclusive relevant mass.
- To make a gain of `g` relevant documents possible, selected routes must cover at least
  `g` exclusive relevant documents. The minimum route-acquisition cost is therefore a
  weighted partial set-cover frontier.
- Ranking quality and recall are distinct: nDCG can improve with unchanged recall. The
  historical favourable nDCG result therefore cannot replace the frozen recall/cost gate.
- The current TREC-COVID adverse packet remains bound exactly: BM25 recall@100 `0.110334`
  vs ORION `0.092642`, BM25 mean reads `85.52` vs ORION `235.8`, and both registered primary
  criteria remain `FAIL`.

## Still open

- Historical TREC-COVID exclusive mass is not asserted by this theorem packet.
- The untouched BEIR successor must bind route-level candidate IDs/qrels and compute the
  route-value frontier prospectively.
- Any superiority/generalization claim across SciFact, NFCorpus or ArguAna.
- External replication, novelty and venue authority.

## Scope condition reviewers must not drop

The baseline-completeness condition is load-bearing. If a comparator itself emits only a
strict subset of its frozen baseline-reachable candidates, a new reranker can sometimes
recover baseline-reachable relevant items without any route-exclusive mass. The theorem
must not be quoted outside the complete-baseline-output contract without a new proof.

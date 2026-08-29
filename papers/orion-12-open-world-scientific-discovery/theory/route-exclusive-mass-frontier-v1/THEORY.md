# ORION12.ROUTE_EXCLUSIVE_MASS_FRONTIER.v1 — what extra retrieval routes can buy

**Paper:** ORION-12 — Open-World Scientific Discovery  
**Status:** `THEORY_PROVED__EXTERNAL_SUCCESSOR_NOT_EXECUTED`  
**Scientific authority delta:** `NONE`  
**Novelty authority:** `NONE`

This packet sharpens the adverse TREC-COVID result without changing its gate. It formalizes
when adding retrieval routes can improve recall, why route count is not itself evidence, and
what route access must cost before any ranking/fusion algorithm is considered.

## 1. Frozen-depth set model

Fix one query/topic with relevant-document set `R`.

Let `A` be the complete candidate set returned by the frozen baseline route at its declared
depth. The baseline outputs all of `A`; this is the load-bearing scope condition. For
TREC-COVID BM25 in the current external packet, the baseline route returns and scores its
100 candidates for recall@100.

Let additional frozen routes `j in J` return candidate sets `N_j` at their declared depths.
A multi-route method may output any set `E` satisfying

`E subseteq A union (union_j N_j)`.

Ranking, fusion and stopping may decide which reachable candidates enter `E`; this theorem
does not assume a particular fusion rule.

Define the **exclusive relevant mass** made reachable by the added routes:

`X_J = R intersect ((union_j N_j) \ A)`.

These are relevant documents the baseline frozen-depth candidate set could not already
supply.

## 2. Theorem 1 — exclusive-mass recall frontier

For every expanded output `E` reachable from the baseline plus added routes,

`|R intersect E| - |R intersect A| <= |X_J|`.

Equivalently, after normalizing by `|R|>0`,

`Recall(E) - Recall(A) <= |X_J| / |R|`.

### Proof

Every newly recalled relevant document must lie in `(R intersect E) \ A`. Because
`E subseteq A union (union_j N_j)`, every such document lies in
`R intersect ((union_j N_j) \ A) = X_J`. The expanded method may also drop relevant
baseline candidates, so the net gain can only be smaller. ∎

The bound is sharp: if the output budget permits `E = A union X_J`, equality holds.

## 3. Corollaries

### 3.1 No exclusive relevant mass means no recall gain

If `X_J` is empty, no fusion, model, stopping rule or reranker using only the frozen route
candidate sets can improve recall over the baseline that already outputs all of `A`.

This is an information boundary, not an algorithm-capacity statement.

### 3.2 Route count does not imply value

Adding arbitrarily many routes whose relevant candidates are all already in `A` leaves
`X_J` empty and therefore cannot improve recall. More routes may still change ranking,
latency, cost or other metrics; they do not create recall mass merely by existing.

### 3.3 nDCG and recall are logically separable

A reranker can move already-recalled relevant documents upward and improve nDCG while
adding zero new relevant documents. Thus an nDCG gain cannot substitute for a recall gate.
This is exactly why the current TREC-COVID packet correctly preserves its favourable
nDCG@10 result as secondary after the recall/cost gate fails.

## 4. Theorem 2 — minimum route-acquisition cost is a partial set-cover frontier

Give each added route a nonnegative acquisition cost `c_j`. For a selected route set
`S subseteq J`, define

`X_S = R intersect ((union_{j in S} N_j) \ A)`.

To make a recall gain of at least `g/|R|` even **possible**, the selected routes must satisfy

`|X_S| >= g`.

Therefore every method capable of that gain has route-acquisition cost at least

`C*(g) = min_{S subseteq J : |X_S| >= g} sum_{j in S} c_j`,

with `C*(g)=infinity` if no such subset exists.

### Proof

By Theorem 1 applied to the selected routes, a gain of `g` relevant documents requires at
least `g` exclusive relevant candidates to be reachable. Any selected route set violating
that condition cannot achieve the target under any downstream ranking policy. Taking the
minimum cost over the necessary feasible route sets gives the lower bound. ∎

`C*(g)` is a **necessary acquisition cost**, not the total realized cost: ranking, reading,
verification and model/tool costs may make the true requirement larger.

## 5. Theorem 3 — macro recall gain is bounded topicwise

For topics `q=1,...,Q`, with relevant sets `R_q`, baseline candidate sets `A_q` and frozen
added-route candidates, let `x_q = |X_{J,q}|/|R_q|` for topics with nonempty relevance sets.
Then the macro-average recall gain satisfies

`mean_q Recall_q(E_q) - mean_q Recall_q(A_q) <= mean_q x_q`.

This follows by averaging Theorem 1 topicwise. No independence or sampling model is needed.

## 6. What the current TREC-COVID result establishes — and what it does not

The frozen external result reports:

- BM25 recall@100 `0.110334` versus ORION `0.092642`;
- paired recall delta `-0.01769`, whose 95% interval `[-0.02729,-0.00906]` fails the
  preregistered noninferiority gate;
- ORION mean reads `235.8` versus BM25 `85.52` (`+175.7%`), failing the cost gate;
- ORION nDCG@10 higher by about `0.1488`, with its interval excluding zero, but nDCG was not
  the frozen gate criterion.

This theorem does **not** claim that `X_J` has been measured from the committed packet.
Unless exact route-level candidate IDs and qrels are bound at the required depths, exclusive
relevant mass remains `CANNOT_CHECK` for that historical run. The theorem explains which
quantity a future route-value study must measure prospectively.

## 7. Consequence for the BEIR successor

A valid new route-aware stopping study on untouched SciFact/NFCorpus/ArguAna should bind,
before protected scoring:

1. exact baseline and added-route candidate IDs at frozen depths;
2. qrels/version identifiers;
3. route acquisition/read/tool costs;
4. `X_S` or enough bound data for an independent checker to recompute it;
5. a predicted route-cost frontier `C*(g)` before evaluating the learned/stopping policy.

The strongest test is then not merely whether a multi-route policy wins, but whether it
captures a material fraction of the **available exclusive relevant mass** at a cost near the
precomputed frontier while preserving the preregistered safety/noninferiority gate.

## 8. Boundaries

The theorem does not say multi-route retrieval is useless, that BM25 is universally
optimal, or that the failed TREC-COVID result predicts the untouched BEIR outcome. It also
does not bound arbitrary reranking experiments where the comparator does **not** output its
complete frozen baseline candidate set: in that different contract, a reranker may recover
baseline-reachable items that the comparator itself omitted.

The result is a finite-set information bound. Generic set coverage and partial set cover are
donor-owned; no novelty is claimed.

**Terminal:** `ROUTE_EXCLUSIVE_MASS_FRONTIER_PROVED__FRESH_ROUTE_VALUE_UNTESTED`.

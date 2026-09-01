# ORION-12 route-aware stopping V3 — findings

**Terminal: `CONDITIONAL_ESTIMATOR_INERT`.** The falsifier frozen in
`PROTOCOL_V3.md` fired: ArguAna is identical to V1 at **5 of 5 depths**.

## Result

| corpus | depths identical to V1 |
|---|---|
| **ArguAna** | **5 / 5** |
| SciFact | 5 / 5 |
| NFCorpus | 0 / 5 |

ArguAna, every depth, V1 and V3 alike: r .6771/c 10, .8222/20, .9047/50,
.9431/100, .9573/200 — against fusion's .7781, .8919, .9502, .9659, .9801.

NFCorpus moved only slightly (depth 200: cost 279.36 → 262.06, recall .3280 →
.3197), nowhere near fusion's 195.67.

## What this rules out

Two independent mechanism hypotheses for ArguAna are now dead:

1. **V2 — threshold scale.** Density-normalizing moved the threshold 1.0 → 0.1.
   ArguAna: no stop decision changed.
2. **V3 — query independence.** Making the estimator query-conditional, scaled by
   each query's own unseen fraction. ArguAna: no stop decision changed.

The decision is invariant to both the scale of the threshold and to conditioning
on the query. What remains is the **information content of the statistic itself**:
on ArguAna the frozen rank-overlap marginal predicts a near-zero contribution from
every unread route, for every query, at every prefix. There is nothing in that
signal for a decision rule to act on.

**That is a sharper negative than V1's.** V1 said a route-aware rule failed to beat
fusion. V1's own findings attributed it to an absolute threshold. Two successors
now show the attribution was incomplete: on ArguAna the rule cannot work at any
threshold or conditioning, because its input carries no signal. The failure is in
the measurement, not the decision.

## Not rescued

`PROTOCOL_V3.md` pre-committed that a fired falsifier is **not** to be rescued by a
fourth estimator in the same round, and it is not. A successor that changes the
statistic rather than the rule reading it would need its own frozen identity, and
its selection would have to be justified against this result rather than by
searching for something that passes.

## Control

Unchanged from V2 and re-verified: V1 reproduced 150/150 values on two machines,
corpus digests matching the frozen SHA-256 on both.

## Authority

`scientific_authority_delta: NONE`. Successor evidence under a new identity;
converts no earlier negative into a pending success.

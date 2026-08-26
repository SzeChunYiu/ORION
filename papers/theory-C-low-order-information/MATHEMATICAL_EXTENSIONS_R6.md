# Mathematical Extensions R6 — Full Proper-Marginal Indistinguishability

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, and `MATHEMATICAL_EXTENSIONS_R5.md`

Status: rigorous representation-theory addendum. It strengthens the previous order-`m-2` obstruction to equality of every proper labeled interaction, through order `m-1`.

## 1. Main advance

The earlier construction distinguished an anchor and proved that interactions through order `m-2` do not determine exact value. That left open whether the complete collection of `(m-1)`-way statistics might suffice. It does not.

For every `m>=5` and `L>=1`, this addendum constructs two Pauli-string partition instances with:

- the same register length;
- the same ordered term weights;
- the same labeled common-factor count for every nonempty proper subset of the `m` terms; and
- different exact optimum values, with the one-block partition uniquely optimal in both.

Thus the exact interaction order required on this family is the full `m`-way statistic.

## 2. The full Boolean parity trade

Index the `m` term labels by `[m]`. For every support cell `S subseteq [m]`, define the signed trade

`delta(S)=(-1)^(m-|S|) L`.

Instance `A` receives `delta(S)` columns supported exactly on `S` when this number is positive; instance `B` receives `-delta(S)` such columns when it is negative. Every occupied entry is the same Pauli `X`, and every unoccupied entry is `I`.

Each parity class contains `2^(m-1)` support cells, so each side has

`N=2^(m-1)L`

trade columns. One parity class contains the empty support cell. That column is an inert all-identity register coordinate, which is permitted by the declared mathematical model and makes the two registers the same length. Every term is nevertheless nonidentity because of the common padding below.

For a labeled subset `T`, the signed difference of its common-factor count is the upper marginal

`M(T)=sum_{S supseteq T} delta(S)`.

## 3. Equality of all proper interactions

**Theorem C12 (full proper-marginal cancellation).** For every proper subset `T subsetneq [m]`,

`M(T)=0`,

whereas

`M([m])=L`.

**Proof.** If `T` is proper, then

`M(T)=L(-1)^(m-|T|) sum_{U subseteq [m]\T} (-1)^|U|`

`=L(-1)^(m-|T|)(1-1)^(m-|T|)=0`.

For the top set, the only superset is itself and `delta([m])=L`. ∎

The empty marginal also vanishes, so the total number of trade columns agrees. Singleton marginals are the ordered weights contributed by the trade; hence the weights agree. Every labeled interaction of orders two through `m-1` agrees as well.

## 4. Unique optimum and exact value gap

Let `b=ceil(log_2 m)` and let `d(m)` be the depth recurrence from the main manuscript. Add to both instances

`K=N m(b+1)+m-1+d(m)+b+1`

columns supported on all `m` terms.

**Theorem C13 (all-proper-interaction value separation).** In both padded instances the one-block partition is uniquely optimal, and

`|Delta(A)-Delta(B)|=[m(b+1)-1]L`.

**Proof.** The padding argument in V3 Section 6 depends only on an upper bound `N` for the number of trade columns on either side. Replacing the former `2^(m-2)L` by the present `2^(m-1)L` leaves the same lower bound for every proper partition:

`3K-Nm(b+1)-[m-1+d(m)+b]>0`.

Thus every proper partition costs strictly more than the full block in both instances.

All proper marginals and all weights agree by Theorem C12. The only objective input that differs is `f([m])`, by exactly `L`. Its coefficient in the one-block improvement is `m(b+1)-1`, which gives the displayed gap. ∎

For fixed `m`, the ambiguity grows without bound as `L` increases.

## 5. Exact interaction-order threshold

Let `Phi_<m` consist of the ordered weights and every labeled common-factor count on a proper nonempty subset of `[m]`.

**Corollary C14 (full-order necessity on the constructed family).** The exact optimum value does not factor through `Phi_<m`. The full `m`-way common-factor count is necessary for exact identification on this family.

This is a representation statement, not an assertion that every algorithm must explicitly materialize all `m`-way features. An algorithm may obtain equivalent information by another sufficient representation.

## 6. Primitive kernel at full dimension

The cancellation theorem is also the complete integer kernel.

**Theorem C15 (full proper-marginal kernel).** Let `delta:2^[m]->Z` satisfy

`sum_{S supseteq T} delta(S)=0`

for every proper `T subsetneq [m]`. Then

`delta(S)=(-1)^(m-|S|)c`,

where `c=delta([m])`.

**Proof.** Apply Möbius inversion on the full Boolean lattice. Every upper marginal except the top one is zero, so only the alternating contribution of the top marginal remains. ∎

A primitive nonzero integer trade therefore uses every Boolean cell and has mass exactly `2^(m-1)` on each signed side. The R6 construction with `L=1` attains this minimum. This proves minimality of the invisible difference trade, not of the common padding.

## 7. Verification

`papers/verify_five_math_extensions_r6.py` independently checks the construction for `m=5` and `m=6`.

- It verifies all 30 and 62 nonempty proper marginals, respectively.
- It enumerates all 52 and 203 set partitions.
- It confirms that the one-block partition is the unique optimum on both sides.
- It obtains exact gaps 19 and 23, matching `m(ceil(log_2 m)+1)-1`.
- It confirms primitive side masses 16 and 32.

The finite checks guard the objective arithmetic. The parity identity and Möbius-inversion proof carry the all-parameter theorem.

## 8. Prior-art and novelty calibration

Hierarchical-model fibers, Markov moves, parity trades, and Boolean-lattice Möbius inversion are established mathematics. The generic one-dimensional kernel is not claimed as new. The paper-specific advance is its exact realization inside the fixed Pauli partition objective together with conservative padding that makes the full block uniquely optimal, yielding a solved identifiability threshold for exact value.

## 9. Atomic status

- Equality of every proper labeled marginal: `VERIFIED`.
- Equality of ordered weights and register length: `VERIFIED`.
- Unique one-block optimum under the displayed padding: `VERIFIED` analytically and by complete finite partition checks at `m=5,6`.
- Exact value gap: `VERIFIED`.
- Primitive full-dimensional parity kernel: `VERIFIED`.
- Claim that order `m-1` generally suffices for other objectives: `REFUTED` only for the declared family and objective.
- Production-compiler or physical-resource transfer: `NOT_CLAIMED`.

## 10. Remaining scientific frontier

The exact worst-case interaction-order question is now closed for the constructed family: all proper interactions fail and the full interaction resolves the hidden coordinate. The next meaningful advance is prevalence rather than another loss function—measure how often large proper-marginal fibers or near-collisions occur in production-derived Pauli instances, and compare alternative representations that recover the missing top-order information more economically.

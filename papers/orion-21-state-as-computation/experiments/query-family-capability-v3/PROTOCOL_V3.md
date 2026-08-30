# ORION-21 capability V3 — an interval that respects the fold split

**Parent:** `PROTOCOL_V2.md`, terminal `QUERY_FAMILY_CAPABILITY_ESTIMATED`
(LINEAR 7/55 `[0.053, 0.245]`, RBF 21/55 `[0.254, 0.523]`, KNN 23/55
`[0.287, 0.559]`, all below 0.6).

## Chronology

Committed before this produces any outcome. It does not retune V2, does not
revisit V1's `>=8/10` gate, and cannot convert either into a positive.

## The limitation this addresses, in V2's own words

> responsibilities within a stratum share one dataset and one fold split, so they
> are not independent; the interval is reported as a nominal binomial interval and
> that dependence is stated rather than modelled away.

Two dependences sit behind that sentence, and they are not equally fixable here.

**Shared dataset.** Not addressable offline. The mechanism needs `d >= 16`
features and several classes; of the datasets available without network access
only `digits` qualifies (`wine` d=13, `iris` d=4, `breast_cancer` two classes).
This protocol does not claim to fix it, and V3's terminal will say so.

**Shared fold split.** Addressable, and this is what V3 does. Every V2
responsibility was scored against one `StratifiedKFold(random_state=20261121)`.
A responsibility that happens to fall the right side of that particular partition
is counted as capability, and 55 responsibilities sharing one partition can move
together. The binomial interval prices none of that.

## Design

Everything mechanical is inherited from V2 unchanged: `digits`, `StandardScaler`
then `SelectKBest(f_classif, k=16)`, the three decoders and their
hyperparameters, the `compiled >= universal - 0.02` quality rule, and the same 55
responsibilities (10 size-one subsets, 45 size-two).

The one change: the estimate is repeated over **20 independent fold seeds**,
`20261121` plus nineteen successors fixed here and not chosen after seeing
anything. The seed is the clustering unit.

## Estimand and uncertainty

`theta` is unchanged: `P(a responsibility is quality-supported)`.

Reported three ways, and the gap between them is the finding either way:

1. **per-seed capability** — 20 values per access class, and their spread;
2. **seed-clustered interval** — a percentile bootstrap resampling *seeds*, not
   responsibilities, so the unit resampled is the unit that varies;
3. **V2's nominal binomial interval** on the pooled count, carried forward for
   comparison only.

If (2) is materially wider than (3), V2's interval was optimistic and this says by
how much. If they agree, the fold split was not carrying the estimate and V2's
number stands better supported than it could claim at the time. Both are useful
and neither is the hoped-for answer.

## Predeclared readings

Fixed before outcomes, on the **seed-clustered** interval:

- entirely below 0.6 → V2's headline survives a dependence-respecting interval,
  and the bound on capability is real rather than nominal;
- straddling 0.6 → V2's exclusion of the 0.6–0.8 band was an artefact of pricing
  dependent observations as independent, and must be withdrawn to
  `CANNOT_CHECK_DEPENDENCE_NOT_PRICED`;
- entirely above 0.6 → V2 was wrong in direction; report it and stop.

Every seed's per-class count is reported. No seed may be dropped after outcomes,
including any that disagrees with the rest.

## Terminals

- `CAPABILITY_SURVIVES_SPLIT_CLUSTERING` (exit 0)
- `CANNOT_CHECK_DEPENDENCE_NOT_PRICED` (exit 3)
- `CAPABILITY_REVERSED` (exit 1)

No terminal here promotes an ORION-21 claim. `P11_ACTIVE_CLAIM_AUTHORITY_V2.json`
remains the authority, V1's `>=8/10` negative is untouched, and the readiness item
"learned non-oracle compiler" stays open.

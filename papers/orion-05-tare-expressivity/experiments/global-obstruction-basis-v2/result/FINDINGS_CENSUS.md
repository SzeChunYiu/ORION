# ORION-05 V2 — full-domain census (supplementary to the Stage 1 terminal)

## What this is, and what it is not

Stage 1's terminal is already certified from the prefix: three positives at
indices 152, 156 and 162 over a gap-free `[0, 960)`. **This census is not part of
that terminal** and changes nothing about it. It answers the separate question the
protocol did not need answered — *how large is C3's candidate class?*

## Coverage

| | |
|---|---|
| shards | 11,252 |
| instances solved | **33,755 / 33,755** |
| domain fully covered | **true** |
| double-counted | 0 |
| integrity problems | **0** |

The entire repeated-target domain, walked once, with no hole and no row solved twice.

## Result

**4,965 positives — 14.7% of the domain.**

The gap histogram is the finding:

```
gap 0 : 28,790
gap 1 :  4,965
```

**Every positive in the entire domain has gap exactly 1.** Not one instance
anywhere shows a gap of 2 or more. The prefix hinted at this — the first three
positives were all `C1=6, C2=5` — but a prefix cannot distinguish "the gap is
always 1" from "we have not yet reached a larger one". The census can, and it
does: across 33,755 instances the C1–C2 separation is either absent or exactly
one, never more.

That is a stronger statement than the terminal needed. Stage 1 asked whether
same-domain positives exist. They do, they are common rather than exceptional at
roughly one instance in seven, and they are uniform in magnitude.

## Cross-validation

Three passes with different shard geometry covered the domain: chunk 2 (480
shards over the prefix), chunk 18 (the original scan) and chunk 3 (this census).
Aggregated together:

| | |
|---|---|
| shards | 11,828 |
| union | 33,755 |
| rows solved by more than one pass | **2,374** |
| integrity problems | **0** |

The aggregator flags any index where two shards disagree on `(C1, C2)`. Zero
problems across 2,374 independently duplicated rows is an empirical check that the
solver is deterministic and that shard indexing is correct — the two assumptions
the whole sharded design rests on, tested rather than assumed.

## Theory reading

Unchanged from the terminal, and now measured rather than inferred: positives are
**O05-C3's candidate class**, so the census **supports O05-C3 and falsifies
O05-C2** on the repeated-target domain. The class is 4,965 instances wide and
uniform at gap 1.

## Cost

33,755 instances at ~492 s each is ~4,613 core-hours, run at up to 916 cores on
LUNARC. `CHUNK=3` was chosen deliberately: the runner breaks out of its loop once
it holds three positives, so any chunk larger than 3 can stop mid-range and leave
a census hole. At chunk 3 the break can only fire on the chunk's last row, which
is why `domain_fully_covered` is true rather than nearly true.

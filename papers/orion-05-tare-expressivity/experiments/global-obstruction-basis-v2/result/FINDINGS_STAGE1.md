# ORION-05 V2 Stage 0 + Stage 1 — result

## Stage 0: controls pass

`STAGE0_CONTROLS_PASS`. The three controls return exactly what COMPUTE_PLAN_V2
requires under the all-matchings estimand, so Stage 1 has authority:

| control | measured (C1, C2) | required | gap |
|---|---|---|---|
| `r6o-16` | (4, 4) | (4, 4) | 0 |
| `r6o-17` | (5, 5) | (5, 5) | 0 |
| `r6o-19` | (6, 6) | (6, 6) | 0 |

`solver_matches_v1_census: true` — the solver is byte-identical
(`642cc67a…`) to the one the v1 census used, so this is the same instrument.

## Stage 1: positives exist, and the first three are certified

Terminal: **`SAME_DOMAIN_POSITIVE_CONTROLS_FOUND`**.

| | |
|---|---|
| gap-free prefix | `[0, 960)` |
| third positive at | index 162 |
| positives in prefix | **69** (7.2% of 960 rows) |
| integrity problems | 0 |

The globally first three positives, in lexicographic order:

| index | lex | codes | C1 | C2 | gap |
|---|---|---|---|---|---|
| 152 | 153 | `[1, 1, 1, 2, 4, 9]` | 6 | 5 | 1 |
| 156 | 157 | `[1, 1, 1, 2, 4, 13]` | 6 | 5 | 1 |
| 162 | 163 | `[1, 1, 1, 2, 5, 8]` | 6 | 5 | 1 |

The authority is not "three positives turned up." It is that the union of shard
coverage contains **every** index from 0 through the third positive with no hole,
which is what makes "first three" a fact about the domain rather than about where
the scan happened to look. The aggregator refuses to assign this terminal if a
single index below the third positive is unaccounted for.

## Theory reading, fixed in advance by the protocol

The compute plan registered both outcomes before the run. A full-domain absence
of positive gaps would have supported **O05-C2** (matching relaxation erases the
historical gaps) and falsified **O05-C3**. Positives are C3's candidate class.

Positives exist. This **supports O05-C3 and falsifies O05-C2** on the
repeated-target domain, and the three instances above are the registered
candidate class.

## Independent cross-check

Two independent passes covered the prefix with different shard geometry: a
chunk-2 pass (480 shards) and a chunk-18 pass. Aggregated together they give 495
shards, union 1,033 rows, 8 double-counted rows — and **0 integrity problems**.
The aggregator flags any index where two shards disagree on `(C1, C2)`, so zero
problems across the overlap is an independent check that the solver is
deterministic and the shard indexing is correct.

## Cost

Measured 492 s per instance (C2 is the whole cost; C1 is ~0.43 s), confirmed
independently by the v1 control records (472.6 / 469.7 / 473.1 s). The prefix
that produced this terminal cost ~131 core-hours. The 4,613-core-hour full-domain
walk was only required for the negative terminal and is not needed for Stage 1.

A separate full-domain census is running as **supplementary** characterisation of
how large C3's candidate class is. It is not part of this terminal.

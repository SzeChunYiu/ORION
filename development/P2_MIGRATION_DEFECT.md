# P2 vocabulary migration (#1078) — RESOLVED

**Status: resolved.** This file previously recorded the migration as blocked
on a design decision. That assessment was wrong, and the record is kept
rather than deleted because the error is the useful part.

## What was claimed here

That `consecutive_zero_novelty_before`, `open_obligation_ids` and
`attempt_index` had *no source in the repository*, so completing the port
meant deciding what opens an obligation in the P2 protocol — the study's
scientific content, not a rename.

## Why that was wrong

The search stopped at `runner.py`. Two working implementations already
existed:

- `baselines.py` — computes all three, with the rationale written beside them
- `arb_systems.py` — a second, independent site doing the same

Nothing needed inventing. It needed reading.

The semantics, taken verbatim from `baselines.py`:

| field | rule |
|---|---|
| `attempt_index` | counts per **route**; read before the call, incremented after |
| `consecutive_zero_novelty_before` | advances only when a route **answered** and returned nothing new — a route that did not answer has said nothing about novelty either way |
| `open_obligation_ids` | a non-OK transport opens `"<route>:<attempt>"`, because *"a provider that did not answer censors what it holds"* |

`repeat_index` came from the sweep's own docstring: *"Every task, every seed,
in a fixed order. Repeats are nested, never pooled."* A repeat **is** a
seed's position.

## What the chain actually contained

Each fix exposed the next, all the same refactor's residue:

1. `SystemTrace(route_events=…)` — the deprecated types
2. `caps.query_count` against a `Budget` that has `max_route_calls`
3. `ProtectedGold` missing `gold_set_complete`
4. `trace.resources.search_queries` where `ResourceUse` has `query_count`
5. the candidate checker filtering a `"scope"` discriminator removed by the
   split into `route_stop_audits` / `route_exhaustion_audits`

## Result

Measured on LUNARC against `main`, comparing failing **sets**:

```
tests/unit/p2:  81 failed / 607 passed  ->  62 failed / 626 passed
fixed: 19    broken: 0
```

`check_p1_p5_native_embedding_v1.py`, which was failing `p6-p8-candidate-ci`,
exits 0: `P1-P5 NATIVE EMBEDDING V1: PASS`.

Both `KNOWN_OPEN` registries — in `test_p2_runner_constructions.py` and
`test_dataclass_drift.py` — are now empty.

## The lesson worth keeping

A blocker asserted from a partial search is not a blocker. The claim "no
source exists" requires a search whose **scope** was justified, not one that
merely returned nothing — the same rule that applies to any absence claim.
One `grep` across the package would have settled it before the record was
written.

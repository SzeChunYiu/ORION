# P2 vocabulary migration is incomplete (#1078)

**64 of 205 current test failures come from one cause.** Recorded here
rather than fixed, because the remaining work is a design decision this
lane should not make alone. The reasoning is below so the owner can make it
quickly.

## What happened

PR #1078 landed a vocabulary refactor in `orion/study/p2`:

| Old | New |
|---|---|
| `RouteEvent` | `RouteTrial` |
| `ReadEvent` | `ReadEncounter` |
| `SystemTrace.route_events` | `SystemTrace.route_trials` |
| `SystemTrace.read_events` | `SystemTrace.read_encounters` |
| `SystemTrace.budget_exhausted` | `SystemTrace.truncated_at_cap` |
| `Evaluation.gold_denominator` | (removed) |

It propagated the new `systems.py` and `gold.py`, but **not `runner.py` or
the p2 test suite**. The old classes were later restored verbatim from
`2a692316` so imports would resolve, and `systems.py` says so plainly:

> *Deprecated: superseded by `RouteTrial` in the vocabulary refactor landed
> as #1078. Restored verbatim from 2a692316 (pre-landing main) because the
> landing propagated the new `systems`/`gold` without migrating `runner.py`
> or the p2 test suite, leaving imports of this name broken.*

Restoring the classes fixed the imports. It did not fix `SystemTrace`, which
still accepts only the new field names. So `runner.py:469` constructs a trace
the dataclass rejects:

```
TypeError: SystemTrace.__init__() got an unexpected keyword argument 'route_events'   x58
TypeError: Evaluation.__init__() got an unexpected keyword argument 'gold_denominator' x6
```

## Why this is not a rename

Most fields port directly:

| `RouteEvent` | `RouteTrial` |
|---|---|
| `index` | `index` |
| `route` | `route_id` |
| `probe` | `probe` |
| `backend_identity` | `backend_identity` |
| `query_derivation_identity` | `query_derivation_identity` |
| `status` | `transport_status` |

Three do not, and they are the reason this is blocked:

- **`captures: tuple[Capture, ...]`** — the old record carried
  `retrieved_doc_ids` and `retrieved_content_identities` as flat tuples. The
  new one wants structured `Capture` objects. Pairing the flat tuples is a
  guess about which identity belongs to which document.
- **`attempt_index`** — the session tracks `_route_calls: dict[str, int]`,
  so this is probably derivable, but whether an attempt counts per route or
  per probe is a design question.
- **`consecutive_zero_novelty_before`** and **`open_obligation_ids` /
  `opened_obligation_id`** — the runner tracks neither. It has no concept of
  an obligation at all: `obligation`, `attempt`, `zero_novelty` and
  `Capture` appear three times in the entire file, none of them as state.

## Why this was not fixed here

Completing the migration means deciding what opens and closes an obligation
in the P2 protocol, and how captures pair with identities. Those are the
study's scientific content.

Values invented to satisfy a constructor would flow through `evaluate()`
into the P2 results, and they would look exactly like measurements. A test
suite going green on fabricated obligation semantics is worse than one that
stays red and says why.

## What would resolve it

The owner decides the three semantics above; the port is then mechanical.
The 48 affected test files are already identified by the failure log, and
`offline_mechanisms.py` (lines 58 and 94) reads `trace.route_events` and
must move with the runner.

# Shipping tested modules that nothing calls

**Observed:** 2026-08-16, measured against my own session output.

## Measurement

Production consumers, excluding the module itself, its tests, and `__init__`
re-exports:

```
knowledge/space.py           0        kernel/hard_gates.py     0 -> 1 (driver stop path, same day)
knowledge/research_loop.py   0        kernel/workorder.py      1
knowledge/ingest.py          0        kernel/report.py         1
knowledge/local.py           0        knowledge/evaluation.py  1
knowledge/rate.py            0
```

**Six of fifteen modules added this session have no caller in the production
path.** All fifteen have tests. All fifteen merged green.

## Failure class

`TESTED_BUT_UNWIRED` — the same defect this repository documents in its
provenance source and which I cited repeatedly while committing instances of it:
`MetricDirection.NON_COMPENSATORY_GATE` as an enum nothing branched on,
`AuthorityTransport` with only a test consumer, `related_failure_episodes`
computed and never consulted, `evolution_archive.py` ported faithfully and never
called. The audit rule I applied to RAKL — *a name with no consumer is ABSENT* —
marks six of my own modules ABSENT.

## Root cause, one level down

A green suite was treated as the completion signal. It is not: a test proves a
module behaves as specified in isolation, and says nothing about whether any
path reaches it. The two failure modes look identical in CI and are opposite in
value.

The incentive compounds it. Adding a module with its own tests always merges
green, because it cannot break anything that does not call it. Wiring a module
into the driver risks breaking the suite. So the cheapest-looking step is always
the one that adds surface without adding capability, and repeating it produces
exactly this repository's characteristic defect.

## Guard

A module is not done when its tests pass. It is done when something on the
production path calls it, and a test exercises it *through* that path.

Concretely, before opening a new module: name the caller. If the caller does not
exist yet, build the caller first and let it fail for want of the module — the
same discipline as writing the failing test first, applied one level up.

For review: `grep -rl "from \.<module>" src/ | grep -v __init__ | grep -v <module>.py`
returning nothing is a blocking finding, not a style note.

## Where this leaves the six

They are not wasted — `space.py` and `hard_gates.py` in particular are correct
and were written against real specs. But they are inventory, not capability, and
this repository already contains more inventory than it can verify. The next
work on any of them is a caller, not a feature.

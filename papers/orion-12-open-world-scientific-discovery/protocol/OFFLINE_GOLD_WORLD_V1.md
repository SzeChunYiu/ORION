# ORION-12 offline complete-gold world V1

**Artifact:** `../evidence/offline_gold/` (`world-000.json`, `world-001.json`,
`topics.json`, `tasks-000.json`, `tasks-001.json`, `MANIFEST.json`)
**Generator:** `src/orion/study/p2/` — `corpus.py`, `cases.py`, `systems.py`, `runner.py`, `gold.py`, `freeze.py`
**Seed:** `20260816`
**Suite fingerprint:** `2f6936ba52fb12dbee7614b6409fe35ee8f34f443088a11fe5f8916552649c1c`
**World content hash:** `f93b1f55c0e0db4f32ed4e4b507a84a51f01d1dd62c28c393296724a82aa89a7`
**Status:** the gold suite was frozen before any system was configured against it.
Systems, baselines, ablations and their results now exist as separately bound
artifacts; they are not inputs to this generator.

## Why an offline world at all

`JOURNAL_READINESS.md` §3 requires an offline controlled-index companion so the
headline evidence survives mutable web results. It also requires something the web
cannot supply: a **complete denominator**. On the open web nobody can enumerate
every relevant paper, so "we found 40" cannot be distinguished from "40 of 41" or
"40 of 400", and recall is not a measurable quantity. Here relevance is decided by
a rule over authored content, so the gold set is complete by construction.

## What it contains

1,210 documents, 78 topics and 390 tasks (5 case families × 78 topics), meeting
the outcome-blind 385-task commitment recorded in `STATISTICAL_PLAN_V1.json`.
Each topic has 9 relevant content identities represented by 11 relevant records:
one republication shares a content identity and one revision shares an identity
while changing its digest. Four distractors per topic and 40 unrelated filler
records complete the corpus. Every emitted record carries
`task_family = "offline_complete_gold"`,
one of the five families `PROTOCOL_V1.json` froze; the case family is internal
structure and never travels as a protocol family.

**Relevance rule.** A topic declares `required_concepts`; a document is relevant
iff it carries all of them. The gold set is a *materialized cache* of applying
that rule to the corpus, not a hand-authored list — which is what lets a test
recompute it over every document and demand agreement, rather than trusting it.

**Heterogeneous reachability.** Relevant works are deliberately not all reachable
the same way. Per topic: 2 lexical-only, 2 paraphrase-only (semantic keys share no
token with the lexical keys), 2 citation-only (reachable solely by following a
reference edge out of a seed you must already hold), 1 reformulation-only, 1
behind a restricted provider, 1 cross-listed on two routes. No single route
reaches the whole gold set, at any budget — which is what makes route diversity,
marginal route gain and fail-closed coverage measurable rather than decorative.

**Route identity.** `LEXICAL` and `REFORMULATION` share the backend
`index:lexical` with different query derivations — nominally distinct routes over
one index, which is the negative case ORION-12.H2 needs and what reformulating a query
against the same index actually is. The other three hit distinct backends and can
earn independence under `orion.knowledge.routes.assess_pair`.

**Separated identity.** A work, a copy and a revision are three things. A
republication shares a content identity at a different locator (so counting
locators inflates coverage); a revision shares the identity and changes the digest
(so rereading it is legitimate). Recall is counted over content identities.

**Case families.** `complete_gold_multiroute`, `route_exhaustion` (a route runs
dry — route-stop is licensed, task-stop is not), `unavailable_route` (a provider
dies mid-run, leaving *censored* rather than absent material),
`extraction_question_shift` (the frame changes after 3 reads, making rereads
legitimate), `duplicate_identity` (read budget tightened to 12 so re-reading a
republication actually costs recall).

**Budgets.** `max_route_calls = 12` against 16 published probes plus earned
citation seeds: exhaustive probing does not fit, so allocation and stopping are
what vary. Citation probes are withheld from the public view and accepted only for
documents the system has actually retrieved — snowballing means chaining from
something you hold.

## Custody

A system receives a `PublicView` and a `DiscoverySession`, never a task, world or
gold. The session is handed a label-free projected index and a gold-free config,
so nothing it holds carries `concept_tags` (the rule) or `protected_gold` (the
answer); a hostile fixture in the tests goes looking and finds neither. Route
calls, reads and stop decisions are recorded host-side as they happen, so a system
cannot under-report a route or edit its own trace. Budget exhaustion closes the
session permanently, and spend is charged against counters that only increment,
never against the length of the event log — charging against the log let a
candidate clear it and query forever.

Python has no hard private attribute, so in-process enforcement can always be
reached around by a determined candidate. The guarantee that does hold is the
host's post-run audit: `gold` compares the recorded run against the frozen budget
and voids any overrun as `INVALID / harness_tamper`. Both evasions are covered —
suppressing the counters leaves an event log longer than the budget, and clearing
the log still trips the counters.

## Emissions

Per (system, task, seed): a result record conforming to
`RESULT_RECORD_SCHEMA_V1.json`, plus a rich artifact it content-addresses via
`raw_artifact_hash`. The record's `metrics` object accepts numbers only, so all
structured material lives in the artifact: discovered/missed gold identities,
per-route unique-relevant contribution, per-route pair overlap by content
identity, marginal relevant gain in route order, stop audits (each replayed
against world state at its timeline index, with still-reachable count and
remaining budget), censored identities, unavailable-route events,
`(content_identity, extraction_question)` processing pairs, read classifications,
and full resource use. The field list is a superset of the obvious needs; new
quantities belong in the artifact, which extends without touching the record shape.

`run_manifest_hash` is supplied by the caller, never minted here. The executed
controlled campaign is bound separately by `OFFLINE_RUN_MANIFEST_V1.json` and its
recorded digest; regenerating this gold suite does not rewrite that execution
identity.

## Regenerating and verifying

```
python3 -m orion.study.p2.freeze              # verify the committed artifact
python3 -m orion.study.p2.freeze --write      # regenerate from FROZEN_SEED
PYTHONPATH=src python3 -m pytest tests/unit/p2 -q
```

Verification requires three fingerprints to agree: regenerated from the seed,
loaded from the committed bytes, and recorded in the manifest. Determinism is
checked across a process boundary with `PYTHONHASHSEED` forced to differ, because
a suite that only reproduces inside one interpreter is not reproducible.

## Licence and provenance

Fully synthetic. Every document, title, abstract, author name, venue and
identifier is generated by `corpus.py` from the recorded seed; no third-party
text, metadata or identifier is copied in, and nothing was scraped. The corpus
therefore carries no third-party licence encumbrance and is redistributable on the
repository's own terms. **No separate licence is asserted here**: at the time of
freezing there is no `LICENSE` file at the repository root, and inventing one in
this document would be worse than saying so.

## What this can and cannot support

**Can.** Complete-gold recall against a real denominator. Route-level unique
contribution and overlap by content identity. Separation of route-stop from
task-stop, and premature closure measured against what was still reachable at the
moment of the claim. Fail-closed behaviour when a provider dies. Content-level
dedup, and legitimate rereads distinguished from duplicated processing. All of it
under matched, enforced budgets, with failures retained as outcomes.

**Cannot.** This is a synthetic world, so a result here measures **mechanism under
a complete denominator** and is not evidence of real-world literature-discovery
superiority. The stronger caveat is more specific: because the route structure is
*authored*, a positive result says the mechanism behaves correctly **given that
structure** — it is not evidence that real providers exhibit that structure, and a
reviewer is entitled to ask whether they do. Nor does it measure query
formulation: probe vocabularies are published, so systems are compared on route
allocation and stopping, not on inventing search terms. Screening is deliberately
easy — relevance is legible from each abstract — so that discovery and stopping
are what vary; MetaSyn-style screening difficulty is a separate task family.
Finally, no cost model, no provider latency and no contamination surface exists
here, because nothing is fetched.

An exact matched live-provider superiority campaign remains unavailable. The
later diagnostic probes and adverse public-screening successors do not convert
that missing comparison into a positive result. This world preserves the
controlled mechanism result when web providers change; it does not stand in for
provider-native execution, population transport or independent custody.

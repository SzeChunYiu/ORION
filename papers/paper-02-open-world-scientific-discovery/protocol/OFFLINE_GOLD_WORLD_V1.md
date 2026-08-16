# ORION-P2 offline complete-gold world V1

**Artifact:** `../evidence/offline_gold/` (`world.json`, `tasks.json`, `MANIFEST.json`)
**Generator:** `src/orion/study/p2/` — `corpus.py`, `cases.py`, `systems.py`, `runner.py`, `gold.py`, `freeze.py`
**Seed:** `20260816`
**Suite fingerprint:** `8d0b826821fc8dc6468e9641fc6bef6dd375f3ea1128a0e28089f28641e4ea65`
**World content hash:** `d3405f686204e50cee28a0e768d6b69a40ab2fb9d823de44a62283eef1428469`
**Status:** frozen before any system was configured against it. No system, baseline
or ablation exists in this package, deliberately.

## Why an offline world at all

`JOURNAL_READINESS.md` §3 requires an offline controlled-index companion so the
headline evidence survives mutable web results. It also requires something the web
cannot supply: a **complete denominator**. On the open web nobody can enumerate
every relevant paper, so "we found 40" cannot be distinguished from "40 of 41" or
"40 of 400", and recall is not a measurable quantity. Here relevance is decided by
a rule over authored content, so the gold set is complete by construction.

## What it contains

100 documents, 4 topics, 20 tasks (5 case families × 4 topics), 9 relevant works
per topic. Every emitted record carries `task_family = "offline_complete_gold"`,
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
one index, which is the negative case P2.H2 needs and what reformulating a query
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
session permanently — swallowing `BudgetExhausted` buys nothing.

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

`run_manifest_hash` is supplied by the caller, never minted here: a run manifest
binds a subject revision, provider revisions and an evaluator hash, none of which
exist while the world is outcome-blind. Manifest binding is next-phase work.

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

Live-provider evidence against AutoResearchBench, SAGE and MetaSyn remains
required and remains `CANNOT_CHECK`. This world makes those results reproducible
when web results change; it does not stand in for them.

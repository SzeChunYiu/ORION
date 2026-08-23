# Acquisition plan for an independent researcher

**Date:** 2026-08-23
**Data:** `EXTERNAL_ACQUISITION_AUDIT_2026-08-23.json` (16 items), `ACQUISITION_ROUTE_PROBE.json` (15 routes, 6 checkpoints)
**Authority:** `AUDIT_OF_CLASSIFICATION_ONLY`. Nothing here discharges, weakens or relabels a registered claim.

## The finding

**Not one of the sixteen blocked items names an institution or a budget.** Every one names a
property of the *evidence*: not authored by you, frozen before outcomes, labels withheld, an
independent scorer, checkpoints and compute, or a bespoke human panel adjudicating your own cases.

Only the last has no free route, and it is the residual on **2** of the 16.

| Requirement | Free route | Verified |
|---|---|---|
| **A** artifact not authored by you | OpenAlex (321.9M works), Crossref (185.7M), arXiv, GitHub | 200 |
| **B** frozen before outcomes, third-party timestamped | OSF Registries, AsPredicted, Zenodo, Software Heritage | 200 |
| **C** labels withheld from you | public benchmarks whose test labels you never see | route-specific |
| **D** independent scorer or adjudicator | PCI Registered Reports, ML Reproducibility Challenge, OpenReview, TMLR | 200 |
| **E** checkpoints and compute | six open-weight checkpoints; your own cluster | 6/6 resolve |
| **F** a panel adjudicating *your* cases | — | none |

Reclassifying the sixteen: **2 locally unexecuted, 1 locally broken, 2 procurable free,
11 partially procurable, 0 with no free route at all.**

## Start here — ranked by what it costs you

### 1. P9-U-T3 frontier: 0 of 1,344 cells, and nothing is missing but a download

This is filed as an external blocker. It is not one.

The grid is **already frozen before outcomes** and pinned by sha256, with `extrapolation_permitted:
false`, `interpolation_permitted: false`, an on-grid rule and Holm–Bonferroni multiplicity. Its
`environment_boundary` records `open_weight_checkpoint_present: false` and an outbound proxy
returning 403 — facts about the box it was written on, not about the world.

Its declared ladders are six openly published checkpoints. All six resolve live:

| Checkpoint | Gated | Licence |
|---|---|---|
| `Qwen/Qwen2.5-0.5B` | no | apache-2.0 |
| `Qwen/Qwen2.5-1.5B` | no | apache-2.0 |
| `Qwen/Qwen2.5-3B` | no | other — research licence, not Apache |
| `Qwen/Qwen2.5-7B` | no | apache-2.0 |
| `meta-llama/Llama-3.2-1B` | **manual** | llama3.2 |
| `meta-llama/Llama-3.2-3B` | **manual** | llama3.2 |

`gated: manual` is free but needs an accepted licence on an account — real friction, stated rather
than glossed. 1,344 cells = 4 relational complexities × 7 representations × 6 scale points ×
4 inference budgets × 2 domain blocks, at a fixed sample budget of 4.

**No new claim identity is needed**, and that is the point: the freeze was written for exactly this.
Every cell executed is a cell the grid already declared.

### 2. P6 clean-room replay: no data, no labels, no panel

Wants a byte-for-byte replay of a bounded **formal** artifact by someone who is not you. The
blocking precondition is local and undone: **the replay bundle has to run from a cold start before
any custodian can be asked.** Package it, put it on Zenodo with a DOI, submit it where third parties
reproduce work for free.

### 3. P2 task-world identity: a local failure filed as an external one

Its disposition opens with *"the archived task-world baseline has not been reproduced."* That is
local. P2's own ceiling diagnosis says the binding stage was `CANDIDATE_GENERATION`: the arm's
routes returned **7 of 229** gold identifiers, capping `avg_iou` at 0.0113 against a 0.03 threshold.
That is a retrieval problem, and keyless bibliographic APIs are a retrieval answer.

A second, distinct P2 reproducibility failure is live in CI right now
(`test_p2_lexical_echo_successor`, frozen digest matching while per-arm numbers diverge). Check
whether they share a root cause before treating them separately.

### 4. P5 H1–H4: its own next step is a local script

`next_executable_step` is a `PREFLIGHT` running locally, and success is nine identity and custody
blockers clearing. Identity bindings are authored, not bought. Run it and **count how many of the
nine actually need an outside party** — the item asserts all nine are external without that count.

## The two that stay hard, and the honest thing to do about them

**P4 naturalistic generality** and **P14D external validity** both carry a class-F residual: a
blinded panel adjudicating *your* cases.

For P14D there is a route worth testing, not assuming. The scientific record already contains a very
large corpus of promotion, retention and reopen decisions adjudicated by editors and publishers,
authored by people who are not you, timestamped long before any ORION protocol existed:
**134,509** works flagged retracted in OpenAlex, **74,828** retraction-notice works in Crossref, and
the Retraction Watch database itself free via Crossref Labs.

**This is a candidate, not a substitute.** A retraction record is an adjudicated outcome; a
governance-contract case packet is a different object. Whether the ORION promotion or reopen
decision is even *defined* on such a record has to be established first — and **if it is not, this
route failed and should be recorded as having failed**, not quietly dropped.

If it does fail: P14D stays externally blocked and P14C's specification-conformance result stands as
the bounded claim, exactly as it already does. Saying "this claim is bounded to publicly adjudicated
cases" is correct scoping. It changes what the result is evidence about, not how strong it is.

## The rule that governs all of this

**Never edit an existing blocker to make it satisfiable.** The ledger's own `historical_policy`
forbids it — `post_hoc_relabeling_prohibited`, `successor_requires_new_claim_id` — and the validator
rejects authority laundering. Every route above requires a **new claim identity, prospectively
frozen, sitting beside the untouched original**. `P9.T3.OPEN_CHECKPOINT_FRONTIER.V1` is a new claim,
not a weakened `P9.U.T3.FRONTIER.EXECUTION.V1`.

The exception is item 1, and only because its freeze already declared the cells.

## What "verified" means here, and what it does not

`probe_acquisition_routes.py` re-probes every route and checkpoint and records what answered. That
establishes **reachability and licence**. It does **not** establish that any route's *content*
satisfies any particular blocker — that is per-item work, and each item's entry names its own
caution. Re-run the probe before acting on this plan; a resource that has moved or become gated is
not a resource.

`check_acquisition_audit.py` runs offline and fails if the audit stops covering every blocked item,
misstates a ledger category, or lets its summary drift from its own items.

## The residual, in one line

Eleven of sixteen reduce to a single missing class: **D, an independent scorer or adjudicator.**
Free venues supply it — but on a publication timescale, not a compute timescale. That, not money and
not affiliation, is the real gate.

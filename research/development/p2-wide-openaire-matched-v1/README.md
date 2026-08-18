# P2 Wide structured-identity matched campaign — development packet V1

**Date:** 2026-08-18  
**Paper:** P2 — Open-World Scientific Knowledge Discovery  
**Parents:** #99, #279, #157  
**Prerequisite:** `P2_OPENAIRE_IDENTITY_PROBE_V1.json` terminal `SCORER_NATIVE_IDENTITY_BRIDGE_OBSERVED`.

## Atomic research question

Given a keyless scorer-native arXiv identity bridge, does P2's provenance/route governance improve AutoResearchBench Wide set retrieval over a **strong matched dual-backend baseline that sees the same raw acquisition evidence under the same request and candidate budgets**?

This is the broad external acquisition test. It is not a replacement for P2's controlled stopping-safety evidence; the paper-level claim may combine external acquisition evidence with the already-frozen stopping/closure evidence, but this experiment itself does not invent an external stopping oracle the benchmark does not provide.

## Knowledge/search-universe saturation for this comparison atom

The search needed to freeze this experiment covers:

1. the pinned AutoResearchBench Wide scorer and its exact set-IoU/recall/precision semantics;
2. current OpenAIRE V3 research-product search and authoritative arXiv PID objects;
3. current Crossref Works bibliographic search and DOI identity;
4. OpenAIRE V3 `pid` lookup/logical-OR semantics for DOI→research-product crosswalk;
5. P2's existing nearest-work and acquisition campaign, which already owns the broader retrieval/stopping literature search.

The experiment does **not** need another general deep-research literature sweep to decide its mechanics. Its comparison atom is whether independent backend provenance and selection over the same retrieved pool changes official Wide performance.

## Challenge to the saturation basis

Missed-knowledge / false-flat risks considered before score:

- Direct OpenAIRE search and Crossref→OpenAIRE crosswalk are not independent if discovery provenance is erased at the crosswalk step. Therefore backend family is bound to the *discovery* source, and identity resolution is recorded separately.
- A weak baseline could create a fake governance win. Therefore the primary baseline gets the exact same direct OpenAIRE and Crossref-derived candidate groups as ORION and uses a route-balanced round-robin cap rather than direct-first truncation.
- The duplicate released Wide question can inflate inferential N. Official output is retained as upstream computes it, but paired uncertainty is over distinct question strings using last-write semantics, yielding 399 inference units under the pinned release if the current split audit is unchanged.
- Crossref may return no DOI. A predeclared OpenAIRE widened-search fallback consumes the third logical request rather than giving ORION a cheaper task or silently minting an empty independent route.
- Provider retries can hide extra spend. Logical request budget and physical HTTP attempts are both recorded; all systems are projections of the same acquisition capture, so retries cannot advantage one system.
- Provider unavailability is not evidence of absence. Transport failures remain open obligations; a campaign with excessive unresolved transport cannot promote.

## Frozen acquisition capture

For every nonempty public Wide row, issue exactly three logical provider requests:

1. **OpenAIRE direct** — V3 research-product `search`, publication type, top four public-question salient terms, page size 20.
2. **Crossref discovery** — Works `query.bibliographic`, the same top-four public terms, rows 20; extract DOI values only.
3. **Identity/candidate completion** — if Crossref produced DOI values, one OpenAIRE V3 `pid` OR query crosswalks the top 20 distinct DOI values to research products and admits only explicit `scheme=arxiv` PIDs. If no DOI exists, use one predeclared OpenAIRE widened search with the top two public terms.

No gold or answer title enters any acquisition request.

## Frozen systems over the same capture

### Primary strong baseline — `wide_dual_backend_balanced`

- direct OpenAIRE structured arXiv IDs and Crossref-discovered/crosswalked arXiv IDs are two candidate groups;
- fallback OpenAIRE IDs are a same-backend second group only when the Crossref group is empty;
- select candidates by deterministic round-robin across groups, deduplicated by normalized arXiv identity;
- max 20 candidates;
- no provenance agreement preference.

### ORION — `wide_dual_backend_governed`

Uses the **same capture** and the same 20-candidate cap. Selection differs only by scientific provenance:

1. IDs independently discovered by both backend families (`OPENAIRE` and `CROSSREF`) first;
2. remaining IDs by the same deterministic route-balanced round robin;
3. same-backend repeat discovery never counts as independent confirmation;
4. unavailable calls remain typed open obligations and cannot produce a completeness claim.

### Secondary diagnostic — `wide_dual_backend_direct_first`

Direct OpenAIRE order followed by Crossref-crosswalk order, deduplicated and capped at 20. This is not the primary baseline; it quantifies how much ordinary first-route truncation matters.

## Frozen budget / transport

- logical requests per nonempty task: 3;
- OpenAIRE page size: 20 direct/fallback, up to 100 crosswalk results;
- Crossref rows: 20;
- returned candidate cap: 20 for every system;
- transport retries: at most 1 retry on 429/503/transport error, with physical attempts recorded;
- OpenAIRE minimum interval: 1.25 s between physical requests;
- Crossref minimum interval: 1.0 s;
- timeout: 30 s;
- raw response bytes + SHA-256 retained for every call.

## Frozen evaluation/statistics

Primary endpoint: pinned official AutoResearchBench Wide `avg_iou` with `--no-jina` and evaluator-only GT file.

Secondary: official `avg_recall`, `avg_precision`, zero/nonzero-IoU task rate, provider/open-obligation rates, physical attempts, candidate-set size.

Paired inference:

- unit = distinct nonempty question string under pinned official last-write GT semantics;
- duplicate released rows are one inferential unit;
- paired difference = ORION task IoU minus primary baseline task IoU;
- 10,000 paired bootstrap resamples;
- seed = 20260818;
- two-sided percentile 95% CI;
- report paired mean/median and win/tie/loss counts;
- official aggregate is retained separately even if its row weighting differs.

## Frozen terminals

`P2_WIDE_EXTERNAL_SUPPORTED` iff all hold:

1. official ORION `avg_iou - baseline avg_iou >= 0.03`;
2. paired 95% CI lower bound for distinct-question IoU difference is `> 0`;
3. ORION official avg recall is not lower than baseline;
4. at least 90% of planned logical provider calls across the capture return parseable HTTP 200 responses;
5. candidate and evaluator custody checks pass; no hidden field reaches acquisition;
6. every system projection uses the same captured evidence and max-20 candidate cap.

Otherwise:

- `P2_WIDE_EXTERNAL_NOT_SUPPORTED` if evidence is valid but the effect rule fails;
- `P2_WIDE_EXTERNAL_CANNOT_CHECK` if transport/custody/evaluator validity fails.

No outcome may cause these thresholds, queries, budgets, selection rules or inferential units to be changed for the same confirmation run.

## Reopen triggers

- official scorer or released dataset identity changes;
- OpenAIRE/Crossref API semantics materially change;
- crosswalk is found to infer arXiv identity from text rather than explicit PID objects;
- candidate and gold custody overlap before candidate output freeze;
- a stronger runnable matched baseline using the same keyless identity boundary becomes available before final confirmation;
- provider failure exceeds the frozen validity threshold.

## Authority boundary

A positive terminal supports an external **acquisition/governance** claim. It does not erase the synthetic/control status of the separate stopping-safety evidence and does not imply universal open-web superiority. A negative valid result remains part of the full-width P2 programme; it is not silently converted into a narrower success claim.

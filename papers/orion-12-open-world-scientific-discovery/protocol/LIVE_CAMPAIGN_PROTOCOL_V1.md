# Live-Provider Campaign Protocol V1

Status: `DESIGN_FROZEN`. Execution requires the preconditions in §9 and an explicit
`EXECUTION_FROZEN` decision by the paper owner. No campaign has been run.

**Index** — §1 standing · §2 routes · §3 freeze identities · §4 budgets · §5 unavailable ≠ absent ·
§6 retention · §7 contamination · §8 valid/invalid metrics · §9 preconditions · §10 verified endpoint status

## 1. Standing

The live campaign is the open-world half of ORION-12: it measures behaviour against real
indices, while the frozen offline complete-gold world measures mechanism against a
known denominator. Neither substitutes for the other. Live results are reported
alongside, never in place of, the offline table, and provider mutability is reported
separately from algorithmic performance (`PROTOCOL_V1.json` `resource_policy`).
Implementation: `src/orion/study/p2/{live_campaign,live_trace,live_metrics}.py`.

## 2. Route definitions

Three families. Independence is *earned* from the three coordinates `assess_pair`
judges, never asserted by labelling.

| route_id | route_kind | backend | query derivation |
|---|---|---|---|
| `arxiv-topic` | `CURRENT_VOCABULARY` | arxiv | frozen-question-terms |
| `openalex-keyword` | `PARENT_DISCIPLINE` | openalex | discipline-keyword-mapping |
| `openalex-citation` | `CITATION_NEIGHBORHOOD` | openalex | reference-graph-from-confirmed-seeds |

Consequences, reported not hidden: `arxiv-topic × openalex-*` earn `INDEPENDENT`;
`openalex-keyword × openalex-citation` is refused as `SHARED_BACKEND` — two query
styles over one index are one capture occasion however different they look. Citation
chaining derives its queries from works confirmed by earlier routes (`cites:` filters
over seed ids), making its derivation genuinely rather than nominally different.

**Overlap key.** `RouteCapture.captured` holds a digest of the *alias-closure-resolved
work*, not of the retrieved text — a deliberate refinement of the single-backend
intuition in `formalism.tex` §"content digests", forced by evidence: arXiv serves an
author abstract and OpenAlex one reconstructed from an inverted index, so one paper
legitimately has two rendition digests. Keying overlap on the rendition would make
every cross-backend re-encounter look like a distinct work and collapse measured
overlap to zero. Rendition digests are still computed and still key the
four-coordinate read state, where a changed rendition is a legitimate reread.
Records with no resolvable identifier fall back to a normalized-text digest so they
still enter the union rather than being dropped.

## 3. Freeze identities

Recorded in the campaign manifest (`build_campaign_manifest`), shaped to
`RUN_MANIFEST_SCHEMA_V1.json` and hashed over its own canonical JSON: provider
endpoints · provider API version strings · client user-agent · rate policy · frozen
research questions (id, text, frame, extraction schema version) · route definitions ·
per-route attempt and monetary budgets · seeds · subject git revision (full 40-char
sha; short shas are refused) · `protocol_digest` = sha256 over `PROTOCOL_V1.json`
**bytes** · start/end UTC timestamps · artifact root ·
`created_before_outcome_access` · contamination note · `manifest_content_sha256`.

## 4. Budgets and politeness

- Request spacing comes from the repository's verified `PROVIDER_BUDGETS` via
  `RateGate`; arXiv is one request per three seconds, single connection.
- A provider client constructed without the campaign's `RateGate` is **refused**:
  only the client records that a request happened, so an ungated client leaves the
  gate permanently at zero and bursts the API while appearing compliant.
- Monetary budget is tracked separately from spacing. OpenAlex meters dollars per
  call against a daily per-IP allowance; exhausting money is its own outcome
  (`COST_BUDGET_EXHAUSTED`), never a silent stall.
- Never parallelise requests to one host; never scrape HTML where an API exists.
- Credentials never reach retained evidence: `redact_url` strips `api_key` and
  friends before any URL touches disk.

## 5. Unavailable is not absent

Typed outcomes (`LiveOutcome`). `is_evidence_of_absence` is `False` for every member,
and that is asserted in the test suite.

| observed the index | leaves an open obligation |
|---|---|
| `RESULTS`, `EMPTY` | `CREDENTIAL_REQUIRED`, `RATE_LIMIT_DEFERRED`, `RATE_GATE_DEFERRED`, `COST_BUDGET_EXHAUSTED`, `NO_DERIVABLE_QUERY`, `PROVIDER_ERROR`, `TRANSPORT_ERROR`, `TIMEOUT`, `MALFORMED_RESPONSE`, `REFUSED_UNSAFE_PAGING` |

`EMPTY` means *this query, against this index, at this moment, matched nothing* — a
statement about the query and the index, never about the world. Everything in the
right column means we never got to look; each yields `SUSPEND` with an open
obligation, not `STOP`. Backend exhaustion (a claim about the index) and transport
failure (a claim about the channel) stay distinct states. Task closure is a judgement
over the route ensemble, refused while any route holds an open obligation; no route
decision certifies task saturation (`certifies_task_saturation` is `False` for every
action, including `STOP`).

## 6. Evidence retention

Per campaign, under the artifact root: `requests.jsonl` (one JSON object per
exchange: redacted URL, UTC timestamp, route id, derivation, HTTP status, response
sha256 and size, elapsed seconds, response headers, transport error),
`responses/<sha256>.raw` (verbatim bodies), `campaign_manifest.json`. Transport
failures are recorded *before* they propagate — a failure missing from the trace
would read as a look never taken. Retention is unconditional.

## 7. Contamination policy

Declared per campaign, before the run, in the manifest. A live route can retrieve the
answer to a public benchmark item simply because the benchmark is on the web, and
that is not detectable afterwards.

- **Our own questions** are authored for this campaign and unpublished; they are not
  benchmark items, so there is no published answer for a search route to find, and
  search-time contamination is removed for this campaign.
- **Public-benchmark tasks** (AutoResearchBench, SAGE, MetaSyn) remain a live risk.
  Those cases record exposure, are reported separately, and do not silently support
  the headline claim (`PROTOCOL_V1.json` `search_contamination_policy`).

## 8. Valid and invalid metrics under an incomplete denominator

| Valid (denominator-free) | Invalid — refused in code |
|---|---|
| unique relevant contribution per route | paper recall / any recall |
| route overlap by content digest | false-negative count |
| marginal relevant gain per added route | completeness / coverage of the literature |
| earned-independence verdicts per pair | miss rate, sensitivity |
| coverage diagnostic (**diagnostic only**, refuses on dependent or non-overlapping routes) | screening recall |
| outcome census, open-obligation census | |
| read-state census (legitimate reread vs duplicate processing) | |
| route-stop census | |
| cost, latency, attempts, query count | |

The right column is not merely unmeasured — it is **undefined** here: a work we did
not retrieve is indistinguishable from a work that does not exist. Requesting any of
it raises `IncompleteDenominator` naming that reason. Report those from the offline
complete-gold world instead.

## 9. Preconditions for `EXECUTION_FROZEN`

1. Funded OpenAlex API credentials. **Two of the three route families cannot execute
   without them** (§10) — a blocking precondition, not a footnote.
2. Frozen research questions, with the §7 contamination declaration.
3. `subject_revision` bound to a full 40-character sha; budgets set per route;
   artifact root allocated with retention per §6.

## 10. Verified endpoint status (2026-08-16, one request each)

Transport capability check only; no scientific outcome, no ORION-vs-baseline number.

- **arXiv** — reachable. `HTTP 200`, Atom feed, real records, `opensearch:totalResults`
  present. No credential required. Published budget honoured (1 req / 3 s).
- **OpenAlex** — **not reachable without funded credentials from this address.**
  `HTTP 429` on the *first* keyless request, reporting $0 of a $0.1 daily per-IP
  allowance remaining against a $0.001 per-call cost, with `Retry-After: 22503`.
  The **mailto polite pool no longer exists** — OpenAlex has required an API key since
  February 2026 and ignores `mailto`. This confirms the OBSERVED note already recorded
  in `orion/knowledge/rate.py`. No retry was attempted: the reset is ~6.25 h away and
  a second call would only spend a budget shared with every other caller on this IP.
  Full record: `LIVE_ENDPOINT_CHECK_2026-08-16.md`.

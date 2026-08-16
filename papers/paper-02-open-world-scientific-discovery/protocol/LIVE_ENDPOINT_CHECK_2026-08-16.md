# Live endpoint capability check — 2026-08-16

A transport capability check, not a scientific result. Two requests total, one per
endpoint, run from the Mac mini development host with a descriptive User-Agent and
no credentials. Raw responses were retained outside the repository (session
scratchpad) and are not committed; the observed facts are recorded here.

| endpoint | result |
|---|---|
| `https://export.arxiv.org/api/query` | `HTTP 200`, Atom feed, 3008 bytes, real entry returned, `opensearch:totalResults` present. No credential required. |
| `https://api.openalex.org/works` | `HTTP 429` on the **first** keyless request. |

OpenAlex response body:

> `Insufficient budget. This request costs $0.001 but you only have $0 remaining.`
> `Resets at midnight UTC.`

Response headers included `Retry-After: 22503`, `X-RateLimit-Limit-USD: 0.1`,
`X-RateLimit-Remaining-USD: 0`, `X-RateLimit-Cost-Required-USD: 0.001`.

Conclusions:

- arXiv is usable for a live campaign as-is, under the published one-request-per-three-seconds budget.
- **The OpenAlex mailto "polite pool" no longer exists.** OpenAlex has required an API
  key since February 2026, ignores `mailto`, and meters requests in dollars against a
  daily per-IP allowance. This independently confirms the OBSERVED note already
  recorded in `src/orion/knowledge/rate.py`.
- Funded OpenAlex credentials are therefore a blocking precondition for the live
  campaign: two of its three route families run on that backend. See
  `LIVE_CAMPAIGN_PROTOCOL_V1.md` §9.
- No retry was attempted. The reset was ~6.25 hours away and a further call would
  only spend a budget shared with every other caller on this address.

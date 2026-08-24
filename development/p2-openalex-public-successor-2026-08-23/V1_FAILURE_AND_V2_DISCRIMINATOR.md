# V1 retained failure and V2 discriminator

## V1 observation

V1 is immutable in `RESULT_V1_RETAINED.json` and its retained candidate file.
Its original trace hash remains bound to a non-redistributed mode-`0600`
quarantine; the in-tree trace is a separately receipted hash-only redaction.
This rights-preserving archival transform changes no V1 scientific outcome.
V1 cannot answer the scientific question:

- 23/24 `Q0_RAW` calls returned HTTP 400. OpenAlex accepted the short derived
  queries but rejected the long raw search strings. The decrypted raw strings
  are not redistributed; only their SHA-256 provenance remains in-tree.
- All 49 HTTP-200 calls appeared to emit zero arXiv identities because the V1
  adapter read only `ids.arxiv`.  In the frozen response trace, 73 returned rows
  instead carry an arXiv identity through the standard DataCite DOI form
  `10.48550/arXiv.<id>`.

The zero score is therefore a transport-and-identity observation, not a
scientific null.  It remains `CANNOT_CHECK` and is not pooled with V2.

## V2 disjoint repair

V2 changes exactly the two failed interface assumptions before making another
provider call:

1. `Q0` becomes a transport-safe 180-character, word-boundary prefix of the
   public question.  The D1 and D2 queries are unchanged.
2. The identity adapter accepts either `ids.arxiv` or a DOI whose normalized
   value starts with `10.48550/arxiv.`.  This is an alias bridge, not a relevance
   label and not access to benchmark gold.

Task identities, task order, provider, three-call batch, selected fields,
candidate cap, RRF constant, statistics, gates, and forbidden claims are
unchanged.  V2 is a new successor identity and does not rewrite V1.

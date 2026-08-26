# Literature citation evidence — ORION Paper II

Raw fetched metadata for every key in `../../manuscript/bibliography.bib`.
One JSON per bibliography key. Regenerate with:

```bash
python3 fetch_literature_evidence.py
```

The script re-fetches from the arXiv API (`export.arxiv.org/api/query`),
Crossref (`api.crossref.org/works/<doi>`), or DataCite
(`api.datacite.org/dois/<doi>` for repository objects whose DOI is not in
Crossref), writes a fresh record per key with a new UTC timestamp, and never
writes a field from recall.

## Record schema

| field | meaning |
|---|---|
| `bib_key` | key in `bibliography.bib` |
| `claimed_title` | title asserted by the bibliography entry |
| `claim_provenance` | see below — determines whether `verdict` is an independent test |
| `fetch_url` | exact URL fetched |
| `fetched_utc` | UTC timestamp of that fetch |
| `verdict` | `VERIFIED` / `MISMATCH` / `CANNOT_CHECK` |
| `verdict_reason` | why that verdict was assigned |
| `fetched_*` | title, authors, year, venue as returned by the source |
| `doi`, `arxiv_id`, `volume`, `pages`, `article_number` | identifiers as returned |
| `abstract` | full abstract where the source supplies one (arXiv always; Crossref sometimes) |

## Verdict semantics

- `VERIFIED` — the claimed title matches the fetched title (exactly, or as a
  normalised substring where the source string carries an artifact).
- `MISMATCH` — the claimed title differs from the fetched title. The entry is
  wrong until corrected; the verdict records the state at fetch time and is
  **not** rewritten when the bibliography is fixed.
- `CANNOT_CHECK` — the fetch failed. This is a reportable outcome, never
  silently upgraded to `VERIFIED`.

## `claim_provenance` — why the counts must be read separately

- `pre_existing_independent_claim` — the title was already in the bibliography
  before this audit. The fetch is a genuine independent test, so `VERIFIED`
  here carries real information.
- `derived_from_this_fetch` — the entry was added by this audit and its fields
  were transcribed *from* the fetch. `VERIFIED` here is a provenance record,
  not an independent test, and must not be counted as corroboration.

Aggregating the two classes into one "N/N verified" figure would overstate the
evidence. The audit reports them separately.

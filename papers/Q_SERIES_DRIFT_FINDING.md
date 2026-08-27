# Q-series content drift became visible on 2026-08-25

Three drift-ratchet tests went red after
`papers/Q_SERIES_CONTENT_BINDING_V1.json` was deduplicated:

- `test_no_paper_drifts_that_was_not_already_drifting`
- `test_no_paper_drifts_further_than_it_already_did`
- `test_no_package_becomes_staler_than_it_already_was`

They name Q-paper-01 through Q-paper-04 as newly drifting. **They were not
newly drifting.** The drift was already there and the ratchet could not see
it.

## Why it was invisible

The binding file listed 58 entries for 46 distinct paths. The Q-series
checker rejects a duplicate outright:

```
raise ValueError(f"duplicate Q-series bound path: {path_value}")
```

So the file raised before any digest was compared. A binding that cannot be
parsed reports no drift — not because there is none, but because nothing
got as far as looking. The ratchet read that silence as clean.

## Evidence that it pre-existed

Measured at `50c60594`, the commit immediately **before** the deduplication:

```
entries=58 unique=46 duplicates=12
entries whose digest ALREADY did not match: 9
```

Nine mismatches at the parent commit. Removing duplicates changed which
entries survive; it did not change any file's bytes, and it could not have
introduced drift that was already recorded in the parent.

## What actually drifted

Six entries record a digest that does not match the file:

| File | recorded | actual |
|---|---|---|
| Q1 `INDEPENDENT_HUMAN_PROOF_SANITY_RESULTS_2026-08-22.json` | `d75e36ea6450` | `1e43cea15f96` |
| Q1 `MANUSCRIPT_SUBMISSION_DRAFT.md` | `7cb04501f168` | `91e8a096a3e7` |
| Q1 `CLAIM_LEDGER_V2.md` | `83ea3dc4e244` | `dcc7acadc313` |
| Q2 `MANUSCRIPT_V2.md` | `881403accbeb` | `240f24815d50` |
| Q3 `CLAIM_LEDGER_V2.md` | `f218f93bb8d4` | `48adef4f7949` |
| Q4 `MANUSCRIPT_V2.md` | `665a366d24a8` | `53f515f84934` |

Manuscripts and claim ledgers, all edited by merged work after the binding
was cut.

## What this lane did not do

The ratchet's own message says it plainly:

> Reconcile the paper — do not regenerate its digests to match the new
> bytes, and do not add it to the baseline.

Both shortcuts were available and both were declined. Regenerating the
digests would assert that whatever is on disk today is the bound content,
which is a claim about four papers rather than about JSON hygiene. Adding
the papers to the baseline would record drift as the permitted normal.

The red is correct. It is the first time this drift has been measurable, and
the ratchet is doing its job on its first honest reading of the file.

## What resolves it

An owner decides, per file, whether the current bytes are the intended
content — then re-binds, or restores. The table above is the whole work
list.

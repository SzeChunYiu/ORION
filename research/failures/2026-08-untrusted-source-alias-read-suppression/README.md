# Untrusted source alias suppresses a required read

## Observed

After `origin/main` `4d384aba8244f20854940717d260599f2cb1c94e`, a
probe recorded DOI `10.1000/a` and DOI `10.1000/b` with the same caller-supplied
URL alias. Only DOI A received a matching read receipt. Replay merged the two
identities and a query for DOI B returned:

```text
known_sources (SourceIdentity(source_id='doi:10.1000/a',
  aliases=('doi:10.1000/b', 'url:https://example.org/shared'), title=''),)
query_b ALREADY_READ
```

## Failure

Alias overlap is treated as established work equivalence even though aliases
are ordinary caller data. The derived equivalence then changes scheduling: a
receipt for one work can suppress reading a distinct work. This can hide
counterevidence and make coverage or saturation look stronger than it is.

Malformed `READ` rows are also silently skipped, which makes protected replay
indistinguishable from a complete history with no malformed records.

## Failure class

`CALLER_ALIAS_AS_EQUIVALENCE_AUTHORITY` + `COVERAGE_SUPPRESSION` +
`SILENT_REPLAY_OMISSION`.

## Correct response

- Preserve raw aliases and reads immediately in shadow history.
- Require content-bound host admission before alias equivalence affects
  deduplication or read scheduling.
- Bind an admitted read to work identity, rendition content, extraction schema,
  frame, and contribution digests.
- Treat malformed protected rows as typed `CANNOT_CHECK`/replay failure; never
  silently omit them.
- Bind the semantic knowledge/read projection or its exact revision into every
  transition whose selection or stopping decision depends on it.

## General lesson candidate

Deduplication is a behavior-changing inference, not harmless normalization.
An unverified equivalence edge can erase required work as effectively as an
incorrect answer can erase an open question.

## Residuals and reopen coordinates

- alias evidence and conflict resolution;
- retractions, split identities, and rendition-versus-work semantics;
- legacy `SOURCE`/`READ` quarantine and strict replay;
- coverage and saturation receipts already influenced by unadmitted aliases.

# ORION-25 publication-freeze addendum V1

**Freeze date:** 2026-08-31  
**Status:** `BOUNDED_SCIENTIFIC_RESULT_EARNED__FILING_GATE_OPEN__NOT_READY_TO_FILE`

This addendum is part of the frozen ORION-25 paper-content packet. It records the
state `closeout/bounded-v1/RESULT.json` already reports, and it deliberately does
**not** describe this paper as ready to file.

## Earned scientific ceiling

The recorded authority is `BOUNDED_SCIENTIFIC_RESULT_EARNED` with
`scientific_authority_delta: NONE` and `promotion_allowed: false`. Four measured
results stand inside the registered harness:

- **Artifact corruption is caught.** All 6 applied faults were detected, with a
  false-promotion rate of 0.0.
- **Benign re-encoding is not punished for it.** All 6 variants across 4
  byte-distinct forms were accepted, false-rejection rate 0.0. The pair matters
  jointly: detection that also rejected benign variants would be worthless.
- **Composition costs what it costs.** Attestation expands bytes by a factor of
  1.393 (9,650 against 6,926) and adds a median 1.34 ms, roughly 111.6 microseconds
  per link.
- **Trust-domain separation buys resistance in steps.** Under single-domain
  compromise the false-promotion rate is 1.0 at `d=1` and 0.0 at both `d=2` and
  `d=3` — verdict `RESISTANCE_STEPS_WITH_D_UNDER_SINGLE_DOMAIN_COMPROMISE`.

## Frozen boundary

**Two of this paper's findings are negative, and they are load-bearing.**

Chain length does not help. Detection is 1.0 at every tested `k` of 1, 2 and 3 with
trust domains fixed at one — verdict `DETECTION_FLAT_IN_K`. Lengthening the chain is
not a lever, and no reader should infer that it is.

More sharply: **a valid artifact does not attest that its run is live.** Across 4
host-process faults, 2 stale-but-valid artifacts were accepted while 2 write-path
failures failed loudly — verdict
`ARTIFACT_VALIDITY_DOES_NOT_ATTEST_CURRENT_RUN_LIVENESS`. That is a limit on what
receipt-checking can mean, established inside the harness rather than conceded
about it.

The trust-domain threshold law remains `HYPOTHESIS_ONLY` — no evidence, no
authority. It becomes evidence only by executing its protocol, and it must not be
cited as a result before then.

## Filing gate: open, and this freeze does not close it

The paper-level disposition is `CANNOT_CHECK`, for the reason the closeout states:
the bounded source is complete, but a fresh final PDF render, a page-level visual
audit, archive binding and filing have not been verified. All four `filing_gate`
flags are `false`:

| gate | state |
|---|---|
| `fresh_pdf_rendered_from_recovered_source` | false |
| `page_level_visual_audit_complete` | false |
| `archive_and_license_binding_complete` | false |
| `human_filing_metadata_complete` | false |

So this is a freeze of *earned science*, not a declaration of submission readiness.
Those four are mechanical steps a filer performs; none is a scientific gap, and none
may be assumed complete because the science is closed.

## Frozen content surface

The content packet consists of the closeout at `closeout/bounded-v1/` — `QUESTION.md`,
`RESULT.json`, `CLAIM_DISPOSITION.md`, `EXPECTED_TERMINALS.json`,
`RESOURCE_ACCOUNTING.json`, `ADVERSE_AND_CANNOT_CHECK.jsonl`, `SOURCE_BINDING.json`
and its `SHA256SUMS` — together with the `execution-integrity-v1` and
`external-trust-domain-v1` experiment lanes that carry the protocol, corpus
manifest, inclusion/exclusion record and baselines, the manuscript, and this
addendum. ORION-25 is the harness paper: it claims fail-closed research execution
with receipt semantics and independence contracts, and it does not own the results
of the papers executed through it.

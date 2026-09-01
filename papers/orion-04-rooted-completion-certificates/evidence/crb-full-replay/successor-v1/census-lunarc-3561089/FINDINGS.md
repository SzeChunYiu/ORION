# CR-B full census, LUNARC job 3561089 — findings

**Terminal (from the receipt): `NQ_CR_B_FULL_CENSUS_GENERATED_INDEPENDENTLY`.**
**Scientific authority delta: `NONE`**, asserted by the receipt itself.
**What this clears: the serialization failure. What it does not clear: D2/D3 authority.**

## The prior failure, and its repair

The predecessor run is recorded as
`NQ_CRB_FULL_REPLAY_JOB_3544056_FAILED_CENSUS_RECEIPT_SERIALIZATION__D2_D3_AUTHORITY_CANNOT_CHECK`.
It did not fail on the mathematics. It failed on writing its own receipt: the census
emitted `d2_wall_seconds` and `d3_wall_seconds` as floats through a canonical-JSON writer
configured with `allow_nan=False`, so the receipt could not be serialised and the D2/D3
authority it was meant to carry became `CANNOT_CHECK` by default rather than by
measurement.

The successor engine replaced those with a helper returning canonical integer
milliseconds. This run confirms the repair against real data:

```
d2_wall_milliseconds: 28114909
d3_wall_milliseconds:   944264
```

Integers, serialised, in a receipt that exists. That is the specific defect closed.

## What the run produced

Job 3561089 on `cn128`, 48 threads, `lu48`, **`COMPLETED` with exit `0:0`** after
08:05:48 of a 12-hour limit. 499 MB of output across two scopes.

| scope | records | expected | match | stream bytes | stream sha256 |
|---|---|---|---|---|---|
| `NQ_D2_NORMALIZED_LENGTH_19` | 98,622 | 98,622 | yes | 66,441,182 | `c8b1e020…` |
| `NQ_D3_STRUCTURED_LENGTH_25` | 230,983 | 230,983 | yes | 159,449,413 | `71ec6f13…` |

`counts_match_frozen_denominators: true`. Search effort was substantial and is recorded:
16,650,563,308 D2 nodes, 506,686,292 D2 states, 446,887,273 line-bound prunes across
147,620 tasks.

Only the receipts and scope manifests are committed here. The 499 MB of record streams
are not, and the manifests' `stream_sha256` is what binds them; a later replay is
compared against those digests rather than against a copy in the tree.

## What is still `CANNOT_CHECK`, stated from the receipt's own fields

The receipt does not claim authority, and this document does not upgrade it:

```
normalization_completeness:   CANNOT_CHECK
predicate_execution:          NOT_RUN
orbit_completeness:           NOT_CLAIMED
engine_a_agreement:           NOT_CHECKED
engine_a_inputs_consumed:     false
engine_a_imports:             0
external_drup_verification:   NOT_RUN
scientific_authority_delta:   NONE
```

So the honest reading is narrow and worth stating plainly: **the census now
materialises and its receipt serialises, but D2/D3 authority remains unestablished.**
The predecessor's `CANNOT_CHECK` had two causes — a broken receipt and unrun checks —
and only the first is repaired. Predicate execution, Engine-A agreement and external
DRUP verification are separate steps that were not run here, and no combination of the
numbers above substitutes for them.

`engine_a_imports: 0` with `engine_a_inputs_consumed: false` is the independence
property the terminal names: this census was generated without consuming Engine-A
output, which is what makes it an independent generation rather than a re-derivation.

## Two defects in the receipt itself

**The subject commit is not reachable from `main`.** The scope manifests pin
`subject_commit 0c451e862a0eeddac7c673813c4dc499f134b088`. That commit exists, but
`git merge-base --is-ancestor` against `origin/main` fails; it lives on
`codex/orion-04-crb-replay-exec-20260827` and other branches. This is the archive-pin
class that `tests/unit/programme/test_content_binding_pin_is_reachable.py` exists to
catch. Nothing here is bound to that commit, so nothing degrades — but a later step that
binds these manifests must re-pin to a commit on `main` first, exactly as #1989 did.

**`lunarc_execution` reads `LOCAL_NOT_SUBMITTED`, which is false for this run.** The
census ran as SLURM job 3561089 on `cn128` under account `lu2026-2-51`. The field appears
to describe whether the generator submitted a sub-job rather than whether it was itself
scheduled, but as written it misdescribes the execution environment of its own receipt.
Recorded here rather than corrected in place, since the receipt is the artifact the run
produced.

## Provenance

Generator `crb_census.py`, a reach-board enumerator over `C_5^3`, run with
`--scope both --threads 48 --max-wall-seconds 39600`.
`coverage_argument_sha256: 3a0efeab…`, `matrix_manifest_sha256: 3c95c26a…`,
`generation_receipt_sha256: 03e56e34…`.

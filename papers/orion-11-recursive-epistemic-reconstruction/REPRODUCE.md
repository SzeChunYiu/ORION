# ORION-11 — reproducing the headline results

Scope: how to verify the archived ORION-11 v2.2.4 primary and disjoint
replication, the R4 faithful-comparator falsification, and the historical V1
negative.

**Current state:** the archived credential-free mechanical successor retains
`P1_MUTATION_NECESSITY_SUPPORTED` in both registered runs, with independent
verification `PASS`. R4 withdraws its comparative mechanism-necessity reading:
Active-VOI with ordered candidate search matches the governed policy on the
primary joint criterion. The R4 replication remains `CANNOT_CHECK`. The historical
66-case V1 broad H1 remains `NOT_SUPPORTED`: the subject and strongest
registered baseline each achieve 1/48 root successes, for a difference of zero.
It is not pooled with the successor. Current bytes are reproducible, but three
cited historical provenance commits are unreachable, so the claimed original
prospective order remains `CANNOT_CHECK`.

## Powered v2.2.4 successor

Verify every archived byte and the two independent-verification terminals:

```bash
(cd research/revival/p1/confirmatory/v2.2/primary && sha256sum -c SHA256SUMS)
(cd research/revival/p1/confirmatory/v2.2/replication && sha256sum -c SHA256SUMS)
jq -e '.verdict == "PASS" and .score_mismatch_count == 0 and .analysis_mismatch_count == 0' \
  research/revival/p1/confirmatory/v2.2/primary/INDEPENDENT_VERIFICATION.json
jq -e '.verdict == "PASS" and .score_mismatch_count == 0 and .analysis_mismatch_count == 0' \
  research/revival/p1/confirmatory/v2.2/replication/INDEPENDENT_VERIFICATION.json
jq -e '.required_concordance | all(.[]; . == true)' \
  research/revival/p1/confirmatory/v2.2/PRIMARY_REPLICATION_CONCORDANCE.json
```

Regenerate and byte-check the publication figure directly from the two result
JSON files:

```bash
MPLCONFIGDIR=/tmp/orion-matplotlib uv run python \
  papers/orion-11-recursive-epistemic-reconstruction/scripts/make_necessity_figure.py --check
```

To re-run the independent primary verification from compressed archives, first
restore the three immutable line-oriented inputs into a temporary directory:

```bash
work=$(mktemp -d /tmp/orion-p1-primary.XXXXXX)
gzip -dc research/revival/p1/confirmatory/v2.2/primary/WORLD_PUBLIC.jsonl.gz > "$work/WORLD_PUBLIC.jsonl"
gzip -dc research/revival/p1/confirmatory/v2.2/primary/PROTECTED_RESPONSE_MATRIX.jsonl.gz > "$work/PROTECTED_RESPONSE_MATRIX.jsonl"
gzip -dc research/revival/p1/confirmatory/v2.2/primary/RAW_RESULTS.jsonl.gz > "$work/RAW_RESULTS.jsonl"
uv run python research/revival/p1/verify_mutation_necessity_independent.py \
  --world-public "$work/WORLD_PUBLIC.jsonl" \
  --protected "$work/PROTECTED_RESPONSE_MATRIX.jsonl" \
  --raw-results "$work/RAW_RESULTS.jsonl" \
  --execution-freeze research/revival/p1/confirmatory/v2.2/PRIMARY_EXECUTION_FREEZE_V3.json \
  --result research/revival/p1/confirmatory/v2.2/primary/PRIMARY_RESULT.json \
  --out "$work/INDEPENDENT_VERIFICATION.json"
cmp "$work/INDEPENDENT_VERIFICATION.json" \
  research/revival/p1/confirmatory/v2.2/primary/INDEPENDENT_VERIFICATION.json
```

The replication uses the analogous files under `replication/` and its
`REPLICATION_EXECUTION_FREEZE.json`. Each run contains 2,882 worlds and 40,348
arm/world result rows. On the current CPU environment the deterministic campaign
and independent verification each take roughly one minute; no network or model
credential is used.

## Clean-source LUNARC replay receipt

LUNARC job 3550083 replayed both campaigns from a Git archive of exact source
commit `58192a3a05c4fc8e55b45e0082cbd1de2792c250`. The job ran on `cn063`,
completed with exit `0:0` in `00:03:45`, and preserved its Python and dependency
deviations rather than normalizing them away. For both the primary and
replication, `RAW_RESULTS.jsonl`, the result record, and the
independent-verification record were byte-identical to the archived objects.
Both scientific terminals remained `P1_MUTATION_NECESSITY_SUPPORTED`, with zero
score and analysis mismatches.

The repository retains compact receipts rather than the reconstructed
world/result directories:

- `papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/lunarc-replay-v1/LUNARC_REPLAY_RECEIPT_V1.json`
  (SHA-256 `f049d2c19c508940188f806315d9b467ccb3139da0ecb2b22e96d17921161acc`);
- `papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/lunarc-replay-v1/LUNARC_REPLAY_JOB_OUTPUT_V1.json`
  (SHA-256 `5cd24e6e9a64a9f6b8c4d8c9e89cd9be25cf330352b28b0859b614f40ff28087`);
- `papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/lunarc-replay-v1/LUNARC_REPLAY_EXECUTION_BINDING_V1.json`
  (SHA-256 `0ccac10a5db611534679b6d3117b7cdacff8cbcbac2f6b15344b9cd68a2204b5`).

Verify the compact receipts without rerunning the cluster job:

```bash
base=papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/lunarc-replay-v1
printf '%s  %s\n' \
  f049d2c19c508940188f806315d9b467ccb3139da0ecb2b22e96d17921161acc \
  "$base/LUNARC_REPLAY_RECEIPT_V1.json" | sha256sum -c -
printf '%s  %s\n' \
  5cd24e6e9a64a9f6b8c4d8c9e89cd9be25cf330352b28b0859b614f40ff28087 \
  "$base/LUNARC_REPLAY_JOB_OUTPUT_V1.json" | sha256sum -c -
jq -e '
  .slurm.job_id == "3550083" and
  .slurm.state == "COMPLETED" and
  .slurm.exit_code == "0:0" and
  (.lane_summaries | length == 2) and
  all(.lane_summaries[];
    .terminal == "EXACT_ARCHIVE_REPLAY" and
    .scientific_terminal == "P1_MUTATION_NECESSITY_SUPPORTED" and
    .score_mismatch_count == 0 and
    .analysis_mismatch_count == 0 and
    all(.comparisons[]; .byte_equal == true)) and
  .discrepancies == []
' "$base/LUNARC_REPLAY_RECEIPT_V1.json"
```

This receipt establishes deterministic replay from current committed source.
It does not establish the original commit order, external scorer custody,
independent review, submission readiness, or paper-freeze authority.

## R4 faithful-comparator falsification

Verify the immutable R4 packet and the authority disposition:

```bash
base=papers/orion-11-recursive-epistemic-reconstruction/experiments/r4-faithful-comparator-v1
(cd "$base" && sha256sum -c SHA256SUMS)
jq -e '
  .verdict == "H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION" and
  .anchor_reproduction_gate.passed == true and
  .falsified_by == ["activevoi_search_admitted_parent"]
' "$base/result/primary/ORION11_R4_FAITHFUL_COMPARATOR_RESULT.json"
jq -e '
  .verdict == "INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ" and
  .anchor_reproduction_gate.passed == false
' "$base/result/replication/ORION11_R4_FAITHFUL_COMPARATOR_RESULT.json"
jq -e '
  .scientific_authority_delta ==
    "WITHDRAW_COMPARATIVE_NECESSITY_READING__PRESERVE_INTERNAL_TERMINAL"
' "$base/AUTHORITY_DISPOSITION_V1.json"
```

The primary comparison contains 480/480 joint successes for both the governed
policy and the ordered-search Active-VOI comparator, zero forbidden mutations,
and zero discordant pairs. Mean intervention cost is 1.834 versus 2.668 units.
The packet therefore supports bounded descriptive economy only. It does not
support comparative mechanism necessity, component attribution, external
independence, or a claim from the failed replication gate.

## Public rights/relation census (outcome-blind development evidence)

The frozen packet is
`development/p1-rw-rights-relation-census-v2-2026-08-23/`. Verify its
24-entry manifest in that directory with `sha256sum -c SHA256SUMS`. The raw
Retraction Watch transport is deliberately not retained. To replay only its
seven-field structural census without touching the packet, copy the directory
to scratch, download the exact commit below, and run the standard-library
reducer there:

```bash
audit=/tmp/p1-rw-rights-relation-census-v2
rm -rf "$audit"
cp -R development/p1-rw-rights-relation-census-v2-2026-08-23 "$audit"
mkdir -p "$audit/.runtime"
curl -L --fail \
  -o "$audit/.runtime/retraction_watch.csv" \
  https://gitlab.com/crossref/retraction-watch-data/-/raw/7bb2ced143b764974c53c6c61abfdd2379f5307d/retraction_watch.csv
cd "$audit"
python3 run_rw_relation_census_v2.py
python3 validate_v2.py
```

The pinned file must have SHA-256
`ceaab201d728dfcf9929ec1e229acd2ad88c650c847ec922ba9ffe831e366abb`,
65,984,968 bytes, and 71,944 data rows. The deterministic relation result is
49,878 admitted relations in 42,924 connected families; the Europe PMC
rights/stratum aggregates are receipt-bound in the packet and should not be
silently refreshed under the same identity.

## Structured-action semantics census (outcome-blind development evidence)

The frozen V3 packet is
`development/p1-structured-action-semantics-v3-2026-08-23/`. Its checksum
manifest can be verified without querying a provider or opening any case or
outcome:

```bash
cd development/p1-structured-action-semantics-v3-2026-08-23
sha256sum -c SHA256SUMS
python3 -m json.tool RESULT_V3.json >/dev/null
python3 -m json.tool OWNER_FIELD_FEASIBILITY_V3.json >/dev/null
```

The immutable packet reproduces the V2 pool counts (12,038 exact-rights
relations in 11,602 families), classifies 11,976 of 11,991 unique notices into
exactly one of three provider-native strata, and records normalized
relation-type agreement for 11,988 notices. It also records the decisive
boundary: 0/12 owner-algebra requirement groups are sufficient. Do not rerun
`collect_v3.py` under the same identity: it performs live provider queries, and
a refresh would require a new protocol/result version. `validate_v3.py` writes
a fresh validation timestamp, so run it only on a scratch copy if a regenerated
receipt is required; the checked-in `SHA256SUMS` verifies the frozen packet.

## Public-standard owner-algebra feasibility (outcome-blind)

The frozen V4 packet is
`development/p1-owner-algebra-construct-validity-v4-2026-08-23/`. Verify its
18-file manifest and native 85-assertion scientific validator without network,
pytest, repository CI, case text, or outcomes:

```bash
(cd development/p1-owner-algebra-construct-validity-v4-2026-08-23 && \
  sha256sum -c SHA256SUMS)
python3 development/p1-owner-algebra-construct-validity-v4-2026-08-23/verify_v4.py
```

The packet binds eight HTTP-200 documents from four institutional families and
retains one frozen HTTP-404 route without substitution. It records 9/12
structural analogues, 0/12 named-custodian/delegation groups, 0/12 sufficient
groups, and zero scientific-action gold. Do not rerun `capture_sources_v4.py`
under the frozen identity: mutable web bytes require a new capture identity.
Do not use `--write-receipt` for ordinary verification because the checked-in
receipt and manifest are already content-bound. Invoke the validator from the
repository root because its frozen predecessor paths are repository-relative.

## Source-native-to-R7 adapter audit (bounded development evidence)

The current audit is re-executable from repository-held sources. Run it into a
temporary output so the tracked receipt remains immutable:

```bash
out=$(mktemp /tmp/orion11-negative-revival-audit.XXXXXX.json)
python3 \
  papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/verify_orion11_negative_revival_v1.py \
  --repo-root . \
  --out "$out"
jq -e '
  .audit_passed == true and
  .historical_broad_h1.terminal == "NOT_SUPPORTED" and
  .historical_broad_h1.subject_root_success == "1/48" and
  .historical_broad_h1.baseline_root_success == "1/48" and
  .historical_broad_h1.difference == 0 and
  .adapter_maps.enumeration == {
    "fully_certified": 0,
    "known_rejected": 116929,
    "not_disproved_but_uncertified": 720,
    "total": 117649
  } and
  .adapter_maps.registry_exact_match == true and
  .adapter_maps.in_repo_reauditable == 720 and
  .adapter_maps.in_repo_resolvable == 0 and
  .rse_donor_subtraction.terminal == "GENERIC_JUSTIFICATION_DONOR_SUFFICIENT" and
  .freeze_authority == "NONE__DO_NOT_FREEZE_OR_MERGE"
' "$out"
```

The tracked receipt is
`papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/AUDIT_RECEIPT.json`
with SHA-256
`e03f3c5b545aa82586539f1d794197bef3674250f42eea5868d8f1c79adbc4ab`.
All 117,649 maps are enumerable: 116,929 are rejected, 720 are not disproved
but uncertified, and zero are fully certified. The complete survivor registry
matches the enumeration, so all 720 are re-auditable in-repository. None is
resolvable there. Each requires external owner or delegate semantics, target
rights, host authority, a signed algebra, authorized delivery, and independent
semantic review. V13 remains at 0/7 signed external outputs and 0/4 closed
authority acts.

The historical 47-entry external handoff and its separate checksum receipt are
not required to rerun this current enumeration. They remain unavailable in a
clean checkout and therefore cannot provide current independent custody. Zero
certified maps must not be restated as zero possible maps. This is an external
authority `CANNOT_CHECK`, not a setup failure or an impossibility result.

## Historical V1 command

## Command

```bash
make paper01-results
```

which is exactly:

```bash
PYTHONPATH=src python3 -m orion.study.p1.tables \
  --archive papers/orion-11-recursive-epistemic-reconstruction/results/raw/test_scored.jsonl \
  --out    papers/orion-11-recursive-epistemic-reconstruction/results \
  --expected-repeats 5 \
  --bootstrap-seed 20260815 \
  --resamples 10000
```

Overridable as make variables: `P1_ARCHIVE`, `P1_OUT`, `P1_REPEATS`,
`P1_BOOTSTRAP_SEED`, `P1_RESAMPLES`, `P1_MIN_UNITS`.

### Outputs

| File | Contents |
|---|---|
| `results/P1-T2_baseline_ablation_results.json` / `.md` | system × family: rate with Wilson 95% CI, paired difference against the strongest matched baseline with bootstrap CI, effect size, hypothesis verdict, Holm-corrected secondary family |
| `results/P1-T3_failure_taxonomy.json` / `.md` | failure modes by frequency with representative **blinded** case ids |

`P1-T1_nearest_work_matrix` is the nearest-work mechanism matrix and is not
produced by this pipeline.

JSON and markdown only. There is no plotting code in `orion.study.p1` and none
should be added — the machine-readable numbers are the artifact.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | tables regenerated from archived records |
| `2` | the archive exists but is malformed; a record was **refused**, never silently skipped |
| `3` | `CANNOT_CHECK` — no archive, an empty archive, or an archive that cannot bind its own numbers |

`3` is deliberately distinct from both success and error: "could not check" is
never reported as "checked and fine". Note that GNU `make` collapses any recipe
failure to its own exit `2`; call the module directly if a caller needs to read
the `3`.

An archive is refused as `CANNOT_CHECK` when it:

- is absent or empty;
- carries no `suite_fingerprint` (nothing binds the results to a frozen suite);
- spans more than one suite fingerprint or subject revision (a pooled number
  would describe neither);
- contains any `(system, case)` group whose repeat count differs from the frozen
  `stochastic_repeats: 5` (systems would be compared at different effort).

## Inputs

| Input | Where it is bound | Current value |
|---|---|---|
| Protocol | `protocol/PROTOCOL_V1.json` (`protocol_status: DESIGN_FROZEN`) | `ORION-11.hidden-formulation.v1` |
| Suite fingerprint | `orion.study.p1.cases.suite_fingerprint()`, written into each raw record and into `execution_bindings.dataset_revisions.hidden_shift_suite` | **UNBOUND** |
| Subject revision | `execution_bindings.subject_revision`, written into each raw record | **UNBOUND** |
| Model/provider revisions | `execution_bindings.model_provider_revisions` | **UNBOUND** |
| Baseline config hashes | `execution_bindings.baseline_config_hashes` | **UNBOUND** |
| Stochastic repeats | `statistics.stochastic_repeats` | 5 per (system, case) |
| Bootstrap seed / resamples | this command | 20260815 / 10000 |

Every `execution_bindings` field is currently `UNBOUND`. A result reported
against an unbound suite is unverifiable, which is why the table generator
refuses an archive with no fingerprint.

## Raw record schema

The archive is a file or directory of `.jsonl` / `.json` raw records, schema
`orion.p1.case-record.v1`, one record per `(system, case, seed)`. Records are
produced by `orion.study.p1.metrics.case_score_to_record` and consumed by
`case_score_from_record`; `tables.py` reads records and nothing else — it never
imports a case, reads a protected gold label, or executes a system.

`metrics.py` is the only module in the package permitted to read
`HiddenShiftCase.protected_gold`. That is what makes the protocol's
`hidden_labels` access policy checkable rather than merely asserted.

## Statistics as frozen

Fixed by the protocol's `statistics` block and implemented in
`orion/study/p1/statistics.py` (stdlib only — no numpy/scipy):

- **Wilson 95%** score intervals for standalone binary rates;
- **paired percentile bootstrap**, 10000 resamples, for matched differences,
  with the interval at sorted indices 250 and 9749;
- **unit of analysis is the frozen case.** The 5 stochastic repeats are reduced
  to one observation per case *before* any interval is taken, so `n` is the case
  count and is never inflated by the repeat factor. Each rate records the
  reduction it used: `MAJORITY` for performance metrics, `ANY` for violations,
  `ALL` for trace fidelity, `MODE_SEVERITY` (worst-outcome tie-break) for the
  categorical control outcome;
- **Holm** correction across the inferential secondary family; the single
  primary hypothesis H1 is uncorrected;
- **practical margins:** H1 superiority ≥ **+0.05** absolute root success against
  the strongest matched baseline; H2 non-inferiority within **+0.02** absolute
  unnecessary-reframe rate. An interval that merely *includes* the margin is
  never reported as `SUPPORTED`.

Bootstrap p-values are floored at `1/resamples` and printed as `<1e-4`; nothing
smaller is resolvable at 10000 resamples and the table does not invent
precision.

**Known cost of the frozen unit.** Majority reduction over 5 repeats is lossy:
two systems succeeding on 90% and 80% of repeats both reduce to a solved case,
and the reported case-level difference is then 0.00. Every difference therefore
carries a `seed_mean_difference` diagnostic — the same matched cases resampled
on per-case seed means, so the discarded within-case resolution stays visible.
On the full-scale synthetic archive above, a difference the frozen reduction
reports as `0.00 [0.00, 0.00]` shows as `+0.10 [0.05, 0.15]` on seed means. The
hypothesis verdict reads the frozen `difference`, never the diagnostic.

## Expected runtime

Measured on an Apple-silicon laptop, CPython 3.11, no parallelism:

| Stage | Cost |
|---|---|
| `make paper01-results` on an empty archive | < 1 s, exit 3 |
| `make paper01-results` on a full-scale archive (11 systems × 60 cases × 5 seeds = 3300 records, 99 table rows, ~10<sup>2</sup> paired bootstraps at 10000 resamples) | ~2 s |
| `make paper01-tests` | ~5 s |
| The study run that *produces* the archive | not performed by this pipeline; see below |

Table generation is pure arithmetic over records on disk. It makes no network
call, needs no credential, and is deterministic given the archive and the
bootstrap seed — regenerating from the same archive reproduces the same numbers
byte for byte apart from the `generated_utc` provenance stamp.

## Failure semantics and historical V1 boundaries

The current frozen V1 archive is complete: all 2,880 expected records are
present and scored. It therefore contains no missing-evidence
`CANNOT_CHECK` result. H1 is nevertheless `NOT_SUPPORTED` (ORION 1/48 versus
the strongest matched baseline 1/48); completeness does not turn that negative
finding into support. The credential-free v2.2.4 result is a narrower successor,
not a scientific supersession of H1.

`CANNOT_CHECK` remains the fail-closed response to a counterfactual incomplete
archive. In particular:

- **H1/H2 contrasts and H3/H4 diagnostics** require the registered systems,
  cases, and repeats. If a required difference cannot be formed,
  `assess_hypothesis` returns `CANNOT_CHECK`, never `NOT_SUPPORTED` or zero.
- **A missing or partial system/case cell** is excluded from both numerator and
  denominator and cannot be silently treated as failure. A case with fewer than
  the registered five repeats is also `CANNOT_CHECK` because it is a different
  measurement.
- **Structurally inapplicable metrics** are `NOT_APPLICABLE`, not
  `CANNOT_CHECK`. For example, hidden-label diagnostics do not apply to control
  scopes, and control-only diagnostics do not apply to hidden scopes.

Two further limits are structural rather than credential-related, and hold even
with a complete archive:

- **`trace_fidelity` is an internal-consistency metric, not a replay check.**
  `SystemTrace` records summary fields (`reframed`, `target_coordinates`,
  `reopened`, `max_recursion_depth`, …), not a step-by-step action log, so no
  step-level trace-replay fidelity can be computed from it. What is computed is
  whether the trace's own claims cohere: a reframe must name a responsibility
  family and target coordinates and imply depth ≥ 1; a reopen implies a reframe;
  an abstention cannot also claim root success. Depth adequacy against gold is
  reported separately as `depth_adequacy` so the H4 x-axis (gold
  `dependency_depth`) stays exogenous.
- **`UNDERPOWERED` is unreachable by default.** The protocol names a prospective
  power analysis but binds no N, so `--min-units` has no frozen value and
  defaults to 0. Until a prospective N is declared, an inconclusive result reads
  `NOT_SUPPORTED`, never `UNDERPOWERED`. No default was invented.

## Abstention is not restraint

On a negative control the three outcomes `UNNECESSARY_REFRAME`, `ABSTAINED` and
`CORRECT_RESTRAINT` partition the cases and are all reported. A system that
declines is never credited with a correct non-reframe. Because a low
unnecessary-reframe rate can in principle be bought with abstentions,
`assess_hypothesis` requires both systems' control-abstention rates for any H2
reading and returns `CANNOT_CHECK` when the subject's exceeds the comparator's
by more than the margin.

## Verification

```bash
PYTHONPATH=src python3 -m pytest -q tests/unit/study/p1/test_metrics.py
PYTHONPATH=src python3 -m ruff check src/orion/study/p1
```

The statistical assertions are pinned to published reference values (standard
tabulated Wilson intervals, including Newcombe's 81/263 worked example, and
hand-worked Holm adjustments), not to this implementation's own output.

## Remaining step-9 items

Not satisfied by this pipeline and still open: frozen baseline prompts/configs,
exact model/provider/tool versions, raw traces alongside the scored records,
licences, a permanent archive/DOI, and an independent session reproducing the
headline result from the raw artifact under external custody. The clean-source
LUNARC replay closes current deterministic reproducibility only; it does not
close that external-authority item or the historical prospective-order gap.

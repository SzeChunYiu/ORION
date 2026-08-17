# P2 permanent archive and reproduction cost ledger

Two questions this file answers: what a permanent DOI-bearing archive may and may
not contain, and what it actually costs a third party to reproduce each tier of
the paper's evidence.

`UNKNOWN_PENDING_RUN` means the number is not knowable until a campaign executes.
It is never replaced with an estimate. Counts and durations recorded below were
read from artifacts or from the run's own metadata, not inferred.

## 1. Permanent archive (Zenodo-style DOI)

### 1.1 May contain

| Contents | Source | Licence basis |
| --- | --- | --- |
| Frozen synthetic world + tasks + manifest | `evidence/offline_gold/**` | Fully synthetic, generated from a recorded seed by `src/orion/study/p2/corpus.py`; contains no third-party text. Ours to publish. |
| Subject code and evaluation harness | `src/orion/study/p2/**` | Repository licence. |
| Publication summaries and supplementary tables | `evidence/offline_results/**` | Derived from our own runs. |
| Protocol, statistical plan, measurement plan, freeze manifest | `protocol/**` | Ours. |
| Claim ledger, checker, access audit | `protocol/CLAIM_LEDGER_V1.json`, `scripts/check_claim_ledger.py`, `protocol/EXTERNAL_ACCESS_AUDIT_V1.json` | Ours. The audit records *facts about* third-party artifacts, not the artifacts. |
| MetaSyn probe archive | `evidence/external_results/METASYN_ID_ONLY_PROBE_V1.json` | Our own scored output plus content-binding digests; no upstream corpus embedded. |
| Manuscript source and figures | `manuscript/**` | Ours. |
| Literature evidence records | `evidence/literature/*.json` | Bibliographic metadata records, not article full text. |

**Mirror before the window closes.** The MetaSyn probe's GitHub Actions artifact
(`artifact_id` 9270589591) records `artifact_expires_at`
`2026-09-15T21:39:53Z` in `METASYN_ID_ONLY_PROBE_V1.json`. After that date the
committed digests remain verifiable but the raw artifact is gone unless it has
been copied into the permanent archive. Copy it now, not at submission time.

### 1.2 May **not** contain

From `protocol/TABLE_P2-1_freeze_manifest.md`, which records the licence audit per
artifact:

| Artifact | State | Why it is excluded |
| --- | --- | --- |
| `SAGE_benchmark` dataset | `AVAILABLE_LICENSE_BLOCKED`, `Redistribute: no` | The fully enumerated pinned tree contains no `LICENSE`, `COPYING` or `NOTICE`. No licence, no redistribution. |
| `AgentSLR` code | `AVAILABLE_LICENSE_BLOCKED`, `Redistribute: no` | Same: licence endpoint returned 404 and the enumerated pinned tree has no licence file. |
| `MetaSyn_dataset` | `Redistribute: partial` | Project-authored annotations are MIT; upstream terms differ. Ship the pinned dataset revision identifier and content binding, not the data. |
| AutoResearchBench code/dataset | Apache-2.0, redistributable | Redistribution is *permitted*, but we still exclude it: the archive should carry pinned revisions and digests so the archive does not become a stale fork of an upstream benchmark. |
| Any live-provider raw response bodies | n/a | Provider terms govern re-publication; excluded until reviewed per provider. Currently moot — no final live campaign exists. |

For every excluded artifact the archive ships the pinned revision, the audited
content binding (git tree SHA or HF revision SHA) and the access state, so a third
party can obtain the original themselves.

## 2. Reproduction ledger

Commands are run from the repository root. `PAPER` abbreviates
`papers/paper-02-open-world-scientific-discovery`.

### Tier 1 — fully reproducible in a clean environment

No network, no credentials, no third-party data, no monetary cost.

| Step | Command | Provider requests | Cost | Runtime |
| --- | --- | --- | --- | --- |
| Verify the frozen world against its committed hashes | `python3 -m orion.study.p2.freeze --write` (then confirm no diff) | 0 | none | `UNKNOWN_PENDING_RUN` — not yet timed in a clean environment |
| Rebuild every offline run and compare to the committed summary | `python3 $PAPER/scripts/run_offline_companion.py --check` | 0 | none | `UNKNOWN_PENDING_RUN` |
| Emit the complete raw record and artifact sets | `python3 $PAPER/scripts/run_offline_companion.py --write-raw DIR` | 0 | none | `UNKNOWN_PENDING_RUN` |
| Regenerate published tables and figures | `render_offline_results.py --check`, `render_offline_mechanisms.py --check`, `render_route_stop_oracle.py --check`, `render_table_p2_1.py --check` | 0 | none | `UNKNOWN_PENDING_RUN` |
| Verify claims against artifacts | `python3 $PAPER/scripts/check_claim_ledger.py --check` | 0 | none | ~1 s (observed on the authoring host) |
| Unit suite for this tier | `python3 -m pytest tests/unit/p2` | 0 | none | `UNKNOWN_PENDING_RUN` |

Scale note: the record count is `frozen_run.n_result_records` in
`RESULTS_SUMMARY_V1.json` and the task count is `task_count` in
`evidence/offline_gold/MANIFEST.json`. Runtime scales with those, so it must be
re-timed after any suite scale-up rather than carried over.

Environment: Python 3.13 on the authoring host; the clean CI job for this tier
runs on `ubuntu-24.04` with Python 3.11. Dependencies are the repository's own —
the claim-ledger checker is stdlib-only.

### Tier 2 — benchmark-dependent

Requires downloading third-party artifacts. Free of monetary charge as configured,
but not free of network dependency, and not reproducible offline.

| Step | Requirements | Provider requests | Cost | Runtime |
| --- | --- | --- | --- | --- |
| MetaSyn ID-only retrieval + screening probe (**completed**) | Workflow `.github/workflows/p2-metasyn-keyless.yml`; clone `THUIR/MetaSyn` at `51b95b7061e1faf241c205eb7f8e5c2bccff4848`; HF dataset `THUIR/MetaSyn` at revision `c8fa07d89c44093d623f9a213c6bf070f40ab960`; CPU `torch==2.3.1`. No LLM credential (`judge_model: null`). | 1 git clone + 1 HF dataset fetch + package installs; **0 LLM API calls** | **$0** — no metered service used | **7 min 34 s** wall clock, verified from Actions run `31973786111` (job `metasyn`, 2026-08-16T21:32:23Z → 21:39:57Z, `ubuntu-24.04`, `timeout-minutes: 120`) |
| AutoResearchBench Wide official scoring | Pinned scorer (Apache-2.0) + decrypted task bundle; credential-free per the access audit | `UNKNOWN_PENDING_RUN` | $0 for scoring itself; candidate generation is separate | `UNKNOWN_PENDING_RUN` |
| AutoResearchBench Wide ORION candidate run | Not executed. Needs an admissible candidate producing resolved arXiv identifiers per candidate | `UNKNOWN_PENDING_RUN` | `UNKNOWN_PENDING_RUN` | `UNKNOWN_PENDING_RUN` |
| AutoResearchBench Deep official metric | Requires an OpenAI-compatible judge endpoint — the one metered dependency in this tier | `UNKNOWN_PENDING_RUN` | `UNKNOWN_PENDING_RUN` (metered judge; must be measured, never estimated) | `UNKNOWN_PENDING_RUN` |
| SAGE as published | **Not reproducible.** Neither the 200k retrieval corpus nor the official evaluator is available | n/a | n/a | n/a |

Caveat inherited from upstream: the Wide evaluator's exact `avg_iou`, `avg_recall`
and `avg_precision` paths were bit-identical across five identical runs, but the
sampled `avg_max_iou_at_k` family is unseeded Monte-Carlo upstream. That metric
family is not reproducible bit-for-bit and is not reported as if it were.

### Tier 3 — archived-only

Cannot be re-derived by a third party; the archive is the evidence.

| Item | Status |
| --- | --- |
| Final live-provider result-bearing campaign: raw request/response bytes, timestamps, typed transport failures | Capture machinery exists and has been exercised. **Campaign not executed.** Request counts, wall-clock and monetary cost all `UNKNOWN_PENDING_RUN`. |
| Live-provider cost/latency/query/token plots (Figure P2-2, Figure P2-7, Table P2-2 with intervals) | Blocked on the above. |
| MetaSyn probe raw Actions artifact | Archived, expires `2026-09-15T21:39:53Z`; mirror into the DOI archive before then (§1.1). |
| Benchmark-wide contamination-rate audit | Not complete; structural exposure and spot checks only. |

Live-provider evidence is archive-only by design, not by omission: providers are
mutable and metered, so a later re-run would produce different results and would
not verify the recorded ones. This is also why provider unavailability is recorded
as a typed transport failure rather than as evidence of absence.

## 3. What a reproducer can honestly conclude

- Reproducing Tier 1 confirms that the mechanism result is exact and drift-free.
  It does **not** raise its statistical authority: `analysis_authority` stays
  `DESCRIPTIVE_ONLY`.
- Reproducing the completed Tier 2 item confirms one bounded external retrieval
  and screening evaluation under an official evaluator. It does **not** produce an
  ORION-vs-baseline external result.
- Nothing in Tier 1 or Tier 2 as currently executed can settle the paper's
  external superiority claim. That remains `CANNOT_CHECK` until a Tier 2 candidate
  run or the Tier 3 campaign is archived.

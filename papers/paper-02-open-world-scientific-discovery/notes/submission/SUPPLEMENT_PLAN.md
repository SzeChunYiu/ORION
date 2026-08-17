# P2 supplement plan

Target container: a single ZIP under TMLR's 100 MB supplementary limit
(<https://jmlr.org/tmlr/author-guide.html>, fetched 2026-08-17), anonymised for
double-blind review. Nothing in the supplement may carry author identity,
institutional paths or non-anonymous repository URLs.

No item below is included unless it already exists in the repository. Items that
depend on an unexecuted campaign are listed in section 4 as deferred, not as
planned content.

## 1. Included: frozen world and reproduction path

| Item | Source | Why it is in the supplement |
| --- | --- | --- |
| Complete-gold world and tasks | `evidence/offline_gold/{world.json,tasks.json}` | The denominator the paper's observability argument rests on. Fully synthetic, so redistributable. |
| World manifest | `evidence/offline_gold/MANIFEST.json` | Carries `task_count`, `document_count`, seed, per-file SHA-256 and `suite_fingerprint`. Reviewers verify the world was frozen before systems were configured (`frozen_before_any_system_configured`). |
| Run manifest + its digest | `protocol/OFFLINE_RUN_MANIFEST_V1.{json,sha256}` | Binds subject revision and blob identities used for the result-bearing campaign; committed before the first outcome snapshot. |
| Regeneration scripts | `scripts/run_offline_companion.py`, `render_offline_results.py`, `render_offline_mechanisms.py`, `render_route_stop_oracle.py`, `render_table_p2_1.py`, `check_claim_ledger.py` | Each carries a `--check` mode that reconstructs its published artifact and refuses drift. |
| Subject code | `src/orion/study/p2/**` | The systems, ablations and evaluator under test. |

## 2. Included: publication summaries and tables

| Item | Source |
| --- | --- |
| Offline publication summary | `evidence/offline_results/RESULTS_SUMMARY_V1.json` |
| Mechanism projection (Figures P2-3/4/5) | `evidence/offline_results/OFFLINE_MECHANISMS_V1.json` |
| Route-stop oracle replay | `evidence/offline_results/ROUTE_STOP_ORACLE_V1.json` + `TABLE_P2-S1_route_stop_oracle.md` |
| Failure taxonomy | `evidence/offline_results/TABLE_P2-3_failure_taxonomy.md` |
| Freeze / licence / access manifest | `protocol/TABLE_P2-1_freeze_manifest.md` |

The summaries record SHA-256 digests of the complete normalized record set
(`frozen_run.record_digest_sha256`, over `frozen_run.n_result_records` records) and
of the rich-artifact hash list, so a reviewer can verify a local reproduction
without the repository carrying hundreds of generated files. Quote the record
count from that key rather than from this document — it moves with the suite. The
raw sets are emitted on demand with `run_offline_companion.py --write-raw DIR`;
see `ARCHIVE_AND_COST_LEDGER.md` for whether to ship them expanded.

## 3. Included: protocol, plan and integrity layer

| Item | Source | Reviewer question it answers |
| --- | --- | --- |
| Frozen protocol | `protocol/PROTOCOL_V1.json` | What was fixed before outcomes were seen. |
| Statistical plan | `protocol/STATISTICAL_PLAN_V1.json` | Where the inferential tiers came from, and why this campaign is below the lowest one. |
| Measurement plan | `protocol/MEASUREMENT_PLAN_V1.md` | How each metric is defined and when a metric is not emitted. |
| External access audit | `protocol/EXTERNAL_ACCESS_AUDIT_V1.json` | Which external evaluators are runnable, which are blocked, and the evidence for each — including the inherited unseeded `max_iou_at_k` nondeterminism. |
| Claim ledger + checker | `protocol/CLAIM_LEDGER_V1.json`, `scripts/check_claim_ledger.py`, `evidence/CLAIM_LEDGER_V1.md` | Which sentence rests on which artifact key, and a command that fails when that stops being true. |
| External probe archive | `evidence/external_results/METASYN_ID_ONLY_PROBE_V1.json` | The one completed external evaluation, with its declared scope and content bindings. |
| Contamination probes | `evidence/access/contamination_probes.md` | Structural exposure analysis and spot checks completed to date (the benchmark-wide rate audit is not complete — see section 4). |

Supplementary tables and figures already generated from the immutable summaries
(P2-3, P2-4, P2-5, P2-6, P2-S1, P2-3 taxonomy) ship as both `.svg` and `.tex` so
the figures cannot drift from the state machine and summary they illustrate.

## 4. Deferred — named, not silently omitted

Each item below is absent because the work has not been done, not because it was
judged unimportant. None may be described in the supplement as if present.

| Item | Blocking condition |
| --- | --- |
| AutoResearchBench Wide ORION-vs-baseline result | No admissible ORION candidate run archived. Scorer runnability is established; a system result is not. |
| AutoResearchBench Deep official metric | Requires an OpenAI-compatible judge endpoint. |
| SAGE result | Published 200k retrieval corpus and official evaluator unavailable. **Struck**, not deferred: no substitute "official" evaluator will be constructed. |
| Table P2-2 with intervals, Figure P2-2, Figure P2-7 | Require the cost-bearing external/live campaign; the offline result is `DESCRIPTIVE_ONLY` and cannot satisfy an interval requirement. |
| Raw final live-provider request/response archive and cost ledger | Capture machinery exists and has been exercised; the final campaign has not been run. |
| Benchmark-wide search-time contamination-rate audit | Only structural exposure and spot checks are complete. |
| Expert-review comparison cases | Deferred pending available domain experts. |

## 5. Excluded on licence grounds

Per `protocol/TABLE_P2-1_freeze_manifest.md`, two upstream families are
`AVAILABLE_LICENSE_BLOCKED` — no `LICENSE`, `COPYING` or `NOTICE` file exists in
the fully enumerated pinned tree — and must **not** be redistributed in any
supplement or archive: the SAGE benchmark dataset and the AgentSLR code. The
MetaSyn dataset is only partially redistributable (project-authored annotations
under MIT; upstream terms differ). Where redistribution is blocked, ship the
pinned revision identifier and the audited content binding so a reviewer can
obtain the artifact themselves, never a copy.

## 6. Pre-submission checklist

1. `python3 papers/paper-02-open-world-scientific-discovery/scripts/run_offline_companion.py --check` → exit 0.
2. `python3 papers/paper-02-open-world-scientific-discovery/scripts/render_offline_results.py --check` → exit 0.
3. `python3 papers/paper-02-open-world-scientific-discovery/scripts/check_claim_ledger.py --check` → exit 0 **and** review every `KNOWN_DEFECT_OPEN` note; ideally `--strict` also exits 0.
4. Confirm the `task_count` written in the paper matches `evidence/offline_gold/MANIFEST.json`; the checker enforces cross-artifact agreement, so a disagreement here is a hard failure, not a typo.
5. Anonymise: strip author names, acknowledgements, funding, absolute local paths and any non-anonymous repository URL from manuscript and supplement.
6. Verify no file under section 5 has been swept into the ZIP.

# P2 permanent archive and reproduction-cost ledger — narrowed track

Scientific terminal: `P2_NARROWED`.

This ledger separates evidence that is exactly reproducible, evidence that depends on pinned third-party benchmarks, and evidence that is archive-only or unavailable. `UNKNOWN_PENDING_RUN` is never replaced with an estimate. The narrowed paper does not require matched Wide/Deep or live-provider superiority; unavailable authorities remain visible reopen conditions rather than being turned into zeros.

## 1. Permanent archive

### 1.1 Include where licence permits

| Contents | Source | Basis |
| --- | --- | --- |
| Frozen synthetic world, tasks and manifest | `evidence/offline_gold/**` | Project-generated synthetic material. |
| P2 subject code/evaluation harness | `src/orion/study/p2/**` | Repository licence. |
| Publication summaries/tables | `evidence/offline_results/**` | Derived project output. |
| Protocol/statistical/measurement plans | `protocol/**` | Project-authored. |
| Claim ledger/checker | `protocol/CLAIM_LEDGER_V1.json`, `scripts/check_claim_ledger.py` | Project-authored integrity layer. |
| P2 donor-assimilation ledger/checker | `protocol/P2_DONOR_ASSIMILATION_LEDGER_V1.json`, `scripts/check_p2_assimilation.py` | Project-authored source/authority binding. |
| MetaSyn bounded probe archive | `evidence/external_results/METASYN_ID_ONLY_PROBE_V1.json` and FN ledger | Project-scored output/content bindings; do not embed upstream restricted data. |
| AutoResearchBench bounded Wide/Deep archives | committed external-results artifacts | Project outputs under their declared bounded authority; keep upstream benchmark revisions/digests separately. |
| Manuscript source and generated figures | `manuscript/**` | Project-authored; archive the final compiled source set after the render gate passes. |
| Dated literature freeze / publication terminal | `protocol/P2_LITERATURE_ASSIMILATION_FREEZE_2026-08-17.md`, `protocol/P2_NARROWED_PUBLICATION_TERMINAL_2026-08-17.md` | Audit trail for final claim scope. |

**Retention risk:** the committed MetaSyn probe records GitHub Actions artifact expiry `2026-09-15T21:39:53Z` (artifact id 9270589591). Mirror the raw artifact into a durable archive before that date where licensing permits; committed digests alone cannot restore expired raw bytes.

### 1.2 Exclude or bind by reference

- SAGE benchmark data: `AVAILABLE_LICENSE_BLOCKED` in the freeze manifest; do not redistribute without a licence basis.
- AgentSLR code: `AVAILABLE_LICENSE_BLOCKED`; do not redistribute without a licence basis.
- MetaSyn upstream data: only redistribute portions whose terms permit it; otherwise ship pinned revision/content bindings.
- AutoResearchBench upstream corpus/code: even where redistribution is permitted, prefer pinned revisions/digests unless the archive has a concrete reason to embed a fork.
- Any live-provider raw response body: provider terms govern redistribution; no final live campaign is claimed by the narrowed paper.

## 2. Reproduction ledger

Commands are run from repository root. `PAPER` abbreviates `papers/paper-02-open-world-scientific-discovery`.

### Tier 1 — controlled result; local/offline authority

No provider credential or metered API is needed for the frozen controlled campaign.

| Step | Command / evidence | Provider requests | Cost authority |
| --- | --- | --- | --- |
| Verify/regenerate controlled campaign | `python3 $PAPER/scripts/run_offline_companion.py --check` | 0 | none |
| Emit raw controlled records | `python3 $PAPER/scripts/run_offline_companion.py --write-raw DIR` | 0 | none |
| Verify publication projections | offline result/mechanism/route-stop/table render `--check` commands | 0 | none |
| Verify result-bearing manuscript claims | `python3 $PAPER/scripts/check_claim_ledger.py --check` | 0 | none |
| Verify donor assimilation | `python3 $PAPER/scripts/check_p2_assimilation.py` | 0 | none |
| Compile publication PDF | `.github/workflows/p2-manuscript.yml` | package-network only | no scientific provider cost |
| P2 unit/integrity suite | repository CI / P2 tests | 0 scientific-provider requests | none |

The record count, task count and all reported headline values come from their bound artifacts, not this prose. Reproduction confirms exact mechanism evidence; it does **not** raise the frozen `TIER_B_committed` result to an inferential superiority claim.

### Tier 2 — pinned third-party benchmark evidence

| Evidence | Current status | Credential/metering | Reproduction meaning |
| --- | --- | --- | --- |
| MetaSyn official ID-only retrieval/screening probe | **COMPLETED** on all 86 released reviews | no LLM credential; archived run used pinned benchmark/data revisions | confirms the bounded retrieval/screening probe only |
| AutoResearchBench Wide bounded credential-free probe | **COMPLETED/ARCHIVED** | official scoring path credential-free | weak/null external stress test; **not** a matched ORION-vs-baseline result |
| AutoResearchBench Deep bounded official-judge probe | **COMPLETED/ARCHIVED** at 0/600 with judge control 9/9 | judge executed through the declared compatible adapter | negative candidate-generation diagnostic; **not** matched multi-provider superiority |
| Matched AutoResearchBench Wide ORION-vs-baseline | `CANNOT_CHECK` | current frozen matched runner/scorer authority is arXiv-native | prospective reopen only |
| Matched multi-provider Deep | `CANNOT_CHECK` | unavailable under current backend/authority setup | prospective reopen only |
| SAGE as published | `CANNOT_CHECK/STRUCK` | official 200k corpus/evaluator unavailable | no substitute may be labelled official |

The Wide scorer's exact IoU/recall/precision path is the relevant deterministic authority. Any upstream unseeded sampled metric remains non-bit-reproducible and must not be presented as exact.

### Tier 3 — live-provider/archive-only future evidence

The final live-provider result-bearing campaign was **not executed** and is no longer required by the narrowed paper because no live-provider superiority, monetary-cost, latency or token claim is made. If reopened prospectively, raw request/response bytes, timestamps, transport outcomes and measured monetary/runtime/token costs must be archived; a later provider rerun would not verify historical mutable-provider evidence.

Provider unavailability remains a typed transport/censoring state, never evidence that no relevant literature exists.

## 3. Publication-authority interpretation

- Tier 1 confirms the controlled mechanism result is reproducible and evidence-bound; it remains descriptive/underpowered under the frozen statistical plan.
- Completed Tier 2 probes characterize external retrieval/screening and candidate-generation failure modes; they do not validate the complete multi-route ORION system.
- Matched Wide/Deep, official SAGE and live-provider routes are reopen conditions, not prerequisites for `P2_NARROWED`.
- No absent credential, unavailable corpus, null probe or unexecuted campaign may be promoted into positive evidence.

## 4. Before public release

1. Retain the final manuscript PDF/log produced by the manuscript workflow and visually audit every page.
2. Mirror expiring raw benchmark-run evidence into a durable repository-independent archive where licensing permits.
3. Deposit the frozen controlled evidence, integrity ledgers, scripts and permitted bounded external artifacts under a persistent identifier where practical.
4. Record the final deposited version/hash in the submission package.
5. Re-run the dated literature refresh within 14 days of the actual submission date and update the archive if the residual claim changes.

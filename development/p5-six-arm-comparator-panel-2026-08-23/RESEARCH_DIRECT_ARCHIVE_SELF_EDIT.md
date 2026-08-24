# P5 C2/C3 primary-source identity research

**Artifact:** `P5.C2.C3.PRIMARY_SOURCE.IDENTITY.RESEARCH.V1`  
**Audit date:** 2026-08-23  
**Owned scope:** `C2_DIRECT_SELF_EDIT`, `C3_ARCHIVE_BASED_SELF_EDIT`  
**Frozen protocol:** `P5_OUTCOME_BLIND_COMPARATOR_AND_PUBLIC_PANEL_PROTOCOL_V1.json`  
**Authority:** source identity, interface, licence-byte and feasibility preflight only. This is not a performance evaluation and grants no confirmatory authority.

The outcome-blind protocol was already frozen before this source audit. I opened no dataset row, issue body selected for the study, label, gold patch, test body/outcome, protected result, or comparator performance record. I did not execute any comparator. Evidence was restricted to current arXiv version metadata/abstracts, primary project pages, paper-linked official repositories at immutable commits, repository README/packaging/source entrypoints, and licence/notice bytes.

## Decision

| Frozen slot | Exact identity | Paper | Official immutable source | Semantic verdict | P5 execution terminal |
|---|---|---|---|---|---|
| `C2_DIRECT_SELF_EDIT` | **MOSS** | `arXiv:2605.22794v2` | `hkgai-official/Moss@5453f1feebad44c199f5887f852fc5bc7fb7d4da` | `EXACT_C2_DIRECT_SELF_EDIT` | `CANNOT_CHECK`: no released outcome-blind eight-class adapter |
| `C3_ARCHIVE_BASED_SELF_EDIT` | **Darwin Gödel Machine** | `arXiv:2505.22954v3` | `jennyzzt/dgm@a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2` | `EXACT_C3_ARCHIVE_BASED_SELF_EDIT` | `CANNOT_CHECK`: no released outcome-blind eight-class adapter |
| C3 alternate audited | **ADAS / Meta Agent Search** | `arXiv:2408.08435v2` | `ShengranHu/ADAS@2702bee8fefda42255efc5be9f60e3bd3db96ae4` | `NEAR_MISS_ARCHIVE_AGENT_DESIGN_NOT_SELF_EDIT` | reject as an exact C3 substitution; a declared protocol reimplementation remains `CANNOT_CHECK` |

**Why the distinction matters.** MOSS directly rewrites the active OpenClaw source along one governed lineage and does not describe archived-parent population selection. DGM both edits the agent implementation and samples/branches from an archive of prior variants. ADAS also keeps an archive, but its released controller uses a meta-agent to program *new candidate agents*; the search controller does not rewrite itself. ADAS is therefore strong neighboring prior work or a separate meta-agent-search baseline, not a lawful silent replacement for the frozen C3 self-edit semantic.

---

## C2 — MOSS

### Identity and primary binding

- **Paper:** Cai et al., “MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems,” [`arXiv:2605.22794v2`](https://arxiv.org/abs/2605.22794v2), updated `2026-05-23T13:08:16Z`.
- The arXiv record itself states `Code: https://github.com/hkgai-official/Moss`.
- **Official repository:** [`hkgai-official/Moss`](https://github.com/hkgai-official/Moss).
- **Audited immutable commit:** [`5453f1feebad44c199f5887f852fc5bc7fb7d4da`](https://github.com/hkgai-official/Moss/tree/5453f1feebad44c199f5887f852fc5bc7fb7d4da), default-branch commit timestamp `2026-05-23T03:57:09Z`.
- **Status:** `OFFICIAL_PAPER_LINKED_IMPLEMENTATION`, not a reproduction and not a benchmark repository.
- Downloaded commit archive SHA-256: `de6bb0e480749757d8e9b05a66c37c82228ea6d9d1e1cb92b6b32a3b28e5610e`.

Primary-source semantic receipts:

> “Each evolution is anchored to an automatically curated batch of production-failure evidence ... Candidates are verified by replaying the batch ... then promoted via user-consent-gated, in-place container swap.” — [paper version page](https://arxiv.org/abs/2605.22794v2)

> “MOSS ... rewrites its own TypeScript source ... verifies the candidate by replaying the batch ... after explicit user authorization ... performs an in-place container swap with health-probe-gated rollback.” — [pinned README line 17](https://github.com/hkgai-official/Moss/blob/5453f1feebad44c199f5887f852fc5bc7fb7d4da/README.md#L17)

This is an exact direct-self-edit identity: a single active lineage rewrites the application-agent substrate, verifies the candidate, and optionally swaps it in. No archive/population parent-selection mechanism is documented in the released interface.

### Licence bytes and rights boundary

| Path at pinned commit | Declared class | Bytes | SHA-256 |
|---|---:|---:|---|
| `LICENSE` | Apache-2.0 for MOSS additions/root integration | 11,277 | `3903e8b0fd6b4f6fc83f194c1e7b8525f1b40a284e4682ba1cec7e77eb765b63` |
| `NOTICE` | composite attribution notice | 1,002 | `da9dce4d4fbd44a4feb37a54e27220788fbcc6887e4367d479b1bd402f63dd19` |
| `openclaw/LICENSE` | MIT for vendored OpenClaw | 1,074 | `62316704df7426e5a79d2827ff8aca36e9abb3a73b8e68557030749ebefec667` |

The pinned README says MOSS-added evolution/daemon/integration code is Apache-2.0, `openclaw/` remains MIT, and vendored a2ui material includes ISC/Apache-2.0 components. Preserve applicable notices and third-party terms. Rights to user sessions, production-failure evidence, external models, and any supplied evaluation content remain separate. This is not legal advice.

### Install and native run identity

Documented prerequisites are Docker 24+, Node 22+, pnpm 10, Python 3.11+, `jq`, an OpenAI-completions-compatible endpoint, and one installed/authenticated external coding-agent CLI (Claude Code, Codex, DeepSeek-TUI, or OpenCode).

```text
git clone https://github.com/hkgai-official/Moss.git moss
cd moss
cp .env.example .env
# fill model/provider configuration
./scripts/setup.sh
```

Native control surface:

```text
moss evo flag --agent <id> --session <id>
moss evo start [<batch-id>] [--depth shallow|standard|deep]
moss evo status
moss evo stop
moss evo apply <batch-id>
# host form: docker exec moss-gateway moss <command>
```

All documented CLI commands accept `--json`. `host-daemon/pyproject.toml` declares Python `>=3.11`, `pyyaml>=6.0`, and `tomli-w>=1.0`; the OpenClaw tree is managed with Node/pnpm and Docker.

### Information, actions, and write surface

**Candidate-visible information:** OpenClaw source; a curated batch of weak session chunks; baseline and candidate replay traces; diagnoses, plans, diffs, reviews and scoring matrices; spawned coding-agent/model/tool outputs; evolution state.

**Native actions:** scan or flag session evidence; spawn coding roles; edit OpenClaw TypeScript source in an inner local Git repository; build candidate images; replay batch tasks in ephemeral workers; write evolution artifacts; request an explicitly authorized image swap; roll back if health probes fail.

**Writes:** `openclaw/` inner-repository branches/commits, `${MOSS_DATA_DIR:-$HOME/.moss}`, Docker images/containers, local `.env`-derived state, and `/tmp/moss.sock`. A P5 adapter must confine these to an isolated candidate workspace.

### Cost/retry/compute envelope

Pinned `state.ts` depth tiers are:

| Depth | max iterations | max plan rounds | max code retries | trials/task | plateau iterations |
|---|---:|---:|---:|---:|---:|
| shallow | 3 | 1 | 0 | 2 | 1 |
| standard | 5 | 2 | 1 | 3 | 2 |
| deep | 8 | 3 | 2 | 5 | 3 |

Other defaults: task trial `300 s`, one validation trial, build smoke `240 s`, Docker build `600 s`, locator/planner `1800 s`, plan reviewer `1500 s`, implementer `3600 s`, code reviewer `1800 s`, task evaluator `1500 s`, reviewer `1200 s`, swap window `90 s`. Spawns return provider, model, elapsed time, USD cost and token counts when the provider exposes them, but the released manifest has no whole-run token or USD cap. Compute includes multiple model/coding-agent roles, Docker builds, and per-task workers.

### Native outputs, errors, and terminals

Native artifacts include status/batch/apply JSON; diagnosis, plan, diff, review, task-evaluation and scoring matrices; and spawn terminals `{exit_code, elapsed_s, session_id, cost_usd, tokens, provider, model}`. The documented loop returns `CONVERGED`, `NEED_MORE_WORK`, `FUNDAMENTAL_LIMIT_MODEL`, or `FUNDAMENTAL_LIMIT_ARCHITECTURE`; manifest statuses include `rolled_back`, `failed`, `aborted_max_iter`, and `aborted_streak`. Unknown providers, role failures/timeouts and Docker-build timeouts are retained errors. Apply can roll back after health-probe failure.

### Lawful P5 adapter and terminal

MOSS does **not** natively emit one of P5’s eight revision classes. Its native replay traces and scores also cannot be exposed on the protected path. A lawful adapter would have to:

1. pass only the frozen candidate-visible motivating packet;
2. block protected labels, gold patches, outcomes and evaluator responses;
3. isolate all source/container writes;
4. map the final frozen successor to exactly one P5 action or `UNRESOLVED`;
5. retain native failures/timeouts/limits;
6. send the frozen output to an evaluator outside candidate custody.

`MOSS_P5_OUTCOME_BLIND_EIGHT_CLASS_ADAPTER_NOT_RELEASED`

**Terminal:** `IDENTITY_BOUND__OFFICIAL_SOURCE_RUNNABLE_IN_NATIVE_OPENCLAW_SETTING__P5_CONFIRMATORY_EXECUTION_CANNOT_CHECK`.

---

## C3 — Darwin Gödel Machine

### Identity and primary binding

- **Paper:** Zhang et al., “Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents,” [`arXiv:2505.22954v3`](https://arxiv.org/abs/2505.22954v3), updated `2026-03-12T23:47:40Z`.
- The arXiv record itself states `Code at https://github.com/jennyzzt/dgm`.
- **Official repository:** [`jennyzzt/dgm`](https://github.com/jennyzzt/dgm).
- **Audited immutable commit:** [`a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2`](https://github.com/jennyzzt/dgm/tree/a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2), default-branch commit timestamp `2025-08-13T10:40:14Z`.
- **Status:** `OFFICIAL_PAPER_LINKED_IMPLEMENTATION`.
- Downloaded commit archive SHA-256: `3c98ae6bfa7b6597cbcddaf02bcce46e56ff97cdf6d14867251211be8069d961`.

Primary-source semantic receipts:

> “DGM ... iteratively modifies its own code ... maintains an archive of generated coding agents ... grows the archive by sampling an agent from it and using a foundation model to create a new ... version.” — [paper version page](https://arxiv.org/abs/2505.22954v3)

> “a novel self-improving system that iteratively modifies its own code ... and empirically validates each change using coding benchmarks.” — [pinned README line 14](https://github.com/jennyzzt/dgm/blob/a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2/README.md#L14)

The released [`choose_selfimproves`](https://github.com/jennyzzt/dgm/blob/a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2/DGM_outer.py#L50-L150) selects archived parents, while `update_archive` retains admitted children. This is the exact frozen C3 semantic.

### Licence bytes and rights boundary

- `LICENSE`: Apache-2.0, 11,361 bytes, SHA-256 `84b7504ce8dda1f37f592cdf67ad21371864583720d79ea289b0b0c75bfcdb17`.
- Pinned raw licence: [`LICENSE`](https://raw.githubusercontent.com/jennyzzt/dgm/a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2/LICENSE).

The README says the evaluation-framework implementations are based on SWE-bench and Polyglot. That statement does **not** make either benchmark repository DGM solver code and does not project DGM’s root Apache licence onto benchmark data, task content, source projects, tests, or containers. Those rights require separate audits.

### Install and native run identity

Documented installation requires Docker, Python virtualenv plus mostly unpinned `requirements.txt`, OpenAI/Anthropic or Bedrock credentials, and a **separate** SWE-bench checkout pinned in the README to `dc4c087c2b9e4cefebf2e3d201d27e36`. The repository is raw scripts rather than an installable package.

```text
python3 -m venv venv
pip install -r requirements.txt
# install the separately cloned/pinned SWE-bench framework
python DGM_outer.py
```

Native entrypoints:

- `python DGM_outer.py` — archive/evolution outer loop;
- `python self_improve_step.py ...` — one self-improvement attempt;
- `python coding_agent.py --problem_statement ... --git_dir ... --base_commit ... --chat_history_file ... [--self_improve]` — coding agent.

### Information, actions, and write surface

**Candidate-visible information:** DGM source/tools; archived variants and parent/child metadata; per-variant performance plus resolved/unresolved/empty-patch identifiers; evaluation logs used for diagnosis; parent patch chain; generated problem statement/test description; current source diff.

**Native actions:** select an archived parent; diagnose a failure target; apply parent patches in a Docker container; edit `/dgm` source; create a diff; run evaluation harnesses; admit compiled children to the archive.

**Writes:** `output_dgm/<run-id>/`, per-child logs/metadata/diffs, temporary `/dgm` container worktrees, and prepared external benchmark checkouts.

This native information flow is explicitly performance-aware. It can be used for public development only unless a separate adapter prevents all protected-outcome access and freezes the evolved policy before protected evaluation.

### Cost/retry/compute envelope

Pinned defaults are 80 generations, two improvement attempts/generation, two parallel self-improvement workers, one SWE evaluation/attempt, `keep_all` archive update, and `score_child_prop` parent choice. Diagnosis uses `o1-2024-12-17`; the coding agent defaults to `bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0`; supported chat/tool responses use up to 4096 output tokens.

Diagnosis makes the initial call plus up to three recursive retries. Tool responses likewise have up to three recursive retries after the initial call and an exponential-backoff decorator capped at 600 seconds. The inner coding-agent process is wrapped in GNU `timeout 1800`.

The outer code comments a 1.5-hour future timeout, but calls `future.result(timeout=5400)` only after `as_completed` has yielded that future. Therefore it does not bound a still-running attempt; build/harness work has no proven whole-attempt watchdog. Total Docker, model and harness cost is not globally capped by tokens or USD.

A pinned static CLI defect also matters for an exact harness: `choices=['random', 'score_prop', 'score_child_prop' 'best']` concatenates the last two strings. Thus `best` is not a valid separate choice and the intended `score_child_prop` option is not represented as written. The P5 binding must either freeze a declared patch/reimplementation or retain the native failure; it may not silently change the official identity.

### Native outputs, errors, and terminals

Outputs include `output_dgm/<run-id>/dgm_outer.log`, `dgm_metadata.jsonl` (generation, entries, children, compiled children, archive), per-child `metadata.json`, `self_improve.log`, `self_evo.md`, `model_patch.diff`, and evaluation artifacts.

Native failures include missing cached initial results, compilation/evaluation exclusion, missing/empty patch, context-length provider error, coding-agent timeout, and logged evaluation exception. There is no native P5 `UNRESOLVED` action or structured eight-class abstention.

### Lawful P5 adapter and terminal

A lawful adapter must evolve only on a frozen public-development pool; never expose protected labels, patches, outcomes or evaluator messages to diagnosis/archive selection; freeze the final archive-selection policy before protected evaluation; enforce one eight-class action or `UNRESOLVED`; isolate writes; and retain every invalid patch/error/timeout.

The released DGM is coupled to benchmark issue identifiers, resolution/patch outcomes, performance-weighted parent selection, Python self-code patches and benchmark harnesses. It contains no P5 action schema, source-disjoint unit, custody split, or protected-fresh adapter.

`DGM_P5_OUTCOME_BLIND_EIGHT_CLASS_ADAPTER_NOT_RELEASED`

**Terminal:** `IDENTITY_BOUND__OFFICIAL_NATIVE_DGM_RUN_PATH_DOCUMENTED__P5_CONFIRMATORY_EXECUTION_CANNOT_CHECK`.

---

## ADAS / Meta Agent Search — audited near miss, not C3 substitution

### Identity and primary binding

- **Paper:** Hu, Lu & Clune, “Automated Design of Agentic Systems,” [`arXiv:2408.08435v2`](https://arxiv.org/abs/2408.08435v2), updated `2025-03-02T05:13:28Z`.
- **Primary project page:** [`shengranhu.com/ADAS`](https://www.shengranhu.com/ADAS/), whose Code control links to the official repository.
- **Official repository:** [`ShengranHu/ADAS`](https://github.com/ShengranHu/ADAS).
- **Audited immutable commit:** [`2702bee8fefda42255efc5be9f60e3bd3db96ae4`](https://github.com/ShengranHu/ADAS/tree/2702bee8fefda42255efc5be9f60e3bd3db96ae4), default-branch commit timestamp `2025-01-28T06:37:51Z`.
- **Status:** official paper-linked Meta Agent Search implementation.
- Downloaded commit archive SHA-256: `cae3cc86151a1bc1f3a75f7f1c764ecef2ecca4d50e111d009b1ced85843c4e6`.
- `LICENSE`: Apache-2.0 for repository code, 11,341 bytes, SHA-256 `2591bb5c650dc96c48e4244d52c7bc179ff904e3129d65dcb9180bc726a4b3ad`. Bundled/supplied dataset content rights remain separate and `CANNOT_CHECK` here.

The paper describes “a meta agent programming ever better [agents] in code ... based on an ever-growing archive of previous discoveries.” The pinned README says the meta-agent “iteratively programs interesting new agents in code based on previous discoveries” ([line 24](https://github.com/ShengranHu/ADAS/blob/2702bee8fefda42255efc5be9f60e3bd3db96ae4/README.md#L24)). This is archive-based automated **agent design**, not self-rewriting of the search controller.

### Native interface and envelope

Install: Python 3.11 conda environment, unpinned `requirements.txt` (`numpy`, `tqdm`, `pandas`, `openai`, `backoff`, `scipy`, `blobfile`), and `OPENAI_API_KEY`. Run `python {DOMAIN}/search.py` in one of the released self-contained domain directories. The README’s new-domain instructions explicitly require modifying `evaluate_forward_fn`, formatting prompts, available functions and domain prompts ([lines 53–64](https://github.com/ShengranHu/ADAS/blob/2702bee8fefda42255efc5be9f60e3bd3db96ae4/README.md#L53-L64)).

The archive exposes prior `name`, `thought`, generated `code`, `generation`, and `fitness`; proposals see evaluation feedback/errors and two reflexion rounds. Generated Python is executed in-process and JSON archives/evaluation files are written under `results/`.

Defaults include 25 ARC or 30 shown-domain generations, 32/48 workers, three debug attempts, and dated `gpt-4o-2024-05-13`. Each generation makes one proposal and two reflexion calls (up to 4096 output tokens each), plus task-evaluation calls. Rate-limit backoff has no explicit source-level max time/tries; no whole-run, per-call, USD or token cap is released. Errors may skip generations or become zero scores; no structured abstention exists.

### Disposition

A declared **non-official protocol reimplementation** could replace `evaluate_forward_fn` with a public-development-only P5 action evaluator, sandbox generated code, separate evaluator custody, freeze promotion, and match resources. But that would be an ADAS-style meta-agent-search adapter, not the official C3 self-edit identity.

`OFFICIAL_ADAS_IDENTITY_BOUND__REJECT_AS_EXACT_C3_SUBSTITUTE__PROTOCOL_REIMPLEMENTATION_CANNOT_CHECK`

---

## Manuscript-ready identity and limitation text

> **Six-arm comparator identity.** The direct-self-edit arm is the paper-linked MOSS implementation (`arXiv:2605.22794v2`; `hkgai-official/Moss@5453f1fe...`), whose active lineage rewrites the deployed agent substrate and gates successor promotion after replay. The archive-based-self-edit arm is the paper-linked Darwin Gödel Machine implementation (`arXiv:2505.22954v3`; `jennyzzt/dgm@a565fd2d...`), which branches self-modified coding-agent successors from an explicit archive. ADAS/Meta Agent Search (`arXiv:2408.08435v2`; `ShengranHu/ADAS@2702bee8...`) is retained as neighboring archive-based agent-design prior work but is not substituted for the self-edit arm because its released controller programs candidate agents rather than rewriting itself.

> **Execution limitation.** These bindings establish comparator identity, not a completed comparison. Neither official implementation exposes the frozen P5 eight-class action interface or the required outcome-blind candidate/evaluator custody boundary. MOSS natively consumes replay traces from curated production failures, while DGM natively uses benchmark outcomes and performance-aware archive selection. Confirmatory execution therefore remains `CANNOT_CHECK` until a prospectively frozen adapter isolates candidate writes, blocks protected outcomes, matches token/tool/time/compute budgets, emits typed invalid/error/timeout/`UNRESOLVED` terminals, and freezes the evolved policy before protected evaluation.

> **Repository/benchmark boundary.** DGM’s official solver code is `jennyzzt/dgm` at the pinned commit. SWE-bench and Polyglot are separately acknowledged evaluation frameworks; neither benchmark repository is solver code, and no comparator repository licence is projected onto external dataset, task, source-project, patch, test, or container content.

## Final terminals

- `C2_DIRECT_SELF_EDIT_IDENTITY_BOUND_OFFICIAL_MOSS_V2`
- `C3_ARCHIVE_BASED_SELF_EDIT_IDENTITY_BOUND_OFFICIAL_DGM_V3`
- `ADAS_NEAR_MISS_ARCHIVE_AGENT_DESIGN_NOT_EXACT_SELF_EDIT`
- `P5_C2_C3_IDENTITY_BOUND__EIGHT_CLASS_OUTCOME_BLIND_ADAPTERS_CANNOT_CHECK`
- `H1_H4_AND_PROTECTED_FRESHNESS_CANNOT_CHECK`

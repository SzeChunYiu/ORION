# P5 C4/C5 primary-source handoff

**As of:** 2026-08-23  
**Scope:** `C4_ISSUE_CENTRIC_OPTIMIZATION`, `C5_EVALUATOR_ONLY_EVOLUTION`  
**Authority:** identity, rights and interface research only. No dataset row, label,
gold patch, test body/outcome, protected result, comparator run, pytest or CI was
opened or executed.

## Decision

| Slot | Exact selected identity | Immutable source | Rights | Current terminal |
|---|---|---|---|---|
| C4 issue-centric optimization | **ADIAS**, arXiv `2608.06410v1` | [`scylj1/adias@fbcf0c73d12d30a4ee0d13c2e64b4c40d00b2993`](https://github.com/scylj1/adias/tree/fbcf0c73d12d30a4ee0d13c2e64b4c40d00b2993) | Repository `LICENSE.md` is CC BY-NC-SA 4.0, SHA-256 `047d2259741a3ebb30d8c8a43d4ba79b5b229a069acd1d2bea49f22b297d8e98`; noncommercial/restricted, not OSI-open | `P5_C4_IDENTITY_BOUND_SOURCE_AVAILABLE_RESTRICTED__P5_EIGHT_CLASS_ACTION_ADAPTER_CANNOT_CHECK` |
| C5 evaluator-only evolution | **Double Ratchet metric-only arm**, arXiv `2607.12790v2`; specifically `scripts/run_metric_evo.py`, **not** `run_co_evo.py` | [`amazon-science/Self-Evolving-Agents-Double-Ratchet@0f14e910d361196422d9b938f45280919952d4fd`](https://github.com/amazon-science/Self-Evolving-Agents-Double-Ratchet/tree/0f14e910d361196422d9b938f45280919952d4fd) | Apache-2.0 `LICENSE`, SHA-256 `09e8a9bcec8067104652c168685ab0931e7868f9c8284b66f5ae6edae5f1130b`; `NOTICE` SHA-256 `5d86be6e681240106316a6763eb0dcb47a8adcb426c19df4693098ceb61bb531` | `P5_C5_IDENTITY_BOUND_OFFICIAL_EVALUATOR_ONLY_IMPLEMENTATION__P5_PROTECTED_EIGHT_CLASS_ADAPTER_CANNOT_CHECK` |

These are exact semantic fits. ADIAS says that persistent issue state carries
stable issue identity, lifecycle, evidence and intervention outcomes into focused
full-code revision. Double Ratchet v2 says the metric that grades one solver
output is the **only** evolving object; its official runner further says the
skill bank is empty and only the evaluation metric evolves.

## C4: ADIAS binding

- **Paper/repository relation:** the [primary full text](https://arxiv.org/html/2608.06410v1)
  says “Code is available at `https://github.com/scylj1/adias/`.” The pinned
  README calls the repository an initial ADIAS code release.
- **Install:** Python 3.12 virtualenv; system Graphviz/build dependencies;
  `pip install -r requirements.txt`, `pip install -r requirements_dev.txt`,
  `pip install -e .`; build the selected domain Docker image.
- **Entrypoints:** `adias-eval`, `adias-harness`, `adias-report`,
  `adias-run-meta-agent`; formal `scripts/run_*.sh` launch
  `generate_loop.py`. The documented Tau-bench-return script defaults to three
  generations, 55 train, 15 validation, 32 test, four evaluation workers and
  one final-test repeat. The general CLI defaults to ten generations.
- **Information:** task protocol/public priors, candidate code/lineage, exposed
  development scores and trajectories, diagnosis, patch history, and
  `profile.json` issue state.
- **Actions:** focused code revision plus issue-state/parent/revision planning.
  The released improver prompt names 1–3 files under `task_agent/`,
  `diagnostic_agent/`, or `profile_agent/`, but the CLI description for
  `agent_and_meta` additionally names `meta_agent.py` and `generate_loop.py`.
  This mismatch requires an external path allow-list at P5 freeze.
- **Cost/errors:** the meta improve/learn subprocess has a 21,600-second timeout;
  aggregate tokens/tool calls are not capped, though `token_usage.json` may be
  recorded. Compile errors produce `compile_status.ok=false` and skip candidate
  evaluation. Empty patches, missing profile artifacts and parallel evaluation
  errors are logged, not converted to a typed P5 terminal.
- **Native output:** `model_patch.diff`, patch summary, issue profile,
  diagnosis, candidate archive/lineage, scores/logs and final summary. There is
  no native one-of-eight minimal-revision output or `CANNOT_CHECK`.

### Required P5 adapter

Pass only the frozen candidate-visible dossier and motivating/replay evidence.
A content-bound deterministic mapper may use the issue target **and actual write
set** to emit one of the eight P5 classes only when the mapping is unique and
the class action is permitted. Ambiguity, unsupported class, cross-class edit,
missing evidence, error or timeout must become `UNRESOLVED` with no broad edit.
Protected fresh/evaluator outcomes must never update `profile.json` before the
terminal decision. The wrapper must externally enforce class-specific write
surfaces and retain null/failed/harmful candidates.

This adapter remains absent. ADIAS natively optimizes agent-side code; it does
not implement the complete P5 evidence/measurement/model-class/representation/
execution/evaluator action ontology. Do not relabel arbitrary full-code patches
as eight-class coverage.

## C5: exact evaluator-only identity

The exact arm is the metric-only runner in Double Ratchet:

```text
python scripts/run_metric_evo.py \
  --single-model global.anthropic.claude-opus-4-7 \
  --rounds 100 --patience 100 --min-delta 0 --seed 42 --tag anchored
```

The repository also provides `run_co_evo.py`, but that jointly evolves metric
and skills and is therefore forbidden for C5.

- **Install/services:** Python >=3.11 and `pip install pydantic pyyaml boto3`;
  AWS Bedrock credentials/IAM. Spider additionally needs hosted Snowflake;
  report generation needs unreleased external data/evaluator. The repository
  ships no datasets/results/logs, so source Apache-2.0 does not establish rights
  to any benchmark/P5 content.
- **Native inputs:** outputs from a prospectively fixed, no-skill solver;
  unlabelled train outputs; a sparse development anchor; typed detector pool,
  marginals, gaps and elite expression history.
- **Native actions:** synthesize/promote/retire typed drawback detectors and
  evolve their inspectable reverse-tree expression. The solver stays fixed.
- **Defaults:** stored MBPP split sizes 60 train / 10 dev / 40 locked; eight
  rounds; `min_delta=0.01`; patience 2; seed 42; parallelism 64; 8,192 maximum
  output tokens per model call. Paper reproduction uses up to 100 rounds and
  seeds 42, 7 and 13. There is no hard aggregate token/call/dollar cap.
- **Retries:** Bedrock transient errors receive at most three attempts, jittered
  backoff base 0.5 s/cap 8 s, 10-second connect and 120-second read timeouts;
  nontransient errors propagate. Soft-label parsing/provider calls receive three
  attempts, then return a null label.
- **Outputs:** `result.json` with final expression, locked agreement, elites,
  history, synthesized-op count and audit event count; `metric.db` with ops,
  evaluation traces, lifecycle state and append-only audit. Detector terminals
  are `CLEAN`, `DRAWBACK`, `ABSTAIN`; all-abstain does not pass. There is no
  native P5 class or typed `CANNOT_CHECK`.

### Required P5 adapter

Freeze solver code, prompt, provider/model revision, tools and seeds. Evolve the
metric only on development inputs and a development anchor. Because this arm can
change only the evaluator, `EVALUATOR_REPAIR` is its only actionable P5 class;
all non-evaluator or ambiguous cases must be `UNRESOLVED`. A native `DRAWBACK`
must **not** be relabelled automatically as evaluator repair.

The official runner computes and stores `eval_locked` agreement each round,
although it does not use it for selection. That is incompatible with using the
P5 protected final panel inside the loop. The P5 wrapper must substitute a
development-only locked surrogate, freeze the final evaluator artifact, and
have an independent custodian score it exactly once on protected cases without
returning those outcomes to evolution, retry, replacement or arm selection.

## Rejected C5 candidates

1. **RewardHackingAgents** — arXiv `2603.11337v1`,
   [`Yonas650/RewardHackingAgents@9ea7cdc…`](https://github.com/Yonas650/RewardHackingAgents/tree/9ea7cdc8dde6c89b1ea75e2ba86a61ffff72eb34),
   MIT license SHA-256 `fb203ad8909d0b73679cbaf597cfad372addd9cb4df08fe76c03094024c66de0`.
   It is an evaluation-integrity benchmark with locking, patch/access telemetry
   and tamper/leak flags; the evaluator does not evolve. The documented
   `requirements.txt` also omits PyYAML even though `grid_runner.py` imports
   `yaml`, so the documented install is not self-sufficient.
2. **Verifier-as-Gatekeeper** — arXiv `2608.05810v1`. It statically gates an
   evolving skill pool using schema, A–B replay, semantic review and marginal
   subset selection. The gate is not the evolving object, and the primary paper
   exposes no official code/revision/licence/entrypoint.
3. **Ratchet** — current paper `2605.22148v3`,
   [`amazon-science/Self-Evolving-Agents-Ratchet@4401662e…`](https://github.com/amazon-science/Self-Evolving-Agents-Ratchet/tree/4401662ef477b8957580263323bc56d0c8fbf40a),
   Apache-2.0. Its README says it assumes a reliable metric; the **skill bank**
   evolves. It is useful for another comparator role, not C5. Its linked Double
   Ratchet repository supplies the exact metric-only arm selected above.

## Rights boundary and final verdict

ADIAS source is restricted CC BY-NC-SA; its root licence does not relicense
HyperAgent or the acknowledged Tau-bench, ALFWorld, ScienceWorld, TextCraft and
WebShop assets. Double Ratchet code is Apache-2.0, but its referenced/fetched
datasets, hosted services and P5 panel need separate content-class rights and
service agreements.

**Cross-slot terminal:**
`P5_C4_C5_IDENTITIES_BOUND__EXECUTION_READY_EIGHT_CLASS_PROTECTED_ADAPTERS_CANNOT_CHECK`.
H1–H4 and protected freshness remain `CANNOT_CHECK`.

Machine-readable detail, evidence quotes, entrypoints, envelopes and hashes are
in `RESEARCH_ISSUE_EVALUATOR.json`.

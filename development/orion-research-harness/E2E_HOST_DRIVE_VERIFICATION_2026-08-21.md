# ORION Research Harness — full host-driven E2E verification

Date: 2026-08-21
Verifying session: Claude Code (claude lane), branch `claude/orion-harness-verification-b17qdj`
Harness head: `main@d7312bc` (merge of PR #728)
Environment: Python 3.11.15, fresh `uv` venv, `pip install -e '.[dev]' -e 'packages/orion-research-harness[dev]'`

## Claim verified

A tool-capable host session (here: Claude Code acting as the external host) can drive the
canonical `OrionRuntime` through `orion-research-harness` end to end: every CLI command, every
implemented capability kind, the deterministic-replay guarantee, and both orchestration failure
lanes behave exactly as documented in `packages/orion-research-harness/README.md`.

This is an orchestration/engineering verification. It makes no claim about scientific closure
of any research programme.

## Ground truth established first

- Capability kinds are plain strings, not an enum. Broker-mediated kinds are validated in
  `src/orion_research_harness/broker.py`: `LLM_COMPLETE` (L96), `WEB_SEARCH` (L134),
  `VERIFY_EVIDENCE` (L192, a pass requires ≥1 certificate id). Local kinds are the
  `_LOCAL_CAPABILITIES` set in `local_tools.py` L12–18: `FILE_READ`, `FILE_WRITE`,
  `FILE_LIST`, `SHELL`, `PYTHON`.
- `GITHUB` appears only in the `cli.py` handoff text (L52); it is documentation-only surface
  with no implementation and no test.
- Test suite: **30/30 passed** (`pytest packages/orion-research-harness/tests`, 3.78s).

## Step-by-step drive (each step observable in the receipts workspace)

Workspace: scratch `.research` with `--project-root <ORION checkout> --allow-process-tools`.
Session: `session:7b2d750debcd46c4b7c723ed7be6bf42`. The complete receipt tree (26 requests,
25 results, 3 problems, runs and notes) is archived next to this file under
`e2e-2026-08-21-receipts/`.

| Step | Command / capability | Observed | Expected per README | OK |
|---|---|---|---|---|
| 1 | `init` (with `--allow-process-tools`) | `ORION.ResearchHarnessSession.v2`, session digest written | session receipt | ✓ |
| 2 | `problem-add` + `problems` | problem receipt saved, listed | — | ✓ |
| 3 | `solve` (1st) | `PENDING_CAPABILITY`, `LLM_COMPLETE plan_search` request, **exit 2** | exit 2 on pending | ✓ |
| 4 | `pending`, `show-request`, `handoff` | pending list, full payload, host-protocol prompt | — | ✓ |
| 5–8 | ingest `plan_search` (3 route families), then 3× `WEB_SEARCH` serviced with repo-grounded items | each ingest advances replay to the next request; earlier answers never re-asked | deterministic replay | ✓ |
| 9–14 | 3× (`LLM_COMPLETE interpret` → `VERIFY_EVIDENCE`) | each contribution verified against its source item; passes carry real certificate ids | fail-closed verification contract | ✓ |
| 15 | `LLM_COMPLETE reconstruct` | summary absorbed | — | ✓ |
| 16–19 | iteration 2: `plan_search` (FRESHNESS route) → `WEB_SEARCH` (git-log evidence) → `interpret` → `VERIFY_EVIDENCE` | route-kind coverage tracked in solver state (`covered_route_kinds` grows) | independent route families | ✓ |
| 20 | `reconstruct` round 2 | — | — | ✓ |
| 21 | iteration 3: `plan_search` answered `{"queries":[]}` | `COMPLETE`, **exit 0**, `solution_status: CANNOT_CHECK`, answer records open saturation coordinates; 4 evidence ids bound; operator sequence `RECURSE→FRAME→SEARCH→ABSORB→RECONSTRUCT→DETECT→…→SATURATE_BOUNDED` ×3 | completed terminal (incl. CANNOT_CHECK) exits 0 | ✓ |
| 22 | `solve` again (replay), `runs`, `show-run` | full re-run from receipts with **zero** new host requests; run persisted with trace, state snapshot, experience episodes | replay + persistence | ✓ |
| 23 | `request-tool` + `service-local` for `FILE_LIST`, `FILE_READ` (bounded), `FILE_WRITE`, `SHELL` (argv, `sandboxed:false` recorded), `PYTHON` | all five serviced, exit 0 | local capability contracts | ✓ |
| 24a | `FILE_READ` with `../../etc/hostname` | `PermissionError: path is outside project root`, `service-local` **exit 3** | path containment, exit 3 on local failure | ✓ |
| 24b | re-ingest identical result | idempotent accept | idempotency | ✓ |
| 24c | re-ingest different content for same request | `ValueError: result already exists with different content or executor` | tamper rejection | ✓ |
| 25 | second problem; ingest `--error "Simulated host outage"`; `solve` | `HOST_CAPABILITY_FAILED`, **exit 3**; failure stays an orchestration condition, not scientific failure evidence | exit 3 lane | ✓ |
| 26 | third problem; `ingest --file` variant | accepted, replay advances, exit 2 on next pending | `--file` = `--json` path | ✓ |

## Honest solver observation (not a defect)

With the default `--max-iterations 3`, a fully serviced run terminates `CANNOT_CHECK`
("Resource bound reached before bounded saturation") rather than a verified positive answer,
because bounded saturation legitimately does not certify flatness after three iterations.
The harness treats this as a completed ORION terminal (exit 0), exactly as the README states.
Hosts wanting a saturated terminal should raise `--max-iterations`.

## Feature-coverage ledger

- CLI commands exercised: `init`, `problem-add`, `problems`, `solve` (incl. `--max-iterations`
  default; `--allow-provisional` exists and is exercised by `test_harness.py`), `pending`,
  `show-request`, `ingest` (`--json`, `--file`, `--error`, `--executor`), `request-tool`,
  `service-local` (all + single-request form exists), `runs`, `show-run`, `handoff` — 12/12.
- Capability kinds exercised live: 8/8 (`LLM_COMPLETE`, `WEB_SEARCH`, `VERIFY_EVIDENCE`,
  `FILE_READ`, `FILE_WRITE`, `FILE_LIST`, `SHELL`, `PYTHON`).
- Exit codes observed: 0 (complete terminal), 2 (pending capability), 3 (host capability /
  local service failure) — matching the documented contract.
- Test suite: 30/30 green in the same environment.

## Verdict

`orion-research-harness` at `d7312bc` is fully drivable end-to-end by this Claude Code session
(and by construction by any host following `HOST_PROTOCOL.md` / `handoff` output, including a
ChatGPT session). No contract deviation found.

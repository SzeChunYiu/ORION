# ORION Research Harness

`orion-research-harness` makes the **canonical ORION runtime** usable from a local research folder while a tool-capable host (ChatGPT, Codex, Claude Code, an API agent, or a human operator) supplies capabilities that ORION core intentionally does not own.

The harness does **not** replace ORION with a prompt or doctrine. `OrionRuntime` remains the scientific control kernel. The harness adds a replayable host-capability boundary around it.

## Why this exists

ORION core already has provider-neutral LLM, retrieval and verification ports, recursive state/reasoning mechanics, evidence authority, residual diagnosis, reframing and bounded saturation. A web ChatGPT session may additionally have current web search, GitHub access, Python and file/shell tools. Those host abilities should be integrated as explicit, auditable capabilities rather than smuggled through free-form model text.

The harness therefore uses this loop:

```text
Problem
  -> canonical OrionRuntime
  -> provider needs host capability
  -> deterministic capability request + receipt file
  -> external ChatGPT / Claude / Codex / local tool services request
  -> digest-bound result receipt
  -> deterministic replay
  -> next capability request OR complete ORION result
```

A missing, failed, or malformed host capability is deliberately raised outside ORION's normal `Exception -> scientific failure evidence` path. Missing web/API access, a failed external command, or an invalid host response is an orchestration condition, not evidence that SEARCH, ABSORB, verification, or another scientific mechanic failed.

## Install from the ORION checkout

```bash
git clone https://github.com/SzeChunYiu/ORION.git
cd ORION
python -m pip install -e '.[dev]'
python -m pip install -e 'packages/orion-research-harness[dev]'
```

No OpenAI, Anthropic, search, GitHub, or other credentials are embedded.

## Start a research workspace

```bash
orion-harness init .research --project-root .
orion-harness problem-add .research p1 \
  "Determine the strongest defensible P1 reformulation-superiority result" \
  --scope "Use the registered P1 scientific programme and preserve all historical negatives." \
  --domain scientific-methodology \
  --criterion "Do not weaken frozen baselines or superiority margins."
```

Then:

```bash
orion-harness solve .research p1
```

If ORION needs a capability that the process cannot supply, it returns `PENDING_CAPABILITY` and writes a request under:

```text
.research/.orion-harness/requests/
```

Inspect it:

```bash
orion-harness pending .research
orion-harness show-request .research hostreq:...
```

`orion-harness solve` returns exit code `2` for `PENDING_CAPABILITY` and exit code `3` for `HOST_CAPABILITY_FAILED`. Completed ORION terminals, including legitimate `BLOCKED` or `CANNOT_CHECK` scientific outcomes, return exit code `0` because the orchestration itself completed correctly.

## Service with another ChatGPT / Claude session

Generate a handoff prompt:

```bash
orion-harness handoff .research
```

Give that output and the repository/workspace to another tool-capable session. The host services the pending request using its real capabilities and ingests a structured result.

### `LLM_COMPLETE`

Result shape:

```json
{
  "content": "{\"queries\":[]}",
  "model_id": "gpt-or-claude-model",
  "response_id": "optional"
}
```

`content` must be a string and must itself follow the JSON schema requested by ORION. A malformed successful receipt is surfaced as `HOST_CAPABILITY_FAILED`; it is never converted into scientific failure evidence.

### `WEB_SEARCH`

The host should use current web search and inspect authoritative/primary sources as needed.

```json
{
  "items": [
    {
      "content": "Source-grounded text useful to ORION.",
      "source_uri": "https://example.org/source",
      "item_id": "optional-stable-id",
      "domain_ids": ["optional-domain"]
    }
  ]
}
```

Ingest:

```bash
orion-harness ingest .research hostreq:... \
  --executor "chatgpt-web" \
  --json '{"items":[...]}'
```

Web items require non-empty string content/source identities and array-valued domain IDs. Invalid host shapes fail at the host boundary rather than inside the scientific solver.

### `VERIFY_EVIDENCE`

Verification is independent and fail-closed:

```json
{
  "passed": true,
  "certificate_ids": ["certificate:source-check:..."],
  "reason": "The retrieved item directly supports the contribution."
}
```

`passed` must be a JSON boolean. A passing verification requires at least one non-empty certificate ID because canonical ORION requires certificate-producing evidence for verified authority. A string such as `"false"` is rejected rather than coerced to a truthy value.

After ingestion, rerun the exact same solve command. Existing request/result receipts are replayed, so execution advances to the next missing capability without changing earlier answers.

## Local capabilities

The harness can directly service:

- `FILE_READ`
- `FILE_WRITE`
- `FILE_LIST`
- `SHELL`
- `PYTHON`

File operations resolve paths under the workspace's configured `project_root` and reject paths that escape it. `FILE_READ` reads only the requested bounded prefix (maximum 1,000,000 characters). `FILE_LIST` fails closed when a directory exceeds 10,000 entries rather than materializing an unbounded listing.

`SHELL` and `PYTHON` are different: a normal subprocess is **not an OS sandbox** and can access anything available to the current OS user. They are disabled by default. To opt in explicitly:

```bash
orion-harness init .research --project-root . --allow-process-tools
```

`SHELL` uses an argv list and never `shell=True`; process timeouts are capped at 120 seconds. On POSIX, the harness starts a separate process session and kills that process group on timeout. Stdout and stderr are continuously drained while retaining at most 100,000 bytes of each in memory, so large output or descendant-held pipes cannot turn the harness into an unbounded buffer. The returned receipt explicitly records `sandboxed: false`.

Create a local request:

```bash
orion-harness request-tool .research PYTHON \
  --json '{"code":"print(2+2)","cwd":"."}'
orion-harness service-local .research
```

`service-local` returns exit code `3` if any serviced local request records failure.

Web, GitHub and model calls remain external-host capabilities so this package does not pretend it possesses credentials or network tools that only the surrounding agent/session has.

## Persistence and receipts

The workspace records:

```text
.orion-harness/
  session.json
  problems/
  requests/
  results/
  runs/
  notes/
```

Capability request IDs are deterministic for `(session, capability, payload)`. Request and result files carry SHA-256 content digests. A result is bound to the exact request digest. These digests are tamper-evidence/content binding; they are **not cryptographic signatures or proof of host identity**.

Immutable JSON records are fully written and fsynced to a same-directory temporary file before an atomic create-if-absent publication. Concurrent hosts therefore cannot replace an already published deterministic request/result identity or expose a partially written receipt. Re-ingesting the exact same result from the same executor is idempotent; different content, success/error state, or executor identity is rejected.

Receipt deserialization is strict and non-coercing. Boolean, string, object and digest fields must have their declared types; malformed receipt types fail validation rather than being silently converted.

Completed ORION runs persist the problem, solution, final K/W/M state snapshot, trace, operator sequence, root/mechanic experience IDs and recorded experience episodes.

## Research-program use

This package is intended to become the common local instrument for P1–P10 and ORION-Q work:

1. run research through canonical ORION;
2. let the surrounding agent supply web/GitHub/code capabilities through receipts;
3. preserve negative results and unresolved residuals;
4. diagnose whether failures belong to search, representation, execution, measurement, evaluator, method, question/boundary or evidence;
5. improve the harness/framework on separate protected branches;
6. rerun prospectively frozen scientific campaigns without post-outcome weakening.

This creates a useful feedback loop: **study the P1–P10 science with ORION while the same instrumented work exposes what ORION itself still lacks.**

## Current claim boundary

This is an engineering integration package. Its existence does not prove autonomous-research superiority, P1–P10 closure, or Self-ORION readiness. Host tools remain externally controlled, and ORION's scientific authority rules remain in force.

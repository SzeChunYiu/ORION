# ORION Research Harness — development packet

Issue: #725  
Branch: `shadow/orion-web-research-harness-20260820`  
Base: `main@1e462d16b006130c5ba93e3fe91635c5d47a55a5`

## Problem

Canonical ORION is provider-neutral but intentionally does not own a vendor model, live web search, GitHub session, shell, Python runtime or local file tools. ChatGPT/Codex/Claude sessions often possess exactly those capabilities. Without an explicit bridge, research is manually orchestrated around ORION or host tools get smuggled through free-form LLM text, undermining provenance and making the system difficult to use across sessions.

## Change

Add an independently installable `packages/orion-research-harness` package.

The harness:
- instantiates canonical `OrionRuntime`;
- supplies broker-backed LLM/retrieval/verification providers;
- converts missing external capability into a deterministic host request;
- lets that request escape the solver's ordinary `Exception -> scientific failure evidence` boundary using a dedicated `BaseException` control signal at the composition boundary;
- stores request/result receipts with content digests;
- deterministically replays completed capability calls;
- persists problems, completed ORION results, full final-state/trace snapshots and experience records;
- provides a CLI and ChatGPT/Claude handoff protocol;
- provides project-root-confined file operations plus explicitly opt-in local Python/subprocess execution.

## Why the BaseException control signal is necessary

`OrionSolver._attempt_mechanic` intentionally catches `Exception` and converts operator failures into evidence. A missing external web/model/tool service is not a scientific operator failure. If a broker raised `Exception`, ORION would incorrectly learn an operator failure from orchestration unavailability.

`HostCapabilityRequired(BaseException)` crosses only the local composition boundary. `run_problem` catches it immediately, writes/returns the already persisted request, and stops. On replay, a validated result satisfies the same deterministic request and canonical ORION continues normally.

This mechanism grants no scientific authority and is not registered as an ORION mechanic.

## Authority and safety

- Host output is provider input, not authority.
- Verification remains a separate broker capability.
- Passing `VerificationResult` still requires certificate IDs.
- Local file operations resolve under the configured project root and reject escapes.
- `SHELL` / `PYTHON` are disabled by default and require explicit workspace opt-in.
- Process tools are **not an OS sandbox** and may access anything available to the current OS user; receipts state `sandboxed: false`.
- Shell commands use argv and never `shell=True`; timeouts are capped.
- Host-tool failures remain host receipts; they are not silently converted into scientific facts.
- No credential storage or vendor SDK dependency is added.

## Validation

Dedicated tests cover:
- deterministic request identity;
- request/result digest binding and tamper rejection;
- persistent problems and session replay;
- project-root path confinement;
- broker LLM/web conversion;
- canonical `OrionRuntime` smoke execution across multiple pending capability requests;
- preservation of BLOCKED/CANNOT_CHECK rather than forced success.

## Claim boundary

This is engineering infrastructure. It does not establish P1–P10 scientific superiority, autonomous research reliability, or governed Self-ORION readiness. Those remain separate evidence programmes.

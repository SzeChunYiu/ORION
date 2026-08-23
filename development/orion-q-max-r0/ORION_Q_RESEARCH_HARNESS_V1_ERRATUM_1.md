# ORION-Q Research Harness V1 — Erratum 1: converge on shared harness package

Date: 2026-08-20
Branch: `shadow/orion-q-max-r0`
Parent protocol: `ORION_Q_RESEARCH_HARNESS_V1_PROTOCOL.md`
Status: frozen immediately after discovering the peer harness branch and before the shared-package ORION-Q adapter is implemented.

## Reopen trigger fired

The parent protocol explicitly required reopening if a production/peer ORION module already owned a material part of the proposed harness responsibility.

Repository branch search found:

- `shadow/orion-web-research-harness-20260820`, 11 commits ahead of its main base, adding `packages/orion-research-harness/`;
- stale `shadow/p9-m0-task-harness-20260818`, currently behind main with no unique current diff;
- `claude/p2-harness-wip-refactor`, an older/diverged P2 benchmark harness rather than the current general host bridge.

The web-research harness is the stronger architectural incumbent. It already provides:

- a standalone `orion-research-harness` package;
- canonical `OrionRuntime` execution rather than a prompt-level imitation;
- deterministic host capability request/result receipts;
- replayable research workspaces;
- explicit host LLM/search/verification brokers;
- confined local FILE/SHELL/PYTHON tools;
- CLI/handoff flow for ChatGPT/Claude/Codex/human hosts;
- an explicit claim boundary that host tools do not grant scientific authority.

Therefore the original ORION-Q implementation hypothesis of a separate engine at `research/extensions/orion-q/harness/` is **withdrawn**.

## Corrected implementation hypothesis

Canonical home:

`packages/orion-research-harness/`

Shared generic responsibilities remain at package root. Domain/campaign adapters live below the same package, initially:

`src/orion_research_harness/domains/orion_q/`

ORION-Q may add only responsibilities missing from the shared harness:

1. typed multi-cycle scientific campaign state;
2. native Self-ORION responsibility/interface/revision/computation adapter;
3. capability registry binding native selected action/revision IDs to auditable host/local capabilities;
4. protected-reference custody/release gates;
5. evidence extraction/admission rules;
6. cycle transition/replay receipts;
7. ORION-Q MAX R6 campaign manifest.

The ORION-Q adapter must reuse the shared `CapabilityRequest`, `CapabilityResult`, `ResearchWorkspace`, broker and host-boundary conventions rather than creating incompatible duplicates.

## Peer provenance / lane boundary

The source branch remains read-only to this session per `AGENTS.md`. Its package files are absorbed into `shadow/orion-q-max-r0` with attribution through this erratum; the peer branch is not modified, rebased or force-updated.

## Temporary duplicate files

Any already-created `research/extensions/orion-q/harness/*` files are scaffolding from the superseded hypothesis. They grant no authority and must be removed once their useful state/receipt ideas are represented under the shared package.

## Strengthened hostile gates

In addition to the parent tests:

- no second `CapabilityRequest` / `CapabilityResult` protocol is allowed under ORION-Q;
- no second research workspace layout is allowed;
- domain adapters cannot bypass the shared broker/result receipt boundary for external tools;
- generic harness changes needed by ORION-Q must be domain-neutral and regression-tested against the original web-research use case;
- ORION-Q-specific code may not be imported by the generic runner/broker unless through a plugin/adapter boundary;
- peer harness behavior must remain usable without installing quantum dependencies;
- same workspace may contain both generic ORION problems and named scientific campaigns without receipt namespace collisions.

## Scientific interpretation

This correction is itself evidence that the harness is beginning to improve through ORION-style failure/reopen discipline: the duplicate architecture was detected before it became the canonical runtime. It is an engineering correction, not scientific R6 evidence.

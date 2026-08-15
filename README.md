# ORION

ORION is an evidence-governed recursive research operating system descended from the RAKL project.

Its fundamental machinery is not a fixed list of research tricks. ORION repeatedly **searches, absorbs, reconstructs, detects residuals, diagnoses responsibility, reframes the responsible layer, reopens dependent work, and searches again**. The same machinery can be applied to ORION itself under stricter self-development governance.

```text
FRAME
  -> SEARCH
  -> ABSORB
  -> RECONSTRUCT
  -> DETECT
  -> DIAGNOSE
  -> REFRAME
  -> REOPEN
  -> RECURSE
  -> BOUNDED SATURATION
```

ORION deliberately absorbs knowledge from any relevant discipline. External disciplines remain contextual projections rather than authorities over the whole system; ORION maps their concepts, assumptions, evidence and failure modes into a provenance-preserving global portrait and may derive its own representation when the synthesis warrants it.

## Current bootstrap status

**MINIMUM_KERNEL_LLM_INTEGRATION_READY.** The current branch contains a modular solver, provider-neutral LLM/retrieval/verification ports, bounded-saturation gating, a known-world recursive solve benchmark, development-governance checks, and a synchronized framework-paper tree.

This is not a claim that general autonomous research is solved. Live-provider reliability, open-web literature recall, scientific-language interpretation, route-level stopping, robust global-portrait reconstruction, hostile external benchmarks, and Self-ORION readiness remain open.

## Repository map

```text
docs/
  00-foundation/       invariant principles and constitutional boundaries
  01-engine/           recursive epistemic reconstruction mechanics
  02-knowledge/        knowledge absorption and global-portrait mechanics
  03-evaluation/       benchmarks, evidence, authority and falsification
  04-self-development/ governed Self-ORION mechanics
  05-runtime/          LLM/retrieval/verifier integration boundary
development/           ORION-on-ORION development protocol and readiness records
papers/                synchronized framework papers and claim/evidence ledgers
research/
  domains/             recursively organized external-domain research programs
  development/         research used to develop ORION itself
  failures/            failure cases and learned guards
  programs/            cross-domain research programs
src/orion/
  core/                typed K/W/M state and invariant objects
  engine/              recursive operators and solver orchestration
  providers/           replaceable LLM/retrieval/verification ports + adapters
  runtime/             composition root for live integrations
  development/         development-governance contracts
  self_orion/          proposal-only self-development machinery
tests/
  unit/
  integration/
  hostile/
provenance/
  rakl/                migration ledger and immutable source references
```

Every substantial node should recursively own its `README/specification/evidence/benchmarks/history` material rather than scattering one subject across unrelated top-level folders.

## Development phases

1. **LLM-led bootstrap** — build the minimum working ORION consistent with the core principles.
2. **Shadow Self-ORION** — ORION diagnoses itself and proposes improvements while external development remains primary.
3. **Governed Self-ORION** — ORION becomes the primary problem-solving process for ordinary framework development; LLMs become major internal workers/proposers rather than the architecture itself.
4. **Self-sustaining research program** — object knowledge, search-universe knowledge and method knowledge co-evolve under protected evaluation.

The legacy `SzeChunYiu/RAKL` repository remains the provenance source for migrated mechanics, experiments, papers and negative history. ORION is a clean-generation reconstruction, not a history rewrite.

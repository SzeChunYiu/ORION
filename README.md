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

## Repository map

```text
docs/
  00-foundation/       invariant principles and constitutional boundaries
  01-engine/           recursive epistemic reconstruction mechanics
  02-knowledge/        knowledge absorption and global-portrait mechanics
  03-evaluation/       benchmarks, evidence, authority and falsification
  04-self-development/ governed Self-ORION mechanics
research/
  domains/             recursively organized external-domain research programs
  failures/            failure cases and learned guards
  programs/            cross-domain research programs
src/orion/
  core/                typed state and invariant objects
  engine/              reconstruction-cycle execution
  knowledge/           absorption/mapping/global-portrait implementation
  evaluation/          verification and benchmark machinery
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

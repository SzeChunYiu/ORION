# P10 — revision-bound Lean evaluation closure

**Terminal:** `TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME`

P10 is peer-review ready as a bounded technical note and programme evidence
object. It is deliberately **not** a standalone paper. Constructive saturation
found that revision-bound benchmark packaging, native checking, semantic
faithfulness audits and tactic-pattern mining are mature research objects. The
remaining ORION distinction—identity is not correctness and neither is
authority—is already owned by P4/P8.

The canonical reviewer-facing artifact is [`TECHNICAL_NOTE.md`](TECHNICAL_NOTE.md);
the canonical bibliography is [`references.bib`](references.bib).

## Evidence retained

- **Programme-scale source study:** 457 exact files (5,655,364 bytes) from 31
  active top-level Mathlib modules at commit
  `e72c1e277f31441626621f7d0c7207862fc25569` and toolchain
  `leanprover/lean4:v4.34.0-rc1`.
- **Hostile correction:** the first V2 output is permanently invalidated after
  1,289/4,861 projected trajectories crossed an intervening top-level command.
- **Corrected V2.1 result:** 4,825 trajectories and 16,667 projected actions;
  leave-top-module-out Markov accuracy `0.3842` versus unigram `0.2796`, a
  difference of `0.1046` with module-bootstrap 95% interval
  `[0.0863, 0.1223]`. Observed cross-module pattern counts fall in the
  significant lower tail of every frozen null: recurrence is concentrated in
  fewer coarse patterns than chance, not evidence for a new macro library.
- **Native audit:** all eight prospectively selected exact upstream files were
  accepted by Lean 4.34.0-rc1 and the planted invalid proof was rejected. Two
  complete replays were byte-identical (receipt SHA-256
  `1aed4fbfb7e9b83eda08bfe19b4d4348dcdbffba82b1db567d05a61aaa8c5b90`).
  See `results/MATHLIB_NATIVE_RECEIPTS_V1.json`.
- **Mutation control:** source revision, dependency snapshot, source bytes,
  statement and attempt substitutions invalidate typed receipts; a task-id-only
  control silently reuses a stale result.

## Explicit nonclaims

P10 does not claim novelty for theorem-proving benchmarks, tactic prediction,
proof-pattern mining, premise retrieval, repository tracing, native checking or
autoformalization. Source hashing establishes identity only. Lean acceptance
does not establish statement faithfulness, scientific truth or authority.
Those meaning/authority judgments remain `CANNOT_CHECK` from P10's identity and
native-acceptance receipts alone.

The missing `HF_MATHLIB_TACTICS_SAMPLE.json` is not reconstructed or guessed.
The old Phase-2B goal-effect question is formally removed from this technical
note and retained only as a triggered follow-up in `FOLLOW_UPS.md`.

## Reproduce

Run `python3 check_technical_note_ready.py`. Full environment-specific replay
commands and exact artifact digests are in `JOURNAL_READINESS.md`.

# ORION-20 technical-note readiness — 2026-08-18

ORION-20 is targeted at **peer-review-ready merged technical evidence**, not a
standalone submission. Standalone-only venue, cover-letter and PDF gates are
routed to the ORION-14/ORION-18 manuscript that adopts the note.

| Gate | Receipt | Status |
|---|---|---|
| Exact public source | Mathlib commit/toolchain, 457 files, licenses and SHA-256 manifest | `PASS` |
| Prospectively frozen protocol | V2 commit preceded outcome; V2.1 amendment preceded repaired outcome | `PASS` |
| Hostile invalidation | Contaminated V2 retained with quantified failure | `PASS` |
| Corrected result | JSON/Markdown and full null distributions | `PASS` |
| Determinism | Two V2.1 runs byte-identical: result `bd3b27849b31b93c0dc7bfe28f5984fac6888aa54141170c3d47999d67cbc24e`; nulls `8089095959819a9f530a40540dd2580ba3495294f16a1fe9bcaec4a1916f16f2` | `PASS` |
| Native audit protocol | Outcome-blind eight-file stratified sample; exact runtime and negative control | `PASS_FROZEN` |
| Native receipts | Eight exact files accepted; planted invalid proof rejected; receipt `1aed4fbfb7e9b83eda08bfe19b4d4348dcdbffba82b1db567d05a61aaa8c5b90` | `PASS` |
| Native determinism | Two complete replays byte-identical | `PASS` |
| Mutation controls | Statement/revision/source/attempt substitutions plus task-id-only control | `PASS` |
| Constructive saturation | Twelve primary/official donors; extraction plus adoption/defer receipt | `PASS_BOUNDED` |
| No-material-change rounds | Two post-stabilization confirmation rounds | `PASS_BOUNDED` |
| Strong tactic-mining baseline | TacMiner-class graph/state baseline on identical corpus | `NOT_RUN`; blocks standalone macro novelty only |
| Phase 2B input | Missing `HF_MATHLIB_TACTICS_SAMPLE.json` | `REMOVED_FROM_NOTE`; follow-up trigger retained |
| Canonical reviewer artifact | `TECHNICAL_NOTE.md`, `CLAIM_LEDGER.md`, `references.bib` | `PASS` |
| Independent paper residual | Mature benchmark/tactic/faithfulness objects; remaining boundary owned ORION-14/ORION-18 | `NO_STANDALONE_RESIDUAL` |
| Standalone venue/template/cover letter/PDF | No standalone manuscript by terminal decision | `N/A_ROUTED_TO_P4_P8` |

## Reproduction

From the repository root:

```bash
python3 papers/candidates/paper-10-content-bound-math-evaluation/check_technical_note_ready.py
```

Native replay additionally requires the exact Mathlib checkout and Lean
toolchain. The recorded command is:

```bash
python3 papers/candidates/paper-10-content-bound-math-evaluation/benchmark/run_native_verification_v1.py \
  --mathlib-checkout /path/to/mathlib4 \
  --lake /path/to/lean-4.34.0-rc1/bin/lake \
  --runtime-adapter /path/to/orion_p10_readlink_self.so
```

The reported runtime is `Lean 4.34.0-rc1`, x86-64 Linux, release commit
`3447a668783dbce1a8fdb97101dd067687b2b418`. The adapter is sandbox
compatibility only. Its committed source digest is
`6914047c0aba5df1ac8d347adf70c02d1d2f62d87398a88306bb5ff10f94abe5`;
the receipt records binary digest
`cd7d3f44759a9c87d67e38514784c140212dda97fe2751d2d671739999641f68`.

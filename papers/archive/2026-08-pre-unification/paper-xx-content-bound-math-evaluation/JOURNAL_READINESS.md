# P10 technical-note readiness — 2026-08-20

P10 is currently targeted at **peer-review-ready bounded technical evidence**. The completed source-transfer result is independently reviewable; stronger native-state, tactic-library and prover-utility claims remain separate prospective expansions and cannot delay or inflate the completed bounded note.

| Gate | Receipt | Status |
|---|---|---|
| Exact public source | Mathlib commit/toolchain, 457 files, licenses and SHA-256 manifest | `PASS` |
| Prospectively frozen protocol | V2 commit preceded outcome; V2.1 amendment preceded repaired outcome | `PASS` |
| Hostile invalidation | Contaminated V2 retained with quantified failure | `PASS` |
| Corrected result | JSON/Markdown and full null distributions | `PASS` |
| Determinism | Two V2.1 runs byte-identical: result `bd3b27849b31b93c0dc7bfe28f5984fac6888aa54141170c3d47999d67cbc24e`; nulls `8089095959819a9f530a40540dd2580ba3495294f16a1fe9bcaec4a1916f16f2` | `PASS` |
| Cross-module breadth/sensitivity | 24/26 positive evaluable modules; exact sign-test `p=1.049e-5`; leave-one-module-out pooled lift `[0.1005,0.1092]`; durable receipt bound to exact-head workflow artifact | `PASS_POST_HOC` |
| Native audit protocol | Outcome-blind eight-file stratified sample; exact runtime and negative control | `PASS_FROZEN` |
| Native receipts | Eight exact files accepted; planted invalid proof rejected; receipt `1aed4fbfb7e9b83eda08bfe19b4d4348dcdbffba82b1db567d05a61aaa8c5b90` | `PASS` |
| Native determinism | Two complete replays byte-identical | `PASS` |
| Mutation controls | Statement/revision/source/attempt substitutions plus task-id-only control | `PASS` |
| Constructive saturation | Twelve primary/official donors; extraction plus adoption/defer receipt | `PASS_BOUNDED` |
| No-material-change rounds | Two post-stabilization confirmation rounds | `PASS_BOUNDED` |
| Strong tactic-mining baseline | TacMiner-class graph/state baseline on identical corpus | `NOT_RUN`; blocks standalone tactic-library novelty only |
| Native-state incremental-value experiment | Frozen B1–B5 protocol, no outcome yet | `PROSPECTIVE_NOT_CLAIMED` |
| Verifier-backed proof-search utility | Frozen follow-on route; no outcome yet | `PROSPECTIVE_NOT_CLAIMED` |
| Phase 2B input | Missing `HF_MATHLIB_TACTICS_SAMPLE.json` | `REMOVED_FROM_NOTE`; follow-up trigger retained |
| Canonical reviewer artifact | `TECHNICAL_NOTE.md`, `CLAIM_LEDGER.md`, `references.bib`, module-robustness receipt | `PASS` |
| Independent standalone residual | Mature benchmark/tactic/faithfulness objects constrain novelty; bounded source-transfer/evaluation residual survives, larger tactic/prover novelty requires new experiments | `PASS_BOUNDED` |

## Strongest completed result

On the exact frozen source projection, leave-top-module-out Markov accuracy is `0.3842` versus `0.2796` for the pooled unigram comparator, difference `+0.1046`, with module-bootstrap 95% interval approximately `[0.0863,0.1223]`.

The post-hoc block-receipt audit shows that this is not a single-module pooled artifact: 24/26 positive-transition held-out modules have positive deltas, the median module lift is `+0.1048`, and removing any one evaluable module leaves the pooled effect above `+0.1005`. Two negative modules (`Control`, `CategoryTheory`) remain visible.

These breadth numbers refine the robustness description of the frozen source result. They do not become a native proof-state or proof-search claim.

## Reproduction

From the repository root:

```bash
python3 papers/candidates/paper-10-content-bound-math-evaluation/check_technical_note_ready.py
python3 papers/candidates/paper-10-content-bound-math-evaluation/analyze_module_robustness_v1.py
```

Native replay additionally requires the exact Mathlib checkout and Lean toolchain. The recorded command is:

```bash
python3 papers/candidates/paper-10-content-bound-math-evaluation/benchmark/run_native_verification_v1.py \
  --mathlib-checkout /path/to/mathlib4 \
  --lake /path/to/lean-4.34.0-rc1/bin/lake \
  --runtime-adapter /path/to/orion_p10_readlink_self.so
```

The reported runtime is `Lean 4.34.0-rc1`, x86-64 Linux, release commit `3447a668783dbce1a8fdb97101dd067687b2b418`. The adapter is sandbox compatibility only. Its committed source digest is `6914047c0aba5df1ac8d347adf70c02d1d2f62d87398a88306bb5ff10f94abe5`; the receipt records binary digest `cd7d3f44759a9c87d67e38514784c140212dda97fe2751d2d671739999641f68`.

## Terminal boundary

The completed bounded note is reviewable on its own. `P10_NATIVE_STATE_INCREMENTAL_VALUE_PROTOCOL_V1.md` and later invariant-state/search protocols are claim-expansion experiments, not supporting results until executed. A null result there leaves the completed source-transfer evidence intact and blocks only the corresponding higher claim rung.

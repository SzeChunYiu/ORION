# Reproduction

Exact commands to reproduce what this package claims, from the committed
evidence, plus an explicit statement of what it does **not** reproduce and why.
"Could not check" and "checked and fine" are kept strictly apart.

All commands run from `packages/typed-merge-evaluator/`. Python 3.9+ and
`pytest` are the only requirements; no network access, no Rust, no Lean, no
OpenSSL build.

## 1. Everything at once

```bash
python -m pytest tests/test_typed_merge_evaluator.py -v
```

Expected: **32 passed**. No test is skipped when the `papers/` evidence tree is
present; skips mean the evidence was not found, which is a `CANNOT_CHECK`, not
a pass.

## 2. Evaluate every shipped instance

```bash
python -m typed_merge_evaluator examples/cedar-multipolicy/*.json \
                                examples/x509-truststore/*.json \
                                examples/manuscript-cases/*.json
```

Expected: 13 `PASS` lines, exit code 0. Exit 1 means an instance evaluated but
a declared expectation failed; exit 2 means an instance could not be read,
parsed or validated.

## 3. Regenerate the examples from their sources

```bash
python examples/build_examples.py
git diff --stat -- examples/
```

Expected: no diff. The record sets are transcribed from
`rust-adjudicator/src/main.rs` and the expectations from the committed
receipts, so a drift here means the encodings no longer match the artifacts
they claim to encode.

## 4. Round 1 — Cedar multi-policy

### REPRODUCED EXACTLY (no toolchain needed)

```bash
python -m pytest tests/test_typed_merge_evaluator.py \
  -k "round1_eight_controls or round1_receipt_digests" -v
```

- **The eight origin-witness controls.** Both the inputs and the expected
  outputs are committed: record sets in
  `evidence/round1-cedar-multipolicy/rust-adjudicator/src/main.rs`, expected
  `(flat, typed)` pairs in `RUST_ADJUDICATION_V1.json`. The packaged evaluator
  reproduces all 8 pairs exactly.
- **Round-1 receipt digests.** The four receipts named in
  `ROUND1_RESULTS_V1.json` still hash and size-match their recorded values.

Three of the four Lean theorems are also reproduced as computations rather than
proofs: `two_origin_flat_but_not_typed` and `alternative_complete_origin_is_typed`
are the `spliced_foreign_origin_requirements` and `alternative_complete_origin`
instances; `unsupported_positive_cycle_is_empty` is
`unsupported_positive_cycle.json` and `test_unsupported_cycle_cannot_self_authorize`.
A computation agreeing with a theorem is not a proof of it.

### CANNOT CHECK here (missing toolchain, not missing data)

| Item | Blocker |
|---|---|
| Native Cedar: 5 fixtures, 15 requests, decision/reason/error/validation exact | needs a Rust toolchain plus `cedar-policy/cedar-integration-tests` @ `75989795c75d861270ce6cac38ef9d9e5b220a0c` and Cedar @ `bcb8bd93a292b59ae8f1dcf53b9b4176a2d3405d` |
| `typed_implies_flat` as a *proof* | needs `leanprover/lean4:v4.33.1` |

To run them, build `evidence/round1-cedar-multipolicy/rust-adjudicator` and
`lake build` in `evidence/round1-cedar-multipolicy/lean`.

## 5. Round 2 — X.509 trust-store merge

### REPRODUCED EXACTLY (no toolchain needed)

```bash
python -m pytest tests/test_typed_merge_evaluator.py \
  -k "round2" -v
```

- **`C6-HOSTILE-SPLIT`.** The one committed hybrid recorded
  `structural_kind: "STRUCTURAL"`. Its committed decisions
  (`M1_FLAT_UNION: true`, `M5_TYPED_WITNESS: false`, `hybrid: true`, and
  `vA/vB/vU = false/false/true`) are reproduced exactly by the structural
  encoding, with no engine invocation.
- **Source-binding digests.** 268 digests in `SOURCE_BINDING_V2.json`
  (252 vendored certificates + 1 recipe + 5 frozen artifacts + 10 results
  artifacts) verify against the committed bytes.
- **Aggregate algebraic consistency.** Family hybrid counts sum to 46, task
  counts to 1962, `M1.unsafe_merges == engine_hybrids` and
  `M5.allows == parent_authorized` per family.

### CANNOT CHECK here (missing data *and* missing toolchain)

| Item | Blocker |
|---|---|
| The 1962-task aggregate counts (unsafe/needless per method) | requires a pinned OpenSSL 3.6.4 build from tarball sha256 `9bffaa1a…3ef`; `repro_independent.py` checks the engine version string and refuses anything else |
| Per-task replay of the 46 hybrids | **the per-task verdicts are not committed.** The `hybrid_tasks` records carry only `family`, `first_mixing`, `leaf`, `purpose`, `task_id`; `vA/vB/vU/vI` appear exactly once in `ROUND2_RESULTS_V2.json`, on the C6 control. Membership in `hybrid_tasks` implies the verdict algebra by definition, so nothing independent is verified by re-deriving it |
| C1 anchor control (186/191), C3 (0/1962), C4 (0 resurrections) | engine-computed |

To run them, build OpenSSL 3.6.4 from the pinned tarball and follow
`evidence/round2-x509-truststore/README.md`.

## 6. Verify the digests yourself

```bash
python - <<'PY'
import json, hashlib, pathlib
r2 = pathlib.Path("../../papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore")
b = json.loads((r2 / "SOURCE_BINDING_V2.json").read_text())
tp = r2 / "third_party" / "openssl-3.6.4-testcerts"
ok = bad = 0
for group, root in (("vendored_files", tp), ("vendored_recipe", tp),
                    ("excluded_list", tp), ("frozen_artifacts", r2),
                    ("results_artifacts", r2)):
    for rel, digest in b[group].items():
        actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        ok, bad = (ok + 1, bad) if actual == digest else (ok, bad + 1)
print(f"OK={ok} MISMATCH={bad}")
PY
```

Expected: `OK=269 MISMATCH=0`. (The test suite asserts 268 for the same
binding: it omits the single `excluded_list` entry, which records the exclusion
manifest rather than a vendored input. Both numbers are correct.)

## 7. Determinism of the committed receipts

Round 2 control C2 requires two full runs to produce byte-identical receipts.
Both runs are committed:

```bash
cd ../../papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore
for p in ROUND2_RESULTS_V2 INDEPENDENT_REPRO_R2 COST_ROUND2_V2; do
  cmp -s $p.json $p.run2.json && echo "$p IDENTICAL" || echo "$p DIFFERS"
done
```

Expected: three `IDENTICAL` lines.

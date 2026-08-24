# P3 cross-construct successor handoff

## Exact result

`PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS__PUBLIC_V3_NO_HARM_SUPERIORITY__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY`

- Full input-only universe: **193,305** cases.
- Cross-construct cases: **125,262**.
- Licensed binary scorable census: **117,914**.
- `CANNOT_CHECK`: **75,391**.
- Binary reference coverage: **1,399/1,399**.
- Non-binary pairs mapped to `CANNOT_CHECK`: **35/35**.
- Maximal binary envelope coverage: **1.0**.
- Information-equivalent ideal: exact tie.
- Candidate-minus-AML harm: **+0.224799430093**, **+0.224731584036**,
  **+0.193522397680**.

The coverage mechanics pass is therefore not comparative superiority. The V3
candidate is unresolved on every scorable case and has harm 0.25 in all three
regimes.

## Primary artifacts

- `RESULTS.md` — compact scientific report.
- `RESULT_V3.json` — full system and per-target metrics.
- `RECURSIVE_FAILURE_DIAGNOSIS_V3.json` — V2 304-failure recursion and V3
  333-failure replay.
- `IDENTIFICATION_ENVELOPE_THEOREM_V3.md` — formal coverage boundary.
- `COORDINATE_IDENTIFICATION_AUDIT_V3.json` — joint coordinate contrasts and
  causal-proof boundary.
- `COMPARATOR_IDENTITY_AUDIT_V3.json` — AML identity, fairness, and missing
  strongest-comparator requirements.
- `MANUSCRIPT_READY_SCIENTIFIC_EDITS.md` — bounded insertion text.
- `TRANSPORT_BLOCKERS_V3.json` — exact remaining promotion blockers.
- `FAILURE_ATLAS_V3.json` — each adverse result as an open discriminator.
- `SHA256SUMS` — retained artifact integrity.

## Reproduction commands

The large JSONL products were removed after their hashes and line counts were
retained in `TEMP_DATA_DISPOSAL_RECEIPT_V3.json`.

```bash
DIR=/Users/billy/Documents/Codex/2026-08-23/can-x20/work/lane-handoffs/p3-cross-construct-successor
TMP=/tmp/p3-cross-construct-successor-v3

rtk mkdir -p "$TMP"
rtk python "$DIR/p3_cross_construct_successor.py" build-cases \
  --archive /tmp/p3-public-data-successor-2026-08-23/oaei/oacontest17.zip \
  --out "$TMP/cases.jsonl" \
  --receipt "$DIR/CASE_UNIVERSE_RECEIPT_V3.replay.json"

rtk python "$DIR/p3_cross_construct_successor.py" run-systems \
  --cases "$TMP/cases.jsonl" \
  --aml-manifest "$DIR/INHERITED_AML_OUTPUT_MANIFEST.json" \
  --aml-output-dir /tmp/p3-oaei-public-dev/aml-outputs \
  --out "$TMP/predictions.jsonl" \
  --receipt "$DIR/PREDICTION_FREEZE_RECEIPT_V3.replay.json"

rtk python "$DIR/p3_cross_construct_successor.py" join-gold \
  --cases "$TMP/cases.jsonl" \
  --archive /tmp/p3-public-data-successor-2026-08-23/oaei/oacontest17.zip \
  --out "$TMP/public_gold.jsonl" \
  --receipt "$DIR/PUBLIC_GOLD_JOIN_RECEIPT_V3.replay.json"

rtk python "$DIR/p3_cross_construct_successor.py" score \
  --cases "$TMP/cases.jsonl" \
  --predictions "$TMP/predictions.jsonl" \
  --gold "$TMP/public_gold.jsonl" \
  --gold-receipt "$DIR/PUBLIC_GOLD_JOIN_RECEIPT_V3.replay.json" \
  --out "$DIR/RESULT_V3.replay.json"
```

## Boundary

V3 was designed after V2 public gold had been opened. OAEI 2004 contributes
one bibliographic seed family. Protected confirmation, causal coordinate
value, a nontrivial selective envelope, current-strongest-comparator
superiority, and source-disjoint multi-family transport all remain
`CANNOT_CHECK`.

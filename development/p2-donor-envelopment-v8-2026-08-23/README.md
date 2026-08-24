# P2 V8 donor-envelopment development packet

This packet evaluates three bounded residual score families around the exact
V7 u4 donor using nested leave-one-review-out KIFMS development. KIFMS outcomes
are open development data. The packet is not confirmation or independent
custody and contains no redistributed source CSVs.

Execution used:

```bash
rtk python run_donor_envelopment_v8.py \
  --packet . \
  --v6 ../p2-continuous-recall-effort-v6-2026-08-23 \
  --v7 ../p2-kifms-transparent-execution-v7-2026-08-23 \
  --stage /Users/billy/Documents/Codex/2026-08-23/can-x20/work/private-sources/p2-kifms-v7 \
  --out RESULT_V8.json
```

Rebuild deterministic derived reports with:

```bash
rtk python finalize_v8.py
```

Validate the complete packet with:

```bash
rtk python validate_v8.py
```

The raw result's execution-level terminal records whether any outer selector
activated. The authoritative scientific classification is
`SCIENTIFIC_ADJUDICATION_V8.json`: both activations harmed their held-out
reviews, all cross-fitted safety checks failed, no residual is admitted, and
exact u4 is retained as fallback.

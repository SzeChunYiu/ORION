# NR07 exact-anchor v2

Forensic successor identity: `ORION21.NR07.EXACT_ANCHOR.v2`.

This lane reconstructs the exact `(14,3,3)` replay anchor as 20,480 ordered
binary decisions, enumerates every top-r support admitted by the correlation
boundary tie, and maps the historical and LUNARC numerators to full raw
prediction transcripts. The compact result references eight committed bitset
files under `transcript/`; this keeps each custody object directly reviewable.

It does **not** re-run or re-adjudicate the width-law experiment. The controlling
scientific terminal remains `CANNOT_CHECK_INSTRUMENT_DRIFT`.

## Reproduce

From a full Git checkout containing the historical source commit:

```bash
LANE=papers/orion-21-state-as-computation/experiments/nr07-exact-anchor-v2
python "$LANE/run_exact_anchor_v2.py" --output-dir /tmp/nr07-exact-anchor-v2
cmp /tmp/nr07-exact-anchor-v2/RESULT.json "$LANE/RESULT.json"
diff -ru /tmp/nr07-exact-anchor-v2/transcript "$LANE/transcript"
python "$LANE/independent_checker/check_exact_anchor_v2.py" \
  /tmp/nr07-exact-anchor-v2/RESULT.json
```

The CI workflow fetches the historical commit explicitly, generates the result
twice, requires byte identity, compares it with the committed result, and runs
the standard-library-only independent checker.

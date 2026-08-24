# P1 owner-algebra construct validity V4

Outcome-blind public-standard successor to P1 V8/V3. The packet binds NISO
CREC, COPE, Crossref, and NLM/JATS source-native postpublication semantics,
then applies the unchanged 12-group V8 custodian rule.

## Result

- Distinct institutional source families byte-bound: **4**.
- V8 groups with a source-native structural analogue: **9/12**.
- Groups with required named-custodian authorship/delegation: **0/12**.
- Sufficient owner-algebra groups: **0/12**.
- Scientific-action gold: **0**.
- P1 readiness: **unchanged, `NOT_SUBMISSION_READY`**.

Exact terminal:

`P1_V4_PUBLIC_POSTPUBLICATION_STANDARD_SCAFFOLD_FEASIBLE__ZERO_OF_TWELVE_OWNER_ALGEBRA_GROUPS_SUFFICIENT__SCIENTIFIC_ACTION_GOLD_AND_CONSTRUCT_VALIDITY_CANNOT_CHECK`

## Verification

Run only the native bounded validator (no pytest or repository CI):

```bash
python verify_v4.py
```

`SHA256SUMS` covers every packet file except itself.

## Capture rerun boundary

`capture_sources_v4.py` retrieves only the frozen official document routes and
writes temporary bytes under `.capture_tmp`; `build_v4.py` hashes/extracts the
bounded evidence and deletes that directory. Web pages are mutable. Any digest
drift is a new capture and must not be silently identified with the frozen V4
receipt. No case, article/notice full text, model output, score, or scientific
action label is accessed.

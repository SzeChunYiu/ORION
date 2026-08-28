# NR07 exact-anchor v2 result receipt

Protocol: `ORION21.NR07.EXACT_ANCHOR.v2`

## Exact result

- Frozen denominator: 20,480 ordered query×test-row decisions.
- Historical numerator: 19,438.
- LUNARC numerator: 19,439.
- Query-0 boundary: fixed features 16 and 311; tied third features
  35, 93 and 263 at absolute correlation `24/64`.
- Candidate aggregate numerators: 19,438, 19,439 and 19,476.
- Historical mapping: feature 35, unique.
- LUNARC mapping: feature 93, unique.
- Raw prediction disagreements between those mapped worlds: 1,011.
- Correct labels among disagreements: 505 versus 506.
- Net aggregate delta: `1/20480`.

## Terminals

- Forensic:
  `NR07_EXACT_ANCHOR_ARGSORT_BOUNDARY_TIE_LOCALIZED`
- Custody:
  `NR07_LUNARC_EXECUTABLE_BYTES_ABSENT`
- Controlling science:
  `CANNOT_CHECK_INSTRUMENT_DRIFT`
- Scientific authority delta: `NONE`

The standard-library-only independent checker reconstructs every candidate
correct count and aggregate world from the committed label/prediction bitsets.

The exact labels and non-identical prediction vectors are stored as eight
base64-encoded 512-byte bitsets under `transcript/`. `RESULT.json` binds each
file by relative path, bit count, and SHA-256.

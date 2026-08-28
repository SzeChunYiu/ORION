# ORION-11 R4 — repairing the replication `CANNOT_CHECK`

**Protocol identity:** `ORION11.R4.ANCHOR_GATE_PARAMETERISED.v1`
**Authority:** instrument repair only · `scientific_authority_delta = NONE`

## The defect

The R4 replication world set terminated

```
INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ
```

so that arm is `CANNOT_CHECK` — neither a pass nor a failure.

Root cause, traced to source: `run_orion11_r4_faithful_comparator.py` defined the
reproduction gate as a **module-level constant**

```python
COMMITTED = {
    "orion_mutation_necessity": (1.0, 0.0),
    "active_voi_repair_parent": (0.49375, 0.0),
    "darc_r2act_dependency_parent": (0.49375, 0.2376821651630812),
    "causalflow_minimal_counterfactual_parent": (0.49375, 0.8213046495489243),
}
```

and applied it to **every** world set. Those rates are a property of the
`(frozen code, world set)` **pair**, not of the protocol. The replication set was
therefore held to the primary set's numbers and failed a gate it could never pass,
so no claim was read.

This is a hardcoded-parameter defect, not a scientific one. Nothing about the
falsification on the primary set is affected.

## The repair

The gate reference becomes an explicit input:

- `--anchor-reference PATH` — per-world-set reference rates. Omitting it falls back
  to `COMMITTED_PRIMARY`, so existing primary invocations are unchanged.
- `--emit-anchor-reference PATH` — stage-1 mode.

A supplied reference is **rejected** unless it declares
`frozen_before_new_arm_outcomes_read: true`.

## Why deriving the replication reference is not post-outcome tuning

The obvious objection: choosing a reference after seeing results is exactly the
forbidden lever. Two properties rule that out here.

1. **Only unchanged arms are used.** The four anchor arms are frozen v2.2.4 code
   that R4 does not modify. Their rates on any world set are a property of that
   frozen code and that set — a second reading of the same instrument, not a
   choice about R4.
2. **The new arms are never executed in stage 1.** In `--emit-anchor-reference`
   mode the arm list is restricted to `ANCHOR_ARMS`, so no new-arm outcome on the
   replication set is computed — not computed and withheld, but never produced.
   The reference is frozen before any such outcome can exist.

## Required execution order

```
# Stage 1 -- anchor arms only; emits the reference; no new-arm outcome exists yet
python run_orion11_r4_faithful_comparator.py \
    --world-dir  $CONF/replication \
    --execution-freeze $CONF/<replication execution freeze> \
    --emit-anchor-reference REPLICATION_ANCHOR_REFERENCE_V1.json

# Freeze: commit REPLICATION_ANCHOR_REFERENCE_V1.json and record its sha256.

# Stage 2 -- full experiment, gated by the now-frozen reference
python run_orion11_r4_faithful_comparator.py \
    --world-dir  $CONF/replication \
    --execution-freeze $CONF/<replication execution freeze> \
    --anchor-reference REPLICATION_ANCHOR_REFERENCE_V1.json \
    --outdir result/replication
```

Stage 2 must not run before stage 1's output is committed. If stage 1 shows the
unchanged arms do **not** reproduce stably on the replication set, that is a real
adverse finding about the instrument and must be reported as such — it is not a
reason to adjust the reference.

## Admissible outcomes of stage 2

| terminal | meaning |
|---|---|
| gate passes, comparative reading admissible | the replication `CANNOT_CHECK` is **resolved**, in whichever direction the data falls |
| gate fails against the set's OWN frozen reference | a genuine instrument instability on the replication set — adverse, and reported |

Note that resolving the `CANNOT_CHECK` does **not** presuppose the replication set
agrees with the primary falsification. It may confirm it, contradict it, or land
partial. The repair only makes the question answerable.

## What is unchanged

The primary-set result, its `H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION`
verdict, the committed v2.2.4 terminal, and every frozen byte. Provenance of which
reference was used is now recorded in the result under
`anchor_reproduction_gate.reference_provenance`.

# R4 packet: why `shasum -a 256 -c SHA256SUMS` reports one FAILED line

**Date:** 2026-08-29
**Status:** expected divergence, documented. Not corruption, and not a defect to "fix"
by rewriting either file.

`SHA256SUMS` and `AUTHORITY_DISPOSITION_V1.json` are recovered byte-exact from
`codex/all25-bounded-freeze-v2-20260828`. Both attest the artifact identities **as the
R4 faithful-comparator experiment was executed** (SLURM job 3550342, 2026-08-28). They
are historical attestations, so neither is regenerated here.

Seven of the eight attested files verify. One does not:

```
run_orion11_r4_faithful_comparator.py: FAILED
  attested   eae3a3bee9da8c4e105855a827c3eef0b8a83caf243ca1448d72177a0684f546
  in tree    d05743ca0fbf918944c73bfa845e4c4b665c6e96f28d8291eae4edcafaa79cbe
```

## Cause

`main` carries a **later** commit that the freeze branch predates:

```
d3e2e8f39  fix(orion-11): parameterise the R4 anchor gate so the replication
           CANNOT_CHECK becomes answerable
```

That commit replaces the single hard-coded `COMMITTED` anchor-rate table with
`COMMITTED_PRIMARY` plus a `--anchor-reference` loader, because applying the primary
world set's committed rates to the replication world set made that set fail a gate it
was never able to pass — the direct cause of the recorded terminal
`INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ`. The loader refuses any
reference that does not declare `frozen_before_new_arm_outcomes_read=true`, so the
repair cannot itself become post-outcome tuning.

## What this does and does not change

- The R4 **result** is unchanged. It was produced by the attested pre-repair runner, and
  the attested hash is the correct record of what produced it.
- The primary terminal `H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION` stands.
- The replication arm remains `CANNOT_CHECK`
  (`INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ`). The parameterization
  makes that `CANNOT_CHECK` *answerable* by a separately frozen run; it does not answer
  it, and it does not convert it to a pass. See `ANCHOR_GATE_REPAIR_V1.md`.
- `AUTHORITY_DISPOSITION_V1.json` records the same pre-repair hash for the same reason
  and is likewise left byte-exact.

Anyone re-running the R4 experiment against the attested hashes must check out the
runner at its attested revision; the tree copy is the later, parameterized one.

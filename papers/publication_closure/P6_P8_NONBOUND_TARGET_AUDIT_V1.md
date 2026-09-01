# P6–P8 non-BOUND reproducibility targets — are any of them bookkeeping?

**Audited:** 2026-09-01. **Authority delta:** `NONE`. **Verdict: none of them.** Every
non-BOUND state across ORION-16/17/18 is earned by the evidence, so none can be
cleared by writing a record.

## Why the question was asked

`check_content_binding_v1.py --check` reports eleven issue-#347 targets as still
`CANNOT_CHECK`, which reads like a large pile of bookkeeping debt. Several
`CANNOT_CHECK` states elsewhere in this programme have turned out to be exactly that
— a real artifact under a stale path, a record never committed — so the aggregate
deserved a per-target check rather than an assumption in either direction.

Running `check_reproducibility_targets_v2.derive_report` per candidate gives the
actual picture, which is much smaller than the aggregate suggests:

| candidate | state counts |
|---|---|
| P6 (ORION-16) | `BOUND 8`, `CANNOT_CHECK 1`, `DEFERRED 1` |
| P7 (ORION-17) | `BOUND 8`, `CANNOT_CHECK 1`, `DEFERRED 1` |
| P8 (ORION-18) | `BOUND 7`, `PARTIAL 1`, `CANNOT_CHECK 1`, `DEFERRED 1` |

Three distinct blockers, not eleven.

## 1. `independent_replay_attestation` — `CANNOT_CHECK` on all three

Blocker: *"no ScientificResultVerification.v1 record names this paper."*

`research/verification/records/` holds nine records covering P1–P5 claims. None sets
`paper_id` to P6, P7 or P8, so the probe returns `CANNOT_CHECK` rather than a
judgement — correctly, since nothing was examined.

The record is not free to mint. `_independent_replay` requires
`verification_state == "BOUNDED_VERIFIED"`, `self_authorizing is False`, a 40-hex
`subject.commit` and `subject.tree`, a non-empty `raw_artifacts` list whose every
`sha256` is re-hashed against the file on disk, and — the load-bearing field —
`scorers.independent_from_written_spec is True`.

That last field is a factual claim about how the replay was scored, not a
configuration flag. ORION-17's density packet ships an independent checker and a
LUNARC execution transcript, and its checker is independent of ORION-17's *modules*;
it is not independent of the packet's own written spec, because it was authored with
it. Setting the field on that basis would be a fabricated attestation, and the probe
would then be reporting a replay that never happened.

**Correct negative.** Discharging it requires performing a genuine independent
replay, not writing a record.

## 2. `permanent_archive_after_authority_stabilizes` — `DEFERRED` on all three

Blocker: *"permanent deposit is a post-authority lifecycle action; candidate status
does not license it."*

This one must not be "fixed". All three papers grant `NONE` for scientific authority,
so the precondition for a permanent deposit has not occurred. `DEFERRED` is the
schema's word for a target that is correctly not yet due, and depositing early to
clear a red line would invert the lifecycle the target exists to enforce.

**Correct negative, and a target that should stay deferred.**

## 3. `protected_labels_custody_and_attack_replay` — `PARTIAL` on P8

Blocker: *"missing protected-label custody record."*

`_p8_custody` looks for `**/*custody*.json{,l}` and for
`**/*attack*result*.json`. It finds the attack side —
`evidence/local/cross_capability_attack_replay_result_v2.json` — and no custody file.

Because the probe matches on filenames, the obvious hypothesis was a false negative:
custody evidence present inside another file and missed by the glob. A content search
does find custody discussed in fourteen ORION-18 files, and the attack result itself
carries `independent_custody` and `protected_labels_used` keys. **The hypothesis is
wrong, and the artifact is the one that refutes it.** Its values read:

```
independent_custody:          false
protected_labels_used:        false
self_authorizing:             true
authority_scope:              LOCAL_REFERENCE_POLICY_PREFLIGHT_ONLY
grants_scientific_authority:  NONE
independent_unit:             "one authored laundering attack contract"
```

The file states plainly that no protected labels were used and that custody was not
independent. It cannot serve as the missing custody record, and re-pointing the glob
at it would convert an honest self-declaration into a false pass.

**Correct negative.** Discharging it needs an attack replay actually run over
protected labels under custody that is independent of the authoring unit. The
existing run is `self_authorizing: true` and cannot be promoted into that role.

## What this audit changes

Nothing in the papers, which is the result. The `CANNOT_CHECK` aggregate looked like
debt and is not: the P6–P8 target set contains no false negatives, every non-BOUND
state is earned, and the two states that could be cleared by work name that work
precisely — a genuine independent replay, and a protected-label attack replay under
independent custody. Neither is bookkeeping and neither should be closed by writing a
record.

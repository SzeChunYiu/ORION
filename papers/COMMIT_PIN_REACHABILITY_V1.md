# A guard for dangling commit pins exists, and it was watching 2 of 45

**Date:** 2026-09-02 · **Scientific authority delta:** `NONE`. No theorem, bound or terminal
changes. This closes a coverage gap in an existing guard and ratchets the class.

## The gap

`tests/unit/programme/test_content_binding_pin_is_reachable.py` exists precisely to catch
commit pins that cannot be resolved. Its scope is one glob:

```python
MANIFESTS = sorted(ROOT.glob("papers/*/CONTENT_MANIFEST_V2.json"))
```

Every dangling pin found so far lives somewhere else — in
`ALL_25_BOUNDED_SCIENCE_FREEZE_V2.json`'s `source_result_commits`, in V1 manifests, and in
ORION-04's scope manifests. **The guard has never seen any of them.** It passes, correctly, on
the files it looks at.

## Measured across `papers/**`

**148 pin references, 45 distinct commits.** Sixteen do not resolve cleanly:

| state | count | meaning |
|---|---|---|
| `ABSENT` | **2** | object does not exist here and the remote refuses it as *not our ref* |
| `OFF_MAIN` | **14** | exists, but is not an ancestor of `origin/main`, so it lives on a branch |

The two `ABSENT` pins are ORION-15's `b6b1e2734d` and ORION-19's `6bc611ed15`, both cited by
the all-25 freeze. Nothing can re-derive them.

The `OFF_MAIN` set is the more instructive one: resolvable *today*, gone the moment those
branches are pruned. That is the class `#1989` repaired, the class ORION-04's own FINDINGS.md
flags against its scope manifests, and the class the all-25 freeze anchor itself fell into —
`fe5da5332` is valid and unreachable from `main` at the same time.

## The ratchet

`scripts/check_commit_pin_reachability_v1.py` scans every commit pin under `papers/**` and
compares against `papers/COMMIT_PIN_REACHABILITY_BASELINE_V1.json` (16 entries). A **new**
dangling pin, or an entry degrading `OFF_MAIN → ABSENT`, exits 2. Existing entries are
reported, not failed, so main stays green while the class stops growing.

An entry leaves the baseline **by becoming reachable, never by being deleted.** That is
enforced, not merely documented:

| mutation | result |
|---|---|
| add a file pinning a nonexistent commit | **exit 2**, names the pin and its file |
| delete a baseline entry to hide it | **exit 2** — it returns immediately as a new finding, naming all 9 files that pin it |
| unmutated | exit 0 |

## What this does not do

It does not repair the two `ABSENT` pins; nothing can. They remain dispositioned as
`UNREACHABLE_PROVENANCE__CANNOT_CHECK` in the V3 freeze work. It does not re-pin the 14
`OFF_MAIN` entries either — re-pinning is a per-record decision about which commit a record
should bind to, and doing it in bulk would be exactly the silent absorption this guard exists
to prevent.

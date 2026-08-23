# P1-U-T3 pre-repair record — the three defects, reproduced

**Date:** 2026-08-21
**Subject:** `research/claim_expansion/p1/gpt_r6/evaluate_native.py` (this tree) and
`research/claim_expansion/p1/gpt_r6_native_primary.py` (shadow ref
`origin/shadow/p1-u-gpt-r6-native-runtime-20260820`, where `_leakage_free` lives).
**Authority:** none. This is a measurement of the instrument, not a P1-U result.
**Reproduction script:** `research/claim_expansion/p1/claude_t3/reproduce_t3_defects.py`
(`python research/claim_expansion/p1/claude_t3/reproduce_t3_defects.py --out <path>`).
**Outputs no repo state.** It reads the frozen corpus and re-derives the stratifier keys.

---

## Defect 1 — class noninferiority never sees the control class

`evaluate_native.py:338` files the **pair-level** selective diff under the **pair's**
`adverse_class`:

```python
pair_by_class[str(pair["adverse_class"])].append(pair_diff)
```

Each pair contributes exactly one row, under one key. `class_noninferiority`
(`evaluate_native.py:411-414`) then iterates `class_means`, derived from `pair_by_class`.

Measured on the frozen 22-pair / 4-unresolved corpus:

| quantity | value |
| --- | --- |
| strata actually created | 6 |
| `NO_HIGH_LEVEL_REFORMULATION` stratum present | **False** |
| rows per stratum | SEARCH 4, REPRESENTATION 4, IMPLEMENTATION 4, MEASUREMENT 3, OBJECTIVE 4, BOUNDARY 3 |
| control-class episodes in the corpus | **22** |
| episodes filed under their own gold class | **0 of 48** |

Per-member gold-class counts, i.e. the strata that *should* exist:

```
IMPLEMENTATION_OR_ENVIRONMENT   4
MEASUREMENT_OR_EVALUATOR        3
NO_HIGH_LEVEL_REFORMULATION    22   <- never evaluated
OBJECTIVE_OR_MODEL_CLASS        4
PROBLEM_BOUNDARY                3
REPRESENTATION_OR_INTERFACE     4
SEARCH_OR_EVIDENCE              4
```

So the guard named "class noninferiority" evaluates 26 of 48 episodes' worth of information,
aggregated pairwise, and the matched-control gold class — the entire reason the control member
exists — contributes to no stratum of its own.

## Defect 2 — the domain margin is not a margin

`domain_diffs` is keyed on `actual_domain`, one distinct value per source.

| quantity | value |
| --- | --- |
| domain strata | **26** |
| strata of size 2 | 22 |
| strata of size 1 | 4 |
| total episodes | 48 |
| frozen floor `domain_or_class_noninferiority_floor` | **-0.10** |
| smallest attainable negative stratum mean, n=2 | **-0.50** |
| smallest attainable negative stratum mean, n=1 | **-1.00** |
| stratum sizes for which one lost episode still clears -0.10 | **none** |

Per-episode diffs live in `{-1, 0, +1}`. For a stratum of size *n*, one net lost episode gives
a mean of `-1/n`. Clearing `-0.10` requires `n >= 10`. No domain stratum in this corpus has
`n >= 10`; the largest has `n = 2`. Therefore, on this corpus,

> `domain_mean >= -0.10`  **is arithmetically identical to**  `domain_mean >= 0`

and the check is a hard "ARD may never lose a net episode in any domain" rule wearing a
noninferiority margin's name.

## Defect 3 — the leakage guard is fail-open and role-blind

Source (shadow ref, `gpt_r6_native_primary.py:211-213`), reproduced verbatim in the script:

```python
def _leakage_free(native, forbidden_tokens):
    serialized = json.dumps(native.get("request_payloads", []), sort_keys=True)
    return all(not token or token not in serialized for token in forbidden_tokens)
```

Measured behaviour:

| input | returns |
| --- | --- |
| `{}` — `request_payloads` key **absent** | **True** ("no leakage") |
| `{"request_payloads": None}` | **True** |
| key present, payload clean | True |
| key present, payload contains a forbidden token | False |
| key present, payload contains **only** `pair_role=adverse` | **True** |

The first two rows are the fail-open defect: the guard reports "clean" for an artifact it never
examined. `ran` is reported as `worked`.

The last row is the token-set defect. The forbidden tuple assembled at the call site is
`(episode_id, pair_id, query_id, adverse_class, gold_class)` — pair role is absent.

`evaluate_native.py` in this tree has **no leakage guard at all** (`_leakage_free` is not
defined in it), so on the evaluator actually being repaired the guard's state is worse than
fail-open: it is missing.

### What a working leakage guard finds on this evaluator, measured before writing it

The frozen native core builds its root problem id as `f"p1-r6-root:{episode_id}"`, and the
episode id is `R5-SEARCH-P1-A` / `R5-SEARCH-P1-C` / `R5-UNRES-P1-U`. Capturing every
`FrozenNativeProviderHost.__call__` request for one ARD episode (6 provider calls, 4892 bytes
of payload) shows the candidate-visible payload contains:

| token | present in candidate-visible provider payload |
| --- | --- |
| episode id `R5-SEARCH-P1-A` | **True** |
| pair id `R5-SEARCH-P1` | **True** |
| query id `SEARCH-P1` | **True** |
| pair role, as the `-A` / `-C` / `-U` suffix of the above | **True** |
| source id | False |
| adverse class literal | False |
| gold class literal | False |

The `-A`/`-C` suffix is a perfect gold predictor for the 22 control episodes, whose gold class
is `NO_HIGH_LEVEL_REFORMULATION` by construction. That is why the missing token matters, and
it is the reason a correctly built guard is expected to go **red** here rather than green.

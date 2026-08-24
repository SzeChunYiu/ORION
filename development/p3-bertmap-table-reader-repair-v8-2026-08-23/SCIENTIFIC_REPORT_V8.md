# P3 BERTMap table-reader repair V8

## Exact terminal

`P3_V8_BERTMAP_TABLE_READER_MINIMAL_REPAIR_SOURCE_HASH_AND_SYNTHETIC_EMPTY_NONEMPTY_EXECUTION_BOUND__MALFORMED_STALE_AND_PROHIBITED_CASES_FAIL_CLOSED__V7_PARSER_SYNTHETIC_COMPATIBILITY_BOUND__NATIVE_SMOKE_AND_SCIENTIFIC_READINESS_UNCHANGED`

## Efficient root-cause repair

V8 repairs exactly one source expression in DeepOnto commit
`74ca8d47f01bad0b8739f19ee2c392bdf6d9c090`, tree
`b499cb5780bbe749f7db44d0bc872d275a2737ea`,
`src/deeponto/align/mapping.py` SHA-256
`9cf0dce1c5bd142e4175f628f8f3267f54ed6deac9f31e165a25b4a073eedff0`:

```diff
- if not threshold or dp["Score"] >= threshold:
+ if not threshold or dp.Score >= threshold:
```

The patch SHA-256 is `412050c5d3a0e7891a21744a9690d3e4ba06886ea51eec273b6045bff688e42b` and the
resulting source SHA-256 is `d0b3b6cfdee45019783707c4bd623cc76f8325142828cf1e10ebb74ad628d70f`.
The upstream root source is Apache-2.0 and the exact licence text is retained;
this is not legal advice and it does not close the full runtime's component
rights.

## Prospective outcome-blind execution

The protocol was frozen before patch execution. Eight of eight authored
synthetic cases passed:

- empty non-reference table: unchanged empty result;
- nonempty table with `threshold=None`: original and repaired methods both
  return both exact rows;
- nonempty table with truthy threshold `0.5`: the pinned source reproduces
  `TypeError`, while V8 returns only the `0.9` row under the pre-existing rule;
- missing and nonnumeric Score tables fail closed;
- stale source identity, reference-mode request and external fixture request
  fail closed before prohibited access.

This corrects a V7 scope overstatement: **not every nonempty table fails**.
The defective expression is reached only when `threshold` is truthy; falsey
thresholds short-circuit it. The normalized method AST is identical after
replacing only that frozen access.

No DeepOnto import, JVM, model, ontology, benchmark, paper `data.zip`,
gold/reference alignment, protected outcome, training, prediction, mapping
repair, scoring or comparison occurred.

## Parser and readiness boundary

The exact V7 parser SHA-256
`d1184dc129082bdcf18b415b551f244a695b4e34417286afc37a3f3a5d788bc5`
accepted a temporary authored five-file fixture with row counts 2 raw, 2
extended, 1 filtered and 1 repaired. Those synthetic files were deleted.
They are not native BERTMap artifacts. Actual native artifact presence is
**0/5**, so native smoke is not claimed.

| Axis | Before | After | Net |
|---|---:|---:|---:|
| Truthy-threshold source defect | blocking | exact patch + synthetic execution bound | root cause repaired at language level |
| Three-family native smoke | 2/3 | 2/3 | 0 |
| Scientific comparator readiness | 0/3 | 0/3 | 0 |
| Actual BERTMap artifacts | 0/5 | 0/5 | 0 |

## Remaining shortest path

1. Bind a complete content-addressed repaired DeepOnto Python runtime.
2. Close component-level JVM/JAR provenance, rights and SBOM decisions.
3. Run one fresh isolated no-gold native BERTMap smoke and require all five
   actual artifacts to pass the unchanged V7 parser.
4. Only then freeze independently custodied rights-valid evaluation.

Correctness, coverage, harm, transport, performance, superiority and top-tier
submission readiness remain `CANNOT_CHECK` / not established.

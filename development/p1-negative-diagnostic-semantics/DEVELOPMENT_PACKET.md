# P1 negative-diagnostic semantics repair

## Development question

How can P1 report every result cell without conflating three different states:

1. an applicable quantity was observed;
2. an applicable quantity could not be checked; and
3. a quantity is structurally outside the domain of the selected case scope?

The immediate defect is in the generated historical P1-T2 artifact. Its complete
2,880-record archive has no unscored records, but the dense mechanistic block
serializes 288 structurally inapplicable cells as `CANNOT_CHECK`.

## Atomic questions

1. Which metrics are defined only for hidden-shift cases?
2. Which metrics are defined only for negative controls?
3. Does the aggregate `ALL` scope legitimately contain both metric families?
4. Can an applicable zero denominator still fail closed as `CANNOT_CHECK`?
5. Can the committed P1-T2 artifact be regenerated without changing any
   numerator, denominator, interval, effect, p value, hypothesis verdict, or raw
   record?
6. Which historical negative findings must remain immutable?
7. Which comparator rows are registered hypotheses versus descriptive contrasts?

## Recovered incumbent mechanics and negative history

- `src/orion/study/p1/tables.py::_mechanistic_block` emits the same dense metric
  family for every scope.
- `_rate_block` currently maps every `n == 0` to `CANNOT_CHECK` without receiving
  the scope or metric applicability domain.
- The 288 cells decompose exactly as follows:
  - 12 systems x 5 hidden-shift scopes x 3 control-only metrics = 180;
  - 12 systems x 3 control scopes x 3 hidden-shift-only metrics = 108.
- Every affected row records `cannot_check_cases == 0`; the archive integrity
  block is coherent and contains all 2,880 expected scored records.
- Historical P1.H1 remains `NOT_SUPPORTED` (1/48 versus 1/48). This repair does
  not change, suppress, or reinterpret that finding.
- The same table contains 90 non-subject rows whose identifiers begin
  `descriptive:` but whose assessments are nevertheless serialized as
  inferential verdicts (69 `NOT_SUPPORTED`, 21 `EQUIVALENT`). A descriptive
  contrast has no registered hypothesis to support or reject; this is a second
  status-ontology defect.

## Bounded saturation assessment

### Knowledge

The local schema, raw archive, result generator, integrity note, reproduction
receipt, independent-verification record, package manifest, and relevant unit
tests were inspected. All three independent reviews reproduced the same 288-cell
decomposition. No external literature is needed to decide the ontology defect:
the applicability domains are frozen by P1's own case families and metrics.

### Search universe

The search covered P1 source, tests, raw and aggregate results, package claims,
verification records, reproduction receipts, and concurrent paper branches.
The active paper-editing branch does not modify `src/orion/study/p1/tables.py`
or the P1-T2 JSON artifact, so an isolated additive regression lane is viable.

### Formulation

Three formulations were considered:

1. replace the cells with `PASS` or zero -- rejected as result laundering;
2. omit every inapplicable metric -- valid but weakens the stable dense schema;
3. retain the dense schema and emit `NOT_APPLICABLE` with an explicit reason --
   selected because it preserves shape and makes the distinction machine-readable.

For non-subject comparator rows, retain the effect, interval, direction, and
margin as descriptive metadata, but emit `DESCRIPTIVE_ONLY` and
`NO_REGISTERED_HYPOTHESIS` instead of an inferential verdict.

## Challenge to the saturation basis

- A zero denominator can mean missing evidence rather than inapplicability. The
  repair therefore requires an explicit `(scope, metric)` applicability map;
  it must never infer `NOT_APPLICABLE` from `n == 0` alone.
- `ALL` contains both hidden shifts and controls, so both metric families remain
  applicable there.
- The historical H1 negative is not a schema defect and remains unchanged. The
  descriptive estimates also remain unchanged, but their inferential-looking
  verdict labels are corrected because no hypotheses were registered for them.
- A flat token counter is not a scientific claim-lifecycle audit. Later work must
  distinguish active claims, superseded historical claims, descriptive contrasts,
  and standing paper terminals without deleting negative history.

## Why prior checks missed the defect

1. Tests enforced that an empty denominator never becomes zero but did not encode
   the separate applicability dimension.
2. The Markdown table renders mechanistic metrics only for `ALL`, where the defect
   is invisible.
3. The top-level table status is `OK`, because the primary metrics are complete.
4. Token-level audits counted nested diagnostics without reading their scope.

## Frozen implementation hypothesis

Add an explicit metric-applicability function in `tables.py`. Pass the row scope
when serializing mechanistic rates. Emit `NOT_APPLICABLE` plus a reason only when
the frozen scope excludes that metric family. Continue emitting `CANNOT_CHECK`
for any applicable rate with `n == 0`. Regenerate P1-T2 from the unchanged raw
archive and assert that:

- `CANNOT_CHECK` falls from 288 to 0 in the complete committed artifact;
- `NOT_APPLICABLE` is exactly 288 with the frozen 180/108 decomposition;
- all scientific numbers and P1.H1 remain unchanged; and
- 90 non-subject contrasts become explicitly descriptive without changing their
  estimates or intervals;
- missing or incoherent evidence continues to fail closed.

## Reopen triggers

Reopen this packet if any of the following occurs:

- a new P1 scope mixes neither or both case families differently;
- a metric's frozen applicability domain changes;
- any numeric or hypothesis field changes during regeneration;
- an applicable missing cell is relabelled `NOT_APPLICABLE`;
- downstream consumers reject the additive status without a versioned migration;
- the current package cannot preserve verification and hash provenance.

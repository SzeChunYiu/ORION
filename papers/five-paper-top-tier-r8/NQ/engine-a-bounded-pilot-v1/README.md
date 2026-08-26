# NQ Engine A — engineering staging only

> `ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK`  
> `EXPECTED_OUTCOME_EXPOSURE`  
> Independence terminal: `CANNOT_CHECK`

This directory implements a structurally different **engineering** route for finite-group
controls: support-basis canonicalization/orderly generation and an exact multi-bin
subset-sum factorization DP. Because the authoring model inherited Engine B context and
public expected outcomes, this is not clean-room, blinded, or independent evidence and
must not count toward the two-engine replay terminal.

## What is implemented

- strict `C_p^d` encoding, arithmetic, rank, and span coordinates;
- exact `GL(d,p)` multiset canonicalization by ordered support bases;
- frozen C5-cubed donor-normalization predicate, complete orbit-slice adapter, and
  machine-checkable basis witnesses;
- deterministic canonical filtering over nondecreasing raw multisets with resumable coverage;
- lossless canonical-construction-path generation using exact stabilizer extension orbits and
  hereditary short-zero-sum/factorization pruning;
- canonical-JSON checkpoint/restart for a source-bound one-level parent slice, with replayed
  prefix validation and inaccessible partial children;
- exact donor class-index range manifests and strict split/merge recomputation;
- exact indistinguishable-bin DP for `k` pairwise-disjoint nonempty zero sums;
- reconstructible original-index certificates and mutation-resistant verification;
- versioned input, certificate, coverage, receipt, and source-manifest JSON Schemas;
- fail-closed resource and partial-run receipt semantics;
- complete tiny-domain brute-force equality panels and hostile/mutation tests;
- explicitly exposed permitted lower-witness controls.
- a prospectively frozen 16-case target-length engineering resource panel and conservative
  future same-pilot SLURM envelope.

## Reproduce the engineering checks

From this directory, in a Python 3.11+ environment:

```bash
python -m pip install -r requirements-test.txt
PYTHONPATH=src pytest -q
ruff check .
ruff format --check .
python -m compileall -q src tests
coverage erase
coverage run --branch -m pytest -q -m "not permitted_lower_control and not augmentation_equivalence"
coverage report -m
```

The repository-level operator must prefix commands with `rtk` when that policy is active.
The expected-outcome-exposed lower controls and largest raw-equivalence panels are included
in the full pytest run; the coverage command omits both marked groups only to avoid repeating
the slower exhaustive panels under instrumentation.

## Authority boundary

A passing engineering suite establishes only the tested implementation properties. It does
not establish the frozen full census, short-spectrum upper bounds, D2/D3 equalities, novelty,
independent replay, peer review, or journal readiness. See `COMPLETENESS_ARGUMENT.md` and
`INTEGRATION.md`. The resource pilot also preserves all 16 expected-outcome-exposed DP
negatives as bounded engineering observations; they are not an independent scientific
negative. See `TARGET_RESOURCE_PILOT_METHOD.md`.

# FiberGuard R21 TSP prerequisite failure

The prospectively frozen TSP-LION2015 executor at
`46c41a8820644ad79242fa9d12d6b5901f08c7f4` stopped before any learned model,
legal pair, route interval, test loss, or scientific comparison was produced.

```text
CANNOT_CHECK_TSP_DIRECT_RELATIVE_SOURCE_OR_RESOURCE
```

This label is an additive post-failure disposition, not an executor-emitted
terminal: the frozen executor raised its recorded `ValueError` and wrote no
result or terminal file.

The first exact witness was `tsplib_eil51/eax_probing`: every recorded cost is
missing and the aggregated feature status is `presolved`. The complete source
audit found 21 such `eax_probing` instance-step cells among 3,106 instances.
The frozen protocol intentionally had no imputation because TSP-LION2015
declares `features_cutoff_time: ?`. Dropping those rows, assigning zero, or
removing `eax_probing` after seeing the failure would change the scientific
grammar and is forbidden.

This is a preserved subject-prerequisite `CANNOT_CHECK`, not a null, adverse,
or positive Round-2 route result. It does not consume a distinct mechanism and
does not permit BNSL retuning. The same frozen direct-relative/joint-route
mechanism therefore moves to a separately frozen untouched recovery subject
whose metadata declares a numeric feature cutoff.

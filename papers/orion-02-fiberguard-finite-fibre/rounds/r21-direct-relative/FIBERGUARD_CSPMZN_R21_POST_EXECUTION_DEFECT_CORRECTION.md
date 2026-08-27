# FiberGuard CSP-MZN R21 post-execution defect correction

The first complete frozen execution at protocol/executor commit
`ec5f757e8747449e40bbfe6fde6e1fa227656f49` emitted:

```text
C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE
result SHA-256 e9be34bd50b5f0a825c3c1b08ae05ed1d19a1b5937af791435283ffeb0e3736b
```

It exposed one reporting-only defect. `post_acquisition_same_route` correctly
used the primary route's losses, timeouts, and acquisition accounting, but its
per-row `choices` entry was omitted. Aggregate serialization therefore reported
`learned_count=0` for that control even though its loss vector was correct.

The correction adds the already-frozen primary choice vector under the post-
acquisition arm and strengthens the completeness control to require identical
arm key sets for choices, losses, timeouts, and acquisition. It does not change
any model, split, source row, legal pair, selected pair, relative prediction,
interval, primary/comparator decision, primary/comparator loss, bootstrap,
terminal predicate, or authority boundary. The first receipt remains preserved
above; the corrected executor must reproduce twice byte-identically before its
result is admitted.


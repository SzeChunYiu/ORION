# Standalone bounded-search replay

Run the public replay harness with Python 3.10 or later and a C11 compiler:

```text
python3 verify_bounded_search.py
```

The harness compiles the four packaged C programs in a temporary directory,
runs the support-eight, support-nine, and two support-ten engines, and checks
their output against `bounded_search_expected.json`. On the reference machine
the support-nine replay is the slowest step and takes approximately 75 seconds.

A successful run prints JSON with `"all_checks": true` and exits with status
zero.  This is a same-package reproducibility check, not an independent
scientific replication.  It does not promote the larger support-through-22
search or settle the unresolved exact generalized Davenport constant.


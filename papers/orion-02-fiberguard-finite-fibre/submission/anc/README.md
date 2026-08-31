# Standalone verification

Run the public claim checker with Python 3.10 or later:

```text
python3 verify_public_claims.py
```

The checker has no third-party dependencies and does not import repository
modules.  It independently evaluates the finite constructions described in
the manuscript:

- the four-term threshold witness;
- the two five-term gadgets and their complete set partitions;
- the two-gadget product cases;
- pair-data equality and the stated product/minimax formulas; and
- the parity trade and its proper upper marginals.

A successful run prints JSON with `"all_checks": true` and exits with status
zero.  The script corroborates the finite constructions.  The displayed
proofs in the manuscript, rather than this finite computation, carry the
all-parameter statements.


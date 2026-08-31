# Public control records

`certificate_control_records.json` is a public, label-free summary of the
finite control rows used in the manuscript.  It separates the abstract
five-bit deletion certificate, the one-Tag three-block control, and the
dependent-triple normalization record.

Run the package-local finite replay with:

```sh
python3 verify_dependent_triple_lemmas.py
```

The verifier uses only the Python standard library and the phase-free
one-site Pauli algebra defined in that file.  It exhausts the 2,880 deletion
rows, 6,912 core-alignment rows, 576 same-site rigidity rows, and 9,216
distinct-site Tag rows, then checks the stated composition arithmetic and the
support-zero obstruction.

This is reproducibility from the same public package, not an independent
scientific replication.  The finite replay corroborates the local case
analyses; it does not replace the manuscript's analytic composition proof.
The abstract zero-sum and product statements are proved in the manuscript,
and the compiler normalization remains subject to the manuscript's stated
scope and independent-review requirements.

# ORION-04 global certified search v1

This is a new prospective promotion lane. It does not alter the completed Wave-3 bounded paper or consume the internal support-through-22 ledger as theorem evidence.

The target is the exact length-31 obstruction problem over `C_5^3`. The lane has only four scientific terminals:

- a proof-checked UNSAT certificate, yielding `31 in C_0(C_5^3)` and the registered exact-`D_4` consequence;
- an explicit independently verified length-31 obstruction;
- a separately proved reusable structural theorem that closes the same obstruction;
- `CANNOT_CHECK`, with no authority promotion.

The committed generator emits a complete pseudo-Boolean encoding. It fixes a support basis by `GL(3,5)`, encodes multiplicities in `{0,1,2,4}`, length 31, total sum zero, support at least 14, and every forbidden zero-sum submultiset of length at most five. A witness checker is independent of the generator. UNSAT authority additionally requires a proof accepted by a pinned external proof checker; a solver exit code is never sufficient.

Run the fast controls:

```bash
python research/orion-rg/promotion/orion04-global-certified-search-v1/generate_opb.py \
  --prime 3 --rank 2 --length 7 --support-lower-bound 3 --output /tmp/orion04-control.opb \
  --manifest /tmp/orion04-control-manifest.json
python -m pytest -q tests/research/test_orion04_global_certified_search_v1.py
```

Generate the registered full object:

```bash
python research/orion-rg/promotion/orion04-global-certified-search-v1/generate_opb.py \
  --output /tmp/orion04-c5r3-l31.opb \
  --manifest /tmp/orion04-c5r3-l31.manifest.json
```

No positive scientific terminal is committed in this directory unless either the external proof or a concrete witness is independently checked.

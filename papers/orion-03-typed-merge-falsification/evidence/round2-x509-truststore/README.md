# ORION-03 Round 2 evidence: X.509 trust-store merge (upstream corpus)

Frozen protocol: PROTOCOL_V2.md. Corpus: OpenSSL `openssl-3.6.4` tag,
complete test/certs public material (content-based rule) + the complete
labeled verify table; identity bindings in SOURCE_BINDING_V2.json,
attribution in THIRD_PARTY_SOURCE.md.

## Freeze (commit preceding any results commit)

- `generate_tasks.py` -> `TASK_MANIFEST_V2.json`
  (sha256 ff54dbd02346d8369a4fa11e71ba179cb74fedfcad8280c97dd47e3dc29e5aff)
  and `UPSTREAM_TABLE_V2.json`: 191 usable upstream labels
  (1 row excluded: pc6-cert references setup.sh-generated material),
  1858 F-U + 104 F-P merge tasks.
- `run_round2.py`: five-method evaluator + controls C1-C6; emits
  `ROUND2_RESULTS_V2.json` (byte-deterministic) and a separate COST receipt.

## Reproduce

1. Build the pinned engine from the sha256-verified tarball (see CI workflow
   for the fail-closed recipe) or point `OPENSSL_BIN`/`OPENSSL_LIB` at an
   existing 3.6.4 install.
2. `python generate_tasks.py` (no engine needed; regenerates the manifest).
3. `python run_round2.py --engine <openssl> [--engine-lib <lib64>]`
   (writes ROUND2_RESULTS_V2.json + COST_ROUND2_V2.json).
4. `python run_round2.py --check-final` re-executes everything and
   byte-compares the regenerated receipt against the committed one.

Results and their interpretation are added by the results commit; this
freeze commit contains no outcome data.

# Omitted transient payloads

Large provider archives and codeload responses were streamed or removed after hashing and normalized path/byte-manifest comparison. They are reproducible from the exact URLs in:

- `EXACT_EDGE_PAYLOAD_COMPARISON_V9.json` (indices 91, 133, 165);
- `EDGE_185_CONTENT_COMPARISON_V9.json` and `EDGE_185_REPRODUCIBLE_SDIST_V9.json`;
- `EDGE_190_CONTENT_COMPARISON_V9.json`;
- `EDGE_199_FULL_COMMIT_PROVIDER_VERIFICATION_V9.json`.

Each receipt records provider URL, byte count, SHA-256, normalized manifest hash and every path difference. The 38 MB compressed GH Archive discovery hour was not retained; its full compressed SHA-256, line count and five exact matching events are bound in `EDGE_199_GHARCHIVE_DISCOVERY_RECEIPT_V9.json`, while only the five matching events are retained under `evidence/`. GH Archive remains discovery-only and does not grant authority.

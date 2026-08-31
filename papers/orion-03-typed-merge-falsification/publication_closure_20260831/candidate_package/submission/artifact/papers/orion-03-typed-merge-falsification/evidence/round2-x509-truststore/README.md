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

1. Build the pinned engine from the sha256-verified tarball using
   `PINNED_OPENSSL_BUILD.md`, or point `OPENSSL_BIN`/`OPENSSL_LIB` at an
   existing 3.6.4 install.
2. `python generate_tasks.py` (no engine needed; regenerates the manifest).
3. `python run_round2.py --engine <openssl> [--engine-lib <lib64>]`
   (writes ROUND2_RESULTS_V2.json + COST_ROUND2_V2.json).
4. `python run_round2.py --check-final` re-executes everything and
   byte-compares the regenerated receipt against the committed one.

Results and their interpretation are added by the results commit; this
freeze commit contains no outcome data.

## Results (results commit)

Terminal `D_R2_REAL_AUTHORITY_PROMOTION_ERROR_PREVENTED`. See
`ROUND2_RESULT_V2.md` for the full table, controls, and the binding claim
boundary. Receipts: `ROUND2_RESULTS_V2.json`,
`COST_ROUND2_V2.json` (byte-identical across two runs, C2);
`INDEPENDENT_REPRO_R2.json` (context-free re-implementation by an agent
with no access to the evaluator). On 1962 tasks: 46 engine-adjudicated
hybrid authorizations; M1 flat union authorizes all 46 (unsafe), the typed
origin-witness layer blocks all 46 with zero needless rejections, at 2x flat
merge engine cost.

**Metric-status correction (2026-08-28).** The `precision = recall = 1.0`
figure recorded in `ROUND2_RESULTS_V2.json` is an **analytic identity**, not a
measurement. `invariants.m5_decision_equals_parent_authorization` is `true`, so
with `parent := vA or vB` and `hybrid := vUnion and not parent`, M5 flags
exactly the hybrid set by construction and its unsafe/needless counts are
identically zero — for *any* corpus. It must not be reported as measured
detector performance or compared against baselines as an experimental win.

What this round *does* establish empirically is unchanged and stands: the
obstruction occurs in third-party OpenSSL test material (46 of 1962 tasks, ~2.3%); the
baselines pay measurably different prices (M1 4 unsafe merges, M2/M3 63
needless rejections each, M4 14 in `PARITY_PARTITION`); and `c3_violations`,
`c4_resurrections` and `c4_upstream_mirrors_ok` hold where they could have
failed. See `../../ROUND2_METRIC_STATUS_FINDING.md`.

The bound records — `ROUND2_RESULT_V2.md`, `PROTOCOL_V2.md` and the results
JSONs — are digest-pinned by `SOURCE_BINDING_V2.json` and are deliberately
left byte-unchanged. This correction is recorded on the navigation surface
only.

# ORION-03 Round 2 result — X.509 trust-store merge (terminal + claim boundary)

Results commit (this file + byte-deterministic receipts). Chronology:
freeze `56fc0772` -> amendment `c6e26da1` -> results commit (this).

- Receipts: `ROUND2_RESULTS_V2.json`
  sha256 `4b2ea6360b6af60abfdaadccb8e0d15c87023910da785cacf6bddd408a34a1f6`,
  `COST_ROUND2_V2.json`
  sha256 `d28225820d89439565a0c9f77f56b4a04a25a50b29ce27a2e84837a97a9a2f39`.
- Task manifest unchanged across every evaluator revision:
  `TASK_MANIFEST_V2.json`
  sha256 `ff54dbd02346d8369a4fa11e71ba179cb74fedfcad8280c97dd47e3dc29e5aff`.
- Engine: OpenSSL 3.6.4 (tag `openssl-3.6.4`, commit
  `d3c1b1169b3569ff3069e5b399f47b2b28e03d79`), built from the sha256-verified
  tarball; `OpenSSL 3.6.4 25 Aug 2026 (Library: OpenSSL 3.6.4 25 Aug 2026)`.
- Determinism C2: two complete back-to-back runs produce byte-identical
  receipts (`run1.log`, `run2.log`; `ROUND2_RESULTS_V2.run2.json` is the
  second run's copy, byte-equal to the committed one).

## Terminal

**`D_R2_REAL_AUTHORITY_PROMOTION_ERROR_PREVENTED`** — earned, on
engine-adjudicated upstream materials.

Terminal reason (receipt): "46 engine-adjudicated hybrid authorizations on
upstream-authored materials; M1 authorizes all of them, M5 blocks all with
the first-mixing reason, engine output carries no origin distinction."

This satisfies #1541's external/domain adjudication requirement: the
adjudicating authority is the OpenSSL engine on the OpenSSL project's own
authored test materials and labels — a public, independent, pinned
maintainer of the domain semantics — not an ORION-authored judge.

## Primary measurements (1962 tasks: 1858 F-U + 104 F-P)

| Method | allows | unsafe merges | needless rejections |
|---|---|---|---|
| M1 flat/textual union (deployed merge) | 810 | **46** | 379 |
| M2 intersection | 250 | 0 | 970 |
| M3 reject-all | 0 | 0 | 1143 |
| M4 ours-preference (side B) | 699 | 0 | 444 |
| M5 typed origin-witness (ORION) | 1143 | **0** | **0** |

Union-authorized tasks: 810. Parent-authorized: 1143. Engine hybrids
(`vU AND NOT vA AND NOT vB`): **46** (42 F-U, 4 F-P).

Obstruction detection: precision 1.0, recall 1.0, false flags on
single-origin-complete union-authorized tasks: **0** (C5 green, 764
non-hybrid union-authorized tasks, all unflagged).

Invariant: M5's decision equals parent authorization on every task
(`m5_decision_equals_parent_authorization: true`) — the typed layer is
exactly the union of the single-origin closures, never more, never less.

## The 46 hybrids (what flat merge manufactures)

Every hybrid localizes at boundary index 2 from the leaf:

- 42 F-U tasks, all link `(ca-cert, root-cert)`: two upstream-authored
  partial-chain store states, each holding the leaf `ee-cert` + intermediate
  `ca-cert` under `-partial_chain` with a DIFFERENT non-self-same trusted
  anchor set; each origin's closure fails, the union anchors. 41 of these
  are `POLICY` kind (structure derivable per origin; only the trust
  admission differs); one (`FU-1588`) is `STRUCTURAL`: the leaf side is
  held by origin B alone, so neither origin derives even the chain shape.
- 4 F-P tasks (parity split of the vendored corpus): leaves `ee-name2` /
  `ee-pss-cert`, links `(ca-name2, croot+anyEKU)` / `(ca-pss-cert,
  croot+anyEKU)`: leaf+intermediate land in one parity origin, the
  engine-attestable root anchor in the other.

In every hybrid, both single-origin engine runs fail; the concatenated
store authorizes. `openssl verify` output carries no origin distinction —
this is the residual the typed layer earns.

## Controls (all green)

- **C1 upstream anchoring**: 191 rows, 186 agree (97.38% >= 95% gate). The
  5 disagreements are the FIPS-provider rows carrying the perl runtime token
  `@prov` (documented pre-run in PROTOCOL_V2 §9; not statically executable
  — counted as disagreements, never excluded). 1 row excluded at freeze
  (setup.sh-generated material), 1 `exit_checker` row engine-flipped as
  documented.
- **C2 determinism**: byte-identical receipts across two full runs.
- **C3 white-box witness agreement**: 0 violations across all 1962 tasks
  (after the documented depth-0 anchor repair; one-directional soundness).
- **C4 retraction non-resurrection**: all 3 upstream CRL adjudications fail
  with their upstream-grepped stderr markers (delta-as-complete x2,
  CVE-2026-28388); positive control authorizes without `-crl_check`;
  parents, union-with-CRL, the operational cert-only flat merge, and the
  intersection all deny (0 resurrections). CRL side-files dropped by
  `cat`-style merges do not resurrect revoked chains here because the
  hybrid mechanism requires path re-anchoring, not retraction loss — the
  receipt records both mechanisms separately.
- **C5 no-flag on complete-alternative-origin**: 0 false flags.
- **C6 hostile first-mixing control**: detected and localized with the exact
  boundary link (`ee-cert, ca-cert | root-cert`), ORION-labeled mechanics
  only.

## Cost (COST_ROUND2_V2.json)

- Measured unique engine verify invocations: 2458 (cache-backed;
  8159 requested). Graph probes: 1468. Engine wall time 33.6 s (total run
  41.7 s) on one LUNARC core.
- Required invocations per 1962 tasks: M1 1962, M2 1962, M3 0, M4 1962,
  M5 3924 (2x flat: both origins' closures), ground-truth basis 4 per task.
  The typed layer's honest price is exactly 2x the flat merge's engine cost
  on this corpus, with zero unsafe merges and zero needless rejections
  against M1's 46 unsafe + 379 needless and M3's 1143 needless.

## Independent reproduction

`INDEPENDENT_REPRO_R2.json` + `repro_independent.py`: a context-free agent
wrote its own checker from PROTOCOL_V2 §3-5 (no import of `run_round2.py`),
re-derived vA/vB/vU/vI for all 1962 tasks, and compared its hybrid set
against the receipt. Result recorded in the receipt file; the reproduction checklist
in the PR body carries the outcome.

## Final claim boundary (binding)

EARNED: on upstream-authored OpenSSL 3.6.4 test materials, with the pinned
native engine as adjudicator, flat textual trust-store merge authorizes 46
of 810 union authorizations that NO originating store authorizes; the typed
origin-witness layer (vA OR vB) blocks exactly those 46 (precision/recall
1.0) while preserving every single-origin authorization (0 needless
rejections), at 2x the flat merge's engine cost.

NOT CLAIMED: no specific production incident, whole-PKI or WebPKI security
claim, external human review, novelty of X.509 chain building itself,
performance superiority, or journal/submission authority. C6 remains an
ORION-authored mechanics control, not domain evidence. The engine stays
authoritative for all X.509 semantics once stores are fixed; ORION's
positive is exactly the origin distinction the engine output does not
carry.

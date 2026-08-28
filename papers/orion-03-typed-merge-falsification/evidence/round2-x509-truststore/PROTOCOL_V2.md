# ORION-03 Round 2 — frozen X.509 trust-store merge protocol

Protocol freeze date: 2026-08-27
ORION event base: `origin/main@fe1313ef` (Round 1 base was `27ea5e1b`)
Round: canonical ORION-03 Round 2 of at most 3 (#1514)
Protected Task-3 / ORION-19 paths: excluded

## 1. Scientific question

Round 1 (#1549) terminated `D_R11_POLICY_REQUIRES_RICHER_SEMANTICS`: the Cedar
corpus carries no upstream evidence/licence/retraction provenance. #1514 Round 2
therefore requires a different permission-bearing corpus in which provenance and
retraction are NATIVE.

X.509 chain validation is that corpus class. Every certificate carries issuer
provenance (issuer/AKI/SKI chain of issuance), every trust store carries explicit
origin anchors, and retraction (revocation) is a native, engine-enforced
mechanism (CRLs). The operational merge is real and deployed: two organizations'
trust stores are concatenated (`update-ca-certificates`, container base-image
merges, M&A store reconciliation).

Question: on upstream-authored PKI materials adjudicated by the pinned native
OpenSSL engine, does flat textual trust-store merge authorize chains that
NO originating store authorizes (first-mixing / hybrid authorizations), and does
the typed origin-witness layer (R12 calculus) block exactly those authorizations
while preserving every single-origin authorization?

The OpenSSL engine remains authoritative for all X.509 semantics once stores are
fixed. ORION may earn a real-domain positive only for a distinction the engine
output itself does not carry: `openssl verify` reports OK/FAIL only and never
reports whether an OK arose only through cross-origin mixing.

## 2. Frozen source and complete selection

Public official repository `openssl/openssl`, release tag `openssl-3.6.4`
(GitHub-verified commit `d3c1b1169b3569ff3069e5b399f47b2b28e03d79`). Source
tarball `openssl-3.6.4.tar.gz` sha256
`9bffaa1ad1e07b354c21bd3324ec02fa15579f45a7d0494b3e74bc449b7333ef`.

License: Apache License 2.0 (OpenSSL Project Authors). Attribution in
`THIRD_PARTY_SOURCE.md`. Vendored bytes are unmodified and individually bound in
`SOURCE_BINDING_V2.json`.

Selection (complete, frozen):

- the complete `test/certs/` public material at that tag under a content-based
  rule: a file is vendored iff it contains at least one CERTIFICATE /
  TRUSTED-CERTIFICATE / X509-CRL PEM block and no private-key block. This
  vendors 252 files (247 certificate-bearing, 5 CRL-only) and excludes 110
  (89 private-key files, 17 auxiliary non-certificate files, 4 public-key-only
  files); the per-file exclusion list with reasons is frozen in
  `EXCLUDED_FILES.txt`. Name-based filtering was rejected: it wrongly drops
  certificates whose filenames merely contain "key" (keyCertSign /
  anyExtendedKeyUsage variants referenced by the upstream table).
- the complete upstream labeled verify table
  `test/recipes/25-test_verify.t` at that tag: 192 `verify()` rows parsed.
  One row (`pc6-cert`) references material that `test/certs/setup.sh`
  generates at test runtime and is therefore absent from the tag snapshot;
  that row is excluded with the reason frozen in the manifest, leaving 191
  usable upstream-authored labels. One `ok(verify(...))` row
  (`bad-othername-namec`) sits inside a `with({ exit_checker ... })` block
  that asserts a nonzero engine exit; its engine-level expectation is
  INVALID and is recorded as flipped.

No fixture may be added or removed after the freeze commit.

The native engine is OpenSSL 3.6.4 built from the same pinned tarball
(`util/opensslv.h` at that tag), built by the recorded fail-closed recipe,
identical on LUNARC and CI so receipts replay byte-exactly.

## 3. Frozen systems (methods)

A *store state* is a pair `(trusted, untrusted)` of certificate sets plus a
frozen option list. `engine(state)` = `openssl verify -auth_level 1
[-purpose p] [opts] -trusted ... -untrusted ... <leaf>`; exit 0 = authorized.
Every invocation is hermetic (`-no-CAfile -no-CApath -no-CAstore`): an
origin with an empty trust list denies; it never falls back to the host
system trust store (which would make verdicts machine-dependent). CRL-only
files are retraction material passed via `-CRLfile` and are never store
members (the engine rejects cert-less files in `-trusted`/`-untrusted`).

Merge task = (leaf, purpose, opts, stateA, stateB). Methods:

1. **M1 flat/textual union merge** — the deployed operational merge
   (`cat storeA.pem storeB.pem`): trusted = A∪B, untrusted = A∪B;
   decision = engine(union).
2. **M2 conservative intersection merge** — common-trust reconciliation:
   trusted = A∩B (by corpus file identity), untrusted = A∩B;
   decision = engine(intersection).
3. **M3 conservative reject-all** — fail-closed conflict policy: every task
   yields DENY/CONFLICT; no merged store is produced.
4. **M4 ours-preference textual merge** — resolve the textual conflict by
   taking side B wholesale (the common manual git resolution);
   decision = engine(B).
5. **M5 typed origin-witness merge (ORION)** — merged store = union, but an
   authorization is licensed iff at least one single origin's independent
   closure derives it: decision = engine(A) OR engine(B). When engine(union)
   is OK while both single-origin closures fail, M5 emits
   `BLOCKED_FIRST_MIXING` with the first-mixing chain localization
   (boundary link where leaf-side and anchor-side origins separate).

M5 is the R12 origin-witness/first-mixing calculus instantiated on chains: a
certificate chain is an acyclic positive derivation, origins are stores, and
`W(x)` = origins whose independent closure derives `x`.

## 4. Frozen merge-task families

Constructed mechanically before any merge evaluation; manifest digested and
committed in the freeze commit.

- **F-U upstream-pair family**: parse the upstream labeled table; each
  `ok(verify(leaf, purpose, trusted, untrusted, opts...))` row is an
  upstream-authored store state. Group states by (leaf, purpose, opts);
  every unordered pair of distinct states within a group is one merge task
  (two originating authorities' stored views of the same request).
- **F-P parity-partition family**: the operational two-organization split.
  Universe = vendored certificate-bearing files, sorted by filename; origin A
  = even-index certs, origin B = odd-index certs; each origin state trusts
  and distributes exactly its own certs. Tasks = every `ee-*` leaf cert ×
  purposes {`sslserver`, ``}.

Evaluation time: F-U/F-P rows carrying their own upstream `-attime` keep it
(their group key shares it, so paired states are evaluated at one instant);
rows without one are evaluated at the frozen `-attime 1759276800`
(2026-08-27T00:00:00Z), so no verdict depends on the host clock.

## 5. Frozen primary measurements

Engine-computed ground truth per task: `vA = engine(A)`, `vB = engine(B)`,
`vU = engine(A∪B)`, `vI = engine(A∩B)`.

- hybrid task: `vU AND NOT vA AND NOT vB` (authorization manufactured purely
  by the merge; neither origin ever vetted it);
- parent-authorized task: `vA OR vB`;
- unsafe merge (per method): decision = ALLOW on a hybrid task;
- needless rejection (per method): decision = DENY on a parent-authorized task;
- obstruction detection (M5): flagged set vs hybrid set (precision/recall) and
  false-flag count on non-hybrid union-authorized tasks;
- cost: engine invocation counts per method and total wall time.

## 6. Required controls

1. **C1 upstream-table anchoring**: re-execute every upstream `verify()` label
   with the pinned engine (upstream's own arguments, frozen `-attime` where the
   upstream row is time-independent); report exact per-case agreement.
2. **C2 determinism**: the complete evaluation runs twice; receipts must be
   byte-identical.
3. **C3 white-box witness agreement**: witness sets computed by independent
   issuer-graph closure (subject/issuer + AKI/SKI edges) must agree with the
   black-box engine per-origin verdicts on every task.
4. **C4 retraction non-resurrection**: re-execute the OpenSSL project's own
   CRL adjudications with upstream's exact option lists (delta-CRL-as-complete
   ×2, CVE-2026-28388) — each must fail with its upstream-grepped stderr
   marker, and the delta chain must authorize without `-crl_check` (positive
   control). Merge measurement: origin A carries the retraction material,
   origin B does not; parents, union (with A's CRL bytes), the operational
   cert-only flat merge (concatenated cert bundles drop CRL side-files), and
   the intersection must all deny.
5. **C5 complete-alternative-origin no-flag**: on union-authorized tasks where
   some single origin already authorizes (R12 property 4), M5 must NOT flag.
   Measured across all tasks, not on synthetic data.
6. **C6 hostile first-mixing control (ORION-labeled, not domain evidence)**:
   deliberately split upstream chain material across two stores; M5 must flag
   with the exact first-mixing boundary link. As in Round 1, ORION-authored
   controls separate the mechanics but cannot self-authorize a domain positive.

## 7. Honest terminals

- `D_R2_REAL_AUTHORITY_PROMOTION_ERROR_PREVENTED` — ≥1 engine-adjudicated
  hybrid task exists on upstream-authored materials; M1 authorizes it, M5
  blocks it with the registered first-mixing reason, and the native engine
  output carries no origin distinction.
- `D_R2_NATIVE_VERIFIER_ALREADY_SUBSUMES_RESIDUAL` — the engine output itself
  already exposes the origin distinction.
- `D_R2_TYPED_UNTYPED_EQUIVALENT` — no hybrid task exists on real materials
  (flat and typed decisions coincide).
- `D_R2_POLICY_REQUIRES_RICHER_SEMANTICS` — the corpus cannot adjudicate.
- `CANNOT_CHECK_INDEPENDENT_DOMAIN_ADJUDICATION`

## 8. Claim boundary

Any positive terminal is a mechanism demonstration on upstream-authored
corpus materials with the pinned native engine: it does not claim a specific
production incident, whole-PKI security, external human review, novelty of
X.509 chain building, or journal/submission authority.

## 9. Post-freeze amendment (before any results; repair commit follows 56fc0772)

The first diagnostic execution after the freeze commit surfaced a gap in the
C3 white-box model, not in the corpus or the task manifest (both unchanged;
TASK_MANIFEST_V2.json sha256 stays
ff54dbd02346d8369a4fa11e71ba179cb74fedfcad8280c97dd47e3dc29e5aff):

- 18 of 1962 tasks triggered C3 disagreements, every one of them an
  upstream `-partial_chain` row of the "last-resort direct leaf match" family
  (upstream recipe rows 227-239). Under `-partial_chain`, the engine also
  anchors a chain at depth 0 when the store contains a certificate with the
  SAME subject and SAME public key as the leaf — even when it is a different
  file (ee+serverAuth vs ee-cert) — while the white-box model only modeled
  issuer-chain termination at a trusted certificate.
- Repair: the structural model gains the second anchor rule (zero-length
  chain on subject+SPKI identity; SPKI = sha256 of the DER SubjectPublicKeyInfo).
  Purpose/EKU/trust admission on the anchor remains deliberately unmodeled
  (policy, not structure): C3 keeps its one-directional soundness
  (engine-valid implies structurally derivable). All 18 disagreements
  resolve; no corpus byte, task, or expected label changed.
- C1 note recorded for the results commit: 5 of 191 upstream rows sit in the
  FIPS-provider SKIP block and carry the perl runtime token `@prov`; they are
  not statically executable and are honestly counted as disagreements
  (anchor rate 186/191 = 97.38% >= 95% gate with them included).
- Second diagnostic pass (same pre-results window; lands with the results
  commit): the first-mixing LOCALIZATION (an M5 reason payload, not a frozen
  §5 measurement) initially selected chains by lexicographic path enumeration
  through the corpus root family (~35 same-subject/same-key root variants form
  a fully interconnected clique, so naive enumeration explodes and picks
  degenerate long chains). The evaluator now (a) terminates enumeration at
  self-signed roots (the engine never builds past one), (b) caps depth at 8
  defensively (corpus chains are <= 4 deep), and (c) filters candidate chains
  to engine-attestable ones for the SAME option list (depth-0 zero-length
  chains only under `-partial_chain` or a self-signed trusted leaf;
  positive-length chains must terminate at a SELF-SIGNED trusted anchor,
  matching the empirically established default-anchoring semantics). No
  frozen §5 measurement changed: every decision verdict, the 46-hybrid set,
  unsafe/needless counts, and all C1-C6 outcomes are identical before and
  after; `run_round2.py` and this protocol's digests in SOURCE_BINDING_V2.json
  are updated together in the results commit. Cost receipts gained explicit
  counters (`engine_verify_invocations_requested`,
  `per_method_required_invocations`, `ground_truth_basis_invocations_per_task`);
  the measured unique-invocation count was already cache-backed and unchanged.

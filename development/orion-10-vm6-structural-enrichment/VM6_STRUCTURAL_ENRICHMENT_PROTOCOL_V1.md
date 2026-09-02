# VM6 — Structural Psi-side enrichment, recorded before outcomes (PROTOCOL V1)

Status: FROZEN BEFORE ANY OUTCOME COMPUTATION. This file, plus the driver
`research/extensions/orion-10-vocabulary/vm6_structural_enrichment.py`, is the
registration artifact. No result row exists at registration time.

- Paper: orion-10 (certified static forecasting)
- Lane directory: `development/orion-10-vm6-structural-enrichment/`
- Study id: `VM6_STRUCTURAL_ENRICHMENT`
- Parent result: `papers/orion-10-certified-static-forecasting/theory/vocabulary-minimality-v5-unselected-fibres/RESULT_V5.md`
  (terminal `FIBRE_CONSTANCY_REFUTED_ON_UNSELECTED_POPULATION`)
- Parent revival directive: `.../vocabulary-minimality-v2-full-census/REVIVAL_PASS_V1.md`,
  improvement path #3.
- Frozen machinery: `.../vocabulary-minimality-v4-per-panel-dedupe/run_per_panel_v4.py`
  (imported unmodified; see §2), its receipt `RUN_3561900_RAW.json.gz`
  (decompressed sha256 `28a760c7b4abb552cb9c4cd66c705bd070c21c4332b5330d7b53191e8ee7857f`).

## 1. Aim

V5 established, on the unselected 13,458-row population of the frozen V4 census,
that cost (`C_Dxx`) is NOT constant on every `f_Bprime` fibre: by the
certificate-explanation-gap-v1 Theorem 2, no function of `f_Bprime` alone is an
exact cost explanation, and Theorem 3 says the only productive moves are (a)
enlarge Psi with a separating structural primitive, or (b) prove a
vocabulary-level lower bound.

REVIVAL_PASS_V1 improvement path #3 names move (a) precisely, and states the
admissibility condition this study obeys: the enrichment feature must not be
computed from cost (no circularity), and the census should record Psi-side
invariants BEFORE outcomes. The V4 census recorded only `f_Bprime`, three costs,
`gap4`, `regime`, `panel` — every one of those enrichments is inadmissible
(V2 enrichment table: `f_B'+regime / gap4 / C_Dplus / C_DP / panel`).

This study (VM6) supplies the missing structural record. It replays the frozen
enumeration (derivation + canonical key only — no outcome search), binds each
replayed instance positionally to the frozen receipt row, computes a
pre-registered family of cost-independent structural features for every
instance, and asks the Theorem-1/2 question for each candidate vocabulary in
the registered family.

## 2. Frozen definitions (imported machinery only — no math is copied)

Everything below is imported at runtime from the frozen module
`run_per_panel_v4.py` at the registration SHA; the driver re-implements nothing:

- `derive_instance`, `canonical_key`, `instance_from_key`, `evaluate`,
  `_clear_instance_caches`, `SKELETON_BUILDERS`, `CAPS`, `PANEL_ORDER`;
- the module's own imports (`p10`, `r6m`, `r6o`, `r6p`, `r6s`, `qg5b`) resolve
  because the driver pre-inserts `research/extensions/orion-q` and
  `research/extensions/orion-qg` on `sys.path` BEFORE importing (the module's
  internal `theory/orion-q` path no longer exists; this is a path fix, not an
  edit — the module file is byte-identical to the merged main version, verified
  by a hard assert on its sha256).
- Enumeration control flow: the driver replicates ONLY the loop structure
  (template-pair-major iteration, cap semantics, dedupe set reset per panel)
  using the imported builders and the module-level pair-list functions
  (`template_pairs`, `template_pairs_h5`, `qg5b` support masks). This loop was
  verified in smoke tests to reproduce every receipt panel counter exactly.
- Costs and all outcome quantities come from the receipt rows; the imported
  `evaluate()` is used ONLY for binding controls (gate G3), never as a data
  source for the constancy analysis.

## 3. Registered questions

Q1 (primary). For which registered vocabularies Psi (§4) is `C_Dxx` constant
on every Psi-fibre of the 13,458-row population? (Theorem 1: exact Psi-only
explanation exists iff yes. Theorem 2: any fibre with mixed cost refutes.)

Q2 (secondary, diagnostic only — carries no terminal weight). Which single
registered feature separates most (largest reduction in cost-mixed-fibre
mass), and what do the surviving worst pairs look like structurally?

Q3 (control). Does `C_DP == C_Dxx` hold on all 13,458 receipt rows (V5's
population fact, re-verified through the replay binding)?

## 4. Registered feature family (frozen; no subset search after the fact)

All features are functions of the instance's letters alone (cost never enters).
Let `key = canonical_key(instance)` be the frozen canonical representative
(letters per qubit, minimised over the frozen `LETTER_PERMS` and qubit
relabeling). Well-definedness on the canonical key is gate-checked (G4).

For every one of the 13,458 instances, compute and serialise:

- `n` — qubit count (3 or 4).
- `weights` — tuple of the six target weights in canonical row order (for each
  of the six target rows of the canonical key, the number of qubits whose
  letter is non-identity). Row order is fixed by canonicalisation, so no
  further sorting is applied.
- `column_supports` — tuple of per-qubit column support sizes in the canonical
  key's column order (for each qubit, how many of the six rows are
  non-identity on it); the column order is already canonical (sorted by
  `canonical_key`).
- `letter_multiset` — sorted tuple of all letters in the canonical key,
  flattened and encoded I=0, X=1, Y=2, Z=3.
- `commutation_matrix` — the pairwise symplectic commutation matrix of the
  key's rows: entry (i,j) = 1 iff rows i,j commute (mod-2 symplectic inner
  product of their binary symplectic vectors is 0). Invariant under
  `LETTER_PERMS` (distinct non-identity single-qubit Pauli letters always
  anticommute, so the letter-form of the symplectic form is preserved) and
  under qubit relabeling (mod-2 sums preserved). Gate G4 checks equality
  against the pre-canonicalisation instance on a registered sample.
- `pair_commute` — tuple of the three target-pair commute bits in canonical
  row order, for the pairs (t0,t1), (t2,t3), (t4,t5) (function of the matrix
  above; subsumed by it, registered separately for readability).

Registered candidate vocabularies Psi (all include `f_Bprime`; the question is
whether a structural primitive separates the mixed fibres):

| id | Psi |
|----|-----|
| B0 | {f_Bprime} (V5 baseline — must reproduce REFUTED) |
| S1 | {f_Bprime, n} |
| S2 | {f_Bprime, weights} |
| S3 | {f_Bprime, column_supports} |
| S4 | {f_Bprime, letter_multiset} |
| S5 | {f_Bprime, commutation_matrix} |
| S6 | {f_Bprime, pair_commute} |
| C  | {f_Bprime, n, weights, column_supports, letter_multiset, commutation_matrix} |
| DIAG-g | {g} alone for each single feature g (secondary diagnostics, Q2 only) |
| CONTROL | {canonical_key} (must be constant on fibres; never a candidate) |

No other vocabulary may be reported as a finding. If every S1..S6 and C fails,
the study says so — it does not search further.

## 5. Hard gates (executed as asserts; failure => CANNOT_CHECK, never a verdict)

- G1 receipt integrity: decompressed sha256 of `RUN_3561900_RAW.json.gz` equals
  the frozen value above; `full_census_rows_v2` has exactly 13,458 rows.
- G2 replay fidelity: per panel (10 panels), the replay's counters
  (evaluated, raw_scanned, zero_target_skipped, duplicate_skipped, cap_hit)
  equal the receipt panel summary, and the replayed row sequence aligns with
  the receipt rows (panel + local_index) exactly, cursor-consumed in order.
- G3 binding controls: for the registered probe set — local_index in
  {0, evaluated//2, evaluated-1} for each of the 10 panels (30 probes; ~1.8 s
  per n=4 evaluation, ~0.2 s per n=3, well inside the run budget) — the
  imported frozen `evaluate()` reproduces the receipt row's `C_DP`, `C_Dxx`,
  `C_Dplus`, `f_Bprime`, `gap4`, `regime` exactly.
- G4 feature well-definedness: for the registered sample (every 500th replayed
  row plus every probe row), `canonical_key(instance_from_key(key)) == key`
  (round-trip) and `commutation_matrix(instance_from_key(key)) ==
  commutation_matrix(instance)` (canonical invariance).
- G5 cross-panel key consistency: every canonical key appearing in two or more
  panels carries identical receipt `(C_DP, C_Dxx, C_Dplus, f_Bprime)`.
  (This is simultaneously the discrete-vocabulary control: a full canonical
  key is an exact vocabulary iff its fibres — the key collision classes — are
  cost-constant.)
- G6 anti-instrument: (a) AST gate over the driver's feature functions
  (`feature_*`): their subtrees reference no cost-machinery symbol
  (`evaluate`, `r6m`, `r6o`, `r6p`, `r6s`, `qg5b`, `p10`, `C_D`, `f_Bprime`,
  `gap4`, `regime`); (b) staged output — the full feature table is computed
  and its sha256 written to the run log BEFORE any constancy computation
  starts.
- G7 population fact: `C_DP == C_Dxx` on all 13,458 receipt rows.

## 6. Pre-recorded prediction (before any outcome computation)

Primary prediction: `NO_REGISTERED_STRUCTURAL_ENRICHMENT__BPRIME_MIXING_SURVIVES_ALL`
— every S1..S6 and C has at least one cost-mixed fibre. Secondary: the
commutation matrix (S5) reduces cost-mixed mass the most among single
features, and every worst pair surviving C differs by a local letter
substitution that preserves all registered invariants. Both statements are
falsifiable by this run; either outcome is publishable as-is.

## 7. Terminals (frozen at registration)

1. `STRUCTURAL_ENRICHMENT_EXACT__SEPARATING_PRIMITIVE_FOUND` — at least one of
   S1..S6 or C has zero cost-mixed fibres (and B0 still REFUTED). Report every
   satisfying vocabulary and the fibre-count-minimal one as headline.
2. `NO_REGISTERED_STRUCTURAL_ENRICHMENT__BPRIME_MIXING_SURVIVES_ALL` — every
   S1..S6 and C has at least one cost-mixed fibre. Serialise the worst
   surviving pair under C (largest cost gap within a C-fibre): both canonical
   keys, all features, both costs, both panels, both local indices, plus the
   per-vocabulary mixed-fibre mass table.
3. `CANNOT_CHECK__REPLAY_BINDING_FAILED` — any of G2/G3/G4/G5/G7 fails
   (replay does not reproduce the frozen run; the binding methodology is
   void). G1 failing raises `CANNOT_CHECK__RECEIPT_DIGEST_MISMATCH`.

## 8. Artifacts

- Registration commit: this protocol + the driver only. NO results.
- Outcome commit: `development/orion-10-vm6-structural-enrichment/RUN_VM6.log`
  (raw run log), `RESULT_VM6.json` (canonical JSON: schema id
  `ORION10.VM6_STRUCTURAL_ENRICHMENT.v1`, base_revision, protocol_sha256,
  result_digest, per-vocabulary fibre tables, worst-pair witness, gates),
  `RESULT_VM6.md` (human summary with one-stage failure attribution and a
  named revival lever).
- Run command: `timeout 3600 python research/extensions/orion-10-vocabulary/vm6_structural_enrichment.py`
  executed at the registration SHA in the lane worktree.

## 9. Authority limits (binding on every claim this study makes)

- Finite-population statement over the frozen V4 census (13,458 instances,
  10 registered panels, unit-cost R6M grammar at the frozen config). NOT an
  all-n statement; no promotion of any strategy or deployment.
- `novelty_authority = false`; `physical_quantum_advantage_claim = false`.
- A `STRUCTURAL_ENRICHMENT_EXACT` terminal licenses exactly: "on this
  population, Psi := f_Bprime + <feature> admits an exact cost table" —
  nothing about physical implementations.
- A negative terminal is evidence toward (but not a proof of) the
  vocabulary-level lower bound of certificate-explanation-gap-v1 Theorem 3 /
  UVM2's named-vocabulary question; it does not close it.

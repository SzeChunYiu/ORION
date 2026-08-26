# P11 query-family phase ledger addendum V1

Additive evidence-ledger entry for the ten-responsibility query-family/phase
experiment (programme #977 gap wave). `CLAIM_EVIDENCE_LEDGER.md`,
`README.md` and `P11_ACTIVE_CLAIM_AUTHORITY_V1.json` are being edited by open
PR #993; this addendum carries the gap-wave outcome additively and is to be
folded into the central ledger/README in the post-#993 integration pass
(task #17 manuscript-collision absorption stack).

## Entry

- **Study:** `P11_QUERY_FAMILY_PHASE_V1` (protocol frozen on main in #978, commit `9fc55f68`).
- **Execution:** PR #996, run `32663348906` via `p11-query-family-phase-binding-v1` (verdict-agnostic binding workflow; frozen runner/verifier executed byte-for-byte, unmodified; artifact ID `9499617317`).
- **Prior observation (reconciled 2026-08-23):** the earlier harness `p11-query-family-phase-v1.yml` (#978) executed the same frozen runner on PR #994's head `aedcaf93` — run `32661332644`, conclusion FAILURE at 2026-08-23T19:31:51Z. The failure is the runner's own `assert positive` firing after full completion, i.e. the same preregistered negative, NOT a harness/dependency defect (identical pinned env and runner blob `7b5d13fe…`; no artifacts were captured and the log's assert message was truncated, so it cannot serve as the bound receipt). Runs `32661332644` (first observation) → `32663348906` (authoritative binding) → `32664737225` (final-head re-verification) form the execution chain.
- **Terminal:** `P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET` — the preregistered 8/10 aggregate quality bar fails in every access class (LINEAR 3/10, RBF 5/10, KNN 5/10) while both frozen resource identities hold exactly (memory crossover U<=4; linear break-even growth 1917..19169).
- **Receipt:** `P11_QUERY_FAMILY_PHASE_RESULT_RECEIPT_V1.md` (+ raw JSONs: `p11_query_family_phase_primary_v1.json` sha `9a1f1f9b…`, `p11_query_family_phase_independent_v1.json` sha `b1e92a6b…`, `p11_query_family_phase_binding_v1.json` sha `0c944d62…`) in this directory.
- **Claim impact:** bounds the P11 "compile/cache/materialize as a placement win" narrative — the single-responsibility learned-compiler result does not generalize across a ten-query family on digits; compile-tolerance is a per-(responsibility x access-class) property held by at most 5/10 family members. The resource/phase-diagram identities themselves are *confirmed*, not damaged. Any manuscript sentence claiming family-scale compilation support on non-synthetic data must be removed or conditioned on "small (U<=4) and individually compile-tolerant responsibility sets".
- **Retune policy:** none performed; preregistered thresholds (0.02 per-query tolerance, 8/10 aggregate rule, frozen U/H grids) untouched; the negative is retained and characterized, per programme rule.

## What closes / what opens

- **Closes:** the "stronger access class rescues compilation" escape hatch (RBF/KNN recover only q2/q7; q1, q3, q5, q8, q9 fail under all three classes); the doubt about the frozen phase algebra (all 70 rows correct in both implementations).
- **Opens:** a selector-stability question (q3 selects a different 16-coordinate set in every fold yet compilation still fails on difficulty grounds — stability is not the discriminator here); a k-sweep (k=24/32) is NOT authorised by this result and would be retuning unless preregistered as a new protocol with its own frozen thresholds; the boundary statement gives the precise condition under which compilation remains defensible (U<=4 AND per-member tolerance).

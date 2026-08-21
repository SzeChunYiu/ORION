# ORION-Q N1-D frozen protocol — representation-changing edit (fresh re-execution)

Date frozen: 2026-08-21
Lane: ORION-Q N1 (issue #674), family N1-D
Registered design source: issue #674 body ("N1-D — representation-changing edit") and issue
comment 5355080062 (the original N1-D execution record, never committed).
Status of this document: protocol frozen BEFORE the result-bearing run of
`research/extensions/orion-q/nlanes/n1d_representation_frame_edit.py`.

## Standing

Fresh re-execution of the registered continuous frame-change family. Original recorded numbers
(0/2000 menu, 2000/2000 generated with max residual 5.08e-16, 2000/2000 eigendecomposition with
max residual 1.01e-15) are prior registration, not this run's data. Diagnostic authority only.

## Frozen synthetic world

- 2,000 held-out one-qubit targets `U(phi, theta) = Ry(phi) Rz(theta) Ry(-phi)` with continuous
  parameters drawn deterministically from `numpy.default_rng(20260821)`:
  `phi ~ Uniform(-1.4, 1.4)` rejected while within 0.02 of any menu value below (avoids borderline
  ties), `theta ~ Uniform(0.2, 2.9)` (avoids the identity/degenerate spectrum).
- Incumbent method language expresses only diagonal `Rz` in its current frame; a target counts as
  reached iff some frame `W` makes `W U W^dagger` diagonal.
- Exact verifier: max off-diagonal magnitude of the conjugated operator; solve tolerance `1e-12`.
- Round-trip control (registered): `max|W^dagger (W U W^dagger) W - U| <= 1e-12`.
- Conversion cost charged (registered): each frame conjugation attempt costs 1 unit; per-arm mean
  cost reported.

## Arms

1. **FINITE_FRAME_MENU (old-QC2-style incumbent edit list):** frames `W_m = Ry(-m)` for
   `m in {-pi/2, -pi/4, 0, pi/4, pi/2}`; success iff any menu frame diagonalizes to tolerance.
2. **GENERATED_FRAME_EDIT (candidate mechanism):** from the visible target operator compute the
   Pauli decomposition `a_k = tr(sigma_k U)/2 = -i sin(theta/2) n_k`, recover the rotation axis
   `n` (its y-component must vanish to 1e-10, asserted per instance), set
   `phi_hat = atan2(n_x, n_z)`, apply the single generated frame `W = Ry(-phi_hat)`.
3. **EIGENDECOMPOSITION_PARENT (canonical linear-algebra donor, first right of refusal):**
   `numpy.linalg.eig`, eigenvectors normalized and ordered canonically by eigenvalue phase; success
   iff `V^dagger U V` is diagonal to tolerance and `V` is unitary to 1e-10.

All arms see the same information: the full exact 2x2 target operator (registered control: same
information before/after the representation edit; no arm receives `phi` or `theta`).

## Prespecified gates

- `G1_WORLD_VALID`: finite menu solves 0/2000 (continuous frame genuinely outside the menu).
- `G2_GENERATED_EXACT`: generated frame edit solves 2000/2000, max residual <= 1e-12.
- `G3_ROUND_TRIP`: round-trip max error <= 1e-12 on all generated-frame solves.
- `G4_PARENT_DECISION`: eigendecomposition parent solve count vs generated arm.

## Terminal rule (frozen)

- G1 fails: `N1D_WORLD_INVALID`.
- G2/G3 pass and parent >= generated: `N1D_CANONICAL_TRANSFORM_PARENT_SUFFICIENT`
  (registered expected outcome; negative retained — root cause `KNOWN_TRANSFORM_PARENT_SUFFICIENT`).
- G2/G3 pass and parent < generated: `N1D_REPRESENTATION_EDIT_VALUE` (bounded).
- G2 fails: `N1D_NO_INCREMENTAL_VALUE`.

## Claim boundary

Exact-synthetic scope only. Diagonalization by canonical transforms is an acknowledged donor; no
representation-invention, novelty, P10, or real-quantum claim is authorized by any terminal.
Receipt line `ORIONQ_N1D_REPRESENTATION_EDIT=<canonical sorted json>`; pretty receipt at
`research/extensions/orion-q/nlanes/N1_D_REPRESENTATION_EDIT_RESULTS.json`.

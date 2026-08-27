# FiberGuard R20 BNSL authority correction

Date: 2026-08-27
Owner: #1533 / #1512
Status: POST-OUTCOME AUTHORITY CORRECTION — raw execution preserved

## Bound execution

- workflow: `FiberGuard R20 BNSL adaptive`
- run: `33049783681`
- job: `98442186836`
- executed PR merge subject: `28ae1b9f02c7ce39a7a71bc2dddde977cf8e3ec2`
- branch scientific head: `911ac9876c97b78e4c5e50654251a3f59dac9257`
- upstream subject: `coseal/aslib_data@551b22beef8df17de59286b4822ef720e0aa4d6f`, `BNSL-2016`
- uploaded artifact id: `9637176781`
- uploaded ZIP SHA-256: `c5f2d5b5e93596ab82c03a2bd75cd441c74e6ac08b0265b281c3be7a516ab186`
- raw result JSON SHA-256: `c843a0cb1c0a5a13863f27518e721cf8786334fba21a088f8ca4350ec947c49e`

The workflow executed the frozen evaluator twice byte-identically and all registered source/control checks passed.

## Terminal-classification defect

The executor emitted

`C_R20_BNSL_ADAPTIVE_MATERIAL_VALUE`

because `terminal_for()` checked

`V_adapt <= 0.90 * V_static and M_adapt <= M_static`

before checking equality. The frozen protocol separately registered `C_R20_BNSL_ADAPTIVE_NULL` when `V_adapt == V_static` within `1e-9`. At `V_static=V_adapt=0`, both predicates are true. The terminal vocabulary was therefore not mutually exclusive.

This overlap was not noticed before outcome access. The emitted positive terminal is **not scientific authority** and must not be repaired into a prospective positive result by changing predicate order after seeing the data.

## Quantitative scientific observation

The raw result itself is unambiguous:

- instances: `1179`;
- algorithms: `8`;
- declared feature steps: `7`;
- dependency-closed static representations exhaustively evaluated: `128`;
- no-feature robust total excess: `71999.72` PAR10;
- SBS mean PAR10: `9017.077065309584`;
- VBS mean PAR10: `219.8673112807464`;
- best static representation: `['basic_extended']`;
- best-static fibre count: `1179`;
- best-static maximum fibre size: `1`;
- best-static acquisition cost: `0` on every instance;
- best-static robust total excess: `0`;
- best-static mean total excess: `0`;
- acquisition-only `J0`: `['basic', 'basic_extended', 'lower_bounding']`;
- `J0` fibre count: `1179`, all singleton;
- adaptive root choices: `ACT=1179`, no refinement selected;
- adaptive robust total excess: `0`;
- adaptive mean total excess: `0`;
- adaptive minus static robust difference: `0`;
- adaptive minus static mean difference: `0`.

Five registered static representations already attain zero robust total excess, including the single zero-cost step `basic_extended`.

Thus the intended scientific discriminator has no room to show adaptive value on this pinned scenario: a free static representation already identifies every corpus instance and permits the statewise VBS action at zero acquisition cost.

## Scientific disposition

For manuscript/application interpretation, R20 is a **valid null / representation-saturation boundary**:

`C_R20_BNSL_ADAPTIVE_NULL__FREE_STATIC_REPRESENTATION_ALREADY_VBS`

This string is an authority-correction label, not a new prospectively registered terminal. It summarizes the raw equality without altering the frozen protocol or execution bytes.

The result consumes FiberGuard breakthrough Round 1. Round 2, if executed, must use the already-declared scientifically distinct direct-relative/joint route mechanism on a different untouched subject. It may not remove `basic_extended`, add feature charges, alter the corpus, or otherwise repair BNSL after observing this saturation.

## Authority boundary

The BNSL execution remains corpus-complete closed-world evidence only. It establishes neither unseen-instance generalization nor adaptive superiority. The positive emitted terminal is quarantined solely because the terminal predicates overlapped; the raw quantitative result and all negative/null implications are preserved.

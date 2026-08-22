# ORION-QG QG-26 — Parikh-histogram kernel and finite guarded tropical regime geometry V1

Date: 2026-08-22
Parent programme: #740
Issue: #884
Execution branch: `codex/orion-qg-qg26-parikh-histogram-20260822`
Primary parent: QG-23 protected auxiliary-support compactness (`research/extensions/orion-qg/QG23_AUX_SUPPORT_COMPACTNESS_RESULTS.json`)
Independent exactness control: QG-24 protected finite tropical WFA (`research/extensions/orion-qg/QG24_TROPICAL_WFA_RESULTS.json`)
Structural grammar parent: QG-7c M1 A/P/C protocol/results
Status: **FROZEN BEFORE QG-26 MACHINE OUTCOME.**
Authority: exact compiler representation/regime geometry only. Parikh images, commutative automata, Presburger/semilinear geometry and tropical min-affine mathematics are donor-owned. No novelty, R6, physical-advantage, practical static-forecaster, explicit-template-basis, B''-completeness, or chain-closure authority.

## Scientific question

For one fixed matching of six target Pauli strings into the three frozen R6M/TARE blocks, can the exact all-n optimum be expressed entirely in the 4096-dimensional histogram of target qubit-column types, and more strongly as a finite minimum of affine baseline-plus-correction templates with only threshold guards?

## P1 — column histogram / permutation invariance

Each physical qubit column has one type

`t=(P_A0,P_A1,P_B0,P_B1,P_C0,P_C1) in Sigma={I,X,Y,Z}^6`, `|Sigma|=4096`.

For an n-qubit instance define counts `N_t` and histogram `N in N^4096`.

The production and generic analyzers must bind that simultaneous permutation of physical qubit coordinates preserves:
- all six Pauli weights;
- all three frame-pair symplectic products;
- all six Tag/frame symplectic syndromes;
- frame/Tag support counts;
- every local F3 Restore term up to permutation of the summation order;
- therefore exact feasibility and frozen unit objective.

Consequently any two valid target words with the same histogram have the same exact optimum. This `HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N` authority is logically independent of QG-23's six-active-coordinate bound.

The valid-input histogram domain also requires each of the six full target Paulis to be nonzero:

`sum_{t:t_i != I} N_t >= 1` for each target component `i=0,...,5`.

## P2 — exact spectator baselines

For each of the 8 global target-permutation tuples `pi`, define `b_pi(t)` for every target type t as the two-branch F3 cost when all six frame letters and the Tag letter at that coordinate are identity.

Then

`B_pi(N)=sum_t N_t*b_pi(t)`.

The analyzer must serialize all 8 exact integer coefficient vectors (4096 entries each) by SHA256 plus value histograms and report how many distinct vectors actually occur. No equality/inequality among the 8 may be assumed before computation.

Generic ORION reconstructs all 8 vectors from an independent `F_2^2`/F3 implementation and must reproduce every vector digest.

## P3 — all auxiliary support is inside the QG-23 six-coordinate skeleton

Bind QG-23 GREEN and the exact QG-7c M1 shape definitions:
- anchored A: both frame supports on one Tag coordinate;
- phantom P: frame support `{borrow,home}` with borrow on Tag and home Tag-off;
- comm-s2 C: frame support `{b,a}` with both b,a on Tag.

Thus for every QG-23-normalized irreducible configuration, every nonidentity frame or Tag letter lies in

`U_aux = supp(Tag) union {phantom homes}`,

and QG-23 earns `|U_aux|<=6` all n.

The QG-7f weight-3 overlapping comm-s2 counterexample remains mandatory and must fit this broader skeleton; no common-two-coordinate premise may reappear.

## P4 — frozen active-template object

An active template tau consists of:
- one of 8 target-permutation tuples;
- one of 8 central-bit tuples;
- an integer `k` with `1<=k<=6`;
- an unordered multiset of k target-column types;
- for each active occurrence, six local frame letters plus one local Tag letter, with at least one of those seven auxiliary letters nonidentity;
- global accumulated support counts/parities satisfying exact original R6M acceptance when all nonlisted coordinates carry identity auxiliary letters.

Coordinate order is not part of the template. Multiple active occurrences of the same target type are allowed and recorded by multiplicity `m_tau(t)`.

Finiteness must be machine-audited without enumerating the astronomical complete universe. A valid ordered upper bound is

`64 * sum_{k=1}^6 [4096*(4^7-1)]^k`.

The analyzer serializes this exact integer, its decimal digit count and the local active labeled-choice base `4096*(4^7-1)=67,104,768`. This is a finiteness witness only, not a tractability claim.

## P5 — guarded affine cost identity

For a template tau with permutation pi define its histogram guard

`G_tau(N): N_t >= m_tau(t)` for every type used by tau.

For each active occurrence r of target type t_r, let
- `base_r=b_pi(t_r)`;
- `restore_aux_r` be the exact two-branch F3 value after multiplying that target column by the six local frame letters;
- `struct_tau` be the total frame/Tag support cost over all active occurrences, with multipliers fixed by the central tuple, including the frozen `-18` offset once.

Define constant

`K_tau = struct_tau + sum_r (restore_aux_r-base_r)`.

Then for every histogram satisfying the guard,

`C_tau(N)=B_pi(N)+K_tau`.

The proof relies on the fact that every spectator coordinate has all auxiliary letters identity, so its Restore equals its target and contributes exactly its baseline coefficient.

## P6 — complete local decomposition control

Freeze the following non-adaptive production control before outcome:
- all 4096 target-column types, including types containing I;
- all 48 one-coordinate feasible shared-label frame/Tag rows from QG-24;
- all 8 target-permutation tuples;
- canonical central tuple `(0,0,0)`.

This is exactly `4096*48*8 = 1,572,864` active one-column rows.

For every row require frozen production `config_cost(n=1)` to equal

`b_pi(t) + K_tau`

for the corresponding one-active-coordinate template. Serialize zero mismatches or the first 20 verbatim.

Separately enumerate all `4^7*8 = 131,072` local auxiliary-letter/central combinations and verify the frame/Tag structural support contribution used in K_tau against the frozen multiplier rule. This control includes non-accepting local rows because it audits cost decomposition, not acceptance.

Generic ORION independently reproduces both control counts and all aggregate fingerprints without importing production tables.

## P7 — histogram/template realization bijection

Prove both directions structurally and audit with deterministic synthetic controls:

1. **Configuration -> template.** Every QG-23-normalized optimum has at most six coordinates with nonidentity auxiliary letters. Remove physical coordinate names, retaining each active target type and local auxiliary letters. The remaining multiset is an accepted tau; the original histogram satisfies its multiplicity guard; the P5 identity gives the exact original cost.

2. **Template -> configuration.** If `N_t>=m_tau(t)`, choose distinct physical coordinates of each required type and place the template's local auxiliary letters there; put identity auxiliary letters on every other coordinate. Since all global constraints are sums/XORs/support counts of the active local data, the realized configuration is original-R6M admissible and has exactly `C_tau(N)`.

Coordinate choice among equal-type columns cannot affect feasibility or cost.

## P8 — exact finite guarded tropical representation

Let T be the complete finite accepted template universe from P4. On every valid histogram,

`C_DP(N) = min_{tau in T, G_tau(N)} [B_{pi(tau)}(N)+K_tau]`.

First inequality: every accepted template realizes an original admissible configuration.
Second inequality: QG-23 guarantees at least one unrestricted optimum has a template in T.

Therefore exact all-n TARE cost is a finite **guarded tropical/min-affine function** of the 4096 integer column counts.

## P9 — regime geometry consequence

Each guard is a finite conjunction of integer threshold inequalities. Pairwise template ties/dominance are affine integer inequalities because baselines are linear and K constants.

Thus the valid histogram domain admits a finite semilinear/integer-polyhedral partition into exact optimal-template cells.

QG-26 V1 may authorize this existence theorem only. It does **not** enumerate the complete template basis, produce a practical forecaster, or claim the cell decomposition is small.

## P10 — exact dependence on n / compression statement

May state only:
- target qubit order is irrelevant; histogram N is sufficient;
- building N from a six-target n-qubit instance takes O(n) local-column reads;
- after histogram construction, physical n enters only through the 4096 integer counts;
- the nontrivial auxiliary correction of at least one optimum touches at most six histogram occurrences.

Do not claim constant-time practical compilation or polynomial dependence on the numerical bit-length of all counts without a separately explicit template-basis algorithm.

## Independent generic ORION

Generic verifier must:
- rebuild phase-free Pauli/F3 algebra independently;
- derive all 8 baseline vectors/digests;
- independently derive the active-template finiteness upper bound;
- reproduce the 1,572,864 one-active-column decomposition aggregate and 131,072 structural-cost control;
- bind QG-23/QG-7c only after sealing its local decomposition;
- verify the two realization directions and strict authority separation.

## Native ORION-Q

May authorize only:
- `HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N`;
- `FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION`;
- `COUNT_SPACE_REGIME_GEOMETRY_EXISTS`.

Mandatory false:
- `EXPLICIT_TEMPLATE_BASIS_ENUMERATED`;
- `PRACTICAL_STATIC_FORECASTER`;
- `CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS`;
- `CHAIN_ALL_N`;
- `GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY_IN_OBJECTIVE_SPACE`;
- novelty/R6/physical-advantage authority.

## Intended strong terminal

`QG26_TARE_EXACT_COST_IS_FINITE_GUARDED_TROPICAL_FUNCTION_OF_4096_COLUMN_COUNTS_ALL_N`

Honest alternatives:
- `QG26_QG23_AUX_SUPPORT_BINDING_GAP`
- `QG26_SPECTATOR_BASELINE_NOT_AFFINE__MISSING_COUPLING`
- `QG26_HISTOGRAM_REALIZATION_COUNTEREXAMPLE`
- `QG26_LOCAL_DECOMPOSITION_COUNTEREXAMPLE`
- `QG26_GENERIC_NATIVE_DISAGREEMENT`
- `QG26_CANNOT_CHECK`

## Donor subtraction

Parikh images, commutative monoids, Presburger arithmetic, semilinear sets, rational/weighted series, tropical polynomials and finite min-affine decompositions are established mathematics/computer science and receive zero novelty credit. Candidate contribution is only the exact TARE-specific histogram sufficiency, six-active-occurrence correction theorem and resulting all-n count-space compiler regime geometry.
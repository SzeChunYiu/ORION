# ORION-QG QG-31 — query-indexed abstraction ladder V1

Date: 2026-08-22
Issue: #904
Parent: QG-30 #893 / committed result `research/extensions/orion-qg/QG30_BULK_COARSE_GRAIN_RESULTS.json`
Execution branch: `codex/orion-qg-qg31-query-abstraction-20260822`
Status: **POST-DISCOVERY CONFIRMATION FROZEN BEFORE PROTECTED CONFIRMATION RUN.**

The numerical confirmation targets 54 spectra and 715 indexed responses were exposed by scratch analysis after QG-30 became GREEN. They are not prospectively discovered claims. QG-31 confirms their exact production meaning, partition relations and authority boundaries with independent reconstruction.

## Frozen universe

Use exactly the 715 canonical local-Clifford orbit representatives and the 384 one-active probe rows inherited from QG-30:
- target permutations in lexicographic order over `{0,1}^3`;
- 48 feasible shared-label local frame/Tag rows in their canonical enumeration order;
- central tuple `(0,0,0)`.

For representative `o`, define exact defect correction `K_o[p,a]`.

## Frozen observation maps

1. `A_bulk(o)`: ordered four-form QG-30 bulk signature. Parent count: 45.
2. `A_spectrum(o)`: sorted multiset of all 384 `K_o[p,a]`. Confirmation target: 54 distinct spectra.
3. `A_indexed(o)`: ordered 384-vector indexed by `(p,a)`. Confirmation target: 715 distinct vectors.

## Required partition analysis

Compute exact equivalence partitions under all three maps. Do not assume `P_bulk` and `P_spectrum` are nested.

Serialize:
- class counts and class-size histograms;
- complete bulk-signature × spectrum contingency table in canonical row order;
- whether each partition refines the other;
- first same-spectrum/different-bulk pair if present;
- first same-bulk/different-spectrum pair if present;
- first same-spectrum/different-indexed pair;
- first indexed collision if any.

`P_indexed` must refine both other partitions by construction; if it does not, return CANNOT_CHECK/implementation failure.

## Indexed local-response minimality

If all 715 indexed response vectors are distinct, QG-31 may authorize only:

> Any quotient required to reproduce the complete frozen indexed one-active cost-response experiment needs at least 715 equivalence classes. QG-28's 715 orbit types are minimal for this probe-complete local-response query class.

Mandatory false:
- `FULL_FINITE_N_OPTIMUM_REQUIRES_715_CLASSES`
- `QG28_ORBIT_HISTOGRAM_GLOBALLY_MINIMAL`
- any global minimality beyond the frozen response experiment.

## Spectrum authority

If 54 spectra are confirmed, `A_spectrum` is sufficient only for queries that depend on the unlabeled multiset of one-active K responses. It is not automatically sufficient for indexed local responses, finite-size optimum, or asymptotic bulk geometry.

## Query-indexed abstraction statement

QG-31 may authorize:
- 45 classes for the QG-30 bulk-signature query;
- 54 classes for the unlabeled one-active defect-spectrum query if confirmed;
- 715 classes for the complete indexed one-active response query if injective;
- exact statement of comparability/incomparability between the 45- and 54-class partitions.

This is the source object for MAX-R4E #903's authority-indexed abstraction skill.

## Independent instruments

Production binds to the frozen R6M/TARE production cost semantics.
Generic ORION independently rebuilds phase-free `F_2^2`, local Clifford orbits, F3, structural cost, 48 auxiliary rows and all three partitions before reading the production result.
Native ORION-Q enforces only query-scoped authority.

## Intended confirmation terminal

`QG31_QUERY_INDEXED_ABSTRACTION_LADDER_CONFIRMED__INDEXED_LOCAL_RESPONSE_INJECTIVE_ON_715_ORBITS`

Honest alternatives: spectrum count mismatch, indexed collision, partition relation mismatch, parent-binding gap, generic/native disagreement, CANNOT_CHECK.

## Donor subtraction

Partition refinement, sufficient statistics, observation equivalence and bisimulation are donor mathematics. Candidate value is the exact TARE-specific observation hierarchy and the explicit authority boundary it supplies to ORION-Q.
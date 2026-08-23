# ORION-Q MAX-R6 interface-closure protocol

Date: 2026-08-20
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: frozen before interface-envelope outcome generation.
Authority ceiling: donor/interface closure only. This packet cannot authorize R6 or novelty.

## Reopen cause

The blinded native Self-ORION N1 state is constructed so that, after the N0-selected donor-closure packet, the registered discriminator outcomes identify `RESP:INTERFACE_INADEQUATE`. Under the production `orion.transfer` / `orion.self_orion` control stack this responsibility binds to `REV:CHANGE_INTERFACE`.

This packet follows that system-selected coordinate. The operator-authored ADT3 candidate remains hidden and is not an admissible source for this interface experiment.

## Question

Can a faithfully donor-favourable FOQCS/check-matrix interface Pareto-dominate the frozen H4 direct-anticommuting-clique incumbent under the same non-compensatory scientific/resource coordinates?

If even an optimistic FOQCS envelope cannot dominate because of load-bearing normalization or ancilla coordinates, the actual donor implementation cannot dominate that point. FOQCS is still absorbed as a Pareto interface capability; the result does not call the donor useless.

## Frozen H4 incumbent

Bind the already-open, exact R5H H4 donor-only balanced point:

- `Lambda = 4.862157873932594`;
- controlled/block-internal CNOT-equivalent two-qubit count `= 1428`;
- block-internal projected T `= 5568`;
- outer blocks `= 246`;
- maximum local ancilla capacity `= 0`;
- reference total T `= 31028`.

This point is not recomputed or rematched by the interface experiment.

## FOQCS donor facts absorbed

For an n-qubit Pauli LCU, FOQCS represents Pauli strings by x/z activation registers and implements SELECT as two parallel layers: n controlled-X/CNOT operations plus n controlled-Z/CZ operations.

The current Qrisp implementation exposes `from_foqcs_lcu_prep(prep_r, prep_l, ...)`, accepting caller-supplied right/left PREP routines. The final `2n` ancilla qubits are the x/z activation registers. Thus a generic custom-PREP route exists even where the automatic structured-operator constructor does not apply.

For arbitrary Pauli coefficients the FOQCS normalization remains the Pauli-LCU l1 norm. On the already-open H4 Pauli list this value is frozen from R5H B0:

`Lambda_FOQCS = 5.158046205600001`.

## Optimistic interface envelope

To avoid disadvantaging FOQCS because generic chemistry PREP is not yet instantiated, construct an intentionally unattainable donor-favourable lower envelope:

- PREP_R two-qubit cost = 0;
- PREP_L^dagger two-qubit cost = 0;
- PREP T cost = 0;
- extra PREP ancilla = 0;
- SELECT CNOT = n;
- SELECT CZ = n;
- Clifford two-qubit equivalent = `2n` (CZ counts as one CNOT-equivalent Clifford entangler under local-H conversion);
- T = 0;
- outer blocks = 1;
- unavoidable activation ancilla = `2n`;
- normalization = exact Pauli l1.

For H4, n=8, so the optimistic envelope has:

- `Lambda = 5.158046205600001`;
- Clifford two-qubit equivalent `= 16`;
- projected T `= 0`;
- outer blocks `= 1`;
- ancilla `= 16`.

This is labelled `OPTIMISTIC_FOQCS_ZERO_PREP_ENVELOPE`; it is not an achievable circuit claim.

## Exact interface-closure discriminator

Compare the incumbent and optimistic envelope non-compensatorily on:

1. normalization Lambda (lower is better);
2. Clifford two-qubit equivalent (lower is better);
3. projected T (lower is better);
4. outer block count (lower is better);
5. maximum/additional coherent ancilla (lower is better).

The envelope **dominates** the incumbent only if it is no worse in every coordinate and strictly better in at least one.

### `INTERFACE_CANNOT_DOMINATE_EVEN_OPTIMISTIC`

Allowed only if:

- the frozen H4 incumbent is bound exactly;
- FOQCS l1 normalization and n=8 are bound exactly;
- the zero-PREP envelope is constructed exactly as above;
- the envelope does not dominate the incumbent;
- at least one hard non-compensatory coordinate is strictly worse for FOQCS;
- no real PREP cost is silently treated as negative;
- the FOQCS envelope is nevertheless registered as an absorbed Pareto donor capability.

Interpretation: interface change alone cannot produce a strict all-coordinate Pareto successor to the bound H4 incumbent under this donor-favourable lower bound. This may license the native controller to re-evaluate responsibility; it does not itself license method-language growth.

### `INTERFACE_OPTIMISTIC_DOMINATES`

If the zero-PREP envelope dominates the incumbent, interface remains the responsibility and becomes the stronger incumbent. P10/method-language growth remains blocked.

## Native N2 follow-up freeze rule

Before the interface-envelope result is executed, the next native-control responsibility discriminator is frozen conceptually:

- `CURRENT_SEARCH_INCOMPLETE` predicts the current exact search is not exact;
- `DONOR_CLOSURE_INCOMPLETE` predicts donor/interface closure remains unresolved;
- `INTERFACE_INADEQUATE` predicts the optimistic interface envelope can dominate or remains unbound;
- `METHOD_LANGUAGE_INADEQUATE` predicts: current search exact; general-m donor closed/nondominating; optimistic FOQCS envelope bound and non-dominating; current mixed method has no incremental H4 point beyond the direct-clique donor.

Only a post-result state containing the actual registered envelope outcome may be supplied to native N2.

## Blinding and prospective subject

The following remain unavailable to native control and interface code:

- ADT3 or any operator-authored auxiliary-frame proposal;
- the relation `R2=R0R1` as a candidate hint;
- R5J outcome data;
- stretched-N2 DUCC coefficient contents.

The stretched-N2 discriminator remains unopened.

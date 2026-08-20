# ORION-Q MAX-R6 native-selected donor closure computation packet

Date: 2026-08-20
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: frozen after native Self-ORION N0 selected `COMPUTE:DONOR_CLOSURE_PACKET` and before donor-closure outcome generation.
Authority ceiling: N1 discriminator evidence only; not R6/novelty authority.

## Trigger

Native Self-ORION N0 emitted `COMPUTATION_REQUIRED` and selected `COMPUTE:DONOR_CLOSURE_PACKET` because the hard obligations

- `DONOR_GENERAL_M_TARE_CLOSURE`;
- `DONOR_FOQCS_GENERIC_PREP_CLOSURE`

were unresolved. This packet executes exactly those obligations. It does not inspect the prospective stretched-N2 R6 coefficient file.

## Part A — optimistic general-m TARE donor closure on current H4 state

The frozen R5I donor relaxation remains authoritative for block semantics:

- retain all exact R5H mixed blocks (singleton, direct anticommuting clique, exact controlled m=2 TARE);
- add every subset of size `3 <= m <= min(12,2n+1)` as an optimistic general-m TARE hyperblock;
- hyperblock normalization `sqrt(m)||a_G||_2`;
- hyperblock internal CNOT `0`;
- hyperblock ancilla `0`;
- hyperblock projected T `96*(2m-1)`;
- block count `1`;
- all omitted Tag/Restore/control costs are explicitly optimistic, not achievable claims.

### Exact target-specific acceleration

N1 needs to know whether general-m donor closure can defeat the *current H4 responsibility state*, whose exact R5H donor balanced point is frozen as:

`D_H4 = (Lambda=4.862157873932594, CNOT=1428, T=5568, blocks=246, ancilla=0)`.

Instead of materializing the entire relaxed global frontier, the computation may solve the equivalent exact dominance-feasibility question:

> Does any complete relaxed partition that uses at least one optimistic `m>=3` TARE hyperblock have every non-compensatory coordinate <= `D_H4`?

The DP must:

1. use the same sorted H4 Pauli list and 12-term windows as R5H;
2. enumerate every exact R5H mixed candidate block plus every frozen R5I optimistic hyperblock;
3. enumerate exact set partitions by subset DP;
4. retain the hyperblock-usage bit as a formal state coordinate;
5. prune only states that cannot participate in a dominating completion;
6. bind a witness partition if a threatening state exists.

This acceleration is exact for the N1 discriminator because all block resources are nonnegative. Any partial state exceeding `D_H4` in Lambda/CNOT/T/blocks/ancilla cannot later become a dominating complete state. `reference_total_T` need not be an independent feasibility coordinate: under the frozen formula it is monotone nondecreasing in `(internal T, block count)`, and both are individually bounded by `D_H4`, so satisfying those two inequalities implies reference-total-T <= the target reference total.

### Part-A outcome

`GENERAL_M_DONOR_OUTCOME = NONDOMINATING_OR_CLOSED`

iff no relaxed complete state using at least one optimistic `m>=3` hyperblock weakly dominates `D_H4`.

Because the relaxed hyperblocks omit nonnegative real costs, this is sufficient to exclude the published explicit general-m TARE construction from dominating `D_H4` under the frozen projection on this H4 state.

Otherwise:

`GENERAL_M_DONOR_OUTCOME = DOMINATES_OR_INCONCLUSIVE`.

No novelty implication follows from either outcome.

## Part B — FOQCS generic-PREP route closure

The question is not whether FOQCS has an efficient chemistry PREP for this H4 instance. The narrower N0 discriminator is whether a matched generic route exists that prevents us from treating FOQCS as unavailable.

Evidence may include the current FOQCS paper, official/reference implementation, and current Qrisp integration.

### Resolved route criterion

Return

`FOQCS_GENERIC_PREP_OUTCOME = GENERIC_MATCHED_ROUTE_AVAILABLE`

if an implementation route exists that allows the FOQCS check-matrix SELECT construction to be paired with caller-supplied PREP/left-right PREP circuits for operators beyond the built-in structured models. The resource status of that custom PREP must be reported separately; availability does **not** mean zero cost or an optimized chemistry PREP.

Return

`FOQCS_GENERIC_PREP_OUTCOME = NO_GENERIC_MATCHED_ROUTE`

only if the audited donor stack exposes no such route.

If evidence is conflicting or cannot be bound to a current implementation/source identity, leave the discriminator unresolved rather than guessing.

## N1 feed-forward

Only the two registered discriminator outcomes plus evidence/source identities are added to the blinded native control state. Operator-authored R5J/ADT3 material remains hidden. The same native Self-ORION control stack must then recompute responsibility and revision selection.
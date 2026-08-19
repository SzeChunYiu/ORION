# P6-X theorem protocol V1

Date: 2026-08-19
Parent: #533
Status: `THEOREMS_FROZEN_BEFORE_FINITE_ENUMERATION`

## Donor subtraction
P6-X does not claim dependency maintenance, incremental/self-adjusting computation, typed effects, authorization/UCON-style continuing obligations, provenance, execution attestation, workflow reproducibility signatures, proof-carrying artifacts, or generic certificates as novel.

Fresh pressure includes 2026 proof-of-execution work that binds authorization/effect/history/replay into execution-attestation certificates and formal scientific-workflow work that binds provenance/reproducibility tenets into workflow signatures. This removes any novelty claim for certificates or provenance-bearing execution itself.

## State family
For a donor family D, let donor-visible validity depend on a subset of:
- `compute_valid`
- `dependency_supported`
- `effect_valid`
- `action_authorized`
- `execution_provenance_valid`

The scientific certificate enrichment additionally exposes:
- `evidence_version_current`
- `scientific_source_authorized`
- `claim_scope_supported`
- `verification_epoch_current`

`ScientificAdmissible_D(s)` iff `DonorValid_D(U_D(s))` and every scientific certificate obligation is discharged.

## Donor embeddings
1. `DEPENDENCY_MAINTENANCE`: donor validity = compute_valid AND dependency_supported.
2. `EFFECTFUL_COMPUTATION`: donor validity = compute_valid AND effect_valid.
3. `CONTINUING_AUTH_EXEC_PROVENANCE`: donor validity = action_authorized AND execution_provenance_valid.

These are bounded semantic embeddings/proxies, not claims to mechanize every theorem of TMS, self-adjusting computation, UCON, or proof-of-execution systems.

## Frozen theorem schema
### T1 — donor preservation under erasure
For each embedding D, the forgetful map `U_D` preserves the donor-visible coordinates and therefore preserves evaluation of `DonorValid_D`.

### T2 — scientific non-reflection / typed erasure separation
Assume at least one scientific certificate coordinate c is non-inert: there exist states identical on donor-visible coordinates and all other scientific coordinates where changing c changes scientific admissibility. Then `U_D` does not reflect scientific admissibility: there exist s,t with `U_D(s)=U_D(t)` but `ScientificAdmissible_D(s) != ScientificAdmissible_D(t)`.

This is a conditional separation theorem, not a universal theorem that every donor formalism erases scientific information.

### T3 — conservative special case
If every scientific certificate obligation is discharged, `ScientificAdmissible_D(s)` reduces exactly to `DonorValid_D(U_D(s))`.

### T4 — ideal-product equivalence
An ideal donor product enriched with the exact four scientific certificate coordinates and the same admissibility predicate is extensionally equivalent to P6-X. No inherent expressivity or centralization advantage is permitted.

### T5 — certificate preservation under change
A previously admissible state remains scientifically admissible after a donor-valid transition only if each changed scientific certificate coordinate is preserved or explicitly revalidated. Donor-valid recomputation/support/authorization alone is insufficient when any non-inert scientific certificate coordinate becomes false.

## Finite-model obligations
Enumerate every Boolean state for all three donor embeddings. Require:
- T1 on every state;
- T2 witness for each of the four scientific coordinates in each embedding;
- T3 on every state with all four scientific coordinates true;
- T4 exact equality on every state;
- T5 no-alarm case plus one revocation countermodel for each omitted scientific premise in each embedding.

## Claim ladder
A1: explicit scientific-certificate semantic layer over mature donor dynamics.
A2: generalized conditional computational/operational-vs-scientific-admissibility separation.
A3: conservative-extension theorem family across the three bounded donor embeddings.

No claim of deployed-agent superiority, universal semantic necessity, or faithful full mechanization of every donor system is authorized by this theorem protocol.

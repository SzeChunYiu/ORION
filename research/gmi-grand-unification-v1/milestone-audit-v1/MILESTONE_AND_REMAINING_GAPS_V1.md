# Milestone and Remaining Gaps Audit for #602

**Date**: 2026-09-15  
**Status**: Initial audit  
**Scope**: J3 (physical/analog material cognition, quantum), X/P0, X/P1, X/P3

---

## Part 1: J3 Physical/Quantum Burden Separation

### J3 Physical/Analog Material Cognition

**Current Evidence**:
- The `research/gmi-grand-unification-v1/gmi-domain-gates-v1/NEW_DOMAIN_CLAIM_GATE_AND_UNSEEN_FORMS_V1.md` file contains a detailed protocol (J4) for evaluating new cognitive domains, including the requirement for "Material Lifecycle/Asymptotic Burden Separation" (J4.4).
- The file applies this protocol to "relational-constraint/sheaf intelligence" as a worked example, showing asymptotic burden separation for 6/8 domains (D1, D2, D3, D5, D6, D8) with overheads growing polynomially or exponentially.
- However, this is a *theoretical* protocol and worked example for a specific candidate (sheaf intelligence). There is **no evidence** of *real* burden separation for *physical/analog material cognition* as a distinct candidate domain.
- The search for "physical", "analog", and "material cognition" in the research directory did not yield any files specifically addressing physical/analog material cognition as a candidate domain.

**Gap**: No candidate domain for physical/analog material cognition has been proposed, let alone tested for burden separation. The J4 protocol exists but has not been applied to this specific candidate.

**Action Required**:
1. Propose a candidate domain for physical/analog material cognition (e.g., "embodied material cognition" or "physical resource-bound cognition").
2. Apply the J4 protocol to this candidate, including:
   - Distinct primitive cognitive-state carrier (J4.1)
   - Distinct native operator/execution law (J4.2)
   - Semantics-preserving reduction attempts against D1-D8 (J4.3)
   - Material lifecycle/asymptotic burden separation (J4.4)

### J3 Quantum

**Current Evidence**:
- The search for "quantum" in the research directory found files in `research/orion-v1-freeze/quantumcensus-20260826` and `research/orion-rg/` (nonquantum scripts), but these appear to be about quantum computing or census, not quantum cognition as a candidate cognitive domain.
- The `research/extensions/orion-qn/` directory contains files about quantum networking, but not quantum cognition.
- There is **no evidence** of a candidate domain for quantum cognition that requires a "capability/resource frontier not explainable by known quantum algorithm parents."

**Gap**: No candidate domain for quantum cognition has been proposed. The requirement for a capability/resource frontier not explainable by known quantum algorithm parents has not been addressed.

**Action Required**:
1. Propose a candidate domain for quantum cognition (e.g., "quantum superposition-based cognition" or "entanglement-assisted cognition").
2. Define the "capability/resource frontier" that this domain would provide, and demonstrate that it cannot be explained by known quantum algorithm parents (e.g., Shor's, Grover's, quantum walk algorithms).

---

## Part 2: X Milestone Status Audit

### X/P0: Close known-family zero-prior derivation rows from #431/#433

**Current Evidence**:
- The search for "#431" and "#433" in the research directory found references in `research/saturation/` PR ancestry audits, indicating that #431 and #433 are related to "computed readiness semantics" and "structural-discovery successor."
- However, there is **no file** that explicitly "closes" the zero-prior derivation rows from #431/#433.
- The `research/gmi-grand-unification-v1/` directory does not contain any file with "closure" in the name that addresses #431/#433.

**Gap**: The zero-prior derivation rows from #431/#433 have not been closed. The current codebase (B2-B20 derivations) may represent zero-prior derivations, but there is no audit or closure document.

**Action Required**:
1. Identify the specific derivation rows from #431/#433 that need to be closed.
2. Audit the current codebase (B2-B20 derivations) to determine if they satisfy the requirements of #431/#433.
3. Create a closure document that explicitly maps each derivation row to the evidence in the codebase.

### X/P1: Harden D1-D8 domain basis

**Current Evidence**:
- The `research/gmi-grand-unification-v1/gmi-domain-gates-v1/NEW_DOMAIN_CLAIM_GATE_AND_UNSEEN_FORMS_V1.md` file contains a detailed description of D1-D8 domains (coefficient/function-field, exemplar/memory-indexed, probabilistic-belief, symbolic/program, search/frontier, dynamical-state, collective/distributed, morphogenetic/self-rewriting).
- However, there is **no evidence** of "hardening" the D1-D8 domain basis (e.g., formal proofs of completeness, independence, or minimal representation).
- The J2 completeness attacks (PR #801) may address this, but we have not found a specific file that confirms the hardening.

**Gap**: The D1-D8 domain basis has not been formally hardened. The definitions exist, but there is no proof that they are complete, independent, or minimal.

**Action Required**:
1. Review PR #801 (if available) to determine if it hardens the D1-D8 domain basis.
2. If not, create a formal hardening document that:
   - Proves completeness (any cognitive domain can be reduced to one or more of D1-D8)
   - Proves independence (no D_i can be reduced to the others)
   - Proves minimality (removing any D_i breaks completeness)

### X/P1: Test P0 new-domain candidates

**Current Evidence**:
- The `research/gmi-grand-unification-v1/gmi-domain-gates-v1/NEW_DOMAIN_CLAIM_GATE_AND_UNSEEN_FORMS_V1.md` file lists several candidate domains: relational-constraint, hyperdimensional, local-field, constructive, energy-landscape, population-hereditary, molecular, physical, body-environment, quantum.
- However, these are only *candidates* listed in a protocol document. There is **no evidence** that any of these candidates have been *tested* (i.e., subjected to the J4 protocol).

**Gap**: None of the P0 new-domain candidates have been tested. The protocol exists, but no candidate has been run through it.

**Action Required**:
1. Select one or more candidates from the list (e.g., relational-constraint, which is partially worked in the example).
2. Execute the J4 protocol for each selected candidate, including:
   - J4.1-J4.4 (theoretical burden separation)
   - J4.5-J4.11 (experimental verification)

### X/P1: Test RQM/VRQM/VGSC/IQL/LMHM/SCDI property-first predictions

**Current Evidence**:
- The `research/gmi-grand-unification-v1/gmi-domain-gates-v1/NEW_DOMAIN_CLAIM_GATE_AND_UNSEEN_FORMS_V1.md` file contains a detailed worked example for RQM (Relational Query Machine), including property derivation, ecological conditions, negative twin, neutral grammar, and a test protocol (K.1-K.14).
- However, this is a *protocol* and *theoretical analysis*. There is **no evidence** of *experimental testing* of RQM's property-first predictions.
- There is **no evidence** of VRQM, VGSC, IQL, LMHM, or SCDI in the research directory.

**Gap**: RQM has a detailed protocol but no experimental results. The other forms (VRQM, VGSC, IQL, LMHM, SCDI) have not been addressed.

**Action Required**:
1. Execute the K.7-K.13 experimental protocol for RQM (enrichment, reminting, alternate encoding, parent reduction, overhead, fresh prediction, real-regime test).
2. For the other forms (VRQM, VGSC, IQL, LMHM, SCDI):
   - Define each form (property vector, ecological conditions, negative twin).
   - Create a test protocol for each (similar to K for RQM).
   - Execute the experimental protocol.

### X/P3: Code/math/science/control transfer (overlap with T items)

**Current Evidence**:
- The search for "transfer" in the research directory found many files, including:
  - `research/cross-domain-mechanic-transfer-v1/` (literature matrix, engineering substrate bound)
  - `research/verified-structural-transfer-v1/` and `v2/` (formalism, local validation, far domain audit)
  - `research/failures/` (various failure cases involving transfer)
- These indicate that transfer has been studied, but we need to audit the status specifically for "code/math/science/control transfer."

**Gap**: We need to audit the status of transfer for these specific domains (code, math, science, control). The existing work may cover some, but we need a clear audit.

**Action Required**:
1. Review the existing transfer work in `research/cross-domain-mechanic-transfer-v1/` and `research/verified-structural-transfer-v1/` and `v2/`.
2. Create a status audit that maps:
   - Code transfer: what has been demonstrated?
   - Math transfer: what has been demonstrated?
   - Science transfer: what has been demonstrated?
   - Control transfer: what has been demonstrated?
3. Identify gaps and overlaps with T items.

### X/P3: Physical resource/energy scaling

**Current Evidence**:
- The search for "physical resource" and "energy scaling" found:
  - `research/frontier-support-state-v1/HOSTILE_REVIEW_MATRIX_V1.md`: mentions "cross-domain resource scaling"
  - `research/extensions/orion-qn/ORION_QN_PROVENANCE_BOUNDARY_V1.md`: mentions "physical resources" in quantum networking.
- However, there is **no dedicated work** on physical resource/energy scaling for cognitive domains.

**Gap**: Physical resource/energy scaling has not been systematically studied as a milestone.

**Action Required**:
1. Define what "physical resource/energy scaling" means in the context of cognitive domains (e.g., computational energy cost, memory footprint, communication bandwidth).
2. Conduct a scaling analysis for the D1-D8 domains (and any new candidates) with respect to physical resources.
3. Create a scaling audit document.

---

## Part 3: Priority Recommendations

### 1. Items that can be checked off with existing evidence
- **J3 Physical/Analog Material Cognition**: None. No candidate proposed.
- **J3 Quantum**: None. No candidate proposed.
- **X/P0**: Partially. The B2-B20 derivations may be zero-prior, but no closure document exists.
- **X/P1 D1-D8 hardening**: Possibly, if PR #801 addresses it. Need to check.
- **X/P1 New-domain candidates**: None. No candidate tested.
- **X/P1 RQM/VRQM/VGSC/IQL/LMHM/SCDI**: None. Only RQM has a protocol, no experiments.
- **X/P3 Transfer**: Partially. Some transfer work exists, but not audited for code/math/science/control.
- **X/P3 Scaling**: None. No dedicated work.

### 2. Items that need new work
- **J3 Physical/Analog Material Cognition**: Propose a candidate and apply J4 protocol.
- **J3 Quantum**: Propose a candidate and define the capability/resource frontier.
- **X/P0**: Create a closure document for #431/#433 derivation rows.
- **X/P1 D1-D8 hardening**: Formal hardening (if not done by PR #801).
- **X/P1 New-domain candidates**: Test at least one candidate (e.g., relational-constraint) using J4.
- **X/P1 RQM**: Execute experimental protocol (K.7-K.13).
- **X/P1 Other forms**: Define and test VRQM, VGSC, IQL, LMHM, SCDI.
- **X/P3 Transfer**: Audit transfer status for code/math/science/control.
- **X/P3 Scaling**: Conduct physical resource/energy scaling analysis.

### 3. Items that are blocked and on what
- **X/P1 RQM experiments**: Blocked on experimental infrastructure (code, data, compute).
- **X/P1 Other forms**: Blocked on definition and protocol creation.
- **X/P3 Transfer audit**: Blocked on access to existing transfer work and time to review.
- **X/P3 Scaling analysis**: Blocked on definition of metrics and data collection.

---

## Next Steps

1. **Immediate** (next 1-2 days):
   - Check PR #801 for D1-D8 hardening.
   - Review existing transfer work in `research/cross-domain-mechanic-transfer-v1/` and `research/verified-structural-transfer-v1/` and `v2/`.
   - Create a closure document for #431/#433 derivation rows (X/P0).

2. **Short-term** (next week):
   - Propose a candidate for physical/analog material cognition and begin J4 protocol.
   - Propose a candidate for quantum cognition and define the capability/resource frontier.
   - Select one new-domain candidate (e.g., relational-constraint) and execute J4.1-J4.4 (theoretical burden separation).

3. **Medium-term** (next 2-4 weeks):
   - Execute experimental protocol for RQM (K.7-K.13).
   - Define and create protocols for VRQM, VGSC, IQL, LMHM, SCDI.
   - Conduct physical resource/energy scaling analysis for D1-D8 domains.

4. **Long-term** (1-2 months):
   - Complete experimental testing for selected new-domain candidates.
   - Complete transfer audit and scaling analysis.
   - Update milestone document with results.

---

**Conclusion**: Most items require new work. The existing evidence provides a foundation (protocols, definitions, some theoretical analysis), but experimental verification and formal hardening are largely missing. The priority is to close the gaps that are blocking other work (e.g., D1-D8 hardening, #431/#433 closure) and then proceed with experimental testing of candidate domains.
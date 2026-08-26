# P14C Specification-Separated Governance Benchmark V1

**Paper:** ORION-P14 — ORION-RSE  
**Issue:** #669  
**Protocol:** `ORION.P14C.SpecificationSeparatedGovernance.v1`  
**Frozen:** 2026-08-21 before execution.

## Motivation

P14B correctly separates the full governance contract from partial baselines, but its harness implements the full policy by calling the same function used to derive gold. That makes P14B a useful semantic discriminator while creating an avoidable implementation-circularity objection.

P14C is a fresh successor. It does **not** edit or relabel P14B. It separates:

1. an explicit adjudication specification (`P14C_ADJUDICATION_CASES_V1.json`) containing case facts and frozen expected dispositions; and
2. an independently implemented policy function that receives facts only and is never given the expected disposition.

The case table is a specification artifact authored and frozen before policy execution. It is not an external human-adjudicated science dataset; therefore P14C can authorize **contract-conformance superiority**, not external scientific validity.

## Case design

The explicit table contains 28 cases, four for each semantic stratum:

- `SUPPORTED_CLEAN`;
- `SUPPORTED_REOPEN`;
- `RETAIN_NEGATIVE`;
- `SUBSUMED`;
- `INTERACTION_ONLY`;
- `CANNOT_CHECK`;
- `NEGATIVE`.

Variants test precedence as well as isolated components: donor ownership can coexist with later history/interaction facts; interaction can coexist with history; negative evidence can coexist with irrelevant donor/history flags; `CANNOT_CHECK` includes evidence-integrity, freeze, identifiability and multi-defect variants.

## Policies

The registered policies are:

- `RAW_POSITIVE`;
- `REFLECTION_CHECKLIST`;
- `DONOR_AWARE_REVIEW`;
- `MULTI_REVIEW`;
- `ORION_RSE_FULL` implemented independently from the case table;
- ablations for evidence integrity, protocol freeze, identifiability, donor subtraction, interaction handling and negative-history retention.

All policies receive the exact same fact dictionary. Before every policy call, the harness strips `gold_disposition`, `rationale`, `case_id` and `stratum`. The policy therefore cannot inspect the answer field.

## Endpoints

- disposition accuracy over the 28 frozen cases;
- false scientific promotion rate;
- useful-discovery recall over `SUPPORTED_RESIDUAL` gold cases;
- retain-negative accuracy;
- supported-reopen accuracy.

## Positive terminal

`P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED` requires:

1. full ORION-RSE disposition accuracy = 1;
2. full false-promotion rate = 0;
3. full useful-discovery recall = 1;
4. full retain-negative and supported-reopen accuracy = 1;
5. strongest non-ORION baseline false-promotion rate >= 0.10;
6. full disposition-accuracy advantage over strongest non-ORION baseline >= 0.10;
7. every registered component ablation lowers disposition accuracy;
8. no policy input contains the gold field;
9. two executions produce byte-identical canonical JSON.

## Claim authority

A positive P14C result authorizes:

> Against a separately frozen explicit adjudication specification, the full ORION-RSE decision implementation conforms to all registered governance cases and strictly outperforms the registered partial-governance implementations without suppressing valid promotion.

It does **not** authorize the claim that the adjudication specification itself is correct for open-ended real science. That requires external blinded adjudication.

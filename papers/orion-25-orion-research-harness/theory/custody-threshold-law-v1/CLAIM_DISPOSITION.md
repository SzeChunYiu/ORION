# Claim disposition — ORION25.CUSTODY_THRESHOLD_LAW.v1

Terminal: **CUSTODY_THRESHOLD_SAFETY_LIVENESS_LAW_PROVED__INDEPENDENT_DOMAIN_REALIZATION_UNTESTED**  
`scientific_authority_delta: NONE`  
Novelty authority: `NONE`

## Closed

- Exact compromise-safety condition `q > f`.
- Exact availability-liveness condition `q <= n-a`.
- Exact feasibility law `n >= f+a+1` and full threshold interval `f+1 <= q <= n-a`.
- Governance-quotient boundary: correlated keys under one controlling principal count as one domain.
- Explicit separation between cryptographic authorization and scientific truth.

## Existing adverse boundary preserved

The full-key-compromise failure remains load-bearing. This theorem explains why additional signatures do not repair common-control compromise unless custody itself is distributed across independent domains.

## Remaining top-tier gate

Instantiate the law prospectively in at least two native real systems with genuinely independent custody/governance, retained compromise and availability failures, and a scientific-validity endpoint not reducible to signature success.
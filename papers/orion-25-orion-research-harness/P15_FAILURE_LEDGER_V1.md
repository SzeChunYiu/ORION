# ORION-25 Failure Ledger (V1)

**Stable ID:** ORION-ORION-25-FAILURE-LEDGER  
**Created:** 2026-08-24 (issue #1086 ORION-23–ORION-25 lane)  
**Scope:** retained record of blocked, adverse, null and harmful runs and
boundaries for the ORION-25 research-harness instrument. Threat-model counterpart:
`manuscript/chapters/02-threat-model.tex` (adversary capabilities T7/T8 — a
host/network/quota/tool failure converted into a scientific datum, and
inconvenient failures omitted or downgraded). This ledger is the operational
answer to T8: failures are recorded, not dropped.

## Entries

### F1. P15A external acquisition — BLOCKED (adverse-adjacent, fail-closed)

- Artifact: `P15A_ACQUISITION_PREFLIGHT_V1.json`
- Terminal: `P15A_ACQUISITION_BLOCKED_NO_SCIENTIFIC_RESULT`
  (historical; superseded by `P15_ACTIVE_CLAIM_AUTHORITY_V3.json`)
- `execution_authorized=false`; all seven required external artifacts absent;
  no trusted external custody verifier configured.
- Disposition: retained verbatim; never relabelled as external validation.

### F2. Full key-set compromise — adverse boundary result (retained)

- Artifact: `top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md`
- A-COMPROMISE-FULL: **6 attempts, 0 detections at the signature layer**
  (frozen honest-negative expectation — signatures are evidence about the key
  set, not about custody or fact truth).
- CHAIN_AS_SCIENCE arm false-promotes the compromised chains **6/6**;
  CHAIN_PLUS_SEI also false-promotes **6/6**; with the base-corpus hostile
  additions the total chain-as-science false promotions reach **12**.
- Genuine (uncompromised) chains: 22/22 verified. Adversarial manipulation
  arms (TRUNCATE / SUBSTITUTE / SPLICE / REORDER / REPLAY / STALE): detection
  100%; scientific-field leakage 0; valid-workload false rejections 0.
- Disposition: this is the paper's own recorded failure mode of treating
  provenance as scientific truth. Retained verbatim;
  `SIGNATURE_PROVES_SCIENTIFIC_TRUTH` and `KEY_CUSTODY_VERIFIED` remain
  forbidden states in the active authority.

### F3. External replication / production-scale / runtime-matrix — NOT RUN

- `remaining_external_requirements` in `P15_ACTIVE_CLAIM_AUTHORITY_V3.json`:
  production-scale host-and-process fault campaign; runtime/storage and
  false-rejection overhead characterization; clean-environment independent
  replay; final current-nearest-work refresh; final manuscript/evidence/
  environment/PDF binding.
- Issue #1086's heavier boxes (>=30 public workloads, >=20 upstream failure
  cases, three locked runtime images; feature-complete shared package with
  ORION-03; OSI license and versioned release) are **OPEN**, not satisfied.

### F4. Retained-run policy

- No external campaign runs exist for ORION-25 to date, so there are no null or
  harmful external run rows yet; this ledger starts with the internal blocked
  and adverse entries above.
- Policy: any future null, harmful, reverted or aborted run of this
  instrument must be appended here in the same PR as its result, with
  terminal, artifacts and counts verbatim. Failures are never deleted,
  downgraded to "missing rows", or summarized away.

## Boundary

This ledger adds no scientific authority
(`scientific_authority_delta: NONE`). It records what failed, what is
blocked, and what has not been run, so that the bounded positive terminals in
`P15_ACTIVE_CLAIM_AUTHORITY_V3.json` cannot be read as broader than they are.

# P6 real transition audit result receipt V1

**Run:** GitHub Actions `32660765126` (pull_request, head `5ebd4e050950cf0f484c93f1b503218905c85bf3`, conclusion `success`)  
**Artifact:** `p6-real-transition-audit-v1`, artifact ID `9498743691`  
**Artifact ZIP SHA-256:** `98f61dea6615963428f36c9874897ea95dfb0e03d791af61c8f7d5e2bda19b56`  
**Primary terminal:** `P6_REAL_TRANSITION_AUDIT_V1_SUPPORTED`  
**Independent terminal:** `P6_REAL_TRANSITION_AUDIT_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** independent checker reproduces all `16` gold dispositions (`exact_gold_agreement: true`)

## Exact binding

- protocol SHA-256: `bed210611bd7b3feb72e842594d11b8b44a7898c142d15f446f69a468268ac14`
- frozen cases SHA-256: `1c75ca9980c0539a2e2afe78c2538173508460191805c6fe2b8854717feaac97`
- frozen gold SHA-256: `be7210be8c2407b630f7b7053ec556b4abd8e17535e0c45ac80077740edb34df`
- primary receipt SHA-256: `fc3c605165a08c31682805f488dc8a46c346d3f4cf392d4ecef689aa9612b9ac`
- independent receipt SHA-256: `1ffdc8e5c78d5d1cfa9563da243ac3fe0d5c1ab71a805b26037a1b867814f83e`
- deterministic primary replay: GREEN (workflow step `Verify deterministic primary replay` = `success`)
- cross-platform determinism: the primary `receipt_sha256` above is byte-identical to a local replay of `run_real_transition_audit_v1.py` against the same frozen trio on a separate host (macOS/CPython 3.13) before the CI run executed.
- `source_token_audit`: GREEN (primary and independent)

## Case-repair provenance

This is the audit's first green execution. Earlier runs failed at `audit_source` on `RC-UNCHANGED`: its frozen source (`P7_REAL_REGIME_SOURCES_2026-08-23.md`, documenting the public RO-Crate `1.2 -> 1.3` transition and its Bioschemas URI rebindings) never contained the literal `Schema.org`. Commit `502ca72` applied the same repair class as `fd10f0d1` (align the required token to the source's actual language): `Schema.org` -> `bioschemas.org`. No protocol, gold, disposition-flag, or case-semantic change; the frozen trio above is otherwise unchanged.

## Result — heterogeneous real transition audit

Across `16` frozen cases in `4` real-domain families (`4` each: `rocrate-standard`, `p9-artifact-recovery`, `p10-native-coverage`, `p15-provenance-import`):

- epistemic-transition gate (upper layer): `1.0` exact accuracy, `0` unsafe false-admissible, `0` unnecessary reopen, `0` authority laundering — perfect in every family;
- donor-only gate (lower layer): `0.4375` accuracy with `9` unsafe false-admissible decisions and `1` authority-laundering decision; unsafe in all `4` families (`3`/`2`/`2`/`2`), `donor_unsafe_family_count: 4`;
- the independent checker's own lower-layer unsafe counts per family (`3`/`2`/`2`/`2`) agree exactly.

The audit separates real regime-transition admissibility (witness/alias/obligation-aware) from donor-permission-only reasoning across four distinct live programme domains: the public RO-Crate standard transition, P9 artifact recovery, P10 native coverage, and P15 provenance import.

## Scientific disposition

P6 now has a machine-checked, replay-stable, independently corroborated audit showing that donor-permission-only reasoning is unsafe in every tested real domain family while the epistemic-transition gate is exact, without becoming unnecessarily conservative (`0` unnecessary reopens).

This result does **not** certify P6's formal structures beyond the frozen 16-case set, does not substitute for theorem-level generalization work already scoped in the promotion programme, and does not by itself move P6 to `TOP_TIER_SUBMISSION_READY`. Manuscript-level claim scoping and donor refresh remain open per #977.
